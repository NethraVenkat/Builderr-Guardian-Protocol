"""
Gate 3: Execution Assumptions & Cost Model Sensitivity Sweep.
Evaluates Baseline E0 vs Candidate A+E under varied spread, commission, and slippage assumptions.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined
import research.engine.accounting as acc

prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")

spreads = [0.00025, 0.00050, 0.00100, 0.00150] # 2.5 bps, 5 bps, 10 bps, 15 bps
commissions = [0.0, 1.0, 2.0, 5.0] # 0 bps, 1 bps, 2 bps, 5 bps (in bps)

print("=" * 105)
print(f"{'Spread (bps)':<14} | {'Comm (bps)':<12} | {'E0 Return':<12} | {'AE Return':<12} | {'Delta (bps)':<14} | {'E0 MDD':<10} | {'AE MDD':<10} | {'AE Rank'}")
print("=" * 105)

original_slip_equity = acc.SLIP_EQUITY

for s in spreads:
    acc.SLIP_EQUITY = s
    for c in commissions:
        eng_e0 = ReplayEngine("agent.py", prov, commission_bps=c, start_cash=100_000.0)
        res_e0 = eng_e0.run_replay()
        
        cand_ae = CandidateAE_Combined()
        eng_ae = ReplayEngine(cand_ae.decide, prov, commission_bps=c, start_cash=100_000.0)
        res_ae = eng_ae.run_replay()
        
        r0 = res_e0["metrics"]["ret"]
        rae = res_ae["metrics"]["ret"]
        delta_bps = (rae - r0) * 10000.0
        mdd0 = res_e0["metrics"]["mdd"] * 100.0
        mddae = res_ae["metrics"]["mdd"] * 100.0
        rank = "AE > E0" if rae > r0 else "E0 >= AE"
        
        print(f"{s*10000:<14.1f} | {c:<12.1f} | {r0*100:<11.2f}% | {rae*100:<11.2f}% | {delta_bps:>+10.1f} bps | {mdd0:<9.2f}% | {mddae:<9.2f}% | {rank}")

# Restore
acc.SLIP_EQUITY = original_slip_equity
