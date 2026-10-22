"""
Forensic audit of V13-01: Transaction cost inconsistency in calm_uptrend.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined
import json

prov = StaticRegimeProvider("sample_regimes.json.gz", "calm_uptrend")

# 1. Baseline E0
eng_e0 = ReplayEngine("agent.py", prov)
res_e0 = eng_e0.run_replay()

# 2. Candidate A+E
cand_ae = CandidateAE_Combined()
eng_ae = ReplayEngine(cand_ae.decide, prov)
res_ae = eng_ae.run_replay()

print("=== BASELINE E0 SUMMARY ===")
print(f"Total Trades:      {len(res_e0['fill_log'])}")
print(f"Turnover ($):      ${res_e0['turnover']:,.2f}")
print(f"Slippage Cost ($): ${res_e0['slippage_cost']:.6f}")
print(f"Commissions ($):   ${res_e0['commission_cost']:.6f}")
print(f"Reported Costs:    ${res_e0['slippage_cost'] + res_e0['commission_cost']:.6f}")

print("\n=== CANDIDATE A+E SUMMARY ===")
print(f"Total Trades:      {len(res_ae['fill_log'])}")
print(f"Turnover ($):      ${res_ae['turnover']:,.2f}")
print(f"Slippage Cost ($): ${res_ae['slippage_cost']:.6f}")
print(f"Commissions ($):   ${res_ae['commission_cost']:.6f}")
print(f"Reported Costs:    ${res_ae['slippage_cost'] + res_ae['commission_cost']:.6f}")

# Compare fill by fill
print("\n=== DETAILED TRADE COMPARISON ===")
print(f"{'Idx':<4} | {'E0 Ticker':<9} | {'E0 Qty':>8} | {'E0 Notional':>12} | {'E0 Slip $':>10} || {'AE Ticker':<9} | {'AE Qty':>8} | {'AE Notional':>12} | {'AE Slip $':>10}")
print("-" * 105)

max_len = max(len(res_e0['fill_log']), len(res_ae['fill_log']))
for i in range(max_len):
    f0 = res_e0['fill_log'][i] if i < len(res_e0['fill_log']) else None
    fae = res_ae['fill_log'][i] if i < len(res_ae['fill_log']) else None
    
    t0_str = f"{f0.side.upper()} {f0.ticker}" if f0 else "N/A"
    q0_str = f"{f0.filled_qty:.1f}" if f0 else "N/A"
    n0_str = f"${f0.notional:,.2f}" if f0 else "N/A"
    s0_str = f"${f0.slippage * f0.filled_qty:.4f}" if f0 else "N/A"
    
    tae_str = f"{fae.side.upper()} {fae.ticker}" if fae else "N/A"
    qae_str = f"{fae.filled_qty:.1f}" if fae else "N/A"
    nae_str = f"${fae.notional:,.2f}" if fae else "N/A"
    sae_str = f"${fae.slippage * fae.filled_qty:.4f}" if fae else "N/A"
    
    print(f"{i:<4d} | {t0_str:<9} | {q0_str:>8} | {n0_str:>12} | {s0_str:>10} || {tae_str:<9} | {qae_str:>8} | {nae_str:>12} | {sae_str:>10}")
