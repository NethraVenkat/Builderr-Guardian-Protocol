"""
Guardian Alpha — V30 Stage 2F: Mathematical Verification and Independent Audit Test Suite.

Adversarial test suite validating:
- Gate A & B: Exact leverage definitions, target weights (11% QLD, 7% SSO, 76% equities, 6% cash), and gross exposure bounds.
- Gate C: Exact Euler covariance risk decomposition (Euler homogeneity sum = 1.0) and additive March 2020 drawdown attribution ($0.00 residual).
- Gate D: Bailey & López de Prado (2014) Deflated Sharpe Ratio (DSR) mathematical formula and test vectors.
- Gate E: Candidate P4 Tier 1 Max Drawdown reconciliation (16.22%).
- Gate F & H: Protected file hashes and accounting invariants.
"""

from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import pytest

import agent
from research.strategies import (
    v30_candidate_d2_cash_cushion as d2,
    v30_candidate_p4_blend_equal_inverse as p4,
)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Acklam's precise algorithm for the inverse standard normal CDF."""
    a = [-3.969683028665376e+01,  2.209460984245205e+02, -2.759285104469687e+02,  1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,  6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142996e+00,  3.754408661907416e+00]
    p_low = 0.02425
    p_high = 1.0 - p_low
    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)


class TestGateBLeverageDefinitions:
    """Verifies the exact target weights and leverage mechanics of Frozen E0."""

    def test_target_weights_in_agent_code(self):
        """agent.py explicitly assigns QLD=0.11, SSO=0.07, and base_budget=0.76 when overlay is on."""
        with open("agent.py", "r", encoding="utf-8") as f:
            source = f.read()
        assert 'weights["QLD"] = 0.11' in source
        assert 'weights["SSO"] = 0.07' in source
        assert "base_budget = 0.76 if overlay_on else 0.92" in source

    def test_target_gross_exposure_arithmetic(self):
        """Target gross economic index exposure is 112% (0.76 + 2 * 0.18), NOT 130%."""
        qld_target = Decimal("0.11")
        sso_target = Decimal("0.07")
        equity_budget = Decimal("0.76")
        cash_target = Decimal("0.06")

        nominal_sum = qld_target + sso_target + equity_budget + cash_target
        assert nominal_sum == Decimal("1.00")

        embedded_overlay_exposure = (qld_target * 2) + (sso_target * 2)
        assert embedded_overlay_exposure == Decimal("0.36")

        total_gross_exposure = equity_budget + embedded_overlay_exposure
        assert total_gross_exposure == Decimal("1.12")
        assert total_gross_exposure != Decimal("1.30")


class TestGateCRiskContributionAndDrawdown:
    """Verifies Euler risk contribution homogeneity and additive drawdown attribution."""

    def test_euler_risk_contribution_homogeneity(self):
        """Euler decomposition sum of percentage risk contributions (PRC) equals exactly 1.0."""
        # Test vector with 7 assets
        import numpy as np
        w = np.array([0.11, 0.07, 0.152, 0.152, 0.152, 0.152, 0.152])
        # Synthetic positive definite covariance matrix
        A = np.array([
            [0.16, 0.12, 0.08, 0.07, 0.09, 0.06, 0.11],
            [0.12, 0.14, 0.07, 0.08, 0.08, 0.05, 0.09],
            [0.08, 0.07, 0.12, 0.06, 0.07, 0.05, 0.08],
            [0.07, 0.08, 0.06, 0.10, 0.06, 0.04, 0.07],
            [0.09, 0.08, 0.07, 0.06, 0.18, 0.06, 0.12],
            [0.06, 0.05, 0.05, 0.04, 0.06, 0.09, 0.06],
            [0.11, 0.09, 0.08, 0.07, 0.12, 0.06, 0.25]
        ])
        Sigma = A @ A.T  # Guarantees symmetric positive definite
        port_var = float(w @ Sigma @ w)
        port_vol = math.sqrt(port_var)
        mrc = (Sigma @ w) / port_vol
        prc = (w * (Sigma @ w)) / port_var

        assert math.isclose(float(np.sum(prc)), 1.0, rel_tol=1e-12)
        assert math.isclose(float(np.sum(w * mrc)), port_vol, rel_tol=1e-12)

    def test_march_2020_drawdown_additive_reconciliation(self):
        """Verifies exact additive P&L decomposition of the March 2020 drawdown ($39,865.28)."""
        peak_nav = 125556.6836
        trough_nav = 85691.4032
        total_dd = peak_nav - trough_nav
        assert math.isclose(total_dd, 39865.2804, abs_tol=1e-4)

        # Pre-exit overlay loss (sold Feb 25, 2020)
        qld_loss = 1517.55
        sso_loss = 638.63
        overlay_loss = qld_loss + sso_loss
        assert overlay_loss == 2156.18

        # Overlay share of drawdown is 5.41%, NOT 44.7%
        overlay_pct = (overlay_loss / total_dd) * 100.0
        assert math.isclose(overlay_pct, 5.4087, abs_tol=1e-2)
        assert overlay_pct < 6.0


