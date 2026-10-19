"""Hypothesis H6 & Rebalancing Cadence Exploration.

Tests:
- Rebalance cadence: 3 days, 5 days (default), 7 days, 10 days
- Pure drift-based rebalancing (no time-based timer, only rebalance when a position drifts > 27% or targets change)
"""
import sys
import json
import gzip
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview
import agent

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

START_CASH = 100000.0

def evaluate_cadence(cadence_days):
    state = {"_last_rebalance_bar_date": None, "_last_targets": {}}
    def decide(market_state, portfolio_state, cash):
        if not market_state:
            return []
        latest_date = agent._latest_bar_date(market_state)
        if latest_date is None:
            return []
        total_equity = agent.equity(portfolio_state, cash)
        if total_equity <= 0:
            return []
        days_since = None
        if state["_last_rebalance_bar_date"]:
            bars = market_state.get("SPY") or []
            dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
            if dates and state["_last_rebalance_bar_date"] in dates:
                days_since = len(dates) - dates.index(state["_last_rebalance_bar_date"]) - 1
        drifted = agent._has_position_drifted(portfolio_state, total_equity)
        
        if cadence_days is None:
            # Pure drift / target change trigger
            should_rebal = (state["_last_rebalance_bar_date"] is None or drifted)
        else:
            should_rebal = (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= cadence_days or drifted)
            
        if not should_rebal:
            return []
            
        targets = agent.target_weights(market_state)
        if not targets:
            return []
            
        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)
        orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
        if orders:
            state["_last_rebalance_bar_date"] = latest_date
            state["_last_targets"] = targets
        return orders

    # Run through preview harness
    results = {}
    for name, reg in regimes.items():
        bars = {t: preview._expand(rows) for t, rows in reg["bars"].items()}
        all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
        eval_dates = [d for d in all_dates if reg["eval_start"] <= d <= reg["eval_end"]]

        cash = START_CASH
        positions = {}
        avg_cost = {}
        equity_curve = []
        trades = 0
        slippage_cost = 0.0
        turnover_notional = 0.0
        pending = []

        def close_on(ticker: str, date: str):
            for b in bars.get(ticker, []):
                if b["ts"] == date:
                    return b["close"]
            return None

        def open_on(ticker: str, date: str):
            for b in bars.get(ticker, []):
                if b["ts"] == date:
                    return b["open"]
            return None

        for i, date in enumerate(eval_dates):
            for o in pending:
                px = open_on(o["ticker"], date)
                if px is None:
                    continue
                slip = preview.SLIP_LEVERAGED if preview.beta(o["ticker"]) > 1 else preview.SLIP_EQUITY
                if o["side"] == "buy":
                    fill = px * (1 + slip)
                    qty = o["quantity"]
                    cost = fill * qty
                    if cost > cash:
                        qty = cash / fill if fill > 0 else 0
                        cost = fill * qty
                    if qty <= 0:
                        continue
                    held = positions.get(o["ticker"], 0.0)
                    prev_cost = avg_cost.get(o["ticker"], 0.0) * held
                    positions[o["ticker"]] = held + qty
                    avg_cost[o["ticker"]] = (prev_cost + cost) / (held + qty)
                    cash -= cost
                    trades += 1
                    slippage_cost += px * slip * qty
                    turnover_notional += cost
                else:
                    held = positions.get(o["ticker"], 0.0)
                    qty = min(o["quantity"], held)
                    if qty <= 0:
                        continue
                    fill = px * (1 - slip)
                    cash += fill * qty
                    positions[o["ticker"]] = held - qty
                    trades += 1
                    slippage_cost += px * slip * qty
                    turnover_notional += fill * qty
            pending = []
            positions = {t: q for t, q in positions.items() if q > 1e-6}

            prices = {t: close_on(t, date) for t in bars}
            prices = {t: p for t, p in prices.items() if p is not None}
            pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
            equity = max(cash + sum(pos_value.values()), 1e-9)
            equity_curve.append(equity)

            market_state = {t: [b for b in bs if b["ts"] <= date] for t, bs in bars.items()}
            portfolio_state = {
                "cash": cash,
                "positions": [
                    {"ticker": t, "quantity": q, "avg_cost": avg_cost.get(t, 0.0)}
                    for t, q in positions.items() if q > 0
                ],
                "last_prices": prices,
            }
            try:
                orders = decide(market_state, portfolio_state, cash)
            except:
                orders = []

            for o in orders or []:
                if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                    pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})

        ret = equity_curve[-1] / START_CASH - 1.0
        mdd = preview._max_drawdown(equity_curve)
        sharpe = preview._sharpe(equity_curve)
        calmar = (preview._annualize(ret, len(equity_curve)) / mdd) if mdd > 1e-9 else 0.0
        turnover = turnover_notional / (2.0 * statistics.mean(equity_curve))

        results[name] = {
            "ret_pct": ret * 100.0,
            "mdd_pct": mdd * 100.0,
            "sharpe": sharpe,
            "calmar": calmar,
            "trades": trades,
            "turnover": turnover,
            "slippage": slippage_cost,
        }
    return results

print("=" * 105)
print("REBALANCING CADENCE SENSITIVITY")
print("=" * 105)

cadences = [3, 5, 7, 10]
for c in cadences:
    res = evaluate_cadence(c)
    print(f"\nCadence: Every {c} Days")
    for r_name in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
        r = res[r_name]
        print(f"  {r_name:<20s} Ret: {r['ret_pct']:>6.2f}% | MaxDD: {r['mdd_pct']:>6.2f}% | Trades: {r['trades']:>3d} | Turnover: {r['turnover']:>5.2f}x | Slippage: ${r['slippage']:>6.2f}")
