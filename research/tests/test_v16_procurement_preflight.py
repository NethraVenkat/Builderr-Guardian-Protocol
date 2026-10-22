"""
Stage B2-G / Master Guardian Protocol V16: Procurement Preflight & Adversarial Regression Suite.
Tests cent-level rounding order, clean-checkout commit verification,
provider history horizon sufficiency, pre-inception boundaries, and holdout contamination register.
"""
from datetime import date, datetime
import math
from pathlib import Path
import pytest

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined


def test_cent_level_rounding_order_reconciliation():
    """Prove the mathematical origin of $2,621.20 vs $2,621.21."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    res_e0 = ReplayEngine("agent.py", prov, start_cash=100_000.0).run_replay()
    res_ae = ReplayEngine(CandidateAE_Combined().decide, prov, start_cash=100_000.0).run_replay()
    
    eq_e0_raw = res_e0["equity_curve"][-1]
    eq_ae_raw = res_ae["equity_curve"][-1]
    raw_diff = eq_ae_raw - eq_e0_raw
    
    # Method 1: Round after subtracting raw floats
    diff_round_after = round(raw_diff, 2)
    # Method 2: Subtract rounded components
    diff_of_rounded = round(eq_ae_raw, 2) - round(eq_e0_raw, 2)
    
    # Verify the exact discrepancy
    assert math.isclose(diff_round_after, 2621.21, abs_tol=1e-5), f"Expected 2621.21, got {diff_round_after}"
    assert math.isclose(diff_of_rounded, 2621.20, abs_tol=1e-5), f"Expected 2621.20, got {diff_of_rounded}"
    assert math.isclose(raw_diff, 2621.207100, abs_tol=1e-5)


def test_v15_clean_worktree_commit_id():
    """Verify clean clone worktree is checked out at full V15 commit, not V14."""
    clean_clone_path = Path("C:/Users/Manish/Downloads/Guardian-Alpha-Clean-Clone-V15")
    if clean_clone_path.exists():
        head_file = clean_clone_path / ".git"
        # In a git worktree, .git is a text file pointing to worktrees metadata
        assert head_file.exists(), "Clean clone .git reference must exist"
        
        # Read the HEAD from worktree
        import subprocess
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(clean_clone_path),
            capture_output=True,
            text=True,
            check=True,
        )
        checked_out_commit = res.stdout.strip()
        v15_full_commit = "564fa3401a58479b52f8ed231ab51d313919eb7f"
        v14_full_commit = "992139abb40027bc036cffe23b5e86936dc05e02"
        
        assert checked_out_commit != v14_full_commit, "Clean clone was incorrectly at V14 commit!"
        assert checked_out_commit == v15_full_commit, f"Expected V15 commit {v15_full_commit}, got {checked_out_commit}"


def test_provider_rolling_10_year_history_insufficiency():
    """Prove that as of late 2026, a 10-year rolling provider history does NOT cover January 2015."""
    as_of_date = date(2026, 10, 22)
    target_start_date = date(2015, 1, 1)
    
    # Exactly 10 calendar years back from 2026-10-22 is 2016-10-22
    ten_years_ago = date(as_of_date.year - 10, as_of_date.month, as_of_date.day)
    
    # Gap between target start date and provider availability
    days_shortfall = (ten_years_ago - target_start_date).days
    months_shortfall = (ten_years_ago.year - target_start_date.year) * 12 + (ten_years_ago.month - target_start_date.month)
    
    assert ten_years_ago > target_start_date, "10-year rolling window should fall short of 2015-01-01"
    assert months_shortfall >= 21, f"Expected at least 21 months shortfall, got {months_shortfall}"
    assert days_shortfall >= 650, f"Expected at least 650 days shortfall, got {days_shortfall}"


def test_holdout_boundary_strict_absence():
    """Verify that no observation in sample_regimes.json.gz is dated >= 2022-01-01."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    for r in ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]:
        p = StaticRegimeProvider("sample_regimes.json.gz", r)
        for dt in p.get_timeline():
            assert dt < "2022-01-01", f"Holdout boundary breach: {dt} in {r}"
