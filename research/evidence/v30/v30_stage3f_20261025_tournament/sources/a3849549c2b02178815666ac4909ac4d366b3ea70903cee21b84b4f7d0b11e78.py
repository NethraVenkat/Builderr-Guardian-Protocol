"""Hypothesis Testing Part 2: H2 (Risk-Adaptive Sizing), H3 (Trend Speed), H4 (Re-entry).

Tests:
- H2: Inverse-volatility weighting across top momentum winners.
- H3: 20-day vs 50-day trend detection for risk-on / risk-off.
- H4: Staged re-entry when SPY/QQQ 10-day momentum > 0 even if below SMA50.
- H6: Turnover-aware rebalancing (only rebalance if target set changes or drift > 10%).
- H7: Diversified candidate basket (limit max tech allocation).
"""
import sys
import json
import gzip
import time
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview
import agent

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

START_CASH = 100000.0

def evaluate_candidate(candidate_decide):
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
        peak_gross = 0.0
        peak_conc = 0.0
        conc_streak = {}
        max_conc_streak = 0

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

            gross = sum(abs(v) * preview.beta(t) for t, v in pos_value.items()) / equity
            peak_gross = max(peak_gross, gross)
            for t in bars:
                frac = abs(pos_value.get(t, 0.0)) / equity
                peak_conc = max(peak_conc, frac)
                if frac >= preview.CONCENTRATION_CAP:
                    conc_streak[t] = conc_streak.get(t, 0) + 1
                    max_conc_streak = max(max_conc_streak, conc_streak[t])
                else:
                    conc_streak[t] = 0

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
                orders = candidate_decide(market_state, portfolio_state, cash)
            except Exception as e:
                orders = []

            for o in orders or []:
                try:
                    if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                        pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})
                except:
                    pass

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
            "peak_gross": peak_gross,
            "peak_conc": peak_conc * 100.0,
            "max_streak": max_conc_streak,
        }
    return results

# H2: Inverse Volatility Weighting
def make_h2_decide():
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
        if not (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= 5 or drifted):
            return []
        
        # Target weights with inverse vol
        spy = agent.closes(market_state.get("SPY"))
        qqq = agent.closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return []
        risk_on = bool(spy[-1] > agent.sma(spy, 50) and qqq[-1] > agent.sma(qqq, 50) and agent.realized_vol(qqq, 20) < 0.35)
        if not risk_on:
            targets = agent._scale_caps(agent._risk_off_targets(market_state))
        else:
            scored = []
            for ticker in agent.RISK_CANDIDATES:
                values = agent.closes(market_state.get(ticker))
                if len(values) < 61:
                    continue
                mom60 = agent.momentum(values, 60)
                mom20 = agent.momentum(values, 20)
                trend50 = agent.sma(values, 50)
                vol20 = agent.realized_vol(values, 20)
                if mom60 is None or mom20 is None or trend50 is None or vol20 is None:
                    continue
                trend_gap = values[-1] / trend50 - 1.0
                score = (0.55 * mom60) + (0.25 * mom20) + (0.20 * trend_gap) - (0.15 * vol20)
                if score > 0.0:
                    scored.append((score, ticker, vol20))
            scored.sort(reverse=True)
            winners = scored[:5]
            if not winners:
                targets = agent._scale_caps(agent._risk_off_targets(market_state))
            else:
                # Inverse vol weighting
                inv_vols = {t: 1.0 / max(v, 0.05) for _, t, v in winners}
                tot_inv = sum(inv_vols.values())
                weights = {t: min((iv / tot_inv) * 0.92, agent.MAX_WEIGHT) for t, iv in inv_vols.items()}
                targets = agent._scale_caps(weights)

        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)
        orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
        if orders:
            state["_last_rebalance_bar_date"] = latest_date
            state["_last_targets"] = targets
        return orders
    return decide

