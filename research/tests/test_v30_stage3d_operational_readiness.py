"""
Stage 3D Operational Readiness and Verification Suite.
Validates the 12 Stage 3D acceptance dimensions across competition admission contract,
exploratory protocol specifications, synthetic end-to-end execution, and fail-closed incident architecture.
"""

import os
import sys
import math
import json
import subprocess
import hashlib
import pytest

sys.path.insert(0, os.path.abspath("."))

EXPECTED_BRANCH = "archive/v30-stage2h-final-evidence-freeze"
EXPECTED_HEAD = "4540ee49dac29e4599fbbeb96bbcffd2dafd6705"
EXPECTED_PARENT = "ce6b4c21b832044d0ffb45dce2ba949ab867d520"

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


def test_01_frozen_checkpoint_and_ancestry():
    """Verify Git branch, HEAD, parent commit, 87 commit delta files, and 198 archive ancestry."""
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch mismatch: {branch}"

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD mismatch: {head}"

    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent mismatch: {parent}"

    delta_87 = subprocess.check_output(["git", "diff", "--name-only", "HEAD~1", "HEAD"], text=True).strip().splitlines()
    assert len(delta_87) == 87, f"Commit delta mismatch: {len(delta_87)}"

    delta_198 = subprocess.check_output(["git", "diff", "--name-only", f"{EXPECTED_PARENT}~1", EXPECTED_PARENT], text=True).strip().splitlines()
    assert len(delta_198) == 198, f"Ancestry delta mismatch: {len(delta_198)}"


def test_02_protected_source_hashes():
    """Verify the four historically protected source hashes bit-for-bit."""
    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"File missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_03_tier3_holdout_isolation():
    """Verify tiingo_cache/ remains untracked, uninspected, and holds 2 directory entries."""
    assert os.path.exists("tiingo_cache"), "tiingo_cache missing"
    entries = os.listdir("tiingo_cache")
    assert len(entries) == 2, f"Unexpected tiingo_cache entry count: {len(entries)}"

    status = subprocess.check_output(["git", "status", "--porcelain", "tiingo_cache"], text=True).strip()
    assert status == "!! tiingo_cache/" or status == "", f"tiingo_cache is tracked or dirty: {status}"


def test_04_exploratory_protocol_specification_completeness():
    """Verify exploratory protocol defines d_t, ex-ante regime eligibility, and unapproved proposals."""
    path = "research/evidence/v30/v30_stage3d_exploratory_protocol_specification.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["exploratory_protocol_specification"]

    assert "I_{def,T}^{causal} = 1 iff S_{T-1} == DEFENSIVE" in data["causal_eligibility_and_information_boundary"]["causal_eligibility_rule"]
    assert "d_t = max(0, -R_{E0,t}) - max(0, -R_{D2,t})" in data["metrics_framework"]["primary_descriptive_metric"]["formula"]
    unapproved = data["unapproved_historical_proposals"]
    assert unapproved["economic_hurdle_10bps"]["status"] == "UNAPPROVED_PROPOSAL"
    assert unapproved["cagr_guardrail_200bps"]["status"] == "UNAPPROVED_PROPOSAL"
    assert unapproved["evaluation_horizon_252_sessions"]["status"] == "UNAPPROVED_PROPOSAL"
    assert unapproved["maximum_horizon_504_sessions"]["status"] == "UNAPPROVED_PROPOSAL"


def test_05_execution_contract_parity_matrix():
    """Verify contract parity between preview.py and hardened engine across 12 dimensions."""
    path = "research/evidence/v30/v30_stage3d_execution_contract_parity_matrix.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["execution_contract_parity_matrix"]

    dims = {d["dimension"]: d["status"] for d in data["contract_dimensions"]}
    assert dims["Signal Computation Timing"] == "REPRODUCED"
    assert dims["Order Submission Timing"] == "REPRODUCED"
    assert dims["Fill Assumptions & Pricing"] == "REPRODUCED"
    assert dims["Cash Accounting & Order Affordance"] == "REPRODUCED"
    assert dims["Gross Leverage Gate"] == "REPRODUCED"
    assert dims["Position Concentration Breach Gate"] == "REPRODUCED"
    assert dims["Total-Return Adjustments (Dividends vs Price Return)"] == "DIFFERENT"
    assert data["summary"]["reproduced"] == 8


