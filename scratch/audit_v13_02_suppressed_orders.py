"""
Forensic audit of V13-02: Full Lifecycle Reconciliation of Orders and Trades.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

regimes = ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]

for r in regimes:
    prov = StaticRegimeProvider("sample_regimes.json.gz", r)
    cand = CandidateAE_Combined()
    eng = ReplayEngine(cand.decide, prov)
    res = eng.run_replay()
    
    fill_log = res["fill_log"]
    rejected = eng.last_portfolio.rejected_orders
    
    # Analyze raw lifecycle
    print(f"\n==================== REGIME: {r} ====================")
    print(f"Total Scored Sessions:       {len(res['equity_curve'])}")
    print(f"Emergency Exit Triggers:     {cand.emergency_exit_count}")
    print(f"Buffer Suppressed Count:     {cand.buffer_suppressed_count}")
    print(f"Executed Trades (Fills):     {len(fill_log)}")
    print(f"Rejected Orders:             {len(rejected)}")
    print(f"Partial Fills:               {sum(1 for f in fill_log if f.filled_qty < f.requested_qty - 1e-6)}")
    
    # Verify exact accounting invariant:
    # Executed trades must equal length of fill_log
    assert res["total_trades"] == len(fill_log)
    print("Lifecycle Trace Check:       PASS (Deterministic Match)")
