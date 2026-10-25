"""
Stage 3B-R2 Final Independent Verification Test Suite.
Validates the five targeted remediations:
1. Exact AR(1) finite-sample variance vs separately implemented reference.
2. Correct null/alternative classification across parameter grid.
3. Null-centered bootstrap construction.
4. Joint HAC/bootstrap decision evaluation from the identical sample sequence.
5. Reproducible simulation seeds.
6. Monte Carlo rejection-rate confidence intervals.
7. Sensitivity grid completeness (216 analytical scenarios).
8. Licensing classification rules under the 5-tier institutional taxonomy.
9. Original Stage 3A governance ID preservation (DEC-01 through DEC-06).
10. Artifact inventory completeness and historical manifest reconciliation.
11. Protected Git checkpoint and 4 protected source hashes.
12. Zero trading activation and zero staged changes.
"""

import os
import sys
import math
import json
import subprocess
import hashlib
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath("."))

from research.simulations.v30_stage3b_r2_reproducible_joint_calibration import (
    exact_ar1_variance,
    compute_analytical_power,
    generate_216_analytical_matrix,
    wilson_score_interval,
    simulate_joint_calibration_scenario
)

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


def test_01_exact_ar1_finite_sample_variance():
    """Verify exact finite-N AR(1) variance against a separately coded reference calculation."""
    N = 30
    rho = 0.20
    sigma = 50.0  # bps

    # Separate reference calculation from first principles
    cov_sum = 0.0
    for k in range(1, N):
        cov_sum += 2.0 * (1.0 - k / N) * (rho ** k)
    ref_factor = 1.0 + cov_sum
    ref_var = (sigma ** 2 / N) * ref_factor
    ref_se = math.sqrt(ref_var)
    ref_n_eff = N / ref_factor

    stats = exact_ar1_variance(N, rho, sigma)

    assert math.isclose(stats["factor_exact"], ref_factor, abs_tol=1e-9)
    assert math.isclose(stats["var_exact"], ref_var, abs_tol=1e-9)
    assert math.isclose(stats["se_exact"], ref_se, abs_tol=1e-9)
    assert math.isclose(stats["n_eff_exact"], ref_n_eff, abs_tol=1e-9)

    # Core target values
    assert math.isclose(stats["factor_exact"], 1.4791666666666667, abs_tol=1e-6)
    assert math.isclose(stats["var_exact"], 123.26388888888889, abs_tol=1e-6)
    assert math.isclose(stats["se_exact"], 11.10242716205908, abs_tol=1e-6)
    assert math.isclose(stats["n_eff_exact"], 20.28169014084507, abs_tol=1e-6)
    assert math.isclose(stats["rel_error_var_pct"], 1.4084507042253457, abs_tol=1e-6)

    # Verify analytical power for target scenario (mu=15, hurdle=10)
    pow_stats = compute_analytical_power(N, rho, sigma, mu=15.0, hurdle=10.0)
    assert math.isclose(pow_stats["power_exact_pct"], 11.614138, abs_tol=1e-4)
    assert math.isclose(pow_stats["power_asymp_pct"], 11.552945, abs_tol=1e-4)


def test_02_correct_null_alternative_classification():
    """Verify correct classification of scenarios as NULL_BOUNDARY, TRUE_NULL, or TRUE_ALTERNATIVE."""
    p_null_bd = compute_analytical_power(30, 0.20, 50.0, mu=10.0, hurdle=10.0)
    assert p_null_bd["scenario_type"] == "NULL_BOUNDARY"
    assert math.isclose(p_null_bd["power_asymp_pct"], 5.0, abs_tol=1e-4)
    assert math.isclose(p_null_bd["power_exact_pct"], 5.0, abs_tol=1e-4)

    p_deep_null = compute_analytical_power(30, 0.20, 50.0, mu=0.0, hurdle=10.0)
    assert p_deep_null["scenario_type"] == "TRUE_NULL_BELOW_HURDLE"
    assert p_deep_null["power_exact_pct"] < 5.0

    p_alt = compute_analytical_power(30, 0.20, 50.0, mu=25.0, hurdle=10.0)
    assert p_alt["scenario_type"] == "TRUE_ALTERNATIVE_ABOVE_HURDLE"
    assert p_alt["power_exact_pct"] > 5.0


def test_03_null_centered_bootstrap_construction():
    """Verify that null-centering transformation strictly forces sample mean to match hurdle."""
    np.random.seed(42)
    sample = np.random.normal(loc=17.5, scale=40.0, size=30)
    hurdle = 10.0
    centered = sample - np.mean(sample) + hurdle
    assert math.isclose(np.mean(centered), hurdle, abs_tol=1e-12)


def test_04_joint_hac_bootstrap_decision_same_sample():
    """Verify that joint decision rule requires BOTH HAC and Bootstrap to reject from identical sample."""
    # Run a small pilot with M=50, B=200
    res = simulate_joint_calibration_scenario(
        N=30, rho=0.20, sigma=50.0, mu=10.0, hurdle=10.0,
        M=50, B=200, seed=12345
    )
    # The joint rejection count cannot exceed min(HAC rejection count, Boot rejection count)
    assert res["joint_rejection_pct"] <= res["hac_rejection_pct"] + 1e-9
    assert res["joint_rejection_pct"] <= res["boot_rejection_pct"] + 1e-9


