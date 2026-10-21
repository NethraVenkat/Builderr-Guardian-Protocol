"""Unit Tests for Point-in-Time Corporate Actions."""
import pytest
from research.engine.corporate_actions import CorporateActionRegistry


class TestCorporateActions:
    def test_forward_stock_split_accounting_invariant(self):
        registry = CorporateActionRegistry()
        # 2-for-1 forward split on NVDA on 2026-06-10
        registry.register_split("2026-06-10", "NVDA", 2.0)

        positions = {"NVDA": 100.0, "AAPL": 50.0}
        avg_cost = {"NVDA": 120.0, "AAPL": 180.0}

        pre_val = positions["NVDA"] * avg_cost["NVDA"]  # 12,000.0

        logs = registry.apply_splits_for_date("2026-06-10", positions, avg_cost)
        assert len(logs) == 1
        assert positions["NVDA"] == 200.0
        assert avg_cost["NVDA"] == 60.0
        assert positions["AAPL"] == 50.0  # Unaffected

        post_val = positions["NVDA"] * avg_cost["NVDA"]  # 12,000.0
        assert abs(pre_val - post_val) < 1e-9

    def test_reverse_stock_split_accounting_invariant(self):
        registry = CorporateActionRegistry()
        # 1-for-4 reverse split on SOXL on 2026-06-10
        registry.register_split("2026-06-10", "SOXL", 0.25)

        positions = {"SOXL": 400.0}
        avg_cost = {"SOXL": 10.0}

        pre_val = positions["SOXL"] * avg_cost["SOXL"]  # 4,000.0

        logs = registry.apply_splits_for_date("2026-06-10", positions, avg_cost)
        assert positions["SOXL"] == 100.0
        assert avg_cost["SOXL"] == 40.0

        post_val = positions["SOXL"] * avg_cost["SOXL"]  # 4,000.0
        assert abs(pre_val - post_val) < 1e-9

    def test_cash_dividend_distribution(self):
        registry = CorporateActionRegistry()
        # $1.50 per share dividend on SPY on 2026-06-15
        registry.register_dividend("2026-06-15", "SPY", 1.50)

        positions = {"SPY": 250.0}
        payout, logs = registry.apply_dividends_for_date("2026-06-15", positions)

        assert payout == 375.0  # 250 * 1.50
        assert len(logs) == 1
        assert logs[0]["total_payout"] == 375.0

    def test_unheld_ticker_dividend_yields_zero(self):
        registry = CorporateActionRegistry()
        registry.register_dividend("2026-06-15", "XOM", 1.00)
        positions = {"SPY": 100.0}
        payout, logs = registry.apply_dividends_for_date("2026-06-15", positions)
        assert payout == 0.0
        assert len(logs) == 0