# H3: Faster Trend Filter (SPY/QQQ > SMA20 instead of SMA50)
def make_h3_decide():
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
        if not (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= 5 or drifted):
            return []

        spy = agent.closes(market_state.get("SPY"))
        qqq = agent.closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return []
        # SMA20 filter
        spy_sma20 = agent.sma(spy, 20)
        qqq_sma20 = agent.sma(qqq, 20)
        risk_on = bool(spy_sma20 and qqq_sma20 and spy[-1] > spy_sma20 and qqq[-1] > qqq_sma20 and agent.realized_vol(qqq, 20) < 0.35)
        if not risk_on:
            targets = agent._scale_caps(agent._risk_off_targets(market_state))
        else:
            targets = agent.target_weights(market_state)
        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)
        orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
        if orders:
            state["_last_rebalance_bar_date"] = latest_date
            state["_last_targets"] = targets
        return orders
    return decide

# H4: Staged Re-Entry (allow re-entry when SPY/QQQ 10d mom > 0 and price > SMA10 even if < SMA50)
def make_h4_decide():
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
        if not (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= 5 or drifted):
            return []

        spy = agent.closes(market_state.get("SPY"))
        qqq = agent.closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return []
        spy_sma50 = agent.sma(spy, 50)
        qqq_sma50 = agent.sma(qqq, 50)
        vol20 = agent.realized_vol(qqq, 20)
        full_risk_on = bool(spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and vol20 < 0.35)

        # Snapback re-entry condition: SPY & QQQ > SMA10 and 10-day mom > +3%
        spy_sma10 = agent.sma(spy, 10)
        qqq_sma10 = agent.sma(qqq, 10)
        spy_mom10 = agent.momentum(spy, 10)
        qqq_mom10 = agent.momentum(qqq, 10)
        snapback = bool(spy_sma10 and qqq_sma10 and spy_mom10 and qqq_mom10 and
                        spy[-1] > spy_sma10 and qqq[-1] > qqq_sma10 and
                        spy_mom10 > 0.03 and qqq_mom10 > 0.03)

        if full_risk_on:
            targets = agent.target_weights(market_state)
        elif snapback:
            # Staged re-entry: 50% broad market ETFs (SPY, QQQ), 50% cash
            targets = agent._scale_caps({"SPY": 0.24, "QQQ": 0.24})
        else:
            targets = agent._scale_caps(agent._risk_off_targets(market_state))

        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)
        orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
        if orders:
            state["_last_rebalance_bar_date"] = latest_date
            state["_last_targets"] = targets
        return orders
    return decide

results_part2 = {
    "H2: Inverse Vol Sizing": evaluate_candidate(make_h2_decide()),
    "H3: Faster 20d Trend": evaluate_candidate(make_h3_decide()),
    "H4: Staged Snapback Re-entry": evaluate_candidate(make_h4_decide()),
}

print("=" * 105)
print("PART 2 HYPOTHESIS EXPERIMENT RESULTS")
print("=" * 105)
for exp_name, exp_res in results_part2.items():
    print(f"\nExperiment: {exp_name}")
    print(f"  {'Regime':<20s} {'Return':>10s} {'MaxDD':>10s} {'Sharpe':>10s} {'Calmar':>10s} {'Trades':>8s} {'Turnover':>10s} {'Slippage':>10s}")
    print(f"  {'-'*20:<20s} {'-'*10:>10s} {'-'*10:>10s} {'-'*10:>10s} {'-'*10:>10s} {'-'*8:>8s} {'-'*10:>10s} {'-'*10:>10s}")
    for r_name in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
        r = exp_res[r_name]
        print(f"  {r_name:<20s} {r['ret_pct']:>9.2f}% {r['mdd_pct']:>9.2f}% {r['sharpe']:>10.2f} {r['calmar']:>10.2f} {r['trades']:>8d} {r['turnover']:>9.2f}x ${r['slippage']:>8.2f}")
