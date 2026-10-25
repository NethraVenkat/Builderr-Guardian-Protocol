"""Hypothesis Testing Framework for Stage 2A Master Optimization.

Tests H1 through H8 against all 3 public regimes:
H1: Smarter rebalancing (min_trade buffer: 0.015 -> 0.020, 0.025, 0.030)
H2: Risk-adaptive position sizing (inverse vol weighting of top assets)
H3: Faster risk detection (20d vs 50d trend filter)
H4: Improved market re-entry (snapback detection via short momentum)
H5: Defensive signal selection (purge XLE from defensive basket -> pure cash/XLP/XLV)
H6: Turnover-aware order generation (skip rebalancing if targets unchanged)
H7: Sector diversification (cap single sector at 2 assets)
H8: Runtime optimization (pre-parsed closes)

Maintains identical fill rules, slippage, exposure caps, and decision cadence.
"""
import sys
import os
import json
import gzip
import time
import copy
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview
import agent

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

START_CASH = 100000.0

def evaluate_decide_function(decide_fn, label="Candidate"):
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
        errors = 0
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

        t0 = time.perf_counter()

        for i, date in enumerate(eval_dates):
            # 1. Fill pending orders
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
                else:  # sell
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

            # 2. Mark to market
            prices = {t: close_on(t, date) for t in bars}
            prices = {t: p for t, p in prices.items() if p is not None}
            pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
            equity = max(cash + sum(pos_value.values()), 1e-9)
            equity_curve.append(equity)

            # 3. Telemetry
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

            # 4. Decide
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
                orders = decide_fn(market_state, portfolio_state, cash)
            except Exception as e:
                errors += 1
                orders = []

            for o in orders or []:
                try:
                    if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                        pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})
                except:
                    pass

        runtime = time.perf_counter() - t0
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
            "errors": errors,
            "runtime": runtime
        }
    return results

# Benchmark Reference
print("Evaluating Baseline Reference (agent.py)...")
ref_results = evaluate_decide_function(agent.decide, "Reference Agent")

