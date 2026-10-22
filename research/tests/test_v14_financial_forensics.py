"""
Stage B2-E / Protocol V14: Forensic Test Suite & Invariant Verification.
Guarantees source-grounded universe equality, exact event counts,
accounting invariants, and statistical reproducibility.
"""
import ast
import json
import math
from pathlib import Path
import pytest
import numpy as np

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined


def test_production_universe_exact_equality():
    """Verify production manifest matches agent.py source AST exactly."""
    source_text = Path("agent.py").read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    
    risk_candidates = []
    overlay_tickers = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RISK_CANDIDATES":
                    if isinstance(node.value, (ast.Tuple, ast.List)):
                        risk_candidates = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                        
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "target_weights":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and sub.value in ("QLD", "SSO"):
                    if sub.value not in overlay_tickers:
                        overlay_tickers.append(sub.value)
                        
    true_universe = sorted(list(set(risk_candidates + overlay_tickers)))
    assert len(true_universe) == 24
    
    manifest_path = Path("research/manifests/production_universe_manifest.json")
    assert manifest_path.exists(), "Manifest file must exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_tickers = sorted(list(manifest["instruments"].keys()))
    
    # Exact membership equality
    assert manifest_tickers == true_universe
    
    # Explicitly check required E0 instruments
    for required in ["DIA", "IWM", "SMH", "TSLA", "QLD", "SSO"]:
        assert required in manifest_tickers, f"Required E0 instrument {required} missing"
        
    # Explicitly check unauthorized substitutions are absent
    for unauthorized in ["XLB", "JPM", "V", "JNJ", "WMT", "PG"]:
        assert unauthorized not in manifest_tickers, f"Unauthorized substitute {unauthorized} present"


def test_regime_calendar_lengths_and_notional():
    """Verify exact session lengths and turnover bounds for all 3 regimes."""
    expected_lengths = {
        "calm_uptrend": 64,
        "moderate_selloff": 31,
        "vol_spike_snapback": 50,
    }
    
    for regime_name, expected_days in expected_lengths.items():
        prov = StaticRegimeProvider("sample_regimes.json.gz", regime_name)
        eng = ReplayEngine("agent.py", prov, start_cash=100_000.0)
        res = eng.run_replay()
        
        actual_days = len(res["equity_curve"])
        assert actual_days == expected_days, f"{regime_name} expected {expected_days} days, got {actual_days}"
        
        if regime_name == "calm_uptrend":
            assert 700_000.0 < res["turnover"] < 750_000.0
            assert 350.0 < res["slippage_cost"] < 380.0
        elif regime_name == "moderate_selloff":
            assert 250_000.0 < res["turnover"] < 320_000.0
            assert 130.0 < res["slippage_cost"] < 160.0
        elif regime_name == "vol_spike_snapback":
            assert 230_000.0 < res["turnover"] < 270_000.0
            assert 115.0 < res["slippage_cost"] < 140.0


def test_accounting_invariants_and_slippage_integrity():
    """Verify double-entry balance sheet invariant and slippage formula."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    cand = CandidateAE_Combined()
    eng = ReplayEngine(cand.decide, prov, start_cash=100_000.0)
    res = eng.run_replay()
    
    # Portfolio invariant check
    port = eng.last_portfolio
    assert port is not None
    
    # Check that slippage cost in replay equals sum(notional * slippage)
    expected_slippage = sum(f.notional * f.slippage for f in res["fill_log"])
    assert math.isclose(res["slippage_cost"], expected_slippage, rel_tol=1e-6)
    
    # Ending equity must reconcile: Start Cash + Realized + Unrealized + Div - Comm
    last_slice = list(prov.stream_daily_slices())[-1][1]
    last_closes = {t: b[-1]["close"] for t, b in last_slice.items() if b}
    ok, reason = port.check_accounting_invariants(last_closes)
    assert ok, f"Accounting invariant failed: {reason}"
    
    reconstructed = (
        port.start_cash
        + port.realized_pnl
        + port.unrealized_pnl(last_closes)
        + port.total_dividends_credited
        + port.dividend_receivables
        - port.total_commissions
    )
    assert math.isclose(res["equity_curve"][-1], reconstructed, abs_tol=1e-5)


def test_four_way_candidate_deterministic_returns():
    """Verify exact reproduction of V12 four-way comparison metrics."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    
    # E0 Baseline
    res_e0 = ReplayEngine("agent.py", prov, start_cash=100_000.0).run_replay()
    assert math.isclose(res_e0["metrics"]["ret"], -0.1577296, abs_tol=1e-5)
    
    # Candidate A+E
    res_ae = ReplayEngine(CandidateAE_Combined().decide, prov, start_cash=100_000.0).run_replay()
    assert math.isclose(res_ae["metrics"]["ret"], -0.1315176, abs_tol=1e-5)
    
    # Outperformance is exactly +262.1 bps
    delta_bps = (res_ae["metrics"]["ret"] - res_e0["metrics"]["ret"]) * 10000.0
    assert math.isclose(delta_bps, 262.12, abs_tol=0.1)


def test_statistical_uncertainty_negative_control():
    """Verify paired t-test fails to reject null hypothesis at 95% confidence on N=49 days."""
    prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
    res_e0 = ReplayEngine("agent.py", prov, start_cash=100_000.0).run_replay()
    res_ae = ReplayEngine(CandidateAE_Combined().decide, prov, start_cash=100_000.0).run_replay()
    
    eq0 = np.array(res_e0["equity_curve"])
    eqae = np.array(res_ae["equity_curve"])
    diff = (eqae[1:] / eqae[:-1] - 1.0) - (eq0[1:] / eq0[:-1] - 1.0)
    
    n = len(diff)
    assert n == 49
    mean_d = float(np.mean(diff))
    se_d = float(np.std(diff, ddof=1)) / math.sqrt(n)
    t_stat = mean_d / se_d
    
    # Critical value for t(48) at alpha=0.05 two-sided is ~2.01
    assert abs(t_stat) < 2.01, f"t-stat {t_stat} should not be significant at 95% confidence"
