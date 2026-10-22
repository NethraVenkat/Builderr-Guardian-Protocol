"""
Unit & Integration Tests for Tiingo Client, Secret Security, Rate Limiter & Holdout Protection.
"""
import pytest
from unittest.mock import MagicMock, patch
from research.engine.tiingo_client import (
    TiingoClient,
    TiingoHistoricalProvider,
    RateLimiter,
    HoldoutProtectionViolation,
    TiingoTokenMissingError,
    TiingoRateLimitExceeded,
    redact_secret,
    get_tiingo_token,
)


def test_secret_redaction_layer():
    """Verify secret token is stripped from text and URLs."""
    secret = "secret_tiingo_token_12345"
    text = f"Failed to connect: https://api.tiingo.com/api?token={secret}&ticker=SPY"
    redacted = redact_secret(text, secret)
    
    assert secret not in redacted
    assert "[REDACTED_TIINGO_TOKEN]" in redacted


def test_holdout_protection_hardcoded_cutoff():
    """Verify attempts to request data in or after 2022-01-01 are blocked before network call."""
    client = TiingoClient(api_token="dummy_token")
    
    with pytest.raises(HoldoutProtectionViolation) as exc_info:
        client.fetch_historical_prices("SPY", "2021-01-01", "2022-01-05")
    assert "sealed holdout" in str(exc_info.value)
    
    with pytest.raises(HoldoutProtectionViolation) as exc_info:
        client.fetch_historical_prices("SPY", "2022-06-01", "2022-12-31")
    assert "sealed holdout" in str(exc_info.value)
    
    with pytest.raises(HoldoutProtectionViolation) as exc_info:
        client.fetch_historical_prices("SPY", "2015-01-01", None)
    assert "must be explicitly specified" in str(exc_info.value)


def test_rate_limiter_enforcement():
    """Verify sliding-window rate limiter stops requests exceeding max per hour."""
    limiter = RateLimiter(max_per_hour=3, max_per_day=10)
    
    limiter.record_request()
    limiter.record_request()
    limiter.record_request()
    
    assert limiter.remaining_hourly == 0
    with pytest.raises(TiingoRateLimitExceeded) as exc_info:
        limiter.record_request()
    assert "Hourly rate limit reached" in str(exc_info.value)


def test_tiingo_client_normalizes_eod_bars():
    """Verify raw Tiingo JSON payload is normalized correctly into schema."""
    sample_response = [
        {
            "date": "2015-01-05T00:00:00.000Z",
            "open": 205.16,
            "high": 206.38,
            "low": 203.99,
            "close": 204.38,
            "volume": 169632646,
            "adjOpen": 178.6923,
            "adjHigh": 179.7549,
            "adjLow": 177.6732,
            "adjClose": 178.0129,
            "adjVolume": 169632646,
            "divCash": 0.0,
            "splitFactor": 1.0,
        },
        {
            "date": "2015-01-06T00:00:00.000Z",
            "open": 204.38,
            "high": 205.41,
            "low": 201.28,
            "close": 202.68,
            "volume": 209151400,
            "adjOpen": 178.0129,
            "adjHigh": 178.9100,
            "adjLow": 175.3116,
            "adjClose": 176.5310,
            "adjVolume": 209151400,
            "divCash": 0.0,
            "splitFactor": 1.0,
        },
    ]
    
    client = TiingoClient(api_token="mock_token")
    with patch.object(client, "_execute_request", return_value=sample_response):
        bars = client.fetch_historical_prices("SPY", "2015-01-01", "2015-01-10")
        
    assert len(bars) == 2
    assert bars[0]["ts"] == "2015-01-05"
    assert bars[0]["ticker"] == "SPY"
    assert bars[0]["open"] == 205.16
    assert bars[0]["close"] == 204.38
    assert bars[0]["adj_close"] == 178.0129
    assert bars[0]["div_cash"] == 0.0
    assert bars[0]["split_factor"] == 1.0


