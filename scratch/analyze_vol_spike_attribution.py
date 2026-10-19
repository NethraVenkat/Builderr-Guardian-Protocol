"""Task 4: Detailed Attribution Analysis of vol_spike_snapback regime.

Examines:
1. Exact dates, SPY/QQQ prices, regime signals (SMA50, QQQ vol)
2. Positions held before the drop
3. Exact execution timing of sells and buys
4. Equity trajectory vs SPY/QQQ trajectory
5. Why reference lost -15.77% vs baseline -8.21%
"""
import sys
import json
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

with open(ROOT / "scratch" / "agent_day_logs.json") as f:
    agent_logs = json.load(f)

vol_logs = agent_logs["vol_spike_snapback"]

print("=" * 100)
print("VOLATILITY SPIKE SNAPBACK: DAILY ATTRIBUTION TRACE")
print("=" * 100)
print(f"{'Date':<12s} {'Equity ($)':>12s} {'Invested %':>12s} {'Gross Beta':>12s} {'Fills Today':<30s} {'Positions'}")
print("-" * 100)

for d in vol_logs:
    fills_str = ""
    if d["fills"]:
        fills_str = ", ".join([f"{f['side']} {f['qty']} {f['ticker']}" for f in d["fills"]])
    pos_str = ", ".join([f"{t}:{q}" for t, q in d["positions"].items()])
    print(f"{d['date']:<12s} ${d['equity']:>11.2f} {d['invested_pct']*100:>11.1f}% {d['gross_beta']:>11.2f}x {fills_str:<30s} {pos_str}")
