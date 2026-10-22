"""
Forensic P0 Loss-Attribution and Accounting Reconciliation for DEF-V12-06.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from preview import load_decide, _expand, beta, SLIP_LEVERAGED, SLIP_EQUITY, START_CASH

agent_path = Path("agent.py")
raw_regimes = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())
regime = raw_regimes["vol_spike_snapback"]

decide = load_decide(agent_path)
bars = {t: _expand(rows) for t, rows in regime["bars"].items()}
all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
eval_dates = [d for d in all_dates if regime["eval_start"] <= d <= regime["eval_end"]]

cash = START_CASH
positions = {}
avg_cost = {}
equity_curve = []
pending = []
trades = 0

daily_records = []
trade_log = []

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

total_slippage_dollars = 0.0

for i, date in enumerate(eval_dates):
    # 1. Fill pending orders at open
    orders_filled_today = []
    for o in pending:
        px = open_on(o["ticker"], date)
        if px is None:
            continue
        slip_pct = SLIP_LEVERAGED if beta(o["ticker"]) > 1 else SLIP_EQUITY
        if o["side"] == "buy":
            fill = px * (1.0 + slip_pct)
            slip_amt = (fill - px) * o["quantity"]
            qty = o["quantity"]
            cost = fill * qty
            if cost > cash:
                qty = cash / fill if fill > 0 else 0
                cost = fill * qty
                slip_amt = (fill - px) * qty
            if qty <= 0:
                continue
            held = positions.get(o["ticker"], 0.0)
            prev_cost = avg_cost.get(o["ticker"], 0.0) * held
            positions[o["ticker"]] = held + qty
            avg_cost[o["ticker"]] = (prev_cost + cost) / (held + qty)
            cash -= cost
            trades += 1
            total_slippage_dollars += slip_amt
            trade_log.append({
                "date": date, "day_idx": i, "side": "buy", "ticker": o["ticker"],
                "qty": qty, "price": px, "fill": fill, "cost": cost, "slip": slip_amt
            })
        else:
            held = positions.get(o["ticker"], 0.0)
            qty = min(o["quantity"], held)
            if qty <= 0:
                continue
            fill = px * (1.0 - slip_pct)
            slip_amt = (px - fill) * qty
            proceeds = fill * qty
            cost_basis = avg_cost.get(o["ticker"], 0.0) * qty
            realized_pnl = proceeds - cost_basis
            cash += proceeds
            positions[o["ticker"]] = held - qty
            trades += 1
            total_slippage_dollars += slip_amt
            trade_log.append({
                "date": date, "day_idx": i, "side": "sell", "ticker": o["ticker"],
                "qty": qty, "price": px, "fill": fill, "proceeds": proceeds,
                "cost_basis": cost_basis, "realized_pnl": realized_pnl, "slip": slip_amt
            })
    pending = []

    # 2. Mark to market on close
    prices = {t: close_on(t, date) for t in bars if close_on(t, date) is not None}
    pos_val = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions if positions.get(t, 0.0) > 0}
    tot_equity = cash + sum(pos_val.values())
    equity_curve.append(tot_equity)

    daily_records.append({
        "day_idx": i,
        "date": date,
        "cash": cash,
        "pos_val": sum(pos_val.values()),
        "equity": tot_equity,
        "mtm_loss_from_start": tot_equity - START_CASH,
        "positions": {t: (q, prices.get(t, 0.0)) for t, q in positions.items() if q > 0}
    })

    # 3. Agent decide
    market_state = {t: [b for b in bars[t] if b["ts"] <= date] for t in bars}
    portfolio_state = {
        "cash": cash,
        "positions": [
            {"ticker": t, "quantity": q, "avg_cost": avg_cost.get(t, 0.0)}
            for t, q in positions.items() if q > 0
        ],
        "last_prices": prices,
    }
    orders = decide(market_state, portfolio_state, cash)
    for o in orders or []:
        if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
            pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})

# Now perform exact independent accounting
final_equity = equity_curve[-1]
net_regime_loss = final_equity - START_CASH

# Max drawdown
peak = -1e18
mdd_val = 0.0
peak_day = 0
trough_day = 0
mdd_peak_val = 0.0
mdd_trough_val = 0.0

for i, v in enumerate(equity_curve):
    if v > peak:
        peak = v
        peak_idx = i
    dd = (peak - v) / peak if peak > 0 else 0.0
    if dd > mdd_val:
        mdd_val = dd
        mdd_peak_val = peak
        mdd_trough_val = v
        peak_day = peak_idx
        trough_day = i

print("=== INDEPENDENT FINANCIAL ACCOUNTING AUDIT ===")
print(f"Total Scored Sessions: {len(eval_dates)} ({eval_dates[0]} to {eval_dates[-1]})")
print(f"Start Cash:            ${START_CASH:,.2f}")
print(f"Ending Equity:         ${final_equity:,.2f}")
print(f"Net Regime Loss:       ${net_regime_loss:,.2f} ({net_regime_loss/START_CASH*100:.2f}%)")
print(f"Total Trades:          {trades}")
print(f"Total Model Slippage:  ${total_slippage_dollars:,.2f}")
print()
print(f"Max Drawdown (%):      {mdd_val*100:.4f}%")
print(f"Max Drawdown ($):      ${mdd_peak_val - mdd_trough_val:,.2f}")
print(f"MDD Peak Date:         Day {peak_day} ({eval_dates[peak_day]}) @ ${mdd_peak_val:,.2f}")
print(f"MDD Trough Date:       Day {trough_day} ({eval_dates[trough_day]}) @ ${mdd_trough_val:,.2f}")
print()

# First 5 sessions (Day 0, 1, 2, 3, 4, 5)
day5_rec = daily_records[5] # index 5 is 6th session (Day 0 to Day 5)
print(f"Day 5 Close ({day5_rec['date']}) Equity: ${day5_rec['equity']:,.2f}")
print(f"Day 5 MTM Loss from Start:          ${day5_rec['mtm_loss_from_start']:,.2f} ({day5_rec['mtm_loss_from_start']/net_regime_loss*100:.2f}% of total regime loss)")
print()

day6_rec = daily_records[6]
print(f"Day 6 Close ({day6_rec['date']}) Equity: ${day6_rec['equity']:,.2f}")
print(f"Day 6 MTM Loss from Start:          ${day6_rec['mtm_loss_from_start']:,.2f} ({day6_rec['mtm_loss_from_start']/net_regime_loss*100:.2f}% of total regime loss)")
print()

# Day 7 open liquidation
day7_sells = [t for t in trade_log if t["day_idx"] == 7 and t["side"] == "sell"]
day7_proceeds = sum(t["proceeds"] for t in day7_sells)
day7_cost_basis = sum(t["cost_basis"] for t in day7_sells)
day7_realized_loss = sum(t["realized_pnl"] for t in day7_sells)

print(f"Day 7 Open ({eval_dates[7]}) Liquidation of Tech Basket:")
print(f"  Gross Proceeds:      ${day7_proceeds:,.2f}")
print(f"  Original Cost Basis: ${day7_cost_basis:,.2f}")
print(f"  Realized Basket Loss: ${day7_realized_loss:,.2f}")
print(f"  % of Total Net Loss: {day7_realized_loss/net_regime_loss*100:.2f}%")
print(f"  % of Max Drawdown $: {abs(day7_realized_loss)/(mdd_peak_val - mdd_trough_val)*100:.2f}%")
print()

# Per instrument reconciliation
print("=== PER-INSTRUMENT P&L RECONCILIATION ===")
all_tickers = sorted(list(set(t["ticker"] for t in trade_log)))
inst_pnl = {}
tot_realized = 0.0
tot_unrealized = 0.0

final_prices = {t: close_on(t, eval_dates[-1]) for t in all_tickers}

for t in all_tickers:
    t_buys = [x for x in trade_log if x["ticker"] == t and x["side"] == "buy"]
    t_sells = [x for x in trade_log if x["ticker"] == t and x["side"] == "sell"]
    tot_cost = sum(x["cost"] for x in t_buys)
    tot_proc = sum(x["proceeds"] for x in t_sells)
    realized = sum(x["realized_pnl"] for x in t_sells)
    
    held_qty = positions.get(t, 0.0)
    unrealized = (final_prices[t] * held_qty - avg_cost.get(t, 0.0) * held_qty) if held_qty > 0 else 0.0
    
    net_pnl = realized + unrealized
    tot_realized += realized
    tot_unrealized += unrealized
    inst_pnl[t] = {
        "buys": len(t_buys), "sells": len(t_sells),
        "tot_cost": tot_cost, "tot_proc": tot_proc,
        "realized": realized, "unrealized": unrealized, "net_pnl": net_pnl
    }
    print(f"{t:<5} | Cost: ${tot_cost:9.2f} | Proc: ${tot_proc:9.2f} | Realized: ${realized:9.2f} | Unrealized: ${unrealized:9.2f} | Net: ${net_pnl:9.2f}")

sum_net_pnl = tot_realized + tot_unrealized
print("-" * 75)
print(f"Sum of Instrument Net P&L: ${sum_net_pnl:,.2f}")
print(f"Net Portfolio Change:       ${net_regime_loss:,.2f}")
discrepancy = abs(sum_net_pnl - net_regime_loss)
print(f"Reconciliation Discrepancy: ${discrepancy:.6f}")
assert discrepancy < 1e-4, f"P&L Accounting invariant failed! Discrepancy: {discrepancy}"
print("P&L Accounting Conservation: VERIFIED EXACT TO ZERO!")
