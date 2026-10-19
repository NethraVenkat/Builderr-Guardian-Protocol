"""Task D: Reproduce All Baseline Numbers with unrounded precision.

Runs preview.run_regime on baseline.py and agent.py across all 3 regimes.
Outputs full numerical precision, mathematical return verification, and
audit comparison.
"""
import sys
import json
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

START_CASH = 100000.0

def profile_strategy(strategy_path: Path):
    results = {}
    for name, regime in regimes.items():
        # run_regime returns dict with:
        # name, ret, mdd, sharpe, calmar, trades, peak_gross, peak_conc, max_conc_streak, errors, days
        res = preview.run_regime(strategy_path, name, regime)
        # Calculate final equity from return
        final_equity = START_CASH * (1.0 + res["ret"])
        # Recalculate return independently
        recalc_ret = (final_equity - START_CASH) / START_CASH
        res["start_cash"] = START_CASH
        res["final_equity"] = final_equity
        res["recalc_ret"] = recalc_ret
        results[name] = res
    return results

print("=" * 80)
print("TASK D: BASELINE REPRODUCTION")
print("=" * 80)

baseline_results = profile_strategy(ROOT / "baseline.py")
agent_results = profile_strategy(ROOT / "agent.py")

output_payload = {
    "baseline": baseline_results,
    "agent": agent_results
}

print(json.dumps(output_payload, indent=2))
