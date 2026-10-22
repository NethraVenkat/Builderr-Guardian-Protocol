import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from research.engine.provider import StaticRegimeProvider
import agent

# Load vol_spike_snapback raw data
raw_regimes = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())
regime_data = raw_regimes["vol_spike_snapback"]

provider = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
timeline = provider.get_timeline()

cash = 100_000.0
positions = {} # ticker -> qty
avg_cost = {} # ticker -> avg_cost
realized_pnl = 0.0
total_commissions = 0.0
pending_orders = []

history = [] # list of session records
prev_equity = 100_000.0
peak_equity = 100_000.0

print(f"Total timeline sessions: {len(timeline)}")

for day_idx, (current_date, market_state) in enumerate(provider.stream_daily_slices()):
    today_opens = {}
    today_closes = {}
    for sym, bars in market_state.items():
        if bars and bars[-1]["ts"] == current_date:
            today_opens[sym] = bars[-1]["open"]
            today_closes[sym] = bars[-1]["close"]

    # Fills at OPEN
    sells = [o for o in pending_orders if o.get("side") == "sell"]
    buys = [o for o in pending_orders if o.get("side") == "buy"]
    fills = []

    for order in sells:
        sym = order["ticker"]
        px = today_opens.get(sym, 0.0)
        qty = order["quantity"]
        held = positions.get(sym, 0.0)
        filled_qty = min(qty, held)
        if filled_qty > 0 and px > 0:
            proceeds = filled_qty * px
            cost = filled_qty * avg_cost.get(sym, px)
            pnl = proceeds - cost
            realized_pnl += pnl
            cash += proceeds
            positions[sym] = held - filled_qty
            if positions[sym] <= 1e-9:
                positions.pop(sym, None)
                avg_cost.pop(sym, None)
            fills.append({"sym": sym, "side": "sell", "qty": filled_qty, "px": px, "pnl": pnl})

    for order in buys:
        sym = order["ticker"]
        px = today_opens.get(sym, 0.0)
        qty = order["quantity"]
        if px > 0:
            cost = qty * px
            if cost > cash:
                qty = cash / px
                cost = cash
            if qty > 0:
                prev_held = positions.get(sym, 0.0)
                prev_cost = prev_held * avg_cost.get(sym, px)
                new_held = prev_held + qty
                positions[sym] = new_held
                avg_cost[sym] = (prev_cost + cost) / new_held
                cash -= cost
                fills.append({"sym": sym, "side": "buy", "qty": qty, "px": px})

    pending_orders = []

    # Position values at close
    pos_val_close = sum(positions.get(s, 0.0) * today_closes.get(s, 0.0) for s in positions)
    unrealized_pnl = sum(positions.get(s, 0.0) * (today_closes.get(s, 0.0) - avg_cost.get(s, 0.0)) for s in positions)
    ending_equity = cash + pos_val_close
    daily_pnl = ending_equity - prev_equity
    cum_loss = 100_000.0 - ending_equity
    peak_equity = max(peak_equity, ending_equity)
    drawdown = (peak_equity - ending_equity) / peak_equity * 100.0

    # Position PnL attribution for the day:
    # Day-over-day PnL of each held ticker
    pos_pnl_attrib = {}
    for s, q in positions.items():
        # Change in value from prev close (or open fill) to today close
        c_px = today_closes.get(s, 0.0)
        # Approximate price change impact
        pos_pnl_attrib[s] = q * c_px

    history.append({
        "day": day_idx + 1,
        "date": current_date,
        "cash": cash,
        "positions": dict(positions),
        "pos_val": pos_val_close,
        "starting_equity": prev_equity,
        "ending_equity": ending_equity,
        "daily_pnl": daily_pnl,
        "cum_loss": cum_loss,
        "realized_pnl": realized_pnl,
        "unrealized_pnl": unrealized_pnl,
        "drawdown": drawdown,
        "fills": fills,
    })

    # Invoke agent at CLOSE
    port_dict = {
        "cash": cash,
        "positions": [{"ticker": s, "quantity": q, "avg_cost": avg_cost.get(s, 0.0)} for s, q in positions.items()]
    }
    orders = agent.decide(market_state, port_dict, cash)
    for o in orders or []:
        sym = str(o.get("ticker", "")).strip().upper()
        side = str(o.get("side", "")).strip().lower()
        qty = float(o.get("quantity", 0.0))
        if side in ("buy", "sell") and qty > 0 and sym in market_state:
            pending_orders.append({"ticker": sym, "side": side, "quantity": qty})

    prev_equity = ending_equity

print("\n=== Session-by-Session Attribution for vol_spike_snapback ===")
for h in history[:10]:
    fills_str = ", ".join(f"{f['side'].upper()} {f['qty']:.1f} {f['sym']}@{f['px']:.2f}" for f in h["fills"])
    pos_str = ", ".join(f"{s}:{q:.1f}" for s, q in h["positions"].items())
    print(f"Day {h['day']:02d} ({h['date']}): EndEq=${h['ending_equity']:9.2f} | DailyPnL=${h['daily_pnl']:9.2f} | CumLoss=${h['cum_loss']:9.2f} | DD={h['drawdown']:5.2f}% | Cash=${h['cash']:8.2f} | Pos=[{pos_str[:35]}] | Fills=[{fills_str[:35]}]")

print("\n--- Day 1 to 5 Summary ---")
day5 = history[4]
print(f"End of Day 5 (Index 4, date {day5['date']}):")
print(f"  Ending Equity: ${day5['ending_equity']:.2f}")
print(f"  Cumulative Loss: ${day5['cum_loss']:.2f}")
print(f"  Drawdown on Day 5: {day5['drawdown']:.2f}%")
print(f"  Positions on Day 5: {day5['positions']}")

print("\n--- Day 6 Summary (First rebalance execution after Day 5!) ---")
day6 = history[5]
print(f"End of Day 6 (Index 5, date {day6['date']}):")
print(f"  Ending Equity: ${day6['ending_equity']:.2f}")
print(f"  Cumulative Loss: ${day6['cum_loss']:.2f}")
print(f"  Drawdown on Day 6: {day6['drawdown']:.2f}%")
print(f"  Fills at Day 6 Open: {day6['fills']}")

print("\n--- Trough Session Summary ---")
trough = min(history, key=lambda x: x["ending_equity"])
print(f"Trough on Day {trough['day']} ({trough['date']}):")
print(f"  Ending Equity: ${trough['ending_equity']:.2f}")
print(f"  Cumulative Loss at Trough: ${trough['cum_loss']:.2f}")
print(f"  Drawdown at Trough: {trough['drawdown']:.6f}%")

final = history[-1]
print(f"\nFinal Session (Day {final['day']}):")
print(f"  Ending Equity: ${final['ending_equity']:.2f}")
print(f"  Final Net Loss: ${final['cum_loss']:.2f}")
print(f"  Final Return: {((final['ending_equity'] - 100000.0) / 100000.0) * 100:.6f}%")
