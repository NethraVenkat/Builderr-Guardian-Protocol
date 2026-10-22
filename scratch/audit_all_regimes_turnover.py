import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

regimes = ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]

print(f"{'Regime':<18} | {'Strategy':<12} | {'Buys ($)':>11} | {'Sells ($)':>11} | {'Turnover (B+S)':>14} | {'Real Slip ($)':>13} | {'V12 Slip (Shares)':>17}")
print("=" * 110)

for r in regimes:
    prov = StaticRegimeProvider("sample_regimes.json.gz", r)
    
    # E0
    res_0 = ReplayEngine("agent.py", prov).run_replay()
    b_0 = sum(f.notional for f in res_0['fill_log'] if f.side == 'buy')
    s_0 = sum(f.notional for f in res_0['fill_log'] if f.side == 'sell')
    slip_0 = sum(f.notional * f.slippage for f in res_0['fill_log'])
    v12_slip_0 = sum(f.filled_qty * f.slippage for f in res_0['fill_log'])
    
    # AE
    cand = CandidateAE_Combined()
    res_ae = ReplayEngine(cand.decide, prov).run_replay()
    b_ae = sum(f.notional for f in res_ae['fill_log'] if f.side == 'buy')
    s_ae = sum(f.notional for f in res_ae['fill_log'] if f.side == 'sell')
    slip_ae = sum(f.notional * f.slippage for f in res_ae['fill_log'])
    v12_slip_ae = sum(f.filled_qty * f.slippage for f in res_ae['fill_log'])
    
    print(f"{r:<18} | {'Baseline E0':<12} | ${b_0:10.2f} | ${s_0:10.2f} | ${b_0+s_0:13.2f} | ${slip_0:12.2f} | ${v12_slip_0:16.4f}")
    print(f"{r:<18} | {'Cand A+E':<12} | ${b_ae:10.2f} | ${s_ae:10.2f} | ${b_ae+s_ae:13.2f} | ${slip_ae:12.2f} | ${v12_slip_ae:16.4f}")
    print("-" * 110)
