"""
Guardian Alpha V18 Authentic Tier 1 Qualification, Negative Controls, and Invariant Tests.
"""
from __future__ import annotations

import math
import pytest
from unittest.mock import MagicMock, patch

from research.engine.tiingo_client import (
    TiingoClient,
    TiingoHistoricalProvider,
    RateLimiter,
    RequestLedger,
    HoldoutProtectionViolation,
    TiingoTokenMissingError,
    TiingoRateLimitExceeded,
    InvalidBarDataError,
    validate_ohlcv_bar,
    redact_secret,
)


def test_holdout_firewall_blocks_boundary_crossings():
    """Verify holdout firewall blocks any 2022-2024 date prior to socket creation."""
    client = TiingoClient(api_token="dummy_secret")

    # Start date in holdout
    with pytest.raises(HoldoutProtectionViolation):
        client.fetch_historical_prices("SPY", "2022-01-01", "2022-06-01")

    # End date in holdout
    with pytest.raises(HoldoutProtectionViolation):
        client.fetch_historical_prices("SPY", "2021-12-01", "2022-01-02")

    # Unbounded end date
    with pytest.raises(HoldoutProtectionViolation):
        client.fetch_historical_prices("SPY", "2015-01-01", None)


def test_negative_controls_bar_validation():
    """Adversarial negative controls: verify bad bar geometries are strictly rejected."""
    base = {
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "adj_open": 90.0,
        "adj_high": 95.0,
        "adj_low": 85.0,
        "adj_close": 92.0,
        "volume": 10000.0,
    }

    # Zero price
    bad1 = dict(base, open=0.0)
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad1)

    # Negative price
    bad2 = dict(base, close=-5.0)
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad2)

    # Inverted High/Low
    bad3 = dict(base, high=90.0, low=95.0)
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad3)

    # NaN and Inf
    bad4 = dict(base, close=float("nan"))
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad4)

    bad5 = dict(base, adj_close=float("inf"))
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad5)

    # Negative volume
    bad6 = dict(base, volume=-100.0)
    with pytest.raises(InvalidBarDataError):
        validate_ohlcv_bar(bad6)


def test_request_ledger_recording_and_redaction(tmp_path):
    """Verify ledger records query details without leaking tokens."""
    ledger_file = tmp_path / "test_ledger.jsonl"
    ledger = RequestLedger(ledger_path=ledger_file)

    secret = "secret_tiingo_api_token_xyz999"
    client = TiingoClient(api_token=secret, ledger=ledger)

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'[{"date": "2015-01-05T00:00:00.000Z", "open": 204.17, "high": 204.37, "low": 201.35, "close": 201.72, "volume": 1000, "adjOpen": 168.0, "adjHigh": 168.0, "adjLow": 165.0, "adjClose": 166.0, "divCash": 0.0, "splitFactor": 1.0}]'

    with patch("urllib.request.urlopen") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_resp
        client.fetch_historical_prices("SPY", "2015-01-05", "2015-01-05")

    entries = ledger.get_all_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["symbol"] == "SPY"
    assert e["endpoint_type"] == "prices"
    assert e["http_status"] == 200
    assert e["record_count"] == 1
    assert e["result_classification"] == "SUCCESS"

    # Verify secret is never written to ledger
    ledger_text = ledger_file.read_text(encoding="utf-8")
    assert secret not in ledger_text


def test_point_in_time_causality_streaming():
    """Verify that daily slices stream strictly point-in-time (zero lookahead)."""
    bars_spy = [
        {"ts": f"2015-01-0{i}", "open": 200.0 + i, "high": 202.0 + i, "low": 198.0 + i, "close": 201.0 + i, "adj_close": 170.0 + i, "volume": 1000, "div_cash": 0.0, "split_factor": 1.0}
        for i in range(1, 6)
    ]
    provider = TiingoHistoricalProvider(
        symbols=["SPY"],
        start_date="2015-01-01",
        end_date="2015-01-05",
        preloaded_bars={"SPY": bars_spy},
    )

    slices = list(provider.stream_daily_slices())
    assert len(slices) == 5

    for idx, (dt, state) in enumerate(slices):
        cur_spy_bars = state["SPY"]
        # History length must exactly equal idx + 1
        assert len(cur_spy_bars) == idx + 1
        # Latest bar date must equal cur_dt
        assert cur_spy_bars[-1]["ts"] == dt
        # No subsequent dates may appear in state
        for b in cur_spy_bars:
            assert b["ts"] <= dt
