"""Baseline Parity Verification: ReplayEngine vs Official preview.py.

Executes ReplayEngine on the 3 public sample regimes and compares output
directly against preview.py results and tests/e0_expected.json fixtures.
"""
import gzip
import json
import math
from pathlib import Path
import pytest

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
import preview

ROOT = Path(__file__).resolve().parents[2]


class TestBaselineParity:
    @pytest.mark.parametrize("regime_name", ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"])
    def test_replay_engine_matches_official_preview(self, regime_name):
        agent_path = ROOT / "agent.py"
        fixture_path = ROOT / "sample_regimes.json.gz"
        raw_regimes = json.loads(gzip.open(fixture_path, "rb").read())
        expected_preview = preview.run_regime(agent_path, regime_name, raw_regimes[regime_name])

        provider = StaticRegimeProvider(fixture_path, regime_name)
        engine = ReplayEngine(agent_path, provider)
        result = engine.run_replay()

        metrics = result["metrics"]
        # Discrete metrics match identically
        assert metrics["trades"] == expected_preview["trades"]
        assert metrics["days"] == expected_preview["days"]
        assert metrics["errors"] == expected_preview["errors"]

        # Continuous financial metrics match to 10 decimal places
        assert metrics["ret"] == pytest.approx(expected_preview["ret"], abs=1e-10)
        assert metrics["mdd"] == pytest.approx(expected_preview["mdd"], abs=1e-10)
        assert metrics["sharpe"] == pytest.approx(expected_preview["sharpe"], abs=1e-10)
        assert metrics["calmar"] == pytest.approx(expected_preview["calmar"], abs=1e-10)

        # Risk telemetry matches identically
        assert result["peak_gross"] == pytest.approx(expected_preview["peak_gross"], abs=1e-10)
        assert result["peak_conc"] == pytest.approx(expected_preview["peak_conc"], abs=1e-10)
        assert result["max_conc_streak"] == expected_preview["max_conc_streak"]
        assert result["compliance"]["all_safety_bars_cleared"] is True
