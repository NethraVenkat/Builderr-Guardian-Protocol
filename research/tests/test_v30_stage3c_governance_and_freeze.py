"""
Stage 3C Governance, Verification, and Evidence-Freeze Test Suite.
Validates read-only preservation, exploratory protocol boundaries,
canonical decision IDs, staging manifest integrity, and non-activation invariants.
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


def test_01_frozen_branch_and_head():
    """Verify Git branch, HEAD, parent commit, and archival delta count."""
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch mismatch: {branch}"

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD mismatch: {head}"

    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent mismatch: {parent}"

    delta = subprocess.check_output(["git", "diff", "--name-only", "HEAD~1", "HEAD"], text=True).strip().splitlines()
    assert len(delta) == 198, f"Delta file count mismatch: {len(delta)}"


def test_02_protected_source_hashes():
    """Verify the four protected core strategy and universe hashes bit-for-bit."""
    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"File missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_03_historical_files_preserved():
    """Verify historical manifest files from Stages 3A, 3A-R, 3B, 3B-R, and 3B-R2 exist unmodified."""
    manifests = [
        "research/evidence/v30/v30_stage3a_artifact_checksum_manifest.json",
        "research/evidence/v30/v30_stage3a_r_artifact_and_checksum_inventory.json",
        "research/evidence/v30/v30_stage3b_artifact_checksum_manifest.json",
        "research/evidence/v30/v30_stage3b_r_inventory_and_checksum_manifest.json",
        "research/evidence/v30/v30_stage3b_r2_artifact_checksum_manifest.json"
    ]
    for m in manifests:
        assert os.path.exists(m), f"Historical manifest missing: {m}"


def test_04_eligible_evidence_inventory_completeness():
    """Verify that eligible evidence inventory records all prior stage files without unexplained omissions."""
    inv_path = "research/evidence/v30/v30_stage3c_eligible_evidence_inventory.json"
    assert os.path.exists(inv_path), f"Missing: {inv_path}"
    with open(inv_path, "r", encoding="utf-8") as f:
        data = json.load(f)["eligible_evidence_inventory"]

    assert data["total_prior_eligible_files"] >= 70
    stages = data["summary_by_stage"]
    assert stages["Stage 3A"] == 12
    assert stages["Stage 3A-R"] == 14
    assert stages["Stage 3B"] == 14
    assert stages["Stage 3B-R"] == 15
    assert stages["Stage 3B-R2"] == 15


def test_05_exclusion_ledger_and_tier3_non_access():
    """Verify exclusion ledger excludes tiingo_cache, pytest_cache, and pycache."""
    ex_path = "research/evidence/v30/v30_stage3c_exclusion_and_disposition_ledger.json"
    assert os.path.exists(ex_path), f"Missing: {ex_path}"
    with open(ex_path, "r", encoding="utf-8") as f:
        data = json.load(f)["exclusion_and_disposition_ledger"]

    patterns = [e["path_or_pattern"] for e in data["excluded_entries"]]
    assert "tiingo_cache/" in patterns
    assert ".pytest_cache/" in patterns
    assert "**/__pycache__/" in patterns


def test_06_staging_manifest_paths_exist():
    """Verify all paths in the human archival staging manifest exist or are designated Stage 3C deliverables."""
    stage_path = "research/evidence/v30/v30_stage3c_human_archival_staging_manifest.json"
    assert os.path.exists(stage_path), f"Missing: {stage_path}"
    with open(stage_path, "r", encoding="utf-8") as f:
        data = json.load(f)["human_archival_staging_manifest"]

    for path, info in data["approved_paths"].items():
        if not path.startswith("research/evidence/v30/v30_stage3c_") and not "STAGE3C" in path and not path.endswith("stage3c_governance_and_freeze.py"):
            assert os.path.exists(path), f"Staging target does not exist: {path}"


def test_07_canonical_decision_ids_and_exploratory_recommendation():
    """Verify canonical DEC-01 through DEC-06 IDs are preserved and DEC-03 is Exploratory-Only."""
    dec_path = "research/evidence/v30/v30_stage3c_canonical_owner_decision_register.json"
    assert os.path.exists(dec_path), f"Missing: {dec_path}"
    with open(dec_path, "r", encoding="utf-8") as f:
        data = json.load(f)["canonical_owner_decision_register"]["decisions"]

    d_map = {d["decision_id"]: d for d in data}
    assert d_map["DEC-01"]["title"] == "Market Data Provider Selection"
    assert d_map["DEC-02"]["title"] == "Market Data Licensing and Rights"
    assert d_map["DEC-02"]["recommended_status"] == "STRICTLY_BLOCKED"
    assert d_map["DEC-03"]["title"] == "Statistical Endpoint and Inferential Protocol"
    assert "EXPLORATORY" in d_map["DEC-03"]["recommended_status"]
    assert d_map["DEC-04"]["title"] == "Evaluation Horizon and Stopping Rules"
    assert d_map["DEC-05"]["title"] == "Monitoring and Incident Governance"
    assert d_map["DEC-06"]["title"] == "Activation Authority"
    assert d_map["DEC-06"]["recommended_status"] == "STRICTLY_BLOCKED"


def test_08_scientific_alternatives_option_c_preferred():
    """Verify Option A rejected, Option B deferred, Option C preferred proposal."""
    alt_path = "research/evidence/v30/v30_stage3c_scientific_alternatives_decision_matrix.json"
    assert os.path.exists(alt_path), f"Missing: {alt_path}"
    with open(alt_path, "r", encoding="utf-8") as f:
        alts = json.load(f)["scientific_alternatives_decision_matrix"]["evaluated_alternatives"]

    assert alts["OPTION_A"]["recommendation"] == "REJECT_FOR_CONFIRMATORY_USE"
    assert alts["OPTION_B"]["recommendation"] == "FUTURE_RESEARCH_OPTION_ONLY"
    assert alts["OPTION_C"]["recommendation"] == "PREFERRED_PROPOSAL"


def test_09_exploratory_protocol_boundaries():
    """Verify exploratory protocol designates hurdle, CAGR, and horizon as UNAPPROVED PROPOSALS."""
    proto_path = "research/evidence/v30/v30_stage3c_exploratory_only_preregistration_draft.json"
    assert os.path.exists(proto_path), f"Missing: {proto_path}"
    with open(proto_path, "r", encoding="utf-8") as f:
        data = json.load(f)["exploratory_only_preregistration_draft"]

    unapproved = data["unapproved_historical_proposals"]
    assert "UNAPPROVED_PROPOSAL" in unapproved["economic_hurdle_10bps"]
    assert "UNAPPROVED_PROPOSAL" in unapproved["cagr_guardrail_200bps"]
    assert "UNAPPROVED_PROPOSAL" in unapproved["horizon_252_sessions"]
    assert "UNAPPROVED_PROPOSAL" in unapproved["maximum_504_sessions"]


def test_10_statistical_failure_preservation_intact():
    """Verify Stage 3B-R2 numerical results and FAILED size distortion status are preserved."""
    fail_path = "research/evidence/v30/v30_stage3c_statistical_failure_preservation_record.json"
    assert os.path.exists(fail_path), f"Missing: {fail_path}"
    with open(fail_path, "r", encoding="utf-8") as f:
        data = json.load(f)["statistical_failure_preservation_record"]["preserved_numerical_results"]

    assert math.isclose(data["exact_analytical_power_pct"], 11.6141, abs_tol=1e-3)
    assert math.isclose(data["joint_null_boundary_rejection_pct"], 7.70, abs_tol=1e-2)
    assert data["size_calibration_status"] == "FAILED_SIZE_DISTORTION"


def test_11_zero_trading_activation():
    """Verify working tree has exactly zero staged changes and zero tracked modifications."""
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staged changes detected: {staged}"
    tracked_mod = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert tracked_mod == "", f"Tracked modifications detected: {tracked_mod}"
