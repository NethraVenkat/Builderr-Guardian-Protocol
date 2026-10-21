"""Unit Tests for Competition Risk Limits (Leverage, Concentration, Catastrophe)."""
import pytest
from research.engine.accounting import (
    CATASTROPHE_DD,
    CONCENTRATION_CAP,
    LEVERAGE_CAP,
    PortfolioState,
    START_CASH,
    calculate_metrics,
)


class TestRiskLimits:
    def test_gross_beta_leverage_calculation(self):
        portfolio = PortfolioState(cash=20000.0)
        # 100 shares of TQQQ (3x beta) @ $200 = $20,000 position value -> $60,000 beta exposure
        # 100 shares of SPY (1x beta) @ $500 = $50,000 position value -> $50,000 beta exposure
        # Total equity = $20,000 cash + $20,000 + $50,000 = $90,000
        # Gross beta exposure = ($20,000 * 3.0) + ($50,000 * 1.0) = $110,000
        # Gross leverage = $110,000 / $90,000 = 1.222x
        portfolio.positions = {"TQQQ": 100.0, "SPY": 100.0}
        close_prices = {"TQQQ": 200.0, "SPY": 500.0}

        eq = portfolio.mark_to_market(close_prices)
        assert abs(eq - 90000.0) < 1e-9
        expected_gross = 110000.0 / 90000.0
        assert abs(portfolio.peak_gross - expected_gross) < 1e-6
        assert portfolio.peak_gross <= LEVERAGE_CAP

    def test_concentration_streak_tracking(self):
        portfolio = PortfolioState(cash=10000.0)
        # NVDA = 100 shares @ $900 = $90,000 value / $100,000 equity = 90% concentration!
        portfolio.positions = {"NVDA": 100.0}
        close_prices = {"NVDA": 900.0}

        for day in range(6):
            portfolio.mark_to_market(close_prices)

        assert portfolio.peak_conc == 0.90
        assert portfolio.conc_streak["NVDA"] == 6
        assert portfolio.max_conc_streak == 6
        # Streak > 5 days breaches concentration limit
        assert portfolio.max_conc_streak > 5

    def test_catastrophic_drawdown_detection(self):
        # Equity drops from 100,000 to 45,000 = 55% drawdown (> 50%)
        curve = [100000.0, 90000.0, 70000.0, 45000.0]
        metrics = calculate_metrics(curve)
        assert metrics["mdd"] == 0.55
        assert metrics["mdd"] >= CATASTROPHE_DD
