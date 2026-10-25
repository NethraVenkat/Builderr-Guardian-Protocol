import json
import os
import subprocess
import hashlib
import pytest

EXPECTED_BRANCH = "archive/v30-stage2h-final-evidence-freeze"
EXPECTED_HEAD = "ce6b4c21b832044d0ffb45dce2ba949ab867d520"
EXPECTED_PARENT = "b283ded200c777b130285b0aa56a0b044afbd339"

PROTECTED_HASHES = {
    "agent.py": ("raw", "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"),
    "universe.json": ("lf", "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"),
    "research/strategies/v12_candidate_ae.py": ("lf", "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"),
    "research/strategies/v30_candidate_d2_cash_cushion.py": ("raw", "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215")
}

ORIGINAL_STAGE3A_FILES = [
    "GUARDIAN_ALPHA_V30_STAGE3A_OWNER_GOVERNANCE_REVIEW.md",
    "research/evidence/v30/v30_stage3a_checkpoint_and_preservation_certification.json",
    "research/evidence/v30/v30_stage3a_cross_stage_traceability_matrix.json",
    "research/evidence/v30/v30_stage3a_provider_and_licensing_comparison.json",
    "research/evidence/v30/v30_stage3a_statistical_endpoint_decision_matrix.json",
    "research/evidence/v30/v30_stage3a_horizon_and_power_assessment.json",
    "research/evidence/v30/v30_stage3a_monitoring_and_incident_readiness.json",
    "research/evidence/v30/v30_stage3a_owner_decision_register.json",
    "research/evidence/v30/v30_stage3a_open_risks_and_blockers.json",
    "research/evidence/v30/v30_stage3a_executed_test_ledger.json",
    "research/evidence/v30/v30_stage3a_artifact_checksum_manifest.json",
    "research/tests/test_v30_stage3a_governance_review.py"
]


def compute_sha256(path, normalization="raw"):
    with open(path, "rb") as f:
        content = f.read()
    if normalization == "lf":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def test_01_git_checkpoint_and_parent():
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch mismatch: expected {EXPECTED_BRANCH}, got {branch}"

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, got {head}"

    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent mismatch: expected {EXPECTED_PARENT}, got {parent}"


def test_02_protected_source_file_hashes():
    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"Protected file missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_03_tier3_isolation_and_no_credential_exposure():
    cache_dir = "tiingo_cache"
    if os.path.exists(cache_dir):
        # Must not be tracked by git
        tracked = subprocess.check_output(["git", "ls-files", cache_dir], text=True).strip()
        assert tracked == "", "Tier 3 cache must never be tracked in git index"
    
    # Verify no credential files exist in git tracked index
    tracked_env = subprocess.check_output(["git", "ls-files", ".env"], text=True).strip()
    assert tracked_env == "", "Environment file .env must not be tracked in git index"


def test_04_stage3a_deliverables_intact():
    for path in ORIGINAL_STAGE3A_FILES:
        assert os.path.exists(path), f"Original Stage 3A file missing: {path}"
        assert os.path.getsize(path) > 0, f"Original Stage 3A file empty: {path}"


def test_05_provider_licensing_corrections_schema():
    path = "research/evidence/v30/v30_stage3a_r_provider_licensing_corrections.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    corrections = data["provider_licensing_corrections"]
    assert corrections["owner_decision_gate"]["status"] == "BLOCKED"
    assert "MANDATORY_DATA_PURGE" in corrections["provider_terms_audit"]["Tiingo"]["subscription_termination_clause"]["status"]
    assert "MANDATORY_DATA_PURGE" in corrections["provider_terms_audit"]["Massive_Polygon_io"]["subscription_termination_clause"]["status"]
    assert "MANDATORY_DATA_PURGE" in corrections["provider_terms_audit"]["Interactive_Brokers"]["subscription_termination_clause"]["status"]


def test_06_statistical_hypothesis_two_tier_distinction():
    path = "research/evidence/v30/v30_stage3a_r_statistical_hypothesis_correction.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    hypotheses = data["statistical_hypothesis_correction"]["two_tier_hypothesis_framework"]
    assert "hypothesis_1_directional_improvement" in hypotheses
    assert "hypothesis_2_economic_superiority" in hypotheses
    assert hypotheses["hypothesis_2_economic_superiority"]["decision_role"] == "MANDATORY hurdle for prospective validation and strategy certification."


def test_07_secondary_non_inferiority_distinction():
    path = "research/evidence/v30/v30_stage3a_r_secondary_non_inferiority_assessment.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    critique = data["secondary_non_inferiority_assessment"]["methodological_critique"]
    assert "point_estimate_vs_inferential_testing" in critique
    assert "formal_non_inferiority_specification" in critique
    assert "OPERATIONAL RISK-BUDGET HEURISTIC" in critique["sample_size_and_power_limitation"]["governance_classification"]


def test_08_horizon_and_power_serial_dependence():
    path = "research/evidence/v30/v30_stage3a_r_horizon_and_power_analysis.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    analysis = data["horizon_and_power_analysis"]
    assert "VERIFIED_OUTCOME_INDEPENDENT" in analysis["outcome_independence_audit"]["outcome_independence_verdict"]
    assert "sensitivity_table" in analysis["power_recalculation_under_serial_dependence"]


def test_09_fail_closed_recovery_invariants():
    path = "research/evidence/v30/v30_stage3a_r_fail_closed_monitoring_review.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    review = data["fail_closed_monitoring_review"]
    assert len(review["risks_of_naive_automatic_restarts"]) == 4
    assert "invariant_1_persistent_incident_lock" in review["fail_closed_recovery_invariants"]
    assert "STRUCTURALLY FORBIDDEN" in review["fail_closed_recovery_invariants"]["invariant_2_manual_authorization_required"]["rule"]


def test_10_historical_regression_reconciliation():
    path = "research/evidence/v30/v30_stage3a_r_historical_regression_failure_reconciliation.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    suites = data["historical_regression_failure_reconciliation"]["evaluated_suites"]
    assert len(suites) == 2
    assert suites[0]["reconciliation_verdict"] == "NOT_A_PRODUCT_REGRESSION. All functional preflight guards, glob checks, and hash verifications in this suite pass cleanly (8/10)."
    assert suites[1]["reconciliation_verdict"] == "NOT_A_PRODUCT_REGRESSION. All 11 core financial accounting, Decimal precision, token security, and simulator parity tests PASS 100%. The sole failure is the hardcoded HEAD string."


def test_11_stage3a_evidence_integrity_discrepancy():
    path = "research/evidence/v30/v30_stage3a_r_stage3a_evidence_integrity.json"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    audit = data["stage3a_evidence_integrity_audit"]
    assert audit["hash_comparison"]["hash_match_status"] == "MISMATCH_DETECTED"
    assert audit["forensic_cause_analysis"]["substantive_impact"] == "ZERO SUBSTANTIVE DRIFT. No findings, scores, mathematical definitions, or governance recommendations were altered. Only the embedded summary table was updated."


def test_12_zero_staged_changes_preserved():
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staged changes detected: {staged}"
    tracked_mod = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert tracked_mod == "", f"Tracked modifications detected: {tracked_mod}"
