"""
Stage B2-C: Independent Statistical Verification & Parameter Sensitivity Sweep.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

def run_bootstrap_sweep():
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    
    # Baseline E0
    res_e0 = ReplayEngine("agent.py", prov).run_replay()
    eq_e0 = np.array(res_e0["equity_curve"])
    rets_e0 = eq_e0[1:] / eq_e0[:-1] - 1.0
    
    # Candidate A+E
    cand_ae = CandidateAE_Combined()
    res_ae = ReplayEngine(cand_ae.decide, prov).run_replay()
    eq_ae = np.array(res_ae["equity_curve"])
    rets_ae = eq_ae[1:] / eq_ae[:-1] - 1.0
    
    n_days = len(rets_e0)
    
    def calc_mdd(eq):
        peak, mdd = -1e18, 0.0
        for x in eq:
            peak = max(peak, x)
            if peak > 0:
                mdd = max(mdd, (peak - x) / peak)
        return mdd

    obs_ret_diff = (eq_ae[-1] / eq_ae[0] - 1.0) - (eq_e0[-1] / eq_e0[0] - 1.0)
    obs_mdd_diff = calc_mdd(eq_ae) - calc_mdd(eq_e0)
    
    print("=== MULTI-SEED & MULTI-BLOCK PAIRED BOOTSTRAP ===")
    print(f"Observed Return Difference: {obs_ret_diff*100:+.2f}%")
    print(f"Observed MDD Difference:    {obs_mdd_diff*100:+.2f}%")
    print(f"{'Seed':<6} | {'Block':<6} | {'95% CI Return Diff':<22} | {'p-val (Ret)':<12} | {'95% CI MDD Diff':<22} | {'p-val (MDD)':<12}")
    print("-" * 88)
    
    seeds = [42, 100, 2026, 9999]
    blocks = [3, 5, 10]
    num_bootstraps = 1000
    
    for seed in seeds:
        for b in blocks:
            np.random.seed(seed)
            num_blocks = int(np.ceil(n_days / b))
            b_ret_diffs = []
            b_mdd_diffs = []
            
            for _ in range(num_bootstraps):
                starts = np.random.randint(0, n_days - b + 1, size=num_blocks)
                idx = []
                for s in starts:
                    idx.extend(range(s, s + b))
                idx = idx[:n_days]
                
                b_rets_0 = rets_e0[idx]
                b_rets_ae = rets_ae[idx]
                
                b_eq_0 = 100000.0 * np.cumprod(1.0 + b_rets_0)
                b_eq_ae = 100000.0 * np.cumprod(1.0 + b_rets_ae)
                
                b_ret_diff = (b_eq_ae[-1] / 100000.0 - 1.0) - (b_eq_0[-1] / 100000.0 - 1.0)
                b_mdd_diff = calc_mdd(b_eq_ae) - calc_mdd(b_eq_0)
                
                b_ret_diffs.append(b_ret_diff)
                b_mdd_diffs.append(b_mdd_diff)
                
            b_ret_diffs = np.array(b_ret_diffs)
            b_mdd_diffs = np.array(b_mdd_diffs)
            
            ci_ret = (np.percentile(b_ret_diffs, 2.5), np.percentile(b_ret_diffs, 97.5))
            ci_mdd = (np.percentile(b_mdd_diffs, 2.5), np.percentile(b_mdd_diffs, 97.5))
            
            p_ret = np.mean(b_ret_diffs <= 0.0)
            p_mdd = np.mean(b_mdd_diffs >= 0.0)
            
            ci_ret_str = f"[{ci_ret[0]*100:+.2f}%, {ci_ret[1]*100:+.2f}%]"
            ci_mdd_str = f"[{ci_mdd[0]*100:+.2f}%, {ci_mdd[1]*100:+.2f}%]"
            print(f"{seed:<6d} | {b:<6d} | {ci_ret_str:<22} | {p_ret:<12.4f} | {ci_mdd_str:<22} | {p_mdd:<12.4f}")
    print()

def run_parameter_sensitivity_sweep():
    print("=== PARAMETER SENSITIVITY SWEEP (Candidate A+E) ===")
    shock_thresholds = [-0.020, -0.025, -0.030, -0.035, -0.040]
    buffer_thresholds = [0.015, 0.020, 0.030, 0.040, 0.050]
    
    print(f"{'Shock Thresh':<14} | {'Buffer Thresh':<14} | {'Calm Ret':>10} | {'Mod Ret':>10} | {'Vol Ret':>10} | {'Vol MDD':>10} | {'Vol Trades':>10}")
    print("-" * 88)
    
    # 1. Shock threshold sweep (with fixed buffer = 0.030)
    for st in shock_thresholds:
        cand = CandidateAE_Combined(shock_threshold=st, buffer_threshold=0.030)
        rets = {}
        mdds = {}
        trds = {}
        for r in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
            prov = StaticRegimeProvider("sample_regimes.json.gz", r)
            cand.reset()
            res = ReplayEngine(cand.decide, prov).run_replay()
            rets[r] = res["metrics"]["ret"]
            mdds[r] = res["metrics"]["mdd"]
            trds[r] = res["metrics"]["trades"]
        print(f"{st*100:13.1f}% | {0.030*100:13.1f}% | {rets['calm_uptrend']*100:9.2f}% | {rets['moderate_selloff']*100:9.2f}% | {rets['vol_spike_snapback']*100:9.2f}% | {mdds['vol_spike_snapback']*100:9.2f}% | {trds['vol_spike_snapback']:10d}")
        
    print("-" * 88)
    # 2. Buffer threshold sweep (with fixed shock = -0.030)
    for bt in buffer_thresholds:
        cand = CandidateAE_Combined(shock_threshold=-0.030, buffer_threshold=bt)
        rets = {}
        mdds = {}
        trds = {}
        for r in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
            prov = StaticRegimeProvider("sample_regimes.json.gz", r)
            cand.reset()
            res = ReplayEngine(cand.decide, prov).run_replay()
            rets[r] = res["metrics"]["ret"]
            mdds[r] = res["metrics"]["mdd"]
            trds[r] = res["metrics"]["trades"]
        print(f"{-0.030*100:13.1f}% | {bt*100:13.1f}% | {rets['calm_uptrend']*100:9.2f}% | {rets['moderate_selloff']*100:9.2f}% | {rets['vol_spike_snapback']*100:9.2f}% | {mdds['vol_spike_snapback']*100:9.2f}% | {trds['vol_spike_snapback']:10d}")

if __name__ == "__main__":
    run_bootstrap_sweep()
    run_parameter_sensitivity_sweep()
