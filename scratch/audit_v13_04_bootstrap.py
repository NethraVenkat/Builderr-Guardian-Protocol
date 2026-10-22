"""
Forensic audit of V13-04: Comprehensive Bootstrap Formulation Audit.
Compares:
  - Percentile Bootstrap
  - Centered Null Hypothesis Bootstrap (Two-sided vs One-sided)
  - Sensitivity to block size and random seeds
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
res_0 = ReplayEngine("agent.py", prov).run_replay()
cand_ae = CandidateAE_Combined()
res_ae = ReplayEngine(cand_ae.decide, prov).run_replay()

eq_0 = np.array(res_0["equity_curve"])
eq_ae = np.array(res_ae["equity_curve"])

rets_0 = eq_0[1:] / eq_0[:-1] - 1.0
rets_ae = eq_ae[1:] / eq_ae[:-1] - 1.0
diff_rets = rets_ae - rets_0
n_days = len(diff_rets)

obs_mean_diff = float(np.mean(diff_rets))
obs_ret_diff = float((eq_ae[-1] / eq_ae[0] - 1.0) - (eq_0[-1] / eq_0[0] - 1.0))

print("=== STATISTICAL BOOTSTRAP FORMULATION AUDIT ===")
print(f"Sample Size (Trading Sessions): {n_days}")
print(f"Observed Daily Return Diff Mean: {obs_mean_diff*100:+.4f}%/day")
print(f"Observed Cumulative Return Diff: {obs_ret_diff*100:+.2f}%")
print()

seeds = [42, 100, 2026, 9999]
blocks = [3, 5, 10]
num_bootstraps = 2000

print(f"{'Seed':<6} | {'Block':<5} | {'95% CI (Cumulative)':<24} | {'p (One-sided <=0)':<18} | {'p (Centered Two-sided)':<22}")
print("-" * 88)

for seed in seeds:
    for b in blocks:
        np.random.seed(seed)
        num_blocks = int(np.ceil(n_days / b))
        boot_cum_diffs = []
        boot_daily_means = []
        
        for _ in range(num_bootstraps):
            starts = np.random.randint(0, n_days - b + 1, size=num_blocks)
            idx = []
            for s in starts:
                idx.extend(range(s, s + b))
            idx = idx[:n_days]
            
            b_rets_0 = rets_0[idx]
            b_rets_ae = rets_ae[idx]
            
            b_eq_0 = 100000.0 * np.cumprod(1.0 + b_rets_0)
            b_eq_ae = 100000.0 * np.cumprod(1.0 + b_rets_ae)
            
            b_cum_diff = (b_eq_ae[-1] / 100000.0 - 1.0) - (b_eq_0[-1] / 100000.0 - 1.0)
            boot_cum_diffs.append(b_cum_diff)
            boot_daily_means.append(np.mean(b_rets_ae - b_rets_0))
            
        boot_cum_diffs = np.array(boot_cum_diffs)
        boot_daily_means = np.array(boot_daily_means)
        
        # 1. Percentile 95% CI
        ci_lower = np.percentile(boot_cum_diffs, 2.5)
        ci_upper = np.percentile(boot_cum_diffs, 97.5)
        ci_str = f"[{ci_lower*100:+.2f}%, {ci_upper*100:+.2f}%]"
        
        # 2. Empirical one-sided p-value: Prob(boot_diff <= 0)
        p_one_sided = float(np.mean(boot_cum_diffs <= 0.0))
        
        # 3. Centered null two-sided p-value
        centered_diffs = boot_daily_means - obs_mean_diff
        p_two_sided_centered = float(np.mean(np.abs(centered_diffs) >= np.abs(obs_mean_diff)))
        
        print(f"{seed:<6d} | {b:<5d} | {ci_str:<24} | {p_one_sided:<18.4f} | {p_two_sided_centered:<22.4f}")
