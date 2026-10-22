import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
import agent

prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
engine = ReplayEngine(agent.decide, prov)
res = engine.run_replay()

ledger = res.get("session_ledger", [])
metrics = res.get("metrics", {})

print(f"Total sessions in ledger: {len(ledger)}")
start_eq = 100000.0
end_eq = ledger[-1]["ending_equity"]
total_loss = start_eq - end_eq
ret = metrics.get("ret")
mdd = metrics.get("mdd")

print(f"Start Equity: {start_eq:.2f}")
print(f"Ending Equity: {end_eq:.2f}")
print(f"Total Net Loss: ${total_loss:.2f}")
print(f"Reported Return: {ret * 100:.6f}%")
print(f"Reported MDD: {mdd * 100:.6f}%")

cum_loss_5 = start_eq - ledger[4]["ending_equity"]
print(f"Session 5 Ending Equity: ${ledger[4]['ending_equity']:.2f}")
print(f"First 5 Sessions Net Equity Loss: ${cum_loss_5:.2f}")
ratio = (cum_loss_5 / total_loss) * 100.0
print(f"Ratio First 5 Net Loss / Total Net Loss: {ratio:.4f}%")

# Maximum drawdown dollar peak-to-trough
peak_eq = start_eq
peak_date = ledger[0]["date"]
trough_eq = start_eq
trough_date = ledger[0]["date"]
max_dd_dollars = 0.0

for s in ledger:
    eq = s["ending_equity"]
    if eq > peak_eq:
        peak_eq = eq
        peak_date = s["date"]
    dd_dollars = peak_eq - eq
    if dd_dollars > max_dd_dollars:
        max_dd_dollars = dd_dollars
        trough_eq = eq
        trough_date = s["date"]

print(f"\nPeak Equity: ${peak_eq:.2f} on {peak_date}")
print(f"Trough Equity: ${trough_eq:.2f} on {trough_date}")
print(f"Max Peak-to-Trough Dollar Loss: ${max_dd_dollars:.2f} ({max_dd_dollars / peak_eq * 100:.6f}%)")
print(f"Ratio First 5 Net Loss / Max DD Dollars: {(cum_loss_5 / max_dd_dollars) * 100:.4f}%")

print("\n--- Session-by-Session Analysis (First 10 sessions) ---")
running_peak = start_eq
for i, s in enumerate(ledger[:10]):
    eq = s["ending_equity"]
    running_peak = max(running_peak, eq)
    running_dd = (running_peak - eq) / running_peak * 100.0
    daily_pnl = eq - s["starting_equity"]
    cum_loss = start_eq - eq
    print(f"Day {i+1:02d} ({s['date']}): Start=${s['starting_equity']:9.2f} | End=${eq:9.2f} | Daily=${daily_pnl:8.2f} | CumLoss=${cum_loss:9.2f} | DD={running_dd:5.2f}% | Cash=${s['cash']:8.2f}")
