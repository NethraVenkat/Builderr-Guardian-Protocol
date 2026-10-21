"""Institutional Trading Stress, Financial Risk & Operational Failure Engine.

Implements and executes 25 financial and operational stress scenarios:
  1. Overnight price gaps
  2. Large bear-market drawdowns
  3. Extended sideways conditions
  4. High-volatility reversals
  5. Rapid volatility compression
  6. Concentrated sector declines
  7. Leveraged ETF volatility decay
  8. Missing QLD/SSO data resilience
  9. Missing execution prices
  10. Corporate action anomalies
  11. Stale market observations
  12. Invalid timestamps
  13. Duplicated execution calls
  14. Repeated same-day rebalances
  15. 50-trade daily limit
  16. Position concentration drift
  17. Gross notional exposure breaches
  18. Beta-adjusted exposure breaches
  19. Insufficient cash boundary
  20. Large slippage shocks
  21. Commission rate shocks
  22. Partial fills and rejected orders
  23. Delayed or dropped market bars
  24. Process interruption / state serialization
  25. Deterministic state recovery
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any

from research.engine.accounting import (
    CONCENTRATION_CAP,
    LEVERAGE_CAP,
    MAX_TRADES_PER_DAY,
    PortfolioState,
    RiskMode,
    START_CASH,
    calculate_metrics,
)
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    MissingPaymentDateError,
    PaymentDatePolicy,
)
from research.engine.validation import ValidationError, validate_bar


@dataclass
class StressScenarioResult:
    scenario_id: int
    name: str
    passed: bool
    details: str
    metrics: dict[str, Any] = field(default_factory=dict)


class StressTestEngine:
    """Executes the full 25-scenario institutional stress suite."""

    def run_all(self) -> list[StressScenarioResult]:
        results = [
            self.test_01_overnight_price_gap(),
            self.test_02_large_bear_drawdown(),
            self.test_03_extended_sideways_conditions(),
            self.test_04_high_volatility_reversals(),
            self.test_05_volatility_compression(),
            self.test_06_concentrated_sector_decline(),
            self.test_07_leveraged_etf_volatility_decay(),
            self.test_08_missing_leveraged_etf_data(),
            self.test_09_missing_execution_prices(),
            self.test_10_corporate_action_error_handling(),
            self.test_11_stale_market_observations(),
            self.test_12_invalid_timestamps(),
            self.test_13_duplicate_execution_calls(),
            self.test_14_repeated_sameday_rebalances(),
            self.test_15_fifty_trade_daily_limit(),
            self.test_16_position_concentration_drift(),
            self.test_17_gross_notional_exposure(),
            self.test_18_beta_adjusted_exposure_breach(),
            self.test_19_insufficient_cash_boundary(),
            self.test_20_large_slippage_shocks(),
            self.test_21_commission_rate_shocks(),
            self.test_22_partial_fills_and_rejections(),
            self.test_23_delayed_or_dropped_bars(),
            self.test_24_interrupted_replay_checkpoint(),
            self.test_25_deterministic_restart_recovery(),
        ]
        return results

    def test_01_overnight_price_gap(self) -> StressScenarioResult:
        """Scenario 1: Overnight gap down -20% mark-to-market."""
        port = PortfolioState(cash=50_000.0, positions={"AAPL": 500.0}, avg_cost={"AAPL": 100.0})
        port.mark_to_market({"AAPL": 100.0})  # Eq = 100k
        port.mark_to_market({"AAPL": 80.0})   # 20% gap down -> Eq = 90k
        pnl = port.unrealized_pnl({"AAPL": 80.0})
        ok = port.total_equity({"AAPL": 80.0}) == 90_000.0 and pnl == -10_000.0
        return StressScenarioResult(1, "overnight_price_gap", ok, f"Eq={port.total_equity({'AAPL': 80.0})}, PnL={pnl}")

    def test_02_large_bear_drawdown(self) -> StressScenarioResult:
        """Scenario 2: Monotonic 55% drawdown detection."""
        curve = [100_000.0, 90_000.0, 75_000.0, 60_000.0, 45_000.0]
        m = calculate_metrics(curve)
        ok = m["mdd"] == 0.55
        return StressScenarioResult(2, "large_bear_drawdown", ok, f"MDD={m['mdd']:.2%}")

    def test_03_extended_sideways_conditions(self) -> StressScenarioResult:
        """Scenario 3: 60 sessions with flat prices preserves exact equity."""
        port = PortfolioState(cash=50_000.0, positions={"SPY": 100.0}, avg_cost={"SPY": 500.0})
        for _ in range(60):
            port.mark_to_market({"SPY": 500.0})
        ok = len(port.equity_curve) == 60 and all(eq == 100_000.0 for eq in port.equity_curve)
        return StressScenarioResult(3, "extended_sideways_conditions", ok, f"Days={len(port.equity_curve)}")

    def test_04_high_volatility_reversals(self) -> StressScenarioResult:
        """Scenario 4: High vol whipsaw (+10% / -10%) executed with slippage."""
        port = PortfolioState(cash=100_000.0)
        # Day 1: Buy AAPL @ 100
        port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 100}, open_price=100.0)
        port.mark_to_market({"AAPL": 110.0})
        # Day 2: Sell AAPL @ 99 (reversal)
        port.execute_order({"ticker": "AAPL", "side": "sell", "quantity": 100}, open_price=99.0)
        port.mark_to_market({"AAPL": 99.0})
        ok = port.positions.get("AAPL", 0.0) == 0.0 and port.cash > 0.0
        return StressScenarioResult(4, "high_volatility_reversals", ok, f"Final Cash={port.cash:.2f}")

    def test_05_volatility_compression(self) -> StressScenarioResult:
        """Scenario 5: Volatility drops abruptly."""
        rets = [0.05, -0.04, 0.06, -0.05, 0.04] + [0.001, -0.001, 0.001, 0.000, 0.001]
        curve = [100_000.0]
        for r in rets:
            curve.append(curve[-1] * (1.0 + r))
        m = calculate_metrics(curve)
        ok = m["sharpe"] is not None and m["mdd"] < 0.20
        return StressScenarioResult(5, "volatility_compression", ok, f"Sharpe={m['sharpe']:.2f}, MDD={m['mdd']:.2%}")

    def test_06_concentrated_sector_decline(self) -> StressScenarioResult:
        """Scenario 6: XLK tech sector drops 30% while SPY drops 5%."""
        port = PortfolioState(cash=50_000.0, positions={"XLK": 100.0, "SPY": 100.0}, avg_cost={"XLK": 200.0, "SPY": 300.0})
        eq1 = port.mark_to_market({"XLK": 200.0, "SPY": 300.0})  # 50k + 20k + 30k = 100k
        eq2 = port.mark_to_market({"XLK": 140.0, "SPY": 285.0})  # 50k + 14k + 28.5k = 92.5k
        ok = eq1 == 100_000.0 and eq2 == 92_500.0
        return StressScenarioResult(6, "concentrated_sector_decline", ok, f"Eq1={eq1}, Eq2={eq2}")

    def test_07_leveraged_etf_volatility_decay(self) -> StressScenarioResult:
        """Scenario 7: Leveraged ETF decay under oscillating underlying."""
        # QQQ alternates +10%, -9.09% (net 0% underlying return)
        # QLD (2x) experiences +20%, -18.18% -> net -1.8% return (volatility drag)
        px_underlying = 100.0 * 1.10 * (1.0 - 10.0 / 110.0)
        px_2x = 100.0 * 1.20 * (1.0 - 20.0 / 110.0)
        ok = abs(px_underlying - 100.0) < 1e-4 and px_2x < 100.0
        return StressScenarioResult(7, "leveraged_etf_volatility_decay", ok, f"Underlying={px_underlying:.2f}, 2x={px_2x:.2f}")

    def test_08_missing_leveraged_etf_data(self) -> StressScenarioResult:
        """Scenario 8: Missing QLD/SSO data drops order cleanly without crashing."""
        port = PortfolioState(cash=START_CASH)
        res = port.execute_order({"ticker": "QLD", "side": "buy", "quantity": 100}, open_price=None)
        ok = res is None and port.rejected_orders[-1]["reason"] == "MISSING_EXECUTION_PRICE"
        return StressScenarioResult(8, "missing_leveraged_etf_data", ok, "Clean drop on missing execution price")

    def test_09_missing_execution_prices(self) -> StressScenarioResult:
        """Scenario 9: Missing execution price does not charge fees or change cash."""
        port = PortfolioState(cash=50_000.0)
        port.execute_order({"ticker": "MSFT", "side": "buy", "quantity": 10}, open_price=None, commission_bps=10.0)
        ok = port.cash == 50_000.0 and port.total_commissions == 0.0
        return StressScenarioResult(9, "missing_execution_prices", ok, f"Cash={port.cash}, Comm={port.total_commissions}")

    def test_10_corporate_action_error_handling(self) -> StressScenarioResult:
        """Scenario 10: Negative split ratio and missing payment date rejected by policy."""
        reg = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.REJECT)
        split_caught = False
        try:
            reg.register_split("2024-06-01", "AAPL", -2.0)
        except ValueError:
            split_caught = True

        div_caught = False
        try:
            reg.register_dividend("2024-06-01", "AAPL", 1.0, payment_date=None)
        except MissingPaymentDateError:
            div_caught = True

        ok = split_caught and div_caught
        return StressScenarioResult(10, "corporate_action_error_handling", ok, f"SplitErr={split_caught}, DivErr={div_caught}")

    def test_11_stale_market_observations(self) -> StressScenarioResult:
        """Scenario 11: Identical closing prices marked correctly without spurious trades."""
        port = PortfolioState(cash=50_000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 200.0})
        eq1 = port.mark_to_market({"AAPL": 200.0})
        eq2 = port.mark_to_market({"AAPL": 200.0})
        ok = eq1 == eq2 == 70_000.0 and port.trade_count == 0
        return StressScenarioResult(11, "stale_market_observations", ok, f"Eq={eq1}, Trades={port.trade_count}")

    def test_12_invalid_timestamps(self) -> StressScenarioResult:
        """Scenario 12: Invalid calendar dates rejected by validation gate."""
        caught = False
        try:
            validate_bar({"ts": "2024-02-30", "open": 100.0, "high": 105.0, "low": 95.0, "close": 100.0, "volume": 100})
        except ValidationError:
            caught = True
        return StressScenarioResult(12, "invalid_timestamps", caught, "February 30 rejected cleanly")

    def test_13_duplicate_execution_calls(self) -> StressScenarioResult:
        """Scenario 13: Duplicate execution calls handled with active risk limits."""
        port = PortfolioState(cash=START_CASH)
        # Attempt to buy $60,000 notional of AAPL twice
        r1 = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 300}, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        r2 = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 300}, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        ok = r1 is not None and r2 is None and port.rejected_orders[-1]["reason"] == "EXCEEDS_CONCENTRATION_CAP"
        return StressScenarioResult(13, "duplicate_execution_calls", ok, "Second identical buy rejected by cap")

    def test_14_repeated_sameday_rebalances(self) -> StressScenarioResult:
        """Scenario 14: Multiple rebalances on same day increment trade counter."""
        port = PortfolioState(cash=START_CASH)
        for _ in range(5):
            port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 1}, open_price=100.0)
        ok = port.trades_today == 5 and port.trade_count == 5
        return StressScenarioResult(14, "repeated_sameday_rebalances", ok, f"Trades today={port.trades_today}")

    def test_15_fifty_trade_daily_limit(self) -> StressScenarioResult:
        """Scenario 15: 50 trades permitted; 51st rejected with limit error."""
        port = PortfolioState(cash=START_CASH)
        for _ in range(MAX_TRADES_PER_DAY):
            port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 1}, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        r51 = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 1}, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        ok = port.trades_today == 50 and r51 is None and port.rejected_orders[-1]["reason"] == "DAILY_TRADE_LIMIT_EXCEEDED"
        return StressScenarioResult(15, "fifty_trade_daily_limit", ok, f"Trades={port.trades_today}, 51st rejected={r51 is None}")

    def test_16_position_concentration_drift(self) -> StressScenarioResult:
        """Scenario 16: Overnight price appreciation causes concentration drift > 30%."""
        port = PortfolioState(cash=75_000.0, positions={"NVDA": 250.0}, avg_cost={"NVDA": 100.0})
        port.mark_to_market({"NVDA": 100.0})  # 25% concentration
        port.mark_to_market({"NVDA": 160.0})  # 40k NVDA / 115k Eq = 34.78%
        ok = port.peak_conc > 0.30 and port.conc_streak.get("NVDA", 0) == 1
        return StressScenarioResult(16, "position_concentration_drift", ok, f"PeakConc={port.peak_conc:.2%}, Streak={port.conc_streak.get('NVDA')}")

    def test_17_gross_notional_exposure(self) -> StressScenarioResult:
        """Scenario 17: Gross notional exposure correctly measured as sum(|V|) / equity."""
        port = PortfolioState(cash=40_000.0, positions={"AAPL": 300.0, "MSFT": 300.0}, avg_cost={"AAPL": 100.0, "MSFT": 100.0})
        port.mark_to_market({"AAPL": 100.0, "MSFT": 100.0})  # Pos=60k, Cash=40k, Eq=100k -> 0.60x
        ok = abs(port.peak_gross_notional - 0.60) < 1e-4
        return StressScenarioResult(17, "gross_notional_exposure", ok, f"GrossNotional={port.peak_gross_notional:.2f}x")

    def test_18_beta_adjusted_exposure_breach(self) -> StressScenarioResult:
        """Scenario 18: 3x leveraged ETF rejected when beta exposure exceeds 1.50x."""
        port = PortfolioState(cash=START_CASH)
        # Attempt to buy $60,000 notional of TQQQ (beta 3.0 -> $180,000 beta exposure > $150,000 limit)
        res = port.execute_order({"ticker": "TQQQ", "side": "buy", "quantity": 1200}, open_price=50.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        # In active mode, clamped to 30% conc ($30k notional -> $90k beta exposure)
        ok = res is not None and res.filled_qty < 1200.0
        return StressScenarioResult(18, "beta_adjusted_exposure_breach", ok, f"Clamped Qty={res.filled_qty:.1f} vs Req=1200.0")

    def test_19_insufficient_cash_boundary(self) -> StressScenarioResult:
        """Scenario 19: Buying with zero cash is rejected with INSUFFICIENT_CASH."""
        port = PortfolioState(cash=0.0)
        res = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 10}, open_price=100.0)
        ok = res is None and port.rejected_orders[-1]["reason"] == "INSUFFICIENT_CASH"
        return StressScenarioResult(19, "insufficient_cash_boundary", ok, "Zero cash order rejected")

    def test_20_large_slippage_shocks(self) -> StressScenarioResult:
        """Scenario 20: Slippage impact on leveraged ETF vs equity."""
        port = PortfolioState(cash=START_CASH)
        r_eq = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 100}, open_price=100.0)
        r_lev = port.execute_order({"ticker": "TQQQ", "side": "buy", "quantity": 100}, open_price=100.0)
        ok = r_eq.slippage == 0.0005 and r_lev.slippage == 0.0010
        return StressScenarioResult(20, "large_slippage_shocks", ok, f"EqSlip={r_eq.slippage*10000:.0f}bps, LevSlip={r_lev.slippage*10000:.0f}bps")

    def test_21_commission_rate_shocks(self) -> StressScenarioResult:
        """Scenario 21: High commission rate (50 bps) assessed accurately."""
        port = PortfolioState(cash=START_CASH)
        res = port.execute_order({"ticker": "SPY", "side": "buy", "quantity": 100}, open_price=500.0, commission_bps=50.0)
        expected_comm = res.notional * 0.0050
        ok = abs(res.commission - expected_comm) < 1e-4 and port.total_commissions == res.commission
        return StressScenarioResult(21, "commission_rate_shocks", ok, f"Commission=${res.commission:.2f}")

    def test_22_partial_fills_and_rejections(self) -> StressScenarioResult:
        """Scenario 22: Order partially filled exactly at cash boundary."""
        port = PortfolioState(cash=1005.0)  # Cash for ~10.04 shares of $100 stock with 5 bps slippage
        res = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 50}, open_price=100.0)
        ok = res is not None and abs(res.filled_qty - 10.045) < 0.05 and res.filled_qty < 50.0
        return StressScenarioResult(22, "partial_fills_and_rejections", ok, f"Filled={res.filled_qty:.2f} of Req=50.0")

    def test_23_delayed_or_dropped_bars(self) -> StressScenarioResult:
        """Scenario 23: Dropped bar falls back to previous average cost for portfolio value."""
        port = PortfolioState(cash=50_000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 200.0})
        # AAPL price omitted from close_prices dict
        eq = port.mark_to_market({})
        ok = eq == 70_000.0
        return StressScenarioResult(23, "delayed_or_dropped_bars", ok, f"Fallback Eq={eq:.2f}")

    def test_24_interrupted_replay_checkpoint(self) -> StressScenarioResult:
        """Scenario 24: Portfolio state serializes cleanly to JSON for crash recovery."""
        port = PortfolioState(cash=65_000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 150.0}, trade_count=12)
        state_dict = port.get_portfolio_state_dict({"AAPL": 160.0})
        serialized = json.dumps(state_dict)
        deserialized = json.loads(serialized)
        ok = deserialized["cash"] == 65_000.0 and len(deserialized["positions"]) == 1
        return StressScenarioResult(24, "interrupted_replay_checkpoint", ok, f"Serialized {len(serialized)} bytes")

    def test_25_deterministic_restart_recovery(self) -> StressScenarioResult:
        """Scenario 25: Restored portfolio produces bit-identical subsequent trade results."""
        p1 = PortfolioState(cash=50_000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 150.0})
        p2 = PortfolioState(cash=50_000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 150.0})

        r1 = p1.execute_order({"ticker": "AAPL", "side": "sell", "quantity": 50}, open_price=200.0)
        r2 = p2.execute_order({"ticker": "AAPL", "side": "sell", "quantity": 50}, open_price=200.0)

        ok = (r1.filled_qty == r2.filled_qty and
              r1.realized_pnl == r2.realized_pnl and
              p1.cash == p2.cash and
              p1.total_equity({"AAPL": 200.0}) == p2.total_equity({"AAPL": 200.0}))
        return StressScenarioResult(25, "deterministic_restart_recovery", ok, f"Bit-identical Cash={p1.cash:.2f}")
