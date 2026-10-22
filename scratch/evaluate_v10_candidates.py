import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.loss_reduction_candidates import (
    FastExitDeRiskingCandidate,
    IntegratedLossReductionCandidate,
)

candidates = {
    "E0_Baseline": "agent.py",
    "FastExitDeRisking": FastExitDeRiskingCandidate(),
    "IntegratedLossReduction": IntegratedLossReductionCandidate(),
}

print(f"{'Candidate':<26} | {'Regime':<18} | {'Return':>9} | {'MDD':>8} | {'Sharpe':>7} | {'Calmar':>7} | {'Trades':>6}")
print("-" * 95)

results = {}
for c_name, cand in candidates.items():
    results[c_name] = {}
    for r in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
        prov = StaticRegimeProvider("sample_regimes.json.gz", r)
        if isinstance(cand, str):
            engine = ReplayEngine(cand, prov)
        else:
            cand.reset()
            engine = ReplayEngine(cand.decide, prov)
        res = engine.run_replay()
        metrics = res["metrics"]
        results[c_name][r] = metrics
        print(f"{c_name:<26} | {r:<18} | {metrics['ret']*100:8.2f}% | {metrics['mdd']*100:7.2f}% | {metrics['sharpe']:7.2f} | {metrics['calmar']:7.2f} | {metrics['trades']:6d}")
