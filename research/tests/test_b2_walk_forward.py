"""Stage G6 & G7: Controlled Strategy Optimization & Walk-Forward Validation Tests.

Validates:
  1. Candidate strategy interface compatibility with decide(market_state, portfolio_state, cash).
  2. Candidate drawdown de-risking logic.
  3. Paired block bootstrap statistical properties.
  4. WalkForwardValidator execution on sample regime data.
  5. Formal G7 decision classification.
"""
from __future__ import annotations

from pathlib import Path
import pytest

import agent
from research.engine.provider import StaticRegimeProvider
from research.engine.walk_forward import (
    WalkForwardValidator,
    compute_paired_bootstrap,
)
from research.strategies.candidate_alpha import AdaptiveRiskParityCandidate

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_REGIMES_PATH = REPO_ROOT / "sample_regimes.json.gz"


class TestCandidateStrategyAndOptimization:
    def test_candidate_interface_parity(self):
        cand = AdaptiveRiskParityCandidate()
        dummy_market = {
            "SPY": [{"ts": f"2024-01-{i:02d}", "open": 500.0, "high": 505.0, "low": 495.0, "close": 500.0 + i, "volume": 1000} for i in range(1, 60)],
            "QQQ": [{"ts": f"2024-01-{i:02d}", "open": 400.0, "high": 405.0, "low": 395.0, "close": 400.0 + i, "volume": 1000} for i in range(1, 60)],
        }
        dummy_port = {"cash": 100_000.0, "positions": [], "last_prices": {"SPY": 559.0, "QQQ": 459.0}}
        orders = cand.decide(dummy_market, dummy_port, 100_000.0)
        assert isinstance(orders, list)
        for ord_dict in orders:
            assert "ticker" in ord_dict
            assert "side" in ord_dict
            assert "quantity" in ord_dict

    def test_candidate_drawdown_derisking(self):
        cand = AdaptiveRiskParityCandidate(dd_derisk_threshold=0.10)
        dummy_market = {
            "SPY": [{"ts": f"2024-01-{i:02d}", "open": 500.0, "high": 505.0, "low": 495.0, "close": 500.0 + i, "volume": 1000} for i in range(1, 60)],
            "QQQ": [{"ts": f"2024-01-{i:02d}", "open": 400.0, "high": 405.0, "low": 395.0, "close": 400.0 + i, "volume": 1000} for i in range(1, 60)],
        }
        # Normal equity = $100k
        t1 = cand.compute_targets(dummy_market, 100_000.0)
        sum_t1 = sum(t1.values())

        # Depleted equity = $80k (20% drawdown)
        t2 = cand.compute_targets(dummy_market, 80_000.0)
        sum_t2 = sum(t2.values())

        assert sum_t2 < sum_t1


class TestWalkForwardBootstrapAndValidator:
    def test_paired_bootstrap_identical_series(self):
        rets = [0.01, -0.005, 0.02, -0.01, 0.015, -0.02, 0.005, 0.01, -0.005, 0.008]
        mean_diff, (ci_low, ci_high), p_val = compute_paired_bootstrap(rets, rets)
        assert abs(mean_diff) < 1e-9
        assert ci_low <= 0.0 <= ci_high
        assert p_val == 1.0

    def test_paired_bootstrap_strictly_superior_candidate(self):
        rets_base = [0.001 * i for i in range(20)]
        rets_cand = [0.001 * i + 0.010 for i in range(20)]  # +100 bps daily alpha
        mean_diff, (ci_low, ci_high), p_val = compute_paired_bootstrap(rets_base, rets_cand)
        assert mean_diff > 0.009
        assert ci_low > 0.0
        assert p_val < 0.05

    def test_walk_forward_evaluation_on_calm_uptrend(self):
        provider = StaticRegimeProvider(SAMPLE_REGIMES_PATH, "calm_uptrend")
        timeline = provider.get_timeline()

        cand = AdaptiveRiskParityCandidate()
        baseline_fn = agent.decide

        validator = WalkForwardValidator(provider)
        report = validator.evaluate_candidate_against_baseline(cand.decide, baseline_fn, timeline)

        assert report.total_windows == 1
        assert report.decision in {"IMPROVEMENT_SUPPORTED", "INCONCLUSIVE", "BASELINE_PREFERRED", "CANDIDATE_REJECTED"}
        assert len(report.detailed_comparisons) == 1
        assert len(report.rationale) > 10
