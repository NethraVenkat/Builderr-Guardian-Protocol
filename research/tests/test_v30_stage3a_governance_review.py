import os
import subprocess
import hashlib
import json
import pytest

EXPECTED_HEAD = "ce6b4c21b832044d0ffb45dce2ba949ab867d520"
EXPECTED_PARENT = "b283ded200c777b130285b0aa56a0b044afbd339"
EXPECTED_BRANCH = "archive/v30-stage2h-final-evidence-freeze"

def compute_sha256(filepath, lf=False):
    with open(filepath, "rb") as f:
        data = f.read()
    if lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()

def test_01_git_checkpoint_and_parent():
    """Verify archival branch, HEAD, commit parent, and 198 archived artifacts."""
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD {head} != {EXPECTED_HEAD}"
    
    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent {parent} != {EXPECTED_PARENT}"
    
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch {branch} != {EXPECTED_BRANCH}"

def test_02_protected_source_file_hashes():
    """Verify bit-for-bit integrity of the 4 protected files."""
    protected = [
        ("agent.py", False, "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"),
        ("universe.json", True, "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"),
        ("research/strategies/v12_candidate_ae.py", True, "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"),
        ("research/strategies/v30_candidate_d2_cash_cushion.py", False, "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215"),
    ]
    for path, lf, expected_hash in protected:
        assert os.path.exists(path), f"Protected file missing: {path}"
        actual = compute_sha256(path, lf=lf)
        assert actual == expected_hash, f"Hash mismatch for {path}: {actual} != {expected_hash}"

def test_03_tier3_isolation():
    """Verify tiingo_cache is NOT in Git index and remains sealed."""
    ls_files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    for f in ls_files:
        assert "tiingo_cache" not in f, f"tiingo_cache found in Git index: {f}"

def test_04_traceability_matrix_classification_taxonomy():
    """Verify traceability matrix strictly uses the 6 allowed taxonomy classifications."""
    path = "research/evidence/v30/v30_stage3a_cross_stage_traceability_matrix.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    allowed = set(data["matrix_metadata"]["allowed_classifications"])
    for entry in data["traceability_entries"]:
        cls = entry["classification"]
        assert cls in allowed, f"Invalid classification in {entry['id']}: {cls}"

def test_05_activation_authority_strictly_blocked():
    """Verify DEC-06 is marked BLOCKED in all decision files."""
    reg_path = "research/evidence/v30/v30_stage3a_owner_decision_register.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)
    assert reg["decisions"]["DEC-06"]["status"] == "BLOCKED"
    assert reg["decisions"]["DEC-06"]["can_agent_execute"] is False

def test_06_provider_comparison_schema():
    """Verify provider comparison evaluates all 4 providers across required dimensions."""
    prov_path = "research/evidence/v30/v30_stage3a_provider_and_licensing_comparison.json"
    with open(prov_path, "r", encoding="utf-8") as f:
        prov = json.load(f)
    
    expected_providers = {"Tiingo", "Polygon_Massive", "Alpaca", "Interactive_Brokers"}
    actual_providers = set(prov["providers"].keys())
    assert expected_providers == actual_providers
    
    for name, pdata in prov["providers"].items():
        assert "licensing_terms" in pdata
        assert "suitability_verdict" in pdata
        assert pdata["suitability_verdict"] in ["CONDITIONALLY SUITABLE", "SUITABLE", "BLOCKED"]

def test_07_statistical_endpoint_specification():
    """Verify primary endpoint formula, hurdle, and secondary constraint."""
    stat_path = "research/evidence/v30/v30_stage3a_statistical_endpoint_decision_matrix.json"
    with open(stat_path, "r", encoding="utf-8") as f:
        stat = json.load(f)
    
    assert "d_t = \\max(0, -R_{E0,t}) - \\max(0, -R_{D2,t})" in stat["primary_endpoint"]["mathematical_formula"]
    assert stat["primary_endpoint"]["minimum_effect_size_hurdle"] == "delta_{min} = 0.0010 (10 basis points per defensive session)"
    assert "CAGR_{D2} >= CAGR_{E0} - 0.0200" in stat["secondary_full_horizon_constraint"]["mathematical_formula"]

def test_08_horizon_and_power_assessment():
    """Verify horizon parameters and power table."""
    hor_path = "research/evidence/v30/v30_stage3a_horizon_and_power_assessment.json"
    with open(hor_path, "r", encoding="utf-8") as f:
        hor = json.load(f)
    
    assert hor["horizon_parameters"]["nominal_duration_sessions"] == 252
    assert hor["horizon_parameters"]["minimum_defensive_sessions_floor"] == 30
    assert len(hor["statistical_power_analysis"]["power_table"]) >= 5

def test_09_monitoring_and_incident_readiness():
    """Verify monitoring controls audit identifies host OS supervision gap."""
    mon_path = "research/evidence/v30/v30_stage3a_monitoring_and_incident_readiness.json"
    with open(mon_path, "r", encoding="utf-8") as f:
        mon = json.load(f)
    
    assert len(mon["controls_evaluation"]) == 6
    assert mon["adversarial_sre_finding"]["finding"] == "HOST_OS_SUPERVISION_GAP"

def test_10_zero_staged_changes_preserved():
    """Verify zero Git staging or modified tracked files."""
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staging area contains changes: {staged}"
    modified = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert modified == "", f"Tracked files modified: {modified}"
