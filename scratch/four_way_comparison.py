"""
Stage B2-C: Mandatory 4-Way Comparative Evaluation.
Compares:
  1. Frozen E0 Baseline
  2. Candidate A Alone (Adaptive Rebalancing Shock Exit)
  3. Candidate E Alone (Cost-Aware Turnover Buffer)
  4. Candidate A+E Combined (Adaptive Shock Exit + Cost Buffer)
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

def compute_detailed_metrics(res, start_cash=100000.0):
    m = res["metrics"]
    eq = np.array(res["equity_curve"])
    rets = eq[1:] / eq[:-1] - 1.0 if len(eq) > 1 else np.array([0.0])
    
    worst_daily_loss = float(np.min(rets)) if len(rets) > 0 else 0.0
    
    # Sortino
    downside_rets = [r for r in rets if r < 0.0]
    if downside_rets:
        downside_std = np.sqrt(np.mean(np.array(downside_rets) ** 2))
        sortino = (np.mean(rets) / downside_std * np.sqrt(252.0)) if downside_std > 1e-9 else 0.0
    else:
        sortino = 0.0
        
    net_pnl = eq[-1] - start_cash
    
    # Peak to trough dollar drawdown
    peak = -1e18
    mdd_dollars = 0.0
    for v in eq:
        peak = max(peak, v)
        if peak - v > mdd_dollars:
            mdd_dollars = peak - v

    return {
        "ret": m["ret"],
        "net_pnl": net_pnl,
        "mdd": m["mdd"],
        "mdd_dollars": mdd_dollars,
        "worst_daily_loss": worst_daily_loss,
        "sharpe": m["sharpe"],
        "sortino": sortino,
        "calmar": m["calmar"],
        "trades": m["trades"],
        "turnover": res["turnover"],
        "costs": res["slippage_cost"] + res["commission_cost"],
        "peak_gross": res["peak_gross"],
        "peak_conc": res["peak_conc"],
    }

regimes = ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]

candidates = {
    "1. Baseline E0": "agent.py",
    "2. Candidate A (Adaptive Exit)": CandidateAE_Combined(enable_adaptive_exit=True, enable_cost_buffer=False),
    "3. Candidate E (Cost Buffer)": CandidateAE_Combined(enable_adaptive_exit=False, enable_cost_buffer=True),
    "4. Candidate A+E (Combined)": CandidateAE_Combined(enable_adaptive_exit=True, enable_cost_buffer=True),
}

results = {c: {} for c in candidates}

print("=" * 130)
print(f"{'Strategy':<32} | {'Regime':<18} | {'Return':>8} | {'Net P&L ($)':>11} | {'MDD (%)':>8} | {'Worst Day':>9} | {'Sharpe':>7} | {'Sortino':>7} | {'Trades':>6} | {'Costs ($)':>9}")
print("=" * 130)

for c_name, cand in candidates.items():
    for r in regimes:
        prov = StaticRegimeProvider("sample_regimes.json.gz", r)
        if isinstance(cand, str):
            engine = ReplayEngine(cand, prov)
        else:
            cand.reset()
            engine = ReplayEngine(cand.decide, prov)
        res = engine.run_replay()
        dm = compute_detailed_metrics(res)
        results[c_name][r] = (dm, cand if not isinstance(cand, str) else None)
        print(f"{c_name:<32} | {r:<18} | {dm['ret']*100:7.2f}% | ${dm['net_pnl']:10.2f} | {dm['mdd']*100:7.2f}% | {dm['worst_daily_loss']*100:8.2f}% | {dm['sharpe']:7.2f} | {dm['sortino']:7.2f} | {dm['trades']:6d} | ${dm['costs']:8.2f}")
    print("-" * 130)

# Check emergency exits in Candidate A+E
cand_ae = candidates["4. Candidate A+E (Combined)"]
print("\n=== CANDIDATE A+E OPERATIONAL TELEMETRY ===")
for r in regimes:
    prov = StaticRegimeProvider("sample_regimes.json.gz", r)
    cand_ae.reset()
    engine = ReplayEngine(cand_ae.decide, prov)
    res = engine.run_replay()
    print(f"Regime {r:<18} | Emergency Exits: {cand_ae.emergency_exit_count} | Buffer Suppressed Decisions: {cand_ae.buffer_suppressed_count}")
