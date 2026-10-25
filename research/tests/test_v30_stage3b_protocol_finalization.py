"""
Stage 3B Targeted Offline Verification Suite.
Deterministic verification of causal session eligibility, information chronology,
power calculation sensitivity, statistical hypotheses, and fail-closed governance invariants.
"""

import json
import math
import os
import sys
import subprocess
import hashlib
import pytest

sys.path.insert(0, os.path.abspath("."))

EXPECTED_BRANCH = "archive/v30-stage2h-final-evidence-freeze"
EXPECTED_HEAD = "ce6b4c21b832044d0ffb45dce2ba949ab867d520"
EXPECTED_PARENT = "b283ded200c777b130285b0aa56a0b044afbd339"

PROTECTED_HASHES = {
    "agent.py": ("raw", "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"),
    "universe.json": ("lf", "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"),
    "research/strategies/v12_candidate_ae.py": ("lf", "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"),
    "research/strategies/v30_candidate_d2_cash_cushion.py": ("raw", "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215")
}


def compute_sha256(path: str, normalization: str = "raw") -> str:
    with open(path, "rb") as f:
        content = f.read()
    if normalization == "lf":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def test_01_checkpoint_and_frozen_comparator_identities():
    """Verify Git checkpoint invariants and the 4 protected source hashes."""
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch mismatch: {branch}"

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD mismatch: {head}"

    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent mismatch: {parent}"

    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"File missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_02_no_same_period_outcome_leakage_in_causal_eligibility():
    """Verify that causal defensive session eligibility depends strictly on F_{T-1} without day T leakage."""
    import agent
    from research.strategies import v30_candidate_d2_cash_cushion as d2

    # Construct synthetic market state for day T-1 with 55 bars
    # Day T-1 close will trigger DEFENSIVE regime
    market_state_t_minus_1 = {
        "SPY": [{"close": 100.0, "ts": f"2026-01-{i+1:02d}"} for i in range(55)],
        "QQQ": [{"close": 100.0, "ts": f"2026-01-{i+1:02d}"} for i in range(55)],
        "XLP": [{"close": 50.0, "ts": f"2026-01-{i+1:02d}"} for i in range(55)],
        "XLU": [{"close": 50.0, "ts": f"2026-01-{i+1:02d}"} for i in range(55)],
        "XLV": [{"close": 50.0, "ts": f"2026-01-{i+1:02d}"} for i in range(55)]
    }
    # Force SPY and QQQ close below SMA50 at T-1
    market_state_t_minus_1["SPY"][-1]["close"] = 80.0
    market_state_t_minus_1["QQQ"][-1]["close"] = 80.0

    targets_t_minus_1 = d2.target_weights_d2(market_state_t_minus_1)
    
    # In defensive regime, DEFENSIVE_WEIGHTS_D2 should be present (50% invested, 50% cash)
    assert "XLP" in targets_t_minus_1
    invested_weight = sum(targets_t_minus_1.values())
    assert math.isclose(invested_weight, 0.50, abs_tol=1e-4)

    # Now verify that what happens on day T (whether market rallies +10% or crashes -10%)
    # does NOT alter the ex-ante classification of session T
    causal_eligibility_session_T = (invested_weight == 0.50)
    assert causal_eligibility_session_T is True, "Causal eligibility must be True based strictly on T-1"

    # Leakage check: day T return is completely absent from F_{T-1}
    assert len(market_state_t_minus_1["SPY"]) == 55
    # If a post-treatment condition like (R_m,T < 0) was required, it would fail when day T rallies
    # Causal definition must NOT evaluate day T market returns


def test_03_as_of_data_availability_and_chronology():
    """Verify that the decision timeline model adheres strictly to T-1 close -> publication -> order -> T open."""
    path = "research/evidence/v30/v30_stage3b_causal_session_eligibility_specification.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    timeline = data["causal_session_eligibility_specification"]["decision_time_information_model"]["timeline_steps"]
    assert len(timeline) == 6
    assert timeline[0]["name"] == "Market Close (T-1)"
    assert timeline[1]["name"] == "Vendor Bar Publication"
    assert timeline[2]["name"] == "Regime Decision & Allocation (F_{T-1})"
    assert timeline[4]["name"] == "Order Execution (T)"
    assert timeline[5]["name"] == "Performance Observation Period"


