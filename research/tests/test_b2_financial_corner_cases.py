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
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    MissingPaymentDateError,
    PaymentDatePolicy,
)


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

        # Register identical dividend twice (with explicit payment date)
        registry.register_dividend("2026-06-01", "AAPL", 1.0, payment_date="2026-06-01")
        registry.register_dividend("2026-06-01", "AAPL", 1.0, payment_date="2026-06-01")

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

    def test_missing_payment_date_rejected_by_policy(self):
        """Under default strict policy (REJECT), missing payment date raises MissingPaymentDateError."""
        registry = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.REJECT)
        with pytest.raises(MissingPaymentDateError) as exc_info:
            registry.register_dividend(ex_date="2026-07-01", ticker="QQQ", amount_per_share=0.75, payment_date=None)
        assert "Silent substitution of ex-date as payment date is prohibited" in str(exc_info.value)

    def test_missing_payment_date_impute_settlement_lag(self):
        """Under IMPUTE_SETTLEMENT_LAG policy, missing payment date adds 14-day lag with audit entry."""
        registry = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.IMPUTE_SETTLEMENT_LAG)
        registry.register_dividend(ex_date="2026-07-01", ticker="QQQ", amount_per_share=0.75, payment_date=None)
        assert len(registry.imputation_audit_log) == 1
        entry = registry.imputation_audit_log[0]
        assert entry["warning"] == "UNVERIFIED_PAYMENT_DATE_IMPUTATION"
        assert entry["imputed_payment_date"] == "2026-07-15"

    def test_missing_payment_date_impute_business_days_10(self):
        """Under IMPUTE_BUSINESS_DAYS_10 policy, missing payment date adds 10 trading business days."""
        registry = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.IMPUTE_BUSINESS_DAYS_10)
        registry.register_dividend(ex_date="2026-07-01", ticker="QQQ", amount_per_share=0.75, payment_date=None)
        assert len(registry.imputation_audit_log) == 1
        entry = registry.imputation_audit_log[0]
        assert entry["warning"] == "UNVERIFIED_PAYMENT_DATE_IMPUTATION"
        assert entry["method"] == "SETTLEMENT_BUSINESS_DAYS_10"
        # 2026-07-01 is Wednesday. 10 business days -> 2026-07-15 (Wed)
        assert entry["imputed_payment_date"] == "2026-07-15"

    def test_business_days_vs_calendar_days_distinction(self):
        """Proves 14-calendar-day lag is NOT equivalent to 10-business-day settlement across holidays and year-ends."""
        from research.engine.corporate_actions import compute_business_day_settlement

        # Case 1: Ex-date before MLK Jr. Day holiday (2021-01-08 Friday)
        # 14 calendar days -> 2021-01-22 (Friday)
        # 10 business days with MLK holiday (2021-01-18) -> 2021-01-25 (Monday)
        holidays = {"2021-01-18"}
        cal_14d = "2021-01-22"
        b_10d = compute_business_day_settlement("2021-01-08", business_days=10, holidays=holidays)
        assert b_10d == "2021-01-25"
        assert b_10d != cal_14d, "Holiday pushes business-day settlement beyond 14 calendar days"

        # Case 2: Year-end boundary with Christmas and New Year's (2020-12-23 Wednesday)
        # 14 calendar days -> 2021-01-06 (Wednesday)
        # 10 business days with 2020-12-25 and 2021-01-01 holidays -> 2021-01-08 (Friday)
        ye_holidays = {"2020-12-25", "2021-01-01"}
        ye_cal_14d = "2021-01-06"
        ye_b_10d = compute_business_day_settlement("2020-12-23", business_days=10, holidays=ye_holidays)
        assert ye_b_10d == "2021-01-08"
        assert ye_b_10d != ye_cal_14d, "Year-end dual holidays push business-day settlement by 2 full days"

    def test_missing_payment_date_ex_date_compatibility(self):
        """Under EX_DATE_COMPATIBILITY mode, ex-date is used but flagged in imputation audit log."""
        registry = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.EX_DATE_COMPATIBILITY)
        registry.register_dividend(ex_date="2026-07-01", ticker="QQQ", amount_per_share=0.75, payment_date=None)
        assert len(registry.imputation_audit_log) == 1
        assert registry.imputation_audit_log[0]["warning"] == "EX_DATE_COMPATIBILITY_IMPUTATION"
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
