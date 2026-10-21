"""Unit Tests for Replay Engine Accounting Invariants & Execution."""
import pytest
from research.engine.accounting import (
    FillResult,
    PortfolioState,
    START_CASH,
    calculate_metrics,
    get_beta,
)


class TestReplayAccounting:
    def test_cash_conservation_invariant(self):
        portfolio = PortfolioState(cash=START_CASH)

        # 1. Buy 100 SPY at open 500.0 (slip = 5 bps = 500.25)
        fill1 = portfolio.execute_order({"ticker": "SPY", "side": "buy", "quantity": 100}, 500.0)
        assert fill1 is not None
        assert fill1.fill_price == 500.25
        assert fill1.notional == 50025.0
        assert portfolio.cash == START_CASH - 50025.0  # 49,975.0

        # 2. Sell 50 SPY at open 510.0 (slip = 5 bps = 509.745)
        fill2 = portfolio.execute_order({"ticker": "SPY", "side": "sell", "quantity": 50}, 510.0)
        assert fill2 is not None
        assert fill2.fill_price == 509.745
        assert fill2.notional == 50 * 509.745  # 25,487.25

        expected_cash = START_CASH - fill1.notional + fill2.notional
        assert abs(portfolio.cash - expected_cash) < 1e-9
        assert portfolio.positions["SPY"] == 50.0

    def test_leveraged_etf_slippage(self):
        portfolio = PortfolioState(cash=START_CASH)

        # TQQQ is 3x -> slippage is 10 bps (0.0010)
        assert get_beta("TQQQ") == 3.0
        fill_buy = portfolio.execute_order({"ticker": "TQQQ", "side": "buy", "quantity": 100}, 100.0)
        assert fill_buy.fill_price == 100.10  # 100 * (1 + 0.0010)

        # QLD is 2x -> slippage is 10 bps
        assert get_beta("QLD") == 2.0
        fill_qld = portfolio.execute_order({"ticker": "QLD", "side": "buy", "quantity": 100}, 100.0)
        assert fill_qld.fill_price == 100.10

        # AAPL is 1x -> slippage is 5 bps
        assert get_beta("AAPL") == 1.0
        fill_aapl = portfolio.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 100}, 100.0)
        assert fill_aapl.fill_price == 100.05

    def test_sell_precedes_buy_cash_replenishment(self):
        """Proves that proceeds from sells on day T open are available to fund buys on the same morning."""
        portfolio = PortfolioState(cash=500.0)  # Only $500 available
        portfolio.positions["AAPL"] = 100.0
        portfolio.avg_cost["AAPL"] = 150.0

        # Orders: Sell AAPL (100 shares @ $150 = $15,000 proceeds), Buy SPY ($10,000 cost)
        # Sells first:
        fill_sell = portfolio.execute_order({"ticker": "AAPL", "side": "sell", "quantity": 100}, 150.0)
        assert fill_sell is not None
        assert portfolio.cash > 15400.0

        # Buys second: now has ample cash to buy 20 SPY @ $500
        fill_buy = portfolio.execute_order({"ticker": "SPY", "side": "buy", "quantity": 20}, 500.0)
        assert fill_buy is not None
        assert fill_buy.filled_qty == 20.0
        assert portfolio.cash > 5400.0

    def test_missing_execution_price_drops_cleanly(self):
        portfolio = PortfolioState(cash=START_CASH)
        # Ticker has no open price (None)
        res = portfolio.execute_order({"ticker": "HALTED", "side": "buy", "quantity": 100}, None)
        assert res is None
        assert portfolio.cash == START_CASH
        assert portfolio.trade_count == 0

    def test_short_selling_prevention(self):
        portfolio = PortfolioState(cash=START_CASH)
        # Sell unheld ticker
        res = portfolio.execute_order({"ticker": "MSFT", "side": "sell", "quantity": 50}, 400.0)
        assert res is None
        assert "MSFT" not in portfolio.positions
        assert portfolio.trade_count == 0
