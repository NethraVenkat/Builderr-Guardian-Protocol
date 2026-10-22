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

# Track per-ticker cumulative realized PnL and current unrealized PnL
ticker_stats = {}

for date in eval_dates:
    for o in pending:
        px = open_on(o["ticker"], date)
        if px is None:
            continue
        slip = SLIP_LEVERAGED if beta(o["ticker"]) > 1 else SLIP_EQUITY
        sym = o["ticker"]
        if sym not in ticker_stats:
            ticker_stats[sym] = {"buys": 0, "sells": 0, "total_cost": 0.0, "total_proceeds": 0.0, "realized_pnl": 0.0, "first_buy": date, "last_date": date}
        stats = ticker_stats[sym]
        stats["last_date"] = date
        if o["side"] == "buy":
            fill = px * (1 + slip)
            qty = o["quantity"]
            cost = fill * qty
            if cost > cash:
                qty = cash / fill if fill > 0 else 0
                cost = fill * qty
            if qty <= 0:
                continue
            held = positions.get(sym, 0.0)
            prev_cost = avg_cost.get(sym, 0.0) * held
            positions[sym] = held + qty
            avg_cost[sym] = (prev_cost + cost) / (held + qty)
            cash -= cost
            stats["buys"] += 1
            stats["total_cost"] += cost
        else:
            held = positions.get(sym, 0.0)
            qty = min(o["quantity"], held)
            if qty <= 0:
                continue
            fill = px * (1 - slip)
            cash += fill * qty
            positions[sym] = held - qty
            stats["sells"] += 1
            stats["total_proceeds"] += fill * qty
            c_basis = avg_cost.get(sym, 0.0) * qty
            stats["realized_pnl"] += (fill * qty) - c_basis

    pending = []
    positions = {t: q for t, q in positions.items() if q > 1e-9}
    prices = {t: close_on(t, date) for t in bars if close_on(t, date) is not None}
    pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
    equity = max(cash + sum(pos_value.values()), 1e-9)
    equity_curve.append(equity)

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

# End of regime position accounting
last_date = eval_dates[-1]
final_prices = {t: close_on(t, last_date) for t in bars if close_on(t, last_date) is not None}
print("=== PER-INSTRUMENT P&L ATTRIBUTION IN vol_spike_snapback ===")
print(f"{'Ticker':<8} | {'Buys':>4} | {'Sells':>5} | {'TotCost ($)':>12} | {'TotProc ($)':>12} | {'Realized ($)':>12} | {'Unrealized ($)':>14} | {'Total PnL ($)':>14}")
print("-" * 100)

tot_realized = 0.0
tot_unrealized = 0.0
tot_pnl_all = 0.0

for sym, stats in sorted(ticker_stats.items()):
    held = positions.get(sym, 0.0)
    cur_px = final_prices.get(sym, 0.0)
    unrealized = (held * cur_px) - (held * avg_cost.get(sym, 0.0))
    tot_pnl = stats["realized_pnl"] + unrealized
    tot_realized += stats["realized_pnl"]
    tot_unrealized += unrealized
    tot_pnl_all += tot_pnl
    print(f"{sym:<8} | {stats['buys']:4d} | {stats['sells']:5d} | ${stats['total_cost']:11.2f} | ${stats['total_proceeds']:11.2f} | ${stats['realized_pnl']:11.2f} | ${unrealized:13.2f} | ${tot_pnl:13.2f}")

print("-" * 100)
print(f"{'TOTAL':<8} | {'':>4} | {'':>5} | {'':>12} | {'':>12} | ${tot_realized:11.2f} | ${tot_unrealized:13.2f} | ${tot_pnl_all:13.2f}")
print(f"Ending Equity: ${equity_curve[-1]:.2f}")
print(f"Net P&L ($100k start): ${equity_curve[-1] - 100000.0:.2f}")
