import os
import subprocess
import hashlib
import json
import pytest

EXPECTED_HEAD = "b283ded200c777b130285b0aa56a0b044afbd339"

def compute_sha256(filepath, lf=False):
    with open(filepath, "rb") as f:
        data = f.read()
    if lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()

def test_01_git_checkpoint_and_clean_working_tree():
    """Verify Git HEAD is exact and working tree has zero staged/modified tracked files."""
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD {head} does not match expected {EXPECTED_HEAD}"
    
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staging area is not clean: {staged}"
    
    modified = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert modified == "", f"Tracked files modified: {modified}"

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

def test_03_powershell_script_zero_globs():
    """Static analysis of PowerShell script: verify zero path globs and zero wildcards."""
    script_path = "research/scripts/v30_stage2h_c_r2_human_archival_script.ps1"
    assert os.path.exists(script_path), f"Script missing: {script_path}"
    
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("git add"):
            assert "-A" not in trimmed, f"Glob flag -A found in {line}"
            assert "--all" not in trimmed, f"Glob flag --all found in {line}"
            assert "git add ." not in trimmed, f"Glob git add . found in {line}"
            assert "*" not in trimmed, f"Wildcard * found in {line}"
            assert "?" not in trimmed, f"Wildcard ? found in {line}"

def test_04_human_powershell_instructions_zero_globs():
    """Verify JSON instructions contain zero wildcards or globs in any step command."""
    instr_path = "research/evidence/v30/v30_stage2h_c_r2_human_powershell_instructions.json"
    assert os.path.exists(instr_path), f"Instructions missing: {instr_path}"
    
    with open(instr_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for step in data.get("execution_steps", []):
        cmd = step.get("command", "")
        if "git add" in cmd:
            assert "-A" not in cmd, f"Glob -A in step: {cmd}"
            assert "--all" not in cmd, f"Glob --all in step: {cmd}"
            assert "git add ." not in cmd, f"Glob git add . in step: {cmd}"
            assert "*" not in cmd, f"Wildcard * in step: {cmd}"

def test_05_staging_manifest_explicit_paths_exist():
    """Verify all 198 paths in corrected staging manifest exist on disk."""
    manifest_path = "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json"
    assert os.path.exists(manifest_path), f"Manifest missing: {manifest_path}"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    all_paths = []
    for grp_name, files in data.get("staging_groups", {}).items():
        for file_entry in files:
            path = file_entry["relative_path"] if isinstance(file_entry, dict) else file_entry
            all_paths.append(path)
            assert os.path.exists(path), f"File in staging manifest missing on disk: {path}"
    
    assert len(all_paths) == 198, f"Expected 198 files in staging manifest, got {len(all_paths)}"

def test_06_staging_manifest_no_duplicates_or_case_collisions():
    """Verify staging manifest contains no duplicates and no case collisions."""
    manifest_path = "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    paths = []
    for grp, files in data.get("staging_groups", {}).items():
        for f in files:
            p = f["relative_path"] if isinstance(f, dict) else f
            paths.append(p)
            
    assert len(paths) == len(set(paths)), "Duplicate paths detected in staging manifest!"
    assert len(paths) == len(set(p.lower() for p in paths)), "Case collisions detected in staging manifest!"

def test_07_restricted_paths_exclusion():
    """Verify tiingo_cache and secrets are strictly excluded from staging manifest."""
    manifest_path = "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for grp, files in data.get("staging_groups", {}).items():
        for f in files:
            p = f["relative_path"] if isinstance(f, dict) else f
            assert "tiingo_cache" not in p, f"Restricted path found in staging manifest: {p}"
            assert not p.endswith(".token"), f"Token file found: {p}"
            assert not p.endswith(".secret"), f"Secret file found: {p}"

def test_08_set_based_completeness_unaccounted_zero():
    """Verify set difference between all porcelain untracked files and staging manifest is empty."""
    manifest_path = "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    manifest_paths = set()
    for grp, files in data.get("staging_groups", {}).items():
        for f in files:
            p = f["relative_path"] if isinstance(f, dict) else f
            manifest_paths.add(p)
            
    porcelain = subprocess.check_output(["git", "status", "--porcelain", "-uall"], text=True).splitlines()
    porcelain_untracked = set(l[3:].strip().replace("\\", "/") for l in porcelain if l.startswith("??"))
    
    # All untracked files on disk must be in manifest_paths
    unaccounted = porcelain_untracked - manifest_paths
    assert len(unaccounted) == 0, f"Unaccounted untracked files on disk: {unaccounted}"
    
    # All manifest paths must be on disk
    missing = manifest_paths - porcelain_untracked
    assert len(missing) == 0, f"Manifest paths not present on disk: {missing}"

def test_09_powershell_script_preflight_guards():
    """Verify PowerShell script has pre-flight checks and zero remote push."""
    script_path = "research/scripts/v30_stage2h_c_r2_human_archival_script.ps1"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert EXPECTED_HEAD in content, "PowerShell script missing expected HEAD verification"
    assert "archive/v30-stage2h-final-evidence-freeze" in content, "Missing branch check"
    assert "tiingo_cache" in content, "Missing boundary check for tiingo_cache"
    assert "git push" not in content, "CRITICAL ERROR: git push found in human archival script!"

def test_10_private_backup_reconciliation_status():
    """Verify backup reconciliation declares PLAN COMPLETE, BACKUP NOT EXECUTED, RESTORE NOT VERIFIED."""
    backup_path = "research/evidence/v30/v30_stage2h_c_r2_private_backup_reconciliation.json"
    assert os.path.exists(backup_path), f"Backup reconciliation missing: {backup_path}"
    with open(backup_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["status"] == "PLAN COMPLETE", f"Status is not PLAN COMPLETE: {data['status']}"
    assert data["backup_execution"] == "BACKUP NOT EXECUTED", f"Backup execution is: {data['backup_execution']}"
    assert data["restore_verification"] == "RESTORE NOT VERIFIED", f"Restore verification is: {data['restore_verification']}"
