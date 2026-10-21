"""Comprehensive Unit Tests for Strict Market Data Validation."""
import pytest
from research.engine.validation import (
    ValidationError,
    validate_bar,
    validate_calendar_date,
    validate_market_state,
    validate_series,
)


class TestValidationControls:
    def test_positive_calendar_date(self):
        assert validate_calendar_date("2026-05-18") == "2026-05-18"
        assert validate_calendar_date("2024-02-29") == "2024-02-29"  # Valid leap year
        assert validate_calendar_date("2026-01-01T09:30:00+00:00") == "2026-01-01"

    def test_negative_calendar_date(self):
        with pytest.raises(ValidationError, match="Invalid calendar date"):
            validate_calendar_date("2026-02-30")  # Non-existent date
        with pytest.raises(ValidationError, match="Invalid calendar date"):
            validate_calendar_date("2026-13-01")  # Invalid month
        with pytest.raises(ValidationError, match="too short"):
            validate_calendar_date("2026-1")
        with pytest.raises(ValidationError, match="outside valid epoch"):
            validate_calendar_date("1950-01-01")

    def test_weekend_rejection(self):
        # 2026-05-16 is a Saturday
        with pytest.raises(ValidationError, match="falls on a weekend"):
            validate_calendar_date("2026-05-16", reject_weekends=True)
        # 2026-05-18 is a Monday
        assert validate_calendar_date("2026-05-18", reject_weekends=True) == "2026-05-18"

    def test_positive_bar(self):
        bar = {"ts": "2026-05-18", "open": 500.0, "high": 505.0, "low": 498.0, "close": 503.0, "volume": 1000}
        clean = validate_bar(bar, ticker="SPY")
        assert clean["open"] == 500.0
        assert clean["high"] == 505.0
        assert clean["low"] == 498.0
        assert clean["close"] == 503.0
        assert clean["volume"] == 1000

    def test_negative_prices_and_nonfinite(self):
        base = {"ts": "2026-05-18", "open": 500.0, "high": 505.0, "low": 498.0, "close": 503.0, "volume": 1000}
        
        # Zero price
        b_zero = dict(base, close=0.0)
        with pytest.raises(ValidationError, match="non-positive"):
            validate_bar(b_zero)

        # Negative price
        b_neg = dict(base, open=-500.0)
        with pytest.raises(ValidationError, match="non-positive"):
            validate_bar(b_neg)

        # NaN
        b_nan = dict(base, high=float("nan"))
        with pytest.raises(ValidationError, match="non-finite"):
            validate_bar(b_nan)

        # Inf
        b_inf = dict(base, low=float("-inf"))
        with pytest.raises(ValidationError, match="non-finite"):
            validate_bar(b_inf)

    def test_geometric_boundary_integrity(self):
        base = {"ts": "2026-05-18", "open": 500.0, "high": 505.0, "low": 498.0, "close": 503.0, "volume": 1000}

        # low > high
        with pytest.raises(ValidationError, match="low .* > high"):
            validate_bar(dict(base, low=510.0, high=505.0))

        # open < low
        with pytest.raises(ValidationError, match="Open .* outside"):
            validate_bar(dict(base, open=490.0, low=498.0))

        # open > high
        with pytest.raises(ValidationError, match="Open .* outside"):
            validate_bar(dict(base, open=510.0, high=505.0))

        # close < low
        with pytest.raises(ValidationError, match="Close .* outside"):
            validate_bar(dict(base, close=495.0, low=498.0))

        # close > high
        with pytest.raises(ValidationError, match="Close .* outside"):
            validate_bar(dict(base, close=512.0, high=505.0))

        # negative volume
        with pytest.raises(ValidationError, match="Volume .* negative"):
            validate_bar(dict(base, volume=-100))

    def test_series_chronology_and_duplicate_rejection(self):
        # 1. Monotonic series PASS
        bars = [
            {"ts": f"2026-01-{i+1:02d}", "open": 100.0, "high": 105.0, "low": 95.0, "close": 100.0, "volume": 100}
            for i in range(10)
        ]
        clean_series = validate_series(bars, ticker="AAPL")
        assert len(clean_series) == 10

        # 2. Duplicate timestamp rejection
        bars_dup = list(bars)
        bars_dup[5] = dict(bars[4])  # duplicate date
        with pytest.raises(ValidationError, match="Duplicate timestamp detected"):
            validate_series(bars_dup, ticker="AAPL")

        # 3. Non-monotonic chronological ordering rejection
        bars_rev = list(reversed(bars))
        with pytest.raises(ValidationError, match="Non-monotonic chronological ordering"):
            validate_series(bars_rev, ticker="AAPL")

    def test_future_timestamp_strict_rejection_at_boundary(self):
        """Proves future-dated data is rejected by the research boundary rather than ignored due to short history."""
        # Create 60 valid historical bars across Jan-Feb-Mar 2026
        bars = []
        for month in (1, 2, 3):
            for day in range(1, 21):
                bars.append({
                    "ts": f"2026-{month:02d}-{day:02d}",
                    "open": 100.0,
                    "high": 105.0,
                    "low": 95.0,
                    "close": 100.0,
                    "volume": 100,
                })
        assert len(bars) == 60
        # Append future bar within epoch but after asof cutoff
        bars.append({"ts": "2026-12-31", "open": 100.0, "high": 105.0, "low": 95.0, "close": 100.0, "volume": 100})

        # When asof_date is 2026-03-20, strict_future_rejection MUST raise ValidationError
        with pytest.raises(ValidationError, match="Future timestamp violation: bar date 2026-12-31 > asof decision cutoff 2026-03-20"):
            validate_series(bars, asof_date="2026-03-20", strict_future_rejection=True)

        # When strict_future_rejection is False, future bar must be purged
        purged = validate_series(bars, asof_date="2026-03-20", strict_future_rejection=False)
        assert len(purged) == 60
        assert all(b["ts"] <= "2026-03-20" for b in purged)