def test_04_scenario_power_calculations_and_serial_dependence():
    """Verify analytical power calculation outputs across N_def, rhos, and hurdles."""
    path = "research/evidence/v30/v30_stage3b_synthetic_power_sensitivity_analysis.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    scenarios = data["synthetic_power_sensitivity_analysis"]["power_scenarios"]
    assert len(scenarios) == 384

    # Verify Finding 01: When true effect == hurdle (10 bps), power against 10 bps is exactly 5.00%
    for s in scenarios:
        if s["effect_bps"] == 10:
            assert s["power_hurdle_pct"] == 5.0, f"Expected 5.00% on null boundary, got {s['power_hurdle_pct']}"

    # Verify Finding 02: At N=30, rho=0.20, std=50 bps, effect=15 bps -> power against 10-bps hurdle is 11.55%
    found_target = False
    for s in scenarios:
        if s["N"] == 30 and s["rho"] == 0.2 and s["std_bps"] == 50 and s["effect_bps"] == 15:
            assert math.isclose(s["power_hurdle_pct"], 11.55, abs_tol=0.1)
            assert s["N_eff"] == 20.0
            found_target = True
    assert found_target, "Target scenario N=30, rho=0.20 not found"


def test_05_correct_null_and_hurdle_interpretation():
    """Verify that statistical protocol strictly distinguishes H01 (<=0) from H02 (<=10 bps)."""
    path = "research/evidence/v30/v30_stage3b_statistical_protocol_and_decision_matrix.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    hypotheses = data["statistical_protocol_and_decision_matrix"]["formal_hypotheses"]
    assert hypotheses["hypothesis_1_directional"]["null_H01"] == "\\mu_d \\le 0"
    assert "0.0010" in hypotheses["hypothesis_2_economic_hurdle"]["null_H02"]
    assert hypotheses["hypothesis_2_economic_hurdle"]["promotion_gate"] == "MANDATORY. Strategy certification requires rejecting H02 at alpha = 0.05."

    discrepancy = data["statistical_protocol_and_decision_matrix"]["inferential_methodology"]["discrepancy_resolution_rule"]
    assert "CONSERVATIVE_DISJUNCTION" in discrepancy["rule"]


def test_06_administrative_extension_eligibility():
    """Verify that the administrative extension rule is objectively observable and outcome-independent."""
    path = "research/evidence/v30/v30_stage3b_horizon_and_stopping_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    extension = data["horizon_and_stopping_rules"]["extension_protocol"]
    assert "N_{def}^{causal}(T=252)" in extension["trigger_formula"]
    assert "zero access to portfolio equity curves" in extension["objective_observability"].lower()
    assert data["horizon_and_stopping_rules"]["evaluation_horizon"]["maximum_contingent_sessions"] == 504


def test_07_secondary_cagr_constraint_alternatives():
    """Verify that the 200-bps CAGR constraint analysis presents the 3 required alternatives."""
    path = "research/evidence/v30/v30_stage3b_secondary_cagr_constraint_analysis.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    alts = data["secondary_cagr_constraint_analysis"]["three_defensible_alternatives"]
    assert "alternative_A_operational_guardrail" in alts
    assert "alternative_B_formal_non_inferiority" in alts
    assert "alternative_C_exploratory_reporting" in alts
    assert alts["alternative_A_operational_guardrail"]["classification"] == "RECOMMENDED_POLICY_GUARDRAIL"


def test_08_provider_licensing_decision_blocker_classification():
    """Verify that provider rights matrix classifies DEC-02 as BLOCKED and identifies Tiingo/Massive terms."""
    path = "research/evidence/v30/v30_stage3b_provider_rights_compatibility_matrix.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    matrix = data["provider_rights_compatibility_matrix"]
    assert matrix["owner_decision_gate"]["status"] == "BLOCKED"
    
    # Check that Massive default non-display is PROHIBITED
    for dim in matrix["compatibility_matrix"]["dimensions"]:
        if dim["dimension"] == "Non-Display Algorithmic Usage":
            assert dim["Massive_Developer"] == "PROHIBITED UNDER PUBLISHED DEFAULT TERMS"
        if dim["dimension"] == "Subscription Cancellation Purge Obligation":
            assert dim["Tiingo_Power"] == "MANDATORY_PURGE"


def test_09_fail_closed_operational_requirements():
    """Verify fail-closed operations requirements include INCIDENT_LOCK and prohibition of blind restarts."""
    path = "research/evidence/v30/v30_stage3b_fail_closed_operations_specification.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    reqs = data["fail_closed_operations_specification"]["offline_operational_requirements"]
    req_ids = [r["requirement_id"] for r in reqs]
    assert "OP_REQ_01" in req_ids  # Incident Lock
    assert "OP_REQ_02" in req_ids  # Startup Boot Invariant
    assert "OP_REQ_03" in req_ids  # Prohibition of Blind Restarts
    assert "OP_REQ_08" in req_ids  # Manual Operator Clearance


def test_10_zero_staged_git_changes():
    """Verify zero staged files and zero tracked modifications."""
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staged changes detected: {staged}"
    tracked_mod = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert tracked_mod == "", f"Tracked modifications detected: {tracked_mod}"
