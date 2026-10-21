"""Unit Tests for Provider Interface and License Storage Compliance Guard."""
import pytest
from pathlib import Path
from research.engine.provider import (
    InMemoryStreamProvider,
    StaticRegimeProvider,
    StorageComplianceError,
    StorageComplianceGuard,
)

ROOT = Path(__file__).resolve().parents[2]


class TestProviderCompliance:
    def test_tiingo_storage_prohibition_guard(self):
        """Tiingo free/starter data must NOT be persisted to durable local storage."""
        with pytest.raises(StorageComplianceError, match="prohibits durable local caching/storage"):
            StorageComplianceGuard.assert_can_persist("tiingo_free", "data_cache/tiingo.parquet")

        with pytest.raises(StorageComplianceError, match="prohibits durable local caching/storage"):
            StorageComplianceGuard.assert_can_persist("tiingo_starter", "data_cache/tiingo.csv")

        with pytest.raises(StorageComplianceError, match="prohibits durable local caching/storage"):
            StorageComplianceGuard.assert_can_persist("yahoo_finance_unlicensed", "data_cache/yahoo.sqlite")

    def test_permitted_local_provider_storage(self):
        """Permitted sources (e.g. user-owned CSVs, paid corporate licenses) pass guard."""
        # Should not raise
        StorageComplianceGuard.assert_can_persist("user_authorized_csv_archive", "data_cache/archive.parquet")
        StorageComplianceGuard.assert_can_persist("in_repo_sample_regime")

    def test_in_memory_stream_provider_ephemeral_usage(self):
        """Proves streaming without durable storage."""
        bars = {
            "SPY": [
                {"ts": "2026-01-01", "open": 500.0, "high": 505.0, "low": 495.0, "close": 502.0, "volume": 1000},
                {"ts": "2026-01-02", "open": 502.0, "high": 508.0, "low": 500.0, "close": 506.0, "volume": 1000},
            ]
        }
        provider = InMemoryStreamProvider("tiingo_free", bars, prohibit_durable_storage=True)
        assert provider.get_available_symbols() == ["SPY"]
        timeline = provider.get_timeline()
        assert timeline == ["2026-01-01", "2026-01-02"]

        # Streaming yields slices
        slices = list(provider.stream_daily_slices())
        assert len(slices) == 2
        d1, s1 = slices[0]
        assert d1 == "2026-01-01"
        assert len(s1["SPY"]) == 1

        d2, s2 = slices[1]
        assert d2 == "2026-01-02"
        assert len(s2["SPY"]) == 2

        # But attempting to persist to disk MUST fail
        with pytest.raises(StorageComplianceError):
            provider.persist_to_disk("data_cache/tiingo_stream.parquet", bars)

    def test_static_regime_provider_loading(self):
        fixture = ROOT / "sample_regimes.json.gz"
        provider = StaticRegimeProvider(fixture, "calm_uptrend")
        symbols = provider.get_available_symbols()
        assert len(symbols) == 21
        assert "SPY" in symbols
        timeline = provider.get_timeline()
        assert len(timeline) == 64
        assert timeline[0] == "2021-06-01"
        assert timeline[-1] == "2021-08-30"
