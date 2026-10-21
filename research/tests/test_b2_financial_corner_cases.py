"""Work Package D & E: Comprehensive Financial Accounting Corner Cases & Leverage Metric Separation.

Validates:
  1. Dividend entitlement lifecycle when stock is sold between Ex-Date and Payment Date:
     - Holding stock on Ex-Date creates Dividend Receivable entitlement.
     - Position is fully sold before Payment Date.
     - Cash is successfully credited on Payment Date to a zero-position account.
     - Balance sheet identity holds at every stage.
  2. Duplicate Corporate Action Registration Deduplication:
     - Multiple registrations of identical splits or dividends do not multiply payouts.
  3. Missing Payment Date Graceful Fallback:
     - Dividend registered with payment_date=None defaults to Ex-Date instant credit.
  4. Commission & Fee Protection on Rejected Trades:
     - Rejected orders never incur transaction fees or cash deductions.
  5. Equity Conservation Under Zero Market Movement:
     - Unchanged prices across days preserve bit-identical equity.
  6. Separation of Gross-Notional Leverage vs. Beta-Adjusted Exposure:
     - Leveraged ETF holding demonstrates mathematically distinct gross vs. beta leverage ratios.
"""
from __future__ import annotations

import pytest

from research.engine.accounting import (
    FillResult,
    PortfolioState,
    RiskMode,
    START_CASH,
)
from research.engine.corporate_actions import CorporateActionRegistry


