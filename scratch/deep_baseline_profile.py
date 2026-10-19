"""Deep baseline profiling and day-by-day telemetry for baseline.py and agent.py.

Extracts:
- Total return
- Maximum drawdown
- Sharpe & Calmar
- Turnover
- Executed trade count
- Transaction costs (dollars)
- Average portfolio gross exposure
- Peak gross beta exposure
- Peak concentration
- Cash utilization (invested fraction)
- Runtime per regime
- Order rejection rate
- Daily trajectory logs for attribution analysis
"""
import sys
import os
import json
import gzip
import time
import importlib.util
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview

START_CASH = 100000.0
SLIP_EQUITY = 0.0005
SLIP_LEVERAGED = 0.0010

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

def run_deep_profile(strategy_path: Path):
    decide_func = preview.load_decide(strategy_path)
    regime_metrics = {}
    day_by_day_logs = {}

    for name, reg in regimes.items():
        # Fresh reload
        decide = preview.load_decide(strategy_path)
        bars = {t: preview._expand(rows) for t, rows in reg["bars"].items()}
        all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
        eval_dates = [d for d in all_dates if reg["eval_start"] <= d <= reg["eval_end"]]

        cash = START_CASH
        positions = {}
        avg_cost = {}
        equity_curve = []
        gross_curve = []
        invested_curve = []
        slippage_cost_total = 0.0
        turnover_notional = 0.0
        trades = 0
        total_proposed_orders = 0
        rejected_orders = 0
        pending = []
        errors = 0
        peak_gross = 0.0
        peak_conc = 0.0
        conc_streak = {}
        max_conc_streak = 0
        day_logs = []

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
            fills_today = []
            for o in pending:
                px = open_on(o["ticker"], date)
                if px is None:
                    rejected_orders += 1
                    continue
                is_lev = preview.beta(o["ticker"]) > 1
                slip = SLIP_LEVERAGED if is_lev else SLIP_EQUITY
                if o["side"] == "buy":
                    fill = px * (1 + slip)
                    qty = o["quantity"]
                    cost = fill * qty
                    if cost > cash:
                        qty = cash / fill if fill > 0 else 0
                        cost = fill * qty
                    if qty <= 0:
                        rejected_orders += 1
                        continue
                    held = positions.get(o["ticker"], 0.0)
                    prev_cost = avg_cost.get(o["ticker"], 0.0) * held
                    positions[o["ticker"]] = held + qty
                    avg_cost[o["ticker"]] = (prev_cost + cost) / (held + qty)
                    cash -= cost
                    trades += 1
                    slip_dollars = px * slip * qty
                    slippage_cost_total += slip_dollars
                    turnover_notional += cost
                    fills_today.append({"ticker": o["ticker"], "side": "buy", "qty": qty, "px": fill, "slip": slip_dollars})
                else:  # sell
                    held = positions.get(o["ticker"], 0.0)
                    qty = min(o["quantity"], held)
                    if qty <= 0:
                        rejected_orders += 1
                        continue
                    fill = px * (1 - slip)
                    cash += fill * qty
                    positions[o["ticker"]] = held - qty
                    trades += 1
                    slip_dollars = px * slip * qty
                    slippage_cost_total += slip_dollars
                    turnover_notional += fill * qty
                    fills_today.append({"ticker": o["ticker"], "side": "sell", "qty": qty, "px": fill, "slip": slip_dollars})
            pending = []

            # Clean zero positions
            positions = {t: q for t, q in positions.items() if q > 1e-6}

            # 2. Mark to market on today's close
            prices = {t: close_on(t, date) for t in bars}
            prices = {t: p for t, p in prices.items() if p is not None}
            pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
            tot_pos_val = sum(pos_value.values())
            equity = cash + tot_pos_val
            equity = max(equity, 1e-9)
            equity_curve.append(equity)

            # 3. Risk telemetry
            gross = sum(abs(v) * preview.beta(t) for t, v in pos_value.items()) / equity
            peak_gross = max(peak_gross, gross)
            gross_curve.append(gross)
            invested_curve.append(tot_pos_val / equity)

            for t in bars:
                frac = abs(pos_value.get(t, 0.0)) / equity
                peak_conc = max(peak_conc, frac)
                if frac >= preview.CONCENTRATION_CAP:
                    conc_streak[t] = conc_streak.get(t, 0) + 1
                    max_conc_streak = max(max_conc_streak, conc_streak[t])
                else:
                    conc_streak[t] = 0

            # 4. Ask bot for orders
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
            except Exception as e:
                errors += 1
                orders = []

            order_list = orders or []
            total_proposed_orders += len(order_list)
            for o in order_list:
                try:
                    if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                        pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})
                    else:
                        rejected_orders += 1
                except:
                    rejected_orders += 1

            day_logs.append({
                "date": date,
                "equity": equity,
                "cash": cash,
                "gross_beta": gross,
                "invested_pct": tot_pos_val / equity,
                "fills": fills_today,
                "positions": {t: round(q, 2) for t, q in positions.items()},
                "proposed_orders": len(order_list)
            })

        runtime = time.perf_counter() - t0
        ret = equity_curve[-1] / START_CASH - 1.0 if equity_curve else 0.0
        mdd = preview._max_drawdown(equity_curve)
        sharpe = preview._sharpe(equity_curve)
        calmar = (preview._annualize(ret, len(equity_curve)) / mdd) if mdd > 1e-9 else 0.0
        avg_equity = statistics.mean(equity_curve)
        turnover = turnover_notional / (2.0 * avg_equity)
        rejection_rate = rejected_orders / total_proposed_orders if total_proposed_orders > 0 else 0.0

        regime_metrics[name] = {
            "name": name,
            "days": len(eval_dates),
            "start_cash": START_CASH,
            "final_equity": equity_curve[-1],
            "ret_pct": ret * 100.0,
            "mdd_pct": mdd * 100.0,
            "sharpe": sharpe,
            "calmar": calmar,
            "turnover": turnover,
            "trades": trades,
            "slippage_costs_usd": slippage_cost_total,
            "avg_gross_exposure": statistics.mean(gross_curve),
            "peak_gross_beta": peak_gross,
            "peak_concentration_pct": peak_conc * 100.0,
            "max_conc_streak": max_conc_streak,
            "avg_cash_utilization_pct": statistics.mean(invested_curve) * 100.0,
            "runtime_s": runtime,
            "total_proposed_orders": total_proposed_orders,
            "rejected_orders": rejected_orders,
            "rejection_rate_pct": rejection_rate * 100.0,
            "errors": errors
        }
        day_by_day_logs[name] = day_logs

    return regime_metrics, day_by_day_logs

