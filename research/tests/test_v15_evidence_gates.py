"""
Stage B2-F / Master Guardian Protocol V15: Final Evidence Gate Verification.
Binds raw fixture calendar dates, attribution bridge, cost sensitivity,
and pristine holdout isolation into automated regression assertions.
"""
import gzip
import json
import math
from pathlib import Path
import pytest
import numpy as np

from preview import _expand
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined
import research.engine.accounting as acc


def test_gate1_raw_fixture_calendar_dates():
    """Verify exact raw calendar dates and warmup/scored lengths in sample_regimes.json.gz."""
    data = json.load(gzip.open("sample_regimes.json.gz"))
    
    expected_dates = {
        "calm_uptrend": {
            "eval_start": "2021-06-01",
            "eval_end": "2021-08-31",
            "scored_first": "2021-06-01",
            "scored_last": "2021-08-30",
            "scored_count": 64,
            "warmup_count": 276,
            "total_count": 340,
        },
        "moderate_selloff": {
            "eval_start": "2021-09-01",
            "eval_end": "2021-10-15",
            "scored_first": "2021-09-01",
            "scored_last": "2021-10-14",
            "scored_count": 31,
            "warmup_count": 277,
            "total_count": 308,
        },
        "vol_spike_snapback": {
            "eval_start": "2020-02-19",
            "eval_end": "2020-04-30",
            "scored_first": "2020-02-19",
            "scored_last": "2020-04-29",
            "scored_count": 50,
            "warmup_count": 275,
            "total_count": 325,
        },
    }
    
    for name, exp in expected_dates.items():
        payload = data[name]
        assert payload["eval_start"] == exp["eval_start"]
        assert payload["eval_end"] == exp["eval_end"]
        
        all_dates = set()
        for ticker, rows in payload["bars"].items():
            expanded = _expand(rows)
            all_dates.update(b["ts"] for b in expanded)
            
        sorted_dates = sorted(list(all_dates))
        warmup = [d for d in sorted_dates if d < exp["eval_start"]]
        scored = [d for d in sorted_dates if exp["eval_start"] <= d <= exp["eval_end"]]
        
        assert len(warmup) == exp["warmup_count"], f"{name} warmup count mismatch"
        assert len(scored) == exp["scored_count"], f"{name} scored count mismatch"
        assert scored[0] == exp["scored_first"], f"{name} first scored date mismatch"
        assert scored[-1] == exp["scored_last"], f"{name} last scored date mismatch"
        assert len(sorted_dates) == exp["total_count"], f"{name} total count mismatch"


def test_gate2_attribution_bridge_and_defensive_holdings():
    """Verify cent-accurate terminal equity bridge and subsequent defensive holdings."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    
    res_e0 = ReplayEngine("agent.py", prov, start_cash=100_000.0).run_replay()
    cand_ae = CandidateAE_Combined()
    eng_ae = ReplayEngine(cand_ae.decide, prov, start_cash=100_000.0)
    res_ae = eng_ae.run_replay()
    
    e0_eq = res_e0["equity_curve"]
    ae_eq = res_ae["equity_curve"]
    
    # 1. Terminal equity cent-level reconciliation
    terminal_delta = ae_eq[-1] - e0_eq[-1]
    assert math.isclose(terminal_delta, 2621.20, abs_tol=0.05), f"Expected +$2,621.20, got ${terminal_delta:.2f}"
    
    # 2. Key inflection point: Session 7 (index 6) locks in bulk of outperformance
    s7_delta = ae_eq[6] - e0_eq[6]
    assert 2100.0 < s7_delta < 2200.0, f"Session 7 delta {s7_delta} should be ~+$2,146.20"
    
    # 3. Disprove 'cash-only forever' claim: verify defensive holdings at end
    last_positions = eng_ae.last_portfolio.positions
    assert "XLE" in last_positions and last_positions["XLE"] > 500
    assert "XLP" in last_positions and last_positions["XLP"] > 300
    assert "XLU" in last_positions and last_positions["XLU"] > 700
    assert "XLV" in last_positions and last_positions["XLV"] > 150
    assert eng_ae.last_portfolio.cash < 20_000.0, "Portfolio must be predominantly invested in defensive assets, not 100% cash"


def test_gate3_cost_sensitivity_hierarchy():
    """Verify Candidate A+E strictly outperforms Baseline E0 across realistic spreads & commissions."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    original_slip = acc.SLIP_EQUITY
    
    try:
        for spread in [0.00025, 0.00050, 0.00100, 0.00150]:
            acc.SLIP_EQUITY = spread
            for comm in [0.0, 1.0, 2.0, 5.0]:
                r0 = ReplayEngine("agent.py", prov, commission_bps=comm, start_cash=100_000.0).run_replay()
                rae = ReplayEngine(CandidateAE_Combined().decide, prov, commission_bps=comm, start_cash=100_000.0).run_replay()
                
                delta_bps = (rae["metrics"]["ret"] - r0["metrics"]["ret"]) * 10000.0
                assert delta_bps >= 260.0, f"At spread={spread}, comm={comm}, delta was {delta_bps} bps (< 260 bps)"
                assert rae["metrics"]["mdd"] < r0["metrics"]["mdd"], "Candidate A+E must strictly improve MDD"
    finally:
        acc.SLIP_EQUITY = original_slip


def test_gate7_pristine_holdout_isolation():
    """Verify sample regimes fixture has zero observations in 2022-2024."""
    data = json.load(gzip.open("sample_regimes.json.gz"))
    max_date = max(
        b["ts"]
        for payload in data.values()
        for rows in payload["bars"].values()
        for b in _expand(rows)
    )
    assert max_date == "2021-10-14", f"Expected max date 2021-10-14, got {max_date}"
    assert max_date < "2022-01-01", "Contamination detected! Fixture contains observations from 2022+"
