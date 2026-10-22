import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
import preview
from preview import load_decide, _expand, beta, SLIP_LEVERAGED, SLIP_EQUITY, START_CASH, CONCENTRATION_CAP

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
errors = 0

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

session_records = []
peak_equity = START_CASH

for i, date in enumerate(eval_dates):
    start_cash_of_day = cash
    fills_today = []
    
    # 1. Fill yesterday's orders at today's open
    for o in pending:
        px = open_on(o["ticker"], date)
        if px is None:
            continue
        slip = SLIP_LEVERAGED if beta(o["ticker"]) > 1 else SLIP_EQUITY
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
            fills_today.append({"ticker": o["ticker"], "side": "buy", "qty": qty, "px": px, "fill": fill, "cost": cost})
        else: # sell
            held = positions.get(o["ticker"], 0.0)
            qty = min(o["quantity"], held)
            if qty <= 0:
                continue
            fill = px * (1 - slip)
            cash += fill * qty
            positions[o["ticker"]] = held - qty
            trades += 1
            cost_basis = avg_cost.get(o["ticker"], 0.0) * qty
            realized = (fill * qty) - cost_basis
            fills_today.append({"ticker": o["ticker"], "side": "sell", "qty": qty, "px": px, "fill": fill, "proceeds": fill * qty, "realized": realized})

    pending = []

    # Clean positions
    positions = {t: q for t, q in positions.items() if q > 1e-9}

    # 2. Mark to market on today's close
    prices = {t: close_on(t, date) for t in bars}
    prices = {t: p for t, p in prices.items() if p is not None}
    pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
    equity = cash + sum(pos_value.values())
    equity = max(equity, 1e-9)
    equity_curve.append(equity)
    
    prev_eq = equity_curve[-2] if len(equity_curve) >= 2 else START_CASH
    daily_pnl = equity - prev_eq
    cum_loss = START_CASH - equity
    peak_equity = max(peak_equity, equity)
    drawdown = (peak_equity - equity) / peak_equity * 100.0

    session_records.append({
        "day_num": i + 1,
        "date": date,
        "start_equity": prev_eq,
        "end_equity": equity,
        "daily_pnl": daily_pnl,
        "cum_loss": cum_loss,
        "drawdown_pct": drawdown,
        "cash": cash,
        "positions": {t: {"qty": round(q, 4), "val": round(pos_value[t], 2), "price": round(prices[t], 2)} for t, q in positions.items()},
        "fills": fills_today,
    })

    # 4. Ask bot for orders
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
        try:
            if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})
        except (KeyError, TypeError, ValueError):
            errors += 1

print("=== EXACT E0 SESSION-BY-SESSION RECONCILIATION ===")
total_regime_loss = START_CASH - equity_curve[-1]
print(f"Total Regime Loss: ${total_regime_loss:.2f}")

for s in session_records[:10]:
    pos_summary = ", ".join(f"{t}: ${d['val']:.0f}" for t, d in s["positions"].items())
    fills_summary = ", ".join(f"{f['side'].upper()} {f['qty']:.0f} {f['ticker']}" for f in s["fills"])
    print(f"Day {s['day_num']:02d} ({s['date']}): EndEq=${s['end_equity']:9.2f} | Daily=${s['daily_pnl']:9.2f} | CumLoss=${s['cum_loss']:9.2f} | DD={s['drawdown_pct']:5.2f}% | Cash=${s['cash']:8.2f} | Fills=[{fills_summary}] | Pos=[{pos_summary}]")

print("\n--- Day 5 (index 4) vs Day 6 (index 5) vs Day 7 (index 6) Analysis ---")
s5 = session_records[4]
s6 = session_records[5]
s7 = session_records[6]
print(f"Day 5 ({s5['date']}): CumLoss=${s5['cum_loss']:.2f}, Fraction of Total Loss = {s5['cum_loss'] / total_regime_loss * 100:.2f}%")
print(f"Day 6 ({s6['date']}): CumLoss=${s6['cum_loss']:.2f}, Fraction of Total Loss = {s6['cum_loss'] / total_regime_loss * 100:.2f}%")
print(f"Day 7 ({s7['date']}): CumLoss=${s7['cum_loss']:.2f}, Fraction of Total Loss = {s7['cum_loss'] / total_regime_loss * 100:.2f}%")

# Check if there is any date range where loss is 12,401.57:
for i in range(len(session_records)):
    loss_i = START_CASH - session_records[i]["end_equity"]
    pct = loss_i / total_regime_loss * 100.0
    if 70.0 <= pct <= 85.0:
        print(f"-> Day {session_records[i]['day_num']} ({session_records[i]['date']}): Loss = ${loss_i:.2f} ({pct:.2f}%)")