print("Profiling Baseline...")
base_metrics, base_logs = run_deep_profile(ROOT / "baseline.py")

print("Profiling Reference Agent...")
agent_metrics, agent_logs = run_deep_profile(ROOT / "agent.py")

with open(ROOT / "scratch" / "deep_profile_metrics.json", "w") as f:
    json.dump({"baseline": base_metrics, "agent": agent_metrics}, f, indent=2)

with open(ROOT / "scratch" / "agent_day_logs.json", "w") as f:
    json.dump(agent_logs, f, indent=2)

print("\n" + "=" * 90)
print("DEEP BASELINE VS REFERENCE AGENT METRICS SUMMARY")
print("=" * 90)

for reg_name in base_metrics:
    b = base_metrics[reg_name]
    a = agent_metrics[reg_name]
    print(f"\nRegime: {reg_name} ({b['days']} days)")
    print(f"  {'Metric':<28s} {'Baseline':>16s} {'Reference Agent':>16s}")
    print(f"  {'-'*28:<28s} {'-'*16:>16s} {'-'*16:>16s}")
    print(f"  {'Return':<28s} {b['ret_pct']:>15.2f}% {a['ret_pct']:>15.2f}%")
    print(f"  {'Max Drawdown':<28s} {b['mdd_pct']:>15.2f}% {a['mdd_pct']:>15.2f}%")
    print(f"  {'Sharpe':<28s} {b['sharpe']:>16.2f} {a['sharpe']:>16.2f}")
    print(f"  {'Calmar':<28s} {b['calmar']:>16.2f} {a['calmar']:>16.2f}")
    print(f"  {'Trades':<28s} {b['trades']:>16d} {a['trades']:>16d}")
    print(f"  {'Turnover':<28s} {b['turnover']:>15.2f}x {a['turnover']:>15.2f}x")
    print(f"  {'Slippage Costs ($)':<28s} ${b['slippage_costs_usd']:>14.2f} ${a['slippage_costs_usd']:>14.2f}")
    print(f"  {'Avg Gross Beta':<28s} {b['avg_gross_exposure']:>15.2f}x {a['avg_gross_exposure']:>15.2f}x")
    print(f"  {'Peak Gross Beta':<28s} {b['peak_gross_beta']:>15.2f}x {a['peak_gross_beta']:>15.2f}x")
    print(f"  {'Peak Concentration':<28s} {b['peak_concentration_pct']:>15.1f}% {a['peak_concentration_pct']:>15.1f}%")
    print(f"  {'Avg Cash Utilization':<28s} {b['avg_cash_utilization_pct']:>15.1f}% {a['avg_cash_utilization_pct']:>15.1f}%")
    print(f"  {'Runtime (s)':<28s} {b['runtime_s']:>15.4f}s {a['runtime_s']:>15.4f}s")
    print(f"  {'Proposed Orders':<28s} {b['total_proposed_orders']:>16d} {a['total_proposed_orders']:>16d}")
    print(f"  {'Rejected Orders':<28s} {b['rejected_orders']:>16d} {a['rejected_orders']:>16d}")
    print(f"  {'Rejection Rate':<28s} {b['rejection_rate_pct']:>15.1f}% {a['rejection_rate_pct']:>15.1f}%")