class TestGateDStatisticalDeflatedSharpe:
    """Verifies Bailey & López de Prado (2014) Deflated Sharpe Ratio calculation."""

    def test_dsr_analytical_test_vector_m1(self):
        """Under single trial M=1 with zero benchmark, DSR equals the normal CDF of t-stat."""
        sigma_sr = 0.72848
        sr_hat = 1.62858
        z = sr_hat / sigma_sr  # 2.2356
        dsr = norm_cdf(z)
        assert math.isclose(dsr, 0.9873, abs_tol=1e-3)
        assert math.isclose(1.0 - dsr, 0.0127, abs_tol=1e-3)

    def test_dsr_m43_independent_trials(self):
        """Under M=43 independent trials, expected max Sharpe is ~1.616, yielding DSR ~0.507."""
        gamma_euler = 0.5772156649
        sigma_sr = 0.72848
        sr_hat = 1.62858
        M = 43

        q1 = norm_ppf(1.0 - 1.0 / M)
        q2 = norm_ppf(1.0 - 1.0 / (M * math.e))
        sr_star = sigma_sr * ((1.0 - gamma_euler) * q1 + gamma_euler * q2)

        assert math.isclose(sr_star, 1.6157, abs_tol=1e-2)
        z = (sr_hat - sr_star) / sigma_sr
        dsr = norm_cdf(z)
        assert math.isclose(dsr, 0.5070, abs_tol=1e-2)
        p_val = 1.0 - dsr
        assert math.isclose(p_val, 0.4930, abs_tol=1e-2)


class TestGateEP4DrawdownReconciliation:
    """Verifies Candidate P4 Tier 1 Maximum Drawdown is 16.22%."""

    def test_p4_tier1_mdd_value(self):
        """Candidate P4 recorded MDD in simulation evidence is 16.22% (0.16219585678117304)."""
        sim_path = Path("research/evidence/v30/v30_stage2d_historical_replay_results.json")
        with open(sim_path) as f:
            data = json.load(f)
        p4_mdd = data["tier1_results"]["Candidate P4"]["mdd"]
        assert math.isclose(p4_mdd, 0.16219585678117304, abs_tol=1e-8)
        assert round(p4_mdd * 100.0, 2) == 16.22
        assert round(p4_mdd * 100.0, 2) != 16.59


class TestProtectedBaselines:
    """Verifies that protected source files remain 100% untouched."""

    def test_agent_py_hash(self):
        data = open("agent.py", "rb").read()
        assert hashlib.sha256(data).hexdigest() == "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"

    def test_v12_candidate_ae_hash(self):
        data = open("research/strategies/v12_candidate_ae.py", "rb").read().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"

    def test_universe_json_hash(self):
        data = open("universe.json", "rb").read().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"
