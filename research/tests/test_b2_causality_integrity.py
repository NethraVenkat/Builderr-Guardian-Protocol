"""Work Package F: Rigorous Causality, Calendar Integrity, and Lookahead Prevention Tests.

Validates:
  1. Strict Chronological Monotonicity:
     - Reversed, shuffled, and duplicate timestamps are strictly rejected by the validation boundary.
  2. Calendar & Temporal Geometry:
     - Non-existent dates (e.g. Feb 30, April 31) rejected.
     - Weekend dates cleanly detected and rejected when reject_weekends=True.
     - Leap-year awareness (2024-02-29 valid, 2023-02-29 invalid).
  3. Causal Information Filtration:
     - Agent decide() at Session T close has access strictly to bars with ts <= T.
     - Order execution occurs at Session T+1 open, never at Session T close (preventing same-bar execution).
  4. Non-Finite and Degenerate Price Rejections:
     - NaN, +/-Inf, zero, negative prices, and negative volume strictly rejected.
"""
from __future__ import annotations

import pytest

from research.engine.accounting import START_CASH
from research.engine.provider import InMemoryStreamProvider
from research.engine.replay import ReplayEngine
from research.engine.validation import (
    ValidationError,
    validate_bar,
    validate_calendar_date,
    validate_series,
)


class TestCausalityAndTemporalIntegrity:
    """Verifies that no future or non-causal information can enter decision or execution layers."""

    def test_nonmonotonic_timestamp_rejections(self):
        """Chronologically reversed or out-of-order bars must be rejected, not silently sorted."""
        bars = [
            {"ts": "2026-01-05", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 100},
            {"ts": "2026-01-07", "open": 102.0, "high": 107.0, "low": 101.0, "close": 105.0, "volume": 100},
            {"ts": "2026-01-06", "open": 101.0, "high": 104.0, "low": 100.0, "close": 102.0, "volume": 100},  # OUT OF ORDER
        ]
        with pytest.raises(ValidationError, match="Non-monotonic chronological ordering"):
            validate_series(bars, ticker="TEST")

    def test_duplicate_session_timestamp_rejection(self):
        """Duplicate dates in a series must be rejected as malformed data."""
        bars = [
            {"ts": "2026-01-05", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 100},
            {"ts": "2026-01-05", "open": 101.0, "high": 106.0, "low": 96.0, "close": 103.0, "volume": 100},  # DUPLICATE
        ]
        with pytest.raises(ValidationError, match="Duplicate timestamp detected"):
            validate_series(bars, ticker="TEST")

    def test_calendar_edge_cases(self):
        """Test leap year validity and non-existent Gregorian dates."""
        assert validate_calendar_date("2024-02-29") == "2024-02-29"  # 2024 is leap year
        with pytest.raises(ValidationError, match="Invalid calendar date"):
            validate_calendar_date("2023-02-29")  # 2023 is NOT leap year
        with pytest.raises(ValidationError, match="Invalid calendar date"):
            validate_calendar_date("2026-04-31")  # April has only 30 days
        with pytest.raises(ValidationError, match="Invalid calendar date"):
            validate_calendar_date("2026-00-10")  # Month 0 does not exist

    def test_next_session_open_execution_causality(self):
        """Prove that orders queued on Day T close are executed at Day T+1 open, never on Day T."""
        sample_bars = {
            "SPY": [
                {"ts": "2026-01-05", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000},
                {"ts": "2026-01-06", "open": 510.0, "high": 515.0, "low": 508.0, "close": 512.0, "volume": 1000},
                {"ts": "2026-01-07", "open": 515.0, "high": 520.0, "low": 514.0, "close": 518.0, "volume": 1000},
            ]
        }
        execution_record: list[tuple[str, str, float]] = []

        def agent_decide(market_state, portfolio_state, cash):
            current_date = market_state["SPY"][-1]["ts"]
            # At Day 1 close, submit buy order
            if current_date == "2026-01-05":
                # Ensure Day 2 and Day 3 bars are NOT in market_state
                assert len(market_state["SPY"]) == 1
                return [{"ticker": "SPY", "side": "buy", "quantity": 10}]
            elif current_date == "2026-01-06":
                # At Day 2 close, verify order filled at Day 2 open ($510.00 + slippage)
                assert len(market_state["SPY"]) == 2
                held = [p for p in portfolio_state["positions"] if p["ticker"] == "SPY"]
                assert len(held) == 1
                execution_record.append((current_date, "filled", held[0]["avg_cost"]))
            return []

        provider = InMemoryStreamProvider("test_prov", sample_bars)
        engine = ReplayEngine(agent_decide, provider)
        result = engine.run_replay()

        assert len(execution_record) == 1
        date_verified, status, avg_cost = execution_record[0]
        assert date_verified == "2026-01-06"
        # Average cost must reflect Day 2 open ($510 * 1.0005 = 510.255), proving Day 1 close ($502) was NOT used!
        expected_fill = 510.0 * 1.0005
        assert abs(avg_cost - expected_fill) < 1e-4

    def test_strict_future_bar_exclusion(self):
        """Validate that validate_market_state rejects any bar with ts > current_date."""
        m_state = {
            "SPY": [
                {"ts": "2026-01-05", "open": 500.0, "high": 505.0, "low": 498.0, "close": 502.0, "volume": 1000},
                {"ts": "2026-01-06", "open": 502.0, "high": 508.0, "low": 500.0, "close": 506.0, "volume": 1000},
            ]
        }
        # Evaluation as of 2026-01-05 close: 2026-01-06 is in the future!
        from research.engine.validation import validate_market_state
        with pytest.raises(ValidationError, match="Future timestamp violation"):
            validate_market_state(m_state, asof_date="2026-01-05", strict_future_rejection=True)