def test_tiingo_historical_provider_streaming():
    """Verify provider streams daily point-in-time slices for agent."""
    bars_spy = [
        {"ts": "2015-01-05", "open": 205.16, "high": 206.38, "low": 203.99, "close": 204.38, "adj_close": 178.01, "volume": 1000, "div_cash": 0.0, "split_factor": 1.0},
        {"ts": "2015-01-06", "open": 204.38, "high": 205.41, "low": 201.28, "close": 202.68, "adj_close": 176.53, "volume": 1200, "div_cash": 0.0, "split_factor": 1.0},
    ]
    preloaded = {"SPY": bars_spy}
    
    provider = TiingoHistoricalProvider(
        symbols=["SPY"],
        start_date="2015-01-05",
        end_date="2015-01-06",
        preloaded_bars=preloaded,
    )
    
    timeline = provider.get_timeline()
    assert timeline == ["2015-01-05", "2015-01-06"]
    
    slices = list(provider.stream_daily_slices())
    assert len(slices) == 2
    
    dt1, state1 = slices[0]
    assert dt1 == "2015-01-05"
    assert len(state1["SPY"]) == 1
    assert state1["SPY"][-1]["close"] == 178.01
    
    dt2, state2 = slices[1]
    assert dt2 == "2015-01-06"
    assert len(state2["SPY"]) == 2
    assert state2["SPY"][-1]["close"] == 176.53


def test_invalid_bar_data_rejections():
    """Verify rejection of NaN, non-positive price, and invalid High/Low bounds."""
    from research.engine.tiingo_client import validate_ohlcv_bar, InvalidBarDataError

    # Non-positive price
    bad_price = {"open": 0.0, "high": 10.0, "low": 5.0, "close": 8.0, "adj_open": 10.0, "adj_high": 10.0, "adj_low": 5.0, "adj_close": 8.0, "volume": 100}
    with pytest.raises(InvalidBarDataError) as exc:
        validate_ohlcv_bar(bad_price)
    assert "Non-positive price" in str(exc.value)

    # NaN price
    nan_price = {"open": float("nan"), "high": 10.0, "low": 5.0, "close": 8.0, "adj_open": 10.0, "adj_high": 10.0, "adj_low": 5.0, "adj_close": 8.0, "volume": 100}
    with pytest.raises(InvalidBarDataError) as exc:
        validate_ohlcv_bar(nan_price)
    assert "Non-finite" in str(exc.value)

    # Low > High
    inverted_bounds = {"open": 12.0, "high": 10.0, "low": 15.0, "close": 11.0, "adj_open": 12.0, "adj_high": 10.0, "adj_low": 15.0, "adj_close": 11.0, "volume": 100}
    with pytest.raises(InvalidBarDataError) as exc:
        validate_ohlcv_bar(inverted_bounds)
    assert "Invalid bounds" in str(exc.value)


def test_auth_header_and_request_structure():
    """Verify Authorization header is 'Token <secret>' and Accept is 'application/json'."""
    client = TiingoClient(api_token="valid_secret_token_abc123")
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"ticker": "SPY", "name": "SPDR S&P 500"}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        meta = client.fetch_metadata("SPY")
        assert meta["ticker"] == "SPY"

        # Verify headers sent
        call_args, call_kwargs = mock_urlopen.call_args
        req = call_args[0]
        assert req.headers["Authorization"] == "Token valid_secret_token_abc123"
        assert req.headers["Accept"] == "application/json"


def test_meta_fb_ticker_aliasing():
    """Verify provider maps META to FB for pre-2022 requests."""
    client = TiingoClient(api_token="mock_token")
    with patch.object(client, "fetch_historical_prices", return_value=[{"ts": "2015-01-05", "ticker": "FB", "open": 78.0, "high": 79.0, "low": 77.0, "close": 78.5, "adj_open": 78.0, "adj_high": 79.0, "adj_low": 77.0, "adj_close": 78.5, "volume": 1000, "div_cash": 0.0, "split_factor": 1.0}]) as mock_fetch:
        provider = TiingoHistoricalProvider(
            symbols=["META"],
            start_date="2015-01-05",
            end_date="2015-01-06",
            client=client,
        )
        # Should have called fetch_historical_prices with 'FB'
        mock_fetch.assert_called_once_with("FB", "2014-09-01", "2015-01-06")
        # In provider, it should be mapped to META
        assert "META" in provider.get_available_symbols()