def test_06_synthetic_end_to_end_behavior():
    """Verify synthetic end-to-end trace verifies 220-warmup, 60-eval, and zero catastrophic blowup."""
    path = "research/evidence/v30/v30_stage3d_synthetic_end_to_end_trace.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["synthetic_end_to_end_trace"]["results"]

    summary = data["simulation_summary"]
    checks = data["operational_checks"]
    assert summary["warmup_days"] == 220
    assert summary["eval_days"] == 60
    assert summary["catastrophic_dd_tripped"] is False
    assert checks["warmup_220_completed"] is True
    assert checks["eval_60_completed"] is True
    assert checks["t_minus_1_causality_enforced"] is True
    assert checks["t_open_fills_enforced"] is True
    assert checks["missing_bar_handled"] is True
    assert checks["corporate_split_adjusted"] is True
    assert checks["idempotency_verified"] is True
    assert checks["restart_state_reproduced"] is True


def test_07_failure_injection_behavior():
    """Verify failure injection harness confirms fail-closed behavior across edge cases."""
    path = "research/evidence/v30/v30_stage3d_failure_injection_results.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["failure_injection_results"]

    results = data["results"]
    assert results["idempotent_duplicate"]["pass"] is True
    assert results["conflicting_payload"]["pass"] is True
    assert results["stale_data_behind_watermark"]["pass"] is True
    assert results["nonfinite_price_nan"]["pass"] is True
    assert results["unauthorized_ticker"]["pass"] is True
    assert results["weekend_non_trading_day"]["pass"] is True
    assert results["empty_payload"]["pass"] is True
    assert results["circuit_breaker_slippage"]["pass"] is True


def test_08_data_rights_and_dec02_blocked():
    """Verify data rights matrix keeps DEC-02 strictly blocked."""
    path = "research/evidence/v30/v30_stage3d_data_rights_and_provenance_matrix.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["data_rights_and_provenance_matrix"]

    assert "DEC-02 REMAINS STRICTLY BLOCKED" in data["governance_mandate"]


def test_09_competition_admission_readiness():
    """Verify competition admission assessment confirms 100% safety bar pass."""
    path = "research/evidence/v30/v30_stage3d_competition_readiness_assessment.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["competition_readiness_assessment"]

    assert data["admission_verdict"] == "READY_FOR_SUBMISSION"
    assert data["scoring_model"]["denominator_checks"] == 6
    assert all(c["status"] == "PASS" for c in data["checks"])


def test_10_prospective_readiness_assessment():
    """Verify prospective readiness assessment calculates 72.5% weighted completion with explicit blockers."""
    path = "research/evidence/v30/v30_stage3d_prospective_readiness_assessment.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["prospective_readiness_assessment"]

    assert math.isclose(data["scoring_model"]["weighted_completion_pct"], 72.5, abs_tol=0.1)
    assert len(data["blocking_prerequisites"]) == 3


def test_11_canonical_decision_register():
    """Verify canonical DEC-01 through DEC-06 IDs and statuses."""
    path = "research/evidence/v30/v30_stage3d_canonical_decision_register.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        decs = {d["decision_id"]: d for d in json.load(f)["canonical_decision_register"]["decisions"]}

    assert decs["DEC-01"]["status"] == "PENDING"
    assert decs["DEC-02"]["status"] == "STRICTLY_BLOCKED"
    assert decs["DEC-03"]["status"] == "EXPLORATORY_ONLY_RECOMMENDED_PENDING_APPROVAL"
    assert decs["DEC-04"]["status"] == "PENDING"
    assert decs["DEC-05"]["status"] == "CONDITIONAL"
    assert decs["DEC-06"]["status"] == "STRICTLY_BLOCKED"


def test_12_zero_trading_activation():
    """Verify working tree has exactly zero staged changes and zero tracked modifications."""
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staged changes detected: {staged}"
    tracked_mod = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert tracked_mod == "", f"Tracked modifications detected: {tracked_mod}"
