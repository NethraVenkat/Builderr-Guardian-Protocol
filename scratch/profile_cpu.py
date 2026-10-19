"""Task 3.D & Task 9: Detailed CPU Profiling of agent.decide().

Runs cProfile over 100 iterations of decide() across realistic market state
to quantify exact function call counts and cumulative execution time.
"""
import sys
import cProfile
import pstats
import io
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent
import preview

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

bars = {t: preview._expand(rows) for t, rows in regimes["calm_uptrend"]["bars"].items()}
market_state = {t: [b for b in bs if b["ts"] < "2021-06-01"] for t, bs in bars.items()}
portfolio_state = {"cash": 100_000.0, "positions": [], "last_prices": {}}
cash = 100_000.0

pr = cProfile.Profile()
pr.enable()

for _ in range(500):
    agent._last_rebalance_bar_date = None  # Force rebalance calculation
    _ = agent.decide(market_state, portfolio_state, cash)

pr.disable()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(25)

print("=" * 80)
print("CPU PROFILING RESULTS (500 decide calls):")
print("=" * 80)
print(s.getvalue())