# =========================================================================
# EXPERIMENT H1: Smarter Rebalancing (min_trade threshold tuning)
# =========================================================================
def make_h1_decide(min_trade_pct):
    # Create clone of agent decide with adjusted min_trade_pct
    state = {"_last_rebalance_bar_date": None, "_last_targets": {}}
    def decide_h1(market_state, portfolio_state, cash):
        if not market_state:
            return []
        latest_date = agent._latest_bar_date(market_state)
        if latest_date is None:
            return []
        total_equity = agent.equity(portfolio_state, cash)
        if total_equity <= 0:
            return []
        
        # Check drift
        drifted = agent._has_position_drifted(portfolio_state, total_equity)
        # Check days
        days_since = None
        if state["_last_rebalance_bar_date"]:
            bars = market_state.get("SPY") or market_state.get("QQQ") or []
            dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
            if dates and state["_last_rebalance_bar_date"] in dates:
                days_since = len(dates) - dates.index(state["_last_rebalance_bar_date"]) - 1
        
        should_rebal = (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= 5 or drifted)
        if not should_rebal:
            return []
        targets = agent.target_weights(market_state)
        if not targets:
            return []
        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)

        # Custom orders_to_rebalance with min_trade_pct
        min_trade = total_equity * min_trade_pct
        orders = []
        sell_proceeds = 0.0
        for ticker, pos in positions.items():
            price = prices.get(ticker)
            if price is None or price <= 0:
                continue
            qty = pos["quantity"]
            current_value = qty * price
            target_value = total_equity * targets.get(ticker, 0.0)
            delta = target_value - current_value
            if ticker not in targets:
                sell_qty = int(qty)
                if sell_qty > 0 and current_value >= min_trade:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    sell_proceeds += sell_qty * price
            elif delta < -min_trade:
                sell_qty = min(int(abs(delta) // price), int(qty))
                if sell_qty > 0:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    sell_proceeds += sell_qty * price

        spendable = max(float(cash), 0.0) + (sell_proceeds * 0.98)
        for ticker, weight in sorted(targets.items()):
            price = prices.get(ticker)
            if price is None or price <= 0:
                continue
            current_qty = positions.get(ticker, {}).get("quantity", 0.0)
            current_value = current_qty * price
            target_value = total_equity * weight
            delta = target_value - current_value
            if delta < min_trade:
                continue
            buy_value = min(delta, spendable)
            buy_qty = int(buy_value // price)
            if buy_qty > 0:
                orders.append({"ticker": ticker, "side": "buy", "quantity": buy_qty})
                spendable -= buy_qty * price

        if orders:
            state["_last_rebalance_bar_date"] = latest_date
            state["_last_targets"] = targets
        return orders[:45]
    return decide_h1

# =========================================================================
# EXPERIMENT H5: Defensive Asset Optimization (Purge XLE from defensives)
# =========================================================================
def make_h5_decide(defensive_choice="no_xle"):
    # defensive_choice:
    # "no_xle": (XLP 0.30, XLU 0.25, XLV 0.25, cash 0.20)
    # "pure_cash": (XLP 0.24, XLV 0.24, cash 0.52)
    state = {"_last_rebalance_bar_date": None, "_last_targets": {}}
    
    if defensive_choice == "no_xle":
        custom_defensive = (("XLP", 0.24), ("XLU", 0.24), ("XLV", 0.24)) # 0.72 invested, 0.28 cash
    elif defensive_choice == "conservative":
        custom_defensive = (("XLP", 0.20), ("XLV", 0.20)) # 0.40 invested, 0.60 cash
    else:
        custom_defensive = (("XLP", 0.24), ("XLU", 0.24), ("XLV", 0.20), ("XLE", 0.12))

    def decide_h5(market_state, portfolio_state, cash):
        if not market_state:
            return []
        latest_date = agent._latest_bar_date(market_state)
        if latest_date is None:
            return []
        total_equity = agent.equity(portfolio_state, cash)
        if total_equity <= 0:
            return []
        
        drifted = agent._has_position_drifted(portfolio_state, total_equity)
        days_since = None
        if state["_last_rebalance_bar_date"]:
            bars = market_state.get("SPY") or market_state.get("QQQ") or []
            dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
            if dates and state["_last_rebalance_bar_date"] in dates:
                days_since = len(dates) - dates.index(state["_last_rebalance_bar_date"]) - 1
        
        if not (state["_last_rebalance_bar_date"] is None or days_since is None or days_since >= 5 or drifted):
            return []

        # Target weights with custom defensive
        spy = agent.closes(market_state.get("SPY"))
        qqq = agent.closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return []
        risk_on = bool(
            spy[-1] > agent.sma(spy, 50)
            and qqq[-1] > agent.sma(qqq, 50)
            and agent.realized_vol(qqq, 20) < 0.35
        )
        if not risk_on:
            raw_def = {t: w for t, w in custom_defensive if agent.closes(market_state.get(t))}
            targets = agent._scale_caps(raw_def)
        else:
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
    return decide_h5

# Run Experiments
experiments = {
    "Reference (agent.py)": ref_results,
    "H1: min_trade 2.0%": evaluate_decide_function(make_h1_decide(0.020), "H1_2.0"),
    "H1: min_trade 2.5%": evaluate_decide_function(make_h1_decide(0.025), "H1_2.5"),
    "H1: min_trade 3.0%": evaluate_decide_function(make_h1_decide(0.030), "H1_3.0"),
    "H5: Purge XLE from Defensives": evaluate_decide_function(make_h5_decide("no_xle"), "H5_no_xle"),
    "H5: Conservative Cash/XLP/XLV": evaluate_decide_function(make_h5_decide("conservative"), "H5_conservative"),
}

with open(ROOT / "scratch" / "hypotheses_results.json", "w") as f:
    json.dump(experiments, f, indent=2)

print("\n" + "=" * 105)
print("HYPOTHESIS EXPERIMENT RESULTS ACROSS ALL 3 REGIMES")
print("=" * 105)

for exp_name, exp_res in experiments.items():
    print(f"\nExperiment: {exp_name}")
    print(f"  {'Regime':<20s} {'Return':>10s} {'MaxDD':>10s} {'Sharpe':>10s} {'Calmar':>10s} {'Trades':>8s} {'Turnover':>10s} {'Slippage':>10s}")
    print(f"  {'-'*20:<20s} {'-'*10:>10s} {'-'*10:>10s} {'-'*10:>10s} {'-'*10:>10s} {'-'*8:>8s} {'-'*10:>10s} {'-'*10:>10s}")
    for r_name in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
        r = exp_res[r_name]
        print(f"  {r_name:<20s} {r['ret_pct']:>9.2f}% {r['mdd_pct']:>9.2f}% {r['sharpe']:>10.2f} {r['calmar']:>10.2f} {r['trades']:>8d} {r['turnover']:>9.2f}x ${r['slippage']:>8.2f}")
