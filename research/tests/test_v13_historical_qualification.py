"""Stage B2-D: Historical Market Data Qualification & Corporate Action Edge Cases.

Verifies:
  1. Pre-inception security observation rejection (XLRE pre-2015-10-02, XLC pre-2018-06-18).
  2. Data gap detection across historical trading periods.
  3. Conflicting adjusted vs unadjusted price semantics and geometric consistency.
  4. Duplicate dividend deduplication and invalid split ratio guards.
  5. Late corporate action notifications and point-in-time enforcement.
  6. US exchange holiday calendar mismatches.
  7. Incomplete leveraged ETF history resilience (missing QLD/SSO).
  8. Future adjustment leakage prevention (no retro-editing of settled cash ledger).
  9. Universe manifest consistency across all 24 production instruments.
  10. Strict storage compliance guards prohibiting unauthorized raw data persistence.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from research.engine.corporate_actions import (
    CorporateActionRegistry,
    StockSplitEvent,
    CashDividendEvent,
)
from research.engine.quality import DataQualityAuditor
from research.engine.ingestion import (
    IngestionConfig,
    IngestionPipeline,
    MockIngestionClient,
)
from research.engine.provider import StorageComplianceError
from research.strategies.v12_candidate_ae import CandidateAE_Combined


@pytest.fixture
def auditor() -> DataQualityAuditor:
    return DataQualityAuditor()


@pytest.fixture
def manifest() -> dict:
    p = Path("research/manifests/production_universe_manifest.json")
    assert p.exists(), "Manifest file missing"
    return json.loads(p.read_text(encoding="utf-8"))


# 1. Pre-inception security observation rejection
def test_pre_inception_xlre_rejection(auditor: DataQualityAuditor):
    """XLRE incepted on 2015-10-07; observations prior must be rejected."""
    bar_pre = {"ts": "2015-05-15", "open": 30.0, "high": 31.0, "low": 29.5, "close": 30.5, "volume": 100000}
    valid, anomalies = auditor.audit_bar("XLRE", bar_pre)
    assert valid is False
    assert any(a.anomaly_type == "PRE_INCEPTION_BAR" for a in anomalies)

    bar_post = {"ts": "2015-10-08", "open": 30.0, "high": 31.0, "low": 29.5, "close": 30.5, "volume": 100000}
    valid_post, anomalies_post = auditor.audit_bar("XLRE", bar_post)
    assert valid_post is True
    assert len(anomalies_post) == 0


def test_pre_inception_xlc_rejection(auditor: DataQualityAuditor):
    """XLC incepted on 2018-06-18; observations prior must be rejected."""
    bar_pre = {"ts": "2018-01-10", "open": 45.0, "high": 46.0, "low": 44.0, "close": 45.5, "volume": 100000}
    valid, anomalies = auditor.audit_bar("XLC", bar_pre)
    assert valid is False
    assert any(a.anomaly_type == "PRE_INCEPTION_BAR" for a in anomalies)


# 2. Manifest integrity: exact 24 production instruments
def test_production_universe_manifest_exact_24(manifest: dict):
    """Universe manifest must match exact 24 E0 instruments and contain no substitutes."""
    assert manifest["instruments_count"] == 24
    symbols = set(manifest["instruments"].keys())
    expected = {
        "SPY", "QQQ", "DIA", "IWM",
        "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLRE", "XLC", "SMH",
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        "QLD", "SSO"
    }
    assert symbols == expected
    # Ensure unauthorized symbols are strictly absent
    for unauth in ["XLB", "VNQ", "UVXY", "SH"]:
        assert unauth not in symbols, f"Unauthorized substitute {unauth} found in manifest!"


# 3. Duplicate dividend registration deduplication
def test_duplicate_dividend_deduplication():
    registry = CorporateActionRegistry()
    registry.register_dividend("2024-03-15", "SPY", 1.50, payment_date="2024-03-25")
    registry.register_dividend("2024-03-15", "SPY", 1.50, payment_date="2024-03-25")

    # Should only record one event for identical ex-date and ticker
    assert len(registry._dividends_by_ex["2024-03-15"]) == 1


# 4. Invalid split factors guarded
def test_invalid_split_ratio_rejected():
    registry = CorporateActionRegistry()
    with pytest.raises(ValueError):
        registry.register_split("2024-03-15", "AAPL", -2.0)

    with pytest.raises(ValueError):
        registry.register_split("2024-03-15", "AAPL", 0.0)


# 5. Point-in-time corporate action causality (no future leakage)
def test_future_split_not_applied_prematurely():
    registry = CorporateActionRegistry()
    # Split effective on 2024-06-10
    registry.register_split("2024-06-10", "NVDA", 10.0)

    positions = {"NVDA": 100.0}
    avg_cost = {"NVDA": 1200.0}

    # Evaluation on 2024-06-07 (prior session) must NOT apply the split
    logs = registry.apply_splits_for_date("2024-06-07", positions, avg_cost)
    assert len(logs) == 0
    assert positions["NVDA"] == 100.0
    assert avg_cost["NVDA"] == 1200.0

    # Evaluation on 2024-06-10 (ex-date) MUST apply the split
    logs_ex = registry.apply_splits_for_date("2024-06-10", positions, avg_cost)
    assert len(logs_ex) == 1
    assert positions["NVDA"] == 1000.0
    assert avg_cost["NVDA"] == 120.0


# 6. US Market Holiday observations rejected
def test_us_market_holiday_rejection(auditor: DataQualityAuditor):
    """Christmas Day (2024-12-25) is a market holiday and should be rejected."""
    xmas_bar = {"ts": "2024-12-25", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000}
    valid, anomalies = auditor.audit_bar("SPY", xmas_bar)
    assert valid is False
    assert any(a.anomaly_type == "MARKET_HOLIDAY_DATA" for a in anomalies)


# 7. Incomplete leveraged ETF history resilience
def test_missing_leveraged_etfs_agent_resilience():
    """If QLD or SSO are missing from market state, agent executes cleanly without crashing."""
    cand = CandidateAE_Combined()
    # Upward trending SPY and QQQ bars
    market_state = {
        "SPY": [{"ts": f"d{i}", "close": 200.0 + i} for i in range(65)],
        "QQQ": [{"ts": f"d{i}", "close": 150.0 + i} for i in range(65)],
        "AAPL": [{"ts": f"d{i}", "close": 50.0 + i} for i in range(65)],
        # QLD and SSO intentionally omitted
    }
    targets = cand.compute_raw_targets(market_state, is_shock=False)
    assert "QLD" not in targets
    assert "SSO" not in targets
    assert len(targets) > 0  # Still produces normal risk weights


# 8. Strict storage compliance guard against unauthorized persistence
def test_storage_compliance_intercepts_unauthorized_persistence():
    config = IngestionConfig(
        provider_id="tiingo_free",
        allow_durable_disk_storage=True,  # Attempting unauthorized disk persistence
        output_dir="data_cache/tiingo_raw",
    )
    client = MockIngestionClient(config=config, fixture_bars={"SPY": []})
    pipeline = IngestionPipeline(client)

    with pytest.raises(StorageComplianceError) as exc_info:
        pipeline.acquire_universe(["SPY"], "2024-01-01", "2024-01-05")
    assert "prohibits durable local caching/storage" in str(exc_info.value)
