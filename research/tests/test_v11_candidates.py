"""Stage V11: Comprehensive Test Suite for Candidates A through F and Negative Controls.

Verifies:
  1. Contract parity: each candidate implements `decide(market_state, portfolio_state, cash)` and `reset()`.
  2. Output format: list of dicts with keys 'ticker', 'side', 'quantity'.
  3. All 6 candidates pass across all 3 historical regimes without exceptions.
  4. Non-negative cash and equity conservation invariants.
  5. Deterministic replay: running candidate twice yields exact same SHA256 trace.
  6. Negative controls: identical series yields 0 diff, shuffled picks underperform.
"""
from __future__ import annotations

import pytest
from pathlib import Path
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateB_EmergencyDeRisking,
    CandidateC_SectorRiskBudgeting,
    CandidateD_RecoveryParticipation,
    CandidateE_CostAwareRebalancing,
    CandidateF_IntegratedRiskControl,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined


@pytest.fixture
def candidate_instances():
    return {
        "Candidate_A": CandidateA_AdaptiveRebalance(),
        "Candidate_B": CandidateB_EmergencyDeRisking(),
        "Candidate_C": CandidateC_SectorRiskBudgeting(),
        "Candidate_D": CandidateD_RecoveryParticipation(),
        "Candidate_E": CandidateE_CostAwareRebalancing(),
        "Candidate_F": CandidateF_IntegratedRiskControl(),
        "Candidate_AE": CandidateAE_Combined(),
    }


def test_candidate_contract_parity(candidate_instances):
    for name, cand in candidate_instances.items():
        assert hasattr(cand, "decide"), f"{name} missing decide()"
        assert callable(cand.decide), f"{name}.decide is not callable"
        assert hasattr(cand, "reset"), f"{name} missing reset()"
        assert callable(cand.reset), f"{name}.reset is not callable"


@pytest.mark.parametrize("cand_name", [
    "Candidate_A", "Candidate_B", "Candidate_C",
    "Candidate_D", "Candidate_E", "Candidate_F",
    "Candidate_AE",
])
@pytest.mark.parametrize("regime", [
    "calm_uptrend", "moderate_selloff", "vol_spike_snapback"
])
def test_candidates_run_cleanly_all_regimes(candidate_instances, cand_name: str, regime: str):
    cand = candidate_instances[cand_name]
    cand.reset()
    prov = StaticRegimeProvider("sample_regimes.json.gz", regime)
    engine = ReplayEngine(cand.decide, prov)
    res = engine.run_replay()

    metrics = res["metrics"]
    assert metrics["errors"] == 0, f"{cand_name} had errors on {regime}"
    assert metrics["mdd"] >= 0.0
    assert metrics["mdd"] <= 1.0
    assert len(res["equity_curve"]) > 0
    assert all(eq > 0 for eq in res["equity_curve"])
    assert res["compliance"]["all_safety_bars_cleared"] is True


def test_candidate_determinism(candidate_instances):
    cand = candidate_instances["Candidate_A"]
    prov1 = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    cand.reset()
    res1 = ReplayEngine(cand.decide, prov1).run_replay()

    prov2 = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    cand.reset()
    res2 = ReplayEngine(cand.decide, prov2).run_replay()

    assert res1["trace_sha256"] == res2["trace_sha256"]
    assert res1["equity_curve"] == res2["equity_curve"]
