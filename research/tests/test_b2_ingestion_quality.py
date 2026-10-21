"""Stage G2 & G3: Ingestion Pipeline, Ticker Aliases, Data Quality Audits & Negative Controls.

Validates:
  1. DataQualityAuditor bar validations (price, geometry, volume, dates).
  2. Inception date constraints (XLC, XLRE).
  3. Series monotonicity and duplicate rejection.
  4. Weekend rejection.
  5. Negative controls: corrupted geometry, negative prices, non-finite values.
  6. Ticker alias resolution (META -> FB pre-2022-06-09).
  7. Deterministic dataset hash computation.
  8. Ingestion pipeline compliance gate (prohibits durable persistence for ephemeral providers).
  9. Network error classification.
"""
from __future__ import annotations

import pytest

from research.engine.ingestion import (
    AuthenticationMissingError,
    IngestionConfig,
    IngestionPipeline,
    MockIngestionClient,
    NetworkErrorCategory,
    RateLimitExceededError,
    classify_http_status,
    compute_dataset_hash,
    resolve_ticker_for_date,
)
from research.engine.provider import StorageComplianceError
from research.engine.quality import DataQualityAuditor


class TestDataQualityAuditor:
    def test_clean_bar_passes(self):
        auditor = DataQualityAuditor()
        bar = {"ts": "2024-06-03", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1_000_000}
        valid, anomalies = auditor.audit_bar("AAPL", bar)
        assert valid is True
        assert len(anomalies) == 0

    def test_negative_or_zero_price_rejected(self):
        auditor = DataQualityAuditor()
        bad_zero = {"ts": "2024-06-03", "open": 0.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("AAPL", bad_zero)
        assert valid is False
        assert any(a.anomaly_type == "NON_FINITE_PRICE" for a in anomalies)

        bad_neg = {"ts": "2024-06-03", "open": 100.0, "high": -10.0, "low": -20.0, "close": 104.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("AAPL", bad_neg)
        assert valid is False

    def test_geometric_integrity_rejection(self):
        auditor = DataQualityAuditor()
        # High lower than Open
        bad_geom1 = {"ts": "2024-06-03", "open": 105.0, "high": 100.0, "low": 90.0, "close": 95.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("AAPL", bad_geom1)
        assert valid is False
        assert any(a.anomaly_type == "GEOMETRIC_INTEGRITY_VIOLATION" for a in anomalies)

        # Low higher than Close
        bad_geom2 = {"ts": "2024-06-03", "open": 100.0, "high": 110.0, "low": 95.0, "close": 90.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("AAPL", bad_geom2)
        assert valid is False

    def test_negative_volume_rejection(self):
        auditor = DataQualityAuditor()
        bad_vol = {"ts": "2024-06-03", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": -50.0}
        valid, anomalies = auditor.audit_bar("AAPL", bad_vol)
        assert valid is False
        assert any(a.anomaly_type == "INVALID_VOLUME" for a in anomalies)

    def test_weekend_date_rejection(self):
        auditor = DataQualityAuditor()
        # 2024-06-01 is a Saturday
        sat_bar = {"ts": "2024-06-01", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("AAPL", sat_bar)
        assert valid is False
        assert any(a.anomaly_type == "WEEKEND_DATA" for a in anomalies)

    def test_pre_inception_date_rejection(self):
        auditor = DataQualityAuditor()
        # XLC inception is 2018-06-18
        pre_bar = {"ts": "2018-05-15", "open": 50.0, "high": 52.0, "low": 49.0, "close": 51.0, "volume": 100}
        valid, anomalies = auditor.audit_bar("XLC", pre_bar)
        assert valid is False
        assert any(a.anomaly_type == "PRE_INCEPTION_BAR" for a in anomalies)

    def test_series_chronology_and_duplicate_rejection(self):
        auditor = DataQualityAuditor()
        bars = [
            {"ts": "2024-06-03", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 100},
            {"ts": "2024-06-03", "open": 101.0, "high": 106.0, "low": 96.0, "close": 103.0, "volume": 100},  # duplicate
            {"ts": "2024-06-02", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 100},  # non-monotonic (backward)
            {"ts": "2024-06-04", "open": 102.0, "high": 107.0, "low": 98.0, "close": 105.0, "volume": 100},  # valid
        ]
        rep = auditor.audit_symbol_series("MSFT", bars)
        assert rep.total_bars == 4
        assert rep.valid_bars == 2
        assert rep.rejected_bars == 2
        assert not rep.is_clean


class TestIngestionPipelineAndCompliance:
    def test_http_status_classification(self):
        assert classify_http_status(429) == NetworkErrorCategory.RATE_LIMIT_EXCEEDED
        assert classify_http_status(401) == NetworkErrorCategory.AUTHENTICATION_FAILED
        assert classify_http_status(403) == NetworkErrorCategory.AUTHENTICATION_FAILED
        assert classify_http_status(502) == NetworkErrorCategory.SERVER_ERROR
        assert classify_http_status(200) == NetworkErrorCategory.UNKNOWN

    def test_ticker_alias_resolution(self):
        # META was FB prior to 2022-06-09
        assert resolve_ticker_for_date("META", "2021-01-15") == "FB"
        assert resolve_ticker_for_date("META", "2022-06-08") == "FB"
        assert resolve_ticker_for_date("META", "2022-06-09") == "META"
        assert resolve_ticker_for_date("META", "2024-01-01") == "META"
        # AAPL has no alias
        assert resolve_ticker_for_date("AAPL", "2020-01-01") == "AAPL"

    def test_dataset_hash_reproducibility(self):
        data1 = {
            "SPY": [{"ts": "2024-06-03", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000}],
            "QQQ": [{"ts": "2024-06-03", "open": 400.0, "high": 405.0, "low": 398.0, "close": 402.0, "volume": 2000}],
        }
        data2 = {
            "QQQ": [{"ts": "2024-06-03", "open": 400.0, "high": 405.0, "low": 398.0, "close": 402.0, "volume": 2000}],
            "SPY": [{"ts": "2024-06-03", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000}],
        }
        h1 = compute_dataset_hash(data1)
        h2 = compute_dataset_hash(data2)
        assert h1 == h2
        assert len(h1) == 64

    def test_ingestion_pipeline_prohibits_durable_storage_on_ephemeral_tier(self):
        config = IngestionConfig(
            provider_id="tiingo_free",
            allow_durable_disk_storage=True,  # Attempting to persist
            output_dir="data_cache",
        )
        client = MockIngestionClient(config=config, fixture_bars={"AAPL": []})
        pipeline = IngestionPipeline(client)

        with pytest.raises(StorageComplianceError) as exc_info:
            pipeline.acquire_universe(["AAPL"], "2024-01-01", "2024-01-05")
        assert "prohibits durable local caching/storage" in str(exc_info.value)

    def test_mock_ingestion_handles_rate_limit_and_auth_failures(self):
        config = IngestionConfig(provider_id="mock_test")
        client = MockIngestionClient(config=config)

        # 1. Rate Limit
        client.simulate_rate_limit = True
        with pytest.raises(RateLimitExceededError):
            client.fetch_symbol_bars("AAPL", "2024-01-01", "2024-01-05")

        # 2. Auth Failure
        client.simulate_rate_limit = False
        client.simulate_auth_failure = True
        with pytest.raises(AuthenticationMissingError):
            client.fetch_symbol_bars("AAPL", "2024-01-01", "2024-01-05")
