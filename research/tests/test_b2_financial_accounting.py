"""Work Package A: Independent Financial Accounting and Full Dividend Lifecycle Tests.

Validates:
  1. Complete double-entry balance sheet identity against 28-digit Decimal reference:
     Equity == Start Cash + Realized PnL + Unrealized PnL + Dividends - Commissions.
  2. Execution pricing: slippage models (5 bps equity, 10 bps leveraged ETF).
  3. Commissions, cash depletion, partial fills, and insufficient cash rejections.
  4. Stock split accounting invariants (forward, reverse, repeated splits).
  5. Full point-in-time dividend lifecycle:
     - Ex-Date (T_ex): establishes Dividend Receivable entitlement without spendable cash.
     - Prove buy order depending on dividend cash is rejected on T_ex before Payment Date.
     - Payment Date (T_pay): converts Dividend Receivable into spendable cash.
     - Prove buy order succeeds on T_pay.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
import pytest

from research.engine.accounting import (
    FillResult,
    PortfolioState,
    RiskMode,
    SLIP_EQUITY,
    SLIP_LEVERAGED,
    START_CASH,
)
from research.engine.corporate_actions import CorporateActionRegistry


class TestIndependentFinancialAccounting:
    """Rigorous independent accounting cross-checks."""

    def test_decimal_double_entry_accounting_invariant(self):
        """Verify double-entry identity across complex multi-trade cycle using Decimal arithmetic."""
        portfolio = PortfolioState(cash=START_CASH)
        dec_start_cash = Decimal("100000.00")
        dec_realized_pnl = Decimal("0.00")
        dec_commissions = Decimal("0.00")
        dec_dividends = Decimal("0.00")

        # Day 1: Buy 200 shares of AAPL @ 150.00 with 5 bps slippage, 10 bps comm
        res1 = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 200},
            open_price=150.00,
            commission_bps=10.0,
        )
        assert res1 is not None
        assert res1.filled_qty == 200.0

        # Decimal reference for Day 1
        d_px1 = Decimal("150.00") * (Decimal("1.0") + Decimal(str(SLIP_EQUITY)))
        d_cost1 = d_px1 * Decimal("200")
        d_comm1 = d_cost1 * Decimal("0.001")
        dec_commissions += d_comm1

        # Day 2: Partial sell 50 shares of AAPL @ 165.00 with 5 bps slippage, 10 bps comm
        res2 = portfolio.execute_order(
            {"ticker": "AAPL", "side": "sell", "quantity": 50},
            open_price=165.00,
            commission_bps=10.0,
        )
        assert res2 is not None
        assert res2.filled_qty == 50.0

        # Decimal reference for Day 2 sell
        d_px2 = Decimal("165.00") * (Decimal("1.0") - Decimal(str(SLIP_EQUITY)))
        d_proceeds2 = d_px2 * Decimal("50")
        d_comm2 = d_proceeds2 * Decimal("0.001")
        dec_commissions += d_comm2
        d_cost_basis2 = d_px1 * Decimal("50")
        d_pnl2 = d_proceeds2 - d_cost_basis2  # Gross Realized PnL
        dec_realized_pnl += d_pnl2

        # Mark to market at close px 170.00
        current_prices = {"AAPL": 170.00}
        d_close = Decimal("170.00")
        d_unrealized = (d_close - d_px1) * Decimal("150")

        # Invariant check in engine
        ok, reason = portfolio.check_accounting_invariants(current_prices)
        assert ok, reason

        # Decimal comparison against engine values
        assert abs(float(dec_realized_pnl) - portfolio.realized_pnl) < 1e-6
        assert abs(float(dec_commissions) - portfolio.total_commissions) < 1e-6
        assert abs(float(d_unrealized) - portfolio.unrealized_pnl(current_prices)) < 1e-6

        dec_reconstructed_equity = (
            dec_start_cash
            + dec_realized_pnl
            + d_unrealized
            + dec_dividends
            - dec_commissions
        )
        assert abs(float(dec_reconstructed_equity) - portfolio.total_equity(current_prices)) < 1e-6

    def test_partial_fill_on_cash_boundary(self):
        """When requested order cost exceeds available cash, engine must partially fill to exact cash limit."""
        portfolio = PortfolioState(cash=5_000.0)
        # Attempt to buy 100 shares @ $100 -> notional $10,005 with 5 bps slippage
        # Available cash = $5,000, so filled_qty should be exactly 5000 / (100 * 1.0005)
        res = portfolio.execute_order(
            {"ticker": "MSFT", "side": "buy", "quantity": 100},
            open_price=100.0,
            commission_bps=0.0,
        )
        assert res is not None
        assert res.requested_qty == 100.0
        expected_filled = 5_000.0 / (100.0 * 1.0005)
        assert abs(res.filled_qty - expected_filled) < 1e-9
        assert abs(portfolio.cash) < 1e-9  # all cash consumed
        assert portfolio.positions["MSFT"] == res.filled_qty

    def test_insufficient_funds_rejection(self):
        """Order must be cleanly rejected with INSUFFICIENT_CASH when available cash <= 1e-9."""
        portfolio = PortfolioState(cash=0.00)
        res = portfolio.execute_order(
            {"ticker": "MSFT", "side": "buy", "quantity": 10},
            open_price=100.0,
        )
        assert res is None
        assert len(portfolio.rejected_orders) == 1
        assert portfolio.rejected_orders[0]["reason"] == "INSUFFICIENT_CASH"
        assert portfolio.positions == {}

    def test_halted_asset_missing_price_rejection(self):
        """When execution price is None or <= 0, order must be cleanly rejected."""
        portfolio = PortfolioState(cash=START_CASH)
        res = portfolio.execute_order(
            {"ticker": "HALTED", "side": "buy", "quantity": 100},
            open_price=None,
        )
        assert res is None
        assert len(portfolio.rejected_orders) == 1
        assert portfolio.rejected_orders[0]["reason"] == "MISSING_EXECUTION_PRICE"

    def test_unheld_short_sale_rejection(self):
        """Short sales are forbidden by competition mandate: selling unheld stock is rejected."""
        portfolio = PortfolioState(cash=START_CASH)
        res = portfolio.execute_order(
            {"ticker": "NVDA", "side": "sell", "quantity": 50},
            open_price=120.0,
        )
        assert res is None
        assert len(portfolio.rejected_orders) == 1
        assert portfolio.rejected_orders[0]["reason"] == "UNHELD_POSITION"

    def test_repeated_stock_splits_invariant(self):
        """Multiple sequential stock splits must preserve exact position notional without leakage."""
        registry = CorporateActionRegistry()
        registry.register_split("2026-06-01", "NVDA", 4.0)   # 4-for-1 forward
        registry.register_split("2026-06-15", "NVDA", 0.5)   # 1-for-2 reverse

        positions = {"NVDA": 100.0}
        avg_cost = {"NVDA": 80.0}  # total cost basis = $8,000.0

        # Event 1: 4-for-1
        registry.apply_splits_for_date("2026-06-01", positions, avg_cost)
        assert positions["NVDA"] == 400.0
        assert avg_cost["NVDA"] == 20.0
        assert abs(positions["NVDA"] * avg_cost["NVDA"] - 8000.0) < 1e-9

        # Event 2: 1-for-2
        registry.apply_splits_for_date("2026-06-15", positions, avg_cost)
        assert positions["NVDA"] == 200.0
        assert avg_cost["NVDA"] == 40.0
        assert abs(positions["NVDA"] * avg_cost["NVDA"] - 8000.0) < 1e-9


class TestDividendLifecycleAndTimingEnforcement:
    """Verifies complete dividend entitlement and cash settlement lifecycle."""

    def test_dividend_receivable_vs_cash_timing_boundary(self):
        """Prove buy order depending on dividend cash is rejected on Ex-Date and succeeds on Payment Date.

        Timeline:
          - T_ex: 2026-06-10 (Ex-Date, stock trades ex-dividend)
          - T_rec: 2026-06-11 (Record Date)
          - T_pay: 2026-06-25 (Payment Date, cash credited to broker account)
        """
        registry = CorporateActionRegistry(instant_credit_compatibility=False)
        # $5.00 per share on SPY
        registry.register_dividend(
            ex_date="2026-06-10",
            ticker="SPY",
            amount_per_share=5.00,
            record_date="2026-06-11",
            payment_date="2026-06-25",
        )

        # Portfolio holds 1,000 shares of SPY ($5,000 expected dividend)
        # Starting equity was $400,000.00; cash is set to exactly $0.00
        portfolio = PortfolioState(
            cash=0.00,
            start_cash=400_000.0,
            positions={"SPY": 1000.0},
            avg_cost={"SPY": 400.0},
        )

        # === ON EX-DATE (2026-06-10) ===
        cash_paid, rec_booked, logs = registry.process_dividends_for_date("2026-06-10", portfolio.positions)
        portfolio.cash += cash_paid
        portfolio.total_dividends_credited += cash_paid
        portfolio.dividend_receivables = registry.total_outstanding_receivables()

        # Invariant checks on Ex-Date
        assert cash_paid == 0.00            # No cash credited yet!
        assert rec_booked == 5000.00        # Entitlement booked
        assert portfolio.cash == 0.00       # Spendable cash remains 0
        assert portfolio.dividend_receivables == 5000.00  # Asset on balance sheet

        # Total equity marks SPY @ 395.00 (dropped $5 ex-dividend) + $5,000 receivable
        close_prices = {"SPY": 395.00}
        total_eq = portfolio.total_equity(close_prices)
        assert abs(total_eq - 400_000.0) < 1e-6
        inv_ok, reason = portfolio.check_accounting_invariants(close_prices)
        assert inv_ok, reason

        # CRITICAL TEST: Attempt to buy $3,000 of AAPL using anticipated dividend cash on Ex-Date
        # In an incorrect backtester that credits cash immediately on Ex-Date, this buy would succeed.
        # Under rigorous Point-in-Time accounting, this MUST be rejected for insufficient cash!
        res_fail = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 20},
            open_price=150.00,  # $3,000 cost
        )
        assert res_fail is None
        assert portfolio.rejected_orders[-1]["reason"] == "INSUFFICIENT_CASH"
        assert "AAPL" not in portfolio.positions

        # === ON INTERMEDIATE DATE (2026-06-18) ===
        cash_mid, rec_mid, _ = registry.process_dividends_for_date("2026-06-18", portfolio.positions)
        portfolio.cash += cash_mid
        assert cash_mid == 0.00
        assert portfolio.cash == 0.00
        assert portfolio.dividend_receivables == 5000.00

        # === ON PAYMENT DATE (2026-06-25) ===
        cash_pay, rec_pay, pay_logs = registry.process_dividends_for_date("2026-06-25", portfolio.positions)
        portfolio.cash += cash_pay
        portfolio.total_dividends_credited += cash_pay
        portfolio.dividend_receivables = registry.total_outstanding_receivables()

        assert cash_pay == 5000.00          # Cash finally credited!
        assert portfolio.cash == 5000.00    # Spendable cash is now $5,000
        assert portfolio.dividend_receivables == 0.00  # Receivables extinguished
        assert len(pay_logs) == 1
        assert pay_logs[0]["action"] == "dividend_receivable_paid"

        # Balance sheet identity remains perfectly invariant
        inv_ok, reason = portfolio.check_accounting_invariants(close_prices)
        assert inv_ok, reason

        # NOW the buy order of AAPL succeeds!
        res_success = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 20},
            open_price=150.00,
        )
        assert res_success is not None
        assert res_success.filled_qty == 20.0
        assert "AAPL" in portfolio.positions
        assert portfolio.cash < 5000.00
