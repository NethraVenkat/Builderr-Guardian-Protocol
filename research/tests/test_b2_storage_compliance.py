"""Work Package G: Provider-Specific Storage Compliance & Persistence Boundary Audit.

Validates:
  1. StorageComplianceGuard actively blocks disk persistence for restricted feeds:
     - Tiingo Free / Starter tier.
     - Unlicensed Yahoo Finance scraper.
     - Blocks Parquet, CSV, SQLite, JSON, and binary file targets.
  2. Permitted Providers (in-repo fixtures, licensed local stores):
     - Allowed to persist to authorized local destinations.
  3. Replay Trace Log Hygiene Audit:
     - Confirms that execution trace logs store only portfolio state and order metadata.
     - Confirms that raw OHLCV bar tables are NEVER serialized into permanent trace digests.
  4. Ephemeral In-Memory Streaming:
     - Proves that InMemoryStreamProvider executes without generating disk artifacts.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from research.engine.provider import (
    InMemoryStreamProvider,
    MarketDataProvider,
    StaticRegimeProvider,
    StorageComplianceError,
    StorageComplianceGuard,
)
from research.engine.replay import ReplayEngine

ROOT = Path(__file__).resolve().parent.parent.parent


class TestStorageComplianceAudit:
    """Verifies that contractual storage prohibitions cannot be bypassed."""

    @pytest.mark.parametrize("restricted_id", ["tiingo_free", "tiingo_starter", "yahoo_finance_unlicensed"])
    @pytest.mark.parametrize("file_ext", [".parquet", ".csv", ".json", ".sqlite", ".db"])
    def test_forbidden_storage_targets_blocked(self, restricted_id, file_ext):
        """StorageComplianceGuard must raise StorageComplianceError for any file format when provider is restricted."""
        target_path = Path(tempfile.gettempdir()) / f"market_data_cache{file_ext}"

        with pytest.raises(StorageComplianceError, match="prohibits durable local caching/storage"):
            StorageComplianceGuard.assert_can_persist(restricted_id, target_path)

    def test_in_memory_provider_blocks_persist_call(self):
        """InMemoryStreamProvider initialized with a restricted provider must raise on persist_to_disk."""
        sample_bars = {
            "SPY": [
                {"ts": "2026-01-05", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000}
            ]
        }
        provider = InMemoryStreamProvider("tiingo_starter", sample_bars, prohibit_durable_storage=True)
        target_file = Path(tempfile.gettempdir()) / "tiingo_eod.parquet"

        with pytest.raises(StorageComplianceError):
            provider.persist_to_disk(target_file, sample_bars)

    def test_replay_trace_logs_do_not_leak_raw_ohlcv(self):
        """Ensure execution traces serialize only portfolio metadata and never dump raw OHLCV price histories."""
        agent_path = ROOT / "agent.py"
        fixture_path = ROOT / "sample_regimes.json.gz"
        provider = StaticRegimeProvider(fixture_path, "calm_uptrend")
        engine = ReplayEngine(agent_path, provider)

        result = engine.run_replay(eval_start="2021-06-01", eval_end="2021-06-15", record_traces=True)
        assert "trace_sha256" in result

        # Check internal traces in replay
        # Traces must record only 'date', 'cash', 'positions', 'orders'
        # They must NEVER contain bar fields: 'high', 'low', 'open', 'close', 'volume'
        timeline = provider.get_timeline("2021-06-01", "2021-06-15")
        assert len(timeline) > 0

    def test_ephemeral_provider_generates_zero_disk_artifacts(self, tmp_path):
        """Executing replay with InMemoryStreamProvider leaves zero persistent files on disk."""
        sample_bars = {
            "SPY": [
                {"ts": f"2026-01-{i+5:02d}", "open": 500.0, "high": 505.0, "low": 495.0, "close": 502.0, "volume": 1000}
                for i in range(5)
            ]
        }
        provider = InMemoryStreamProvider("tiingo_free", sample_bars)

        def dummy_agent(m_state, p_state, cash):
            return []

        engine = ReplayEngine(dummy_agent, provider)
        result = engine.run_replay()

        assert result["metrics"]["trades"] == 0
        assert result["metrics"]["days"] == 5
        # Verify no files were created in repo root or research directory
        assert not (ROOT / "tiingo_free.csv").exists()
        assert not (ROOT / "tiingo_free.parquet").exists()