class TestFinancialCornerCases:
    """Verifies subtle financial accounting corner cases and strict balance sheet conservation."""

    def test_dividend_paid_after_position_liquidated(self):
        """Holding stock on Ex-Date establishes legal entitlement; selling before Payment Date does NOT forfeit dividend."""
        registry = CorporateActionRegistry(instant_credit_compatibility=False)
        # Register $2.00 dividend on SPY: Ex-Date 2026-06-01, Pay-Date 2026-06-15
        registry.register_dividend(
            ex_date="2026-06-01",
            ticker="SPY",
            amount_per_share=2.00,
            record_date="2026-06-02",
            payment_date="2026-06-15",
        )

        portfolio = PortfolioState(cash=50_000.0, start_cash=100_000.0, positions={"SPY": 100.0}, avg_cost={"SPY": 500.0})

        # Step 1: On Ex-Date (2026-06-01), entitlement of $200 is booked
        cash_ex, rec_ex, _ = registry.process_dividends_for_date("2026-06-01", portfolio.positions)
        portfolio.cash += cash_ex
        portfolio.dividend_receivables = registry.total_outstanding_receivables()
        assert cash_ex == 0.0
        assert portfolio.dividend_receivables == 200.0

        # Step 2: On 2026-06-05 (before Pay-Date), sell all 100 shares of SPY @ $510.0
        res_sell = portfolio.execute_order(
            {"ticker": "SPY", "side": "sell", "quantity": 100},
            open_price=510.0,
            commission_bps=5.0,
        )
        assert res_sell is not None
        assert "SPY" not in portfolio.positions  # Position is now completely closed!
        assert portfolio.dividend_receivables == 200.0  # Entitlement still intact!

        # Step 3: On Payment Date (2026-06-15), cash is credited despite holding zero shares
        cash_pay, rec_pay, logs = registry.process_dividends_for_date("2026-06-15", portfolio.positions)
        portfolio.cash += cash_pay
        portfolio.total_dividends_credited += cash_pay
        portfolio.dividend_receivables = registry.total_outstanding_receivables()

        assert cash_pay == 200.0
        assert portfolio.dividend_receivables == 0.0
        assert len(logs) == 1
        assert logs[0]["action"] == "dividend_receivable_paid"

        # Balance sheet identity verified with zero open positions
        ok, reason = portfolio.check_accounting_invariants({"SPY": 510.0})
        assert ok, reason

    def test_duplicate_corporate_action_registration_deduplication(self):
        """Repeatedly registering identical corporate actions must be safely deduplicated."""
        registry = CorporateActionRegistry()
        # Register identical 2-for-1 split 3 times
        registry.register_split("2026-06-01", "AAPL", 2.0)
        registry.register_split("2026-06-01", "AAPL", 2.0)
        registry.register_split("2026-06-01", "AAPL", 2.0)

        # Register identical dividend twice
        registry.register_dividend("2026-06-01", "AAPL", 1.0)
        registry.register_dividend("2026-06-01", "AAPL", 1.0)

        positions = {"AAPL": 100.0}
        avg_cost = {"AAPL": 200.0}

        # Apply split: should execute exactly once (200 shares @ $100)
        split_logs = registry.apply_splits_for_date("2026-06-01", positions, avg_cost)
        assert positions["AAPL"] == 200.0
        assert avg_cost["AAPL"] == 100.0
        assert len(split_logs) == 1

        # Apply dividend: should pay exactly once (200 * $1.00 = $200)
        cash_payout, div_logs = registry.apply_dividends_for_date("2026-06-01", positions)
        assert cash_payout == 200.0
        assert len(div_logs) == 1

    def test_missing_payment_date_defaults_gracefully(self):
        """Dividend registered without payment_date defaults gracefully to instant credit."""
        registry = CorporateActionRegistry()
        registry.register_dividend(ex_date="2026-07-01", ticker="QQQ", amount_per_share=0.75, payment_date=None)

        positions = {"QQQ": 400.0}
        payout, logs = registry.apply_dividends_for_date("2026-07-01", positions)
        assert payout == 300.0
        assert len(logs) == 1
        assert logs[0]["total_payout"] == 300.0

    def test_fees_incurred_only_on_executed_trades(self):
        """Rejected trades must never assess commissions or reduce cash."""
        portfolio = PortfolioState(cash=10_000.0)

        # 1. Rejected buy (missing price)
        portfolio.execute_order({"ticker": "MSFT", "side": "buy", "quantity": 10}, open_price=None, commission_bps=10.0)
        assert portfolio.cash == 10_000.0
        assert portfolio.total_commissions == 0.0

        # 2. Rejected sell (unheld ticker)
        portfolio.execute_order({"ticker": "GOOGL", "side": "sell", "quantity": 10}, open_price=150.0, commission_bps=10.0)
        assert portfolio.cash == 10_000.0
        assert portfolio.total_commissions == 0.0

        # 3. Executed buy
        res_exec = portfolio.execute_order(
            {"ticker": "MSFT", "side": "buy", "quantity": 10},
            open_price=100.0,
            commission_bps=10.0,
        )
        assert res_exec is not None
        assert portfolio.cash < 10_000.0
        assert portfolio.total_commissions > 0.0
        assert portfolio.total_commissions == res_exec.commission

    def test_equity_conservation_under_zero_movement(self):
        """With zero price movement and no trades, equity must remain bit-identical across sessions."""
        portfolio = PortfolioState(cash=50_000.0, positions={"AAPL": 200.0}, avg_cost={"AAPL": 250.0})
        prices = {"AAPL": 250.0}

        eq1 = portfolio.mark_to_market(prices)
        eq2 = portfolio.mark_to_market(prices)
        eq3 = portfolio.mark_to_market(prices)

        assert eq1 == 100_000.0
        assert eq1 == eq2 == eq3

    def test_separation_of_gross_notional_vs_beta_adjusted_leverage(self):
        """Prove that Gross-Notional Leverage and Beta-Adjusted Exposure are quantitatively distinct."""
        portfolio = PortfolioState(cash=50_000.0, positions={"TQQQ": 1000.0}, avg_cost={"TQQQ": 50.0})
        # 1,000 shares of TQQQ @ $50.00 = $50,000 notional. Cash = $50,000. Total Equity = $100,000.
        # TQQQ beta = 3.0.
        # Genuine Gross-Notional Leverage = $50,000 / $100,000 = 0.50x
        # Beta-Adjusted Exposure = ($50,000 * 3.0) / $100,000 = 1.50x
        close_prices = {"TQQQ": 50.0}
        portfolio.mark_to_market(close_prices)

        assert abs(portfolio.peak_gross_notional - 0.50) < 1e-6, "Gross notional must be 0.50x"
        assert abs(portfolio.peak_beta_adjusted - 1.50) < 1e-6, "Beta adjusted must be 1.50x"
        assert portfolio.peak_gross_notional != portfolio.peak_beta_adjusted