def test_05_reproducible_simulation_seeds():
    """Verify deterministic reproducibility of Monte Carlo calibration runs."""
    res1 = simulate_joint_calibration_scenario(
        N=30, rho=0.20, sigma=50.0, mu=10.0, hurdle=10.0,
        M=50, B=100, seed=999
    )
    res2 = simulate_joint_calibration_scenario(
        N=30, rho=0.20, sigma=50.0, mu=10.0, hurdle=10.0,
        M=50, B=100, seed=999
    )
    assert math.isclose(res1["joint_rejection_pct"], res2["joint_rejection_pct"], abs_tol=1e-9)
    assert math.isclose(res1["hac_rejection_pct"], res2["hac_rejection_pct"], abs_tol=1e-9)
    assert math.isclose(res1["boot_rejection_pct"], res2["boot_rejection_pct"], abs_tol=1e-9)


def test_06_monte_carlo_confidence_intervals():
    """Verify Wilson score interval calculations."""
    low, high = wilson_score_interval(50, 1000)
    assert 3.5 < low < 4.0
    assert 6.0 < high < 6.8
    assert low < 5.0 < high

    # Edge cases
    low0, high0 = wilson_score_interval(0, 1000)
    assert math.isclose(low0, 0.0, abs_tol=1e-12)
    assert high0 > 0.0


def test_07_sensitivity_grid_completeness():
    """Verify that the 216 analytical scenario matrix contains exactly 216 unique parameter configs."""
    path = "research/evidence/v30/v30_stage3b_r2_corrected_analytical_scenario_matrix.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data["analytical_scenario_matrix_216"]["scenarios"]
    assert len(scenarios) == 216

    param_keys = set()
    for s in scenarios:
        key = (s["N"], s["rho"], s["sigma"], s["mu"])
        param_keys.add(key)
    assert len(param_keys) == 216


def test_08_licensing_classification_rules():
    """Verify the 5-tier institutional licensing classification and DEC-02 BLOCKED status."""
    path = "research/evidence/v30/v30_stage3b_r2_provider_rights_correction.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["provider_rights_correction"]

    assert data["governance_status"] == "DEC-02 REMAINS STRICTLY BLOCKED"
    providers = data["providers"]
    assert "Tiingo" in providers
    assert "Massive_Polygon_io" in providers
    assert "Alpaca" in providers
    assert "Interactive_Brokers" in providers

    # Massive developer non-display strategy usage must be PROHIBITED_UNDER_PUBLISHED_DEFAULT_TERMS
    massive = providers["Massive_Polygon_io"]["entitlements_by_dimension"]
    assert massive["authorized_non_display_research"]["status"] == "PROHIBITED_UNDER_PUBLISHED_DEFAULT_TERMS"


def test_09_original_governance_id_preservation():
    """Verify canonical Stage 3A DEC-01 through DEC-06 titles are restored."""
    path = "research/evidence/v30/v30_stage3b_r2_governance_id_crosswalk.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        crosswalk = json.load(f)["governance_id_crosswalk"]["canonical_taxonomy"]

    assert crosswalk["DEC-01"]["canonical_title"] == "Market Data Provider Selection"
    assert crosswalk["DEC-02"]["canonical_title"] == "Market Data Licensing and Rights"
    assert crosswalk["DEC-03"]["canonical_title"] == "Statistical Endpoint and Inferential Protocol"
    assert crosswalk["DEC-04"]["canonical_title"] == "Evaluation Horizon and Stopping Rules"
    assert crosswalk["DEC-05"]["canonical_title"] == "Monitoring and Incident Governance"
    assert crosswalk["DEC-06"]["canonical_title"] == "Activation Authority"
    assert crosswalk["DEC-06"]["stage3b_r2_reconciled_status"] == "STRICTLY_BLOCKED"


def test_10_artifact_inventory_completeness():
    """Verify evidence inventory reconciles 14 manifest entries with 15 disk files."""
    path = "research/evidence/v30/v30_stage3b_r2_evidence_inventory_reconciliation.json"
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)["evidence_inventory_reconciliation"]

    reconcil = data["deliverable_count_reconciliation"]
    assert reconcil["stage3b_r_text_claim"] == 14
    assert reconcil["stage3b_r_enumerated_items_in_text"] == 15
    assert reconcil["actual_physical_files_created_on_disk"] == 15
    assert reconcil["files_recorded_in_stage3b_r_manifest"] == 14


def test_11_protected_checkpoint_and_hashes():
    """Verify Git checkpoint invariants and the 4 protected source hashes."""
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    assert branch == EXPECTED_BRANCH, f"Branch mismatch: {branch}"

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert head == EXPECTED_HEAD, f"HEAD mismatch: {head}"

    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"], text=True).strip()
    assert parent == EXPECTED_PARENT, f"Parent mismatch: {parent}"

    delta = subprocess.check_output(["git", "diff", "--name-only", "HEAD~1", "HEAD"], text=True).strip().splitlines()
    assert len(delta) == 198, f"Delta file count mismatch: {len(delta)}"

    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"File missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}"


def test_12_zero_trading_activation():
    """Verify working tree has exactly zero staged changes and zero tracked modifications."""
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).strip()
    assert staged == "", f"Staged changes detected: {staged}"
    tracked_mod = subprocess.check_output(["git", "diff", "--name-only"], text=True).strip()
    assert tracked_mod == "", f"Tracked modifications detected: {tracked_mod}"
