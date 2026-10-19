"""Baseline reproduction and determinism test for Stage 2A.

Executes baseline.py and agent.py across all sample regimes,
measuring initial account value, final account value, percentage return,
maximum drawdown, beta-adjusted exposure, maximum concentration, trade count,
runtime, safety checks, and determinism across runs.
"""
import os
import sys
import time
import json
import gzip
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import preview

baseline_path = ROOT / "baseline.py"
agent_path = ROOT / "agent.py"

with gzip.open(ROOT / "sample_regimes.json.gz", "rb") as f:
    regimes = json.load(f)

def evaluate_strategy(path: Path, runs: int = 3):
    results_across_runs = []
    durations = []
    for r in range(runs):
        t0 = time.perf_counter()
        regime_results = [preview.run_regime(path, name, reg) for name, reg in regimes.items()]
        dur = time.perf_counter() - t0
        durations.append(dur)
        results_across_runs.append(regime_results)
    
    # Check determinism across runs
    deterministic = True
    base = results_across_runs[0]
    for other in results_across_runs[1:]:
        for b_dict, o_dict in zip(base, other):
            for k in ["ret", "mdd", "sharpe", "calmar", "trades", "peak_gross", "peak_conc", "max_conc_streak", "errors"]:
                if b_dict[k] != o_dict[k]:
                    deterministic = False
                    print(f"Non-deterministic key {k} in {b_dict['name']}: {b_dict[k]} vs {o_dict[k]}")

    return base, durations, deterministic

print("=" * 75)
print("STAGE 2A: BASELINE (baseline.py) EVALUATION")
print("=" * 75)
base_results, base_durs, base_det = evaluate_strategy(baseline_path, runs=3)
for r in base_results:
    initial_cash = 100000.0
    final_equity = initial_cash * (1.0 + r["ret"])
    print(f"Regime: {r['name']}")
    print(f"  Initial Equity:    ${initial_cash:,.2f}")
    print(f"  Final Equity:      ${final_equity:,.2f}")
    print(f"  Return:            {r['ret']*100:+.2f}%")
    print(f"  Max Drawdown:      {r['mdd']*100:.2f}%")
    print(f"  Sharpe:            {r['sharpe']:.2f}")
    print(f"  Calmar:            {r['calmar']:.2f}")
    print(f"  Trades:            {r['trades']}")
    print(f"  Peak Gross Beta:   {r['peak_gross']:.2f}x (Cap <= 1.50x)")
    print(f"  Peak Conc:         {r['peak_conc']*100:.1f}% (Cap < 30%)")
    print(f"  Max Conc Streak:   {r['max_conc_streak']}d (Limit <= 5d)")
    print(f"  Execution Errors:  {r['errors']}")
print(f"Runtime (3 runs): {base_durs} | Avg: {sum(base_durs)/len(base_durs):.4f}s")
print(f"Determinism Check (3 runs): {'PASS' if base_det else 'FAIL'}")

print("\n" + "=" * 75)
print("STAGE 2A: REFERENCE AGENT (agent.py) EVALUATION")
print("=" * 75)
agent_results, agent_durs, agent_det = evaluate_strategy(agent_path, runs=3)
for r in agent_results:
    initial_cash = 100000.0
    final_equity = initial_cash * (1.0 + r["ret"])
    print(f"Regime: {r['name']}")
    print(f"  Initial Equity:    ${initial_cash:,.2f}")
    print(f"  Final Equity:      ${final_equity:,.2f}")
    print(f"  Return:            {r['ret']*100:+.2f}%")
    print(f"  Max Drawdown:      {r['mdd']*100:.2f}%")
    print(f"  Sharpe:            {r['sharpe']:.2f}")
    print(f"  Calmar:            {r['calmar']:.2f}")
    print(f"  Trades:            {r['trades']}")
    print(f"  Peak Gross Beta:   {r['peak_gross']:.2f}x (Cap <= 1.50x)")
    print(f"  Peak Conc:         {r['peak_conc']*100:.1f}% (Cap < 30%)")
    print(f"  Max Conc Streak:   {r['max_conc_streak']}d (Limit <= 5d)")
    print(f"  Execution Errors:  {r['errors']}")
print(f"Runtime (3 runs): {agent_durs} | Avg: {sum(agent_durs)/len(agent_durs):.4f}s")
print(f"Determinism Check (3 runs): {'PASS' if agent_det else 'FAIL'}")
