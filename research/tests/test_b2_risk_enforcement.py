"""Work Package B: Risk Control Verification & Active Pre-Trade Enforcement Tests.

Validates:
  1. Active Pre-Trade Risk Enforcement vs. Passive Telemetry-Only Mode:
     - Active Concentration Cap (30% max equity per position): clamps or rejects orders.
     - Passive Telemetry: allows orders, records streak and peak metrics post-close.
     - Active Gross Beta Leverage Cap (1.50x): clamps or rejects orders based on ETF beta.
     - Passive Telemetry: allows leverage expansion, records peak gross leverage post-close.
     - Active Daily Trade Cap (50 trades/day): rejects 51st trade on the same date.
     - Passive Telemetry: executes arbitrary trade counts.
  2. Market Gaps & Concentration Drift:
     - Passive drift caused by price appreciation without new trading.
  3. Catastrophic Drawdown (MDD >= 50%) detection.
"""
from __future__ import annotations

import pytest

from research.engine.accounting import (
    CONCENTRATION_CAP,
    FillResult,
    LEVERAGE_CAP,
    MAX_TRADES_PER_DAY,
    PortfolioState,
    RiskMode,
    START_CASH,
    calculate_metrics,
)


class TestRiskEnforcementVersusTelemetry:
    """Verifies that Active Pre-Trade Enforcement is strictly separated from Passive Telemetry."""

    def test_active_concentration_clamping_and_rejection(self):
        """In ACTIVE_ENFORCEMENT mode, an order exceeding 30% concentration must be clamped.

        If already at or above 30%, further buy orders must be rejected.
        """
        portfolio = PortfolioState(cash=START_CASH)  # $100,000 equity

        # 1. Order requesting $50,000 notional of AAPL (50% of equity)
        # In ACTIVE mode, clamped to 30% of $100k = $30,000
        # Price = $100 -> clamped qty = 30,000 / (100 * 1.0005) = 299.85 shares
        res_active = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 500},  # 500 * $100 = $50,000
            open_price=100.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            current_prices={"AAPL": 100.0},
        )
        assert res_active is not None
        assert res_active.requested_qty == 500.0
        expected_clamped = (CONCENTRATION_CAP * START_CASH) / (100.0 * 1.0005)
        assert abs(res_active.filled_qty - expected_clamped) < 1e-4
        assert res_active.filled_qty < 500.0

        # Mark to market at close px 100.00
        portfolio.mark_to_market({"AAPL": 100.0})
        # Peak concentration must NOT exceed 30%
        assert portfolio.peak_conc <= CONCENTRATION_CAP + 1e-6

        # 2. Subsequent buy order for AAPL while already holding 30%
        res_second = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 50},
            open_price=100.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            current_prices={"AAPL": 100.0},
        )
        assert res_second is None
        assert len(portfolio.rejected_orders) == 1
        assert portfolio.rejected_orders[-1]["reason"] == "EXCEEDS_CONCENTRATION_CAP"

    def test_telemetry_only_concentration_breach_monitoring(self):
        """In TELEMETRY_ONLY mode (preview.py contract), orders are NOT clamped or rejected.

        Breaches are accurately tracked and reported in telemetry.
        """
        portfolio = PortfolioState(cash=START_CASH)

        # In TELEMETRY_ONLY mode, buy $50,000 of AAPL
        res_passive = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 400},
            open_price=100.0,
            risk_mode=RiskMode.TELEMETRY_ONLY,
            current_prices={"AAPL": 100.0},
        )
        assert res_passive is not None
        assert res_passive.filled_qty == 400.0  # Full fill permitted!

        # Mark to market at close px 100.00
        portfolio.mark_to_market({"AAPL": 100.0})
        # Peak concentration correctly records 40% breach
        assert portfolio.peak_conc > 0.35
        assert portfolio.conc_streak["AAPL"] == 1

    def test_active_gross_beta_leverage_gating_on_leveraged_etf(self):
        """TQQQ and SOXL carry beta 3.0. In ACTIVE mode, leverage room must be measured in beta-adjusted space."""
        portfolio = PortfolioState(cash=START_CASH)  # $100,000 equity -> Max beta exposure = $150,000

        # Leg 1: Buy $25,000 notional of TQQQ (25% < 30% concentration cap)
        # Beta exposure used = $25,000 * 3.0 = $75,000. Remaining beta room = $75,000.
        qty_tqqq = 25_000.0 / (50.0 * 1.0010)
        res_tqqq = portfolio.execute_order(
            {"ticker": "TQQQ", "side": "buy", "quantity": qty_tqqq},
            open_price=50.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            current_prices={"TQQQ": 50.0},
        )
        assert res_tqqq is not None
        assert abs(res_tqqq.filled_qty - qty_tqqq) < 1e-4

        # Leg 2: Attempt to buy $30,000 of SOXL (beta 3.0).
        # Concentration cap allows $30,000, BUT remaining beta room is only ~$75,037!
        # At beta 3.0, max SOXL notional allowed by leverage cap is ~$75,037 / 3.0 = ~$25,012!
        # Active enforcement must clamp SOXL to remaining leverage room
        res_soxl = portfolio.execute_order(
            {"ticker": "SOXL", "side": "buy", "quantity": 1000},  # 1000 * $30 = $30,000
            open_price=30.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            current_prices={"TQQQ": 50.0, "SOXL": 30.0},
        )
        assert res_soxl is not None
        assert res_soxl.requested_qty == 1000.0
        # Verify clamped filled quantity is within 1 share of theoretical 832.9 shares (~$25,000)
        assert abs(res_soxl.filled_qty - 832.9166) < 0.1

        # Leg 3: Beta room is now 100% exhausted ($75,000 + $75,000 = $150,000).
        # Any further purchase in any asset is rejected with EXCEEDS_LEVERAGE_CAP!
        res_overflow = portfolio.execute_order(
            {"ticker": "UPRO", "side": "buy", "quantity": 10},
            open_price=60.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            current_prices={"TQQQ": 50.0, "SOXL": 30.0, "UPRO": 60.0},
        )
        assert res_overflow is None
        assert portfolio.rejected_orders[-1]["reason"] == "EXCEEDS_LEVERAGE_CAP"

    def test_active_daily_trade_limit_enforcement(self):
        """Active mode must enforce the 50 trades/day competition rule, rejecting the 51st trade."""
        portfolio = PortfolioState(cash=START_CASH)

        # Execute 50 rapid small trades
        for i in range(50):
            res = portfolio.execute_order(
                {"ticker": "AAPL", "side": "buy", "quantity": 1},
                open_price=100.0,
                risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
            )
            assert res is not None

        assert portfolio.trades_today == 50

        # 51st trade on the same session MUST be rejected
        res_51 = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 1},
            open_price=100.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
        )
        assert res_51 is None
        assert portfolio.rejected_orders[-1]["reason"] == "DAILY_TRADE_LIMIT_EXCEEDED"

        # In contrast, in TELEMETRY_ONLY mode, 51st trade would execute
        res_passive = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 1},
            open_price=100.0,
            risk_mode=RiskMode.TELEMETRY_ONLY,
        )
        assert res_passive is not None
        assert res_passive.filled_qty == 1.0

        # Session roll: resetting daily trade counter permits trading again
        portfolio.reset_daily_trade_counter()
        assert portfolio.trades_today == 0
        res_new_day = portfolio.execute_order(
            {"ticker": "AAPL", "side": "buy", "quantity": 1},
            open_price=100.0,
            risk_mode=RiskMode.ACTIVE_ENFORCEMENT,
        )
        assert res_new_day is not None

    def test_overnight_market_gap_concentration_drift(self):
        """Concentration drift caused by price appreciation without new trades is correctly tracked."""
        portfolio = PortfolioState(cash=75_000.0, positions={"NVDA": 250.0}, avg_cost={"NVDA": 100.0})
        # Day 1: NVDA @ 100. Notional = $25,000, Total Eq = $100,000 (25% concentration)
        portfolio.mark_to_market({"NVDA": 100.0})
        assert portfolio.conc_streak.get("NVDA", 0) == 0

        # Day 2: NVDA gaps up +60% to $160. Notional = $40,000, Cash = $75,000, Total Eq = $115,000
        # Concentration = 40,000 / 115,000 = 34.78% (> 30% limit)
        portfolio.mark_to_market({"NVDA": 160.0})
        assert portfolio.peak_conc > 0.30
        assert portfolio.conc_streak["NVDA"] == 1
        assert portfolio.max_conc_streak == 1

    def test_catastrophic_drawdown_detection(self):
        """Detect drawdown >= 50% cleanly in metrics."""
        curve = [100_000.0, 105_000.0, 80_000.0, 48_000.0]  # Peak = 105k, trough = 48k -> MDD = 54.28%
        metrics = calculate_metrics(curve, trades=10, errors=0)
        assert metrics["mdd"] > 0.50
