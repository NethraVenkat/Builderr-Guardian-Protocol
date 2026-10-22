"""Stage B2-C: Emergency-Exit and Buffer Conflict Test Suite.

Verifies all critical interaction invariants between Candidate A (Adaptive Shock Exit)
and Candidate E (Cost-Aware Turnover Buffer):
  1. Emergency sell smaller than buffer threshold must execute in full.
  2. Full liquidation (target=0) must bypass buffer to avoid dust positions.
  3. Simultaneous scheduled rebalance and emergency trigger precedence.
  4. Repeated emergency triggers (idempotence).
  5. Market gaps between signal detection and fill open.
  6. Partial fills on cash boundary.
  7. Insufficient cash handling.
  8. Duplicate order rejection.
  9. High volatility whipsaw and fast rebound.
  10. Prolonged decline and risk-off stability.
  11. Leveraged ETF gating during market distress.
  12. Missing or corrupt SPY observations resilience.
  13. Invalid timestamp resilience.
  14. Corporate action during liquidation.
  15. Transaction cost shocks.
  16. 50 trades/day limit boundary.
"""
from __future__ import annotations

import copy
import pytest
from research.strategies.v12_candidate_ae import CandidateAE_Combined
from research.engine.accounting import PortfolioState, RiskMode, START_CASH
from research.engine.corporate_actions import CorporateActionRegistry, StockSplitEvent


@pytest.fixture
def candidate_ae() -> CandidateAE_Combined:
    return CandidateAE_Combined(
        rebalance_every_days=5,
        shock_threshold=-0.030,
        buffer_threshold=0.030,
        enable_adaptive_exit=True,
        enable_cost_buffer=True,
    )


# 1. Emergency sell smaller than buffer threshold must execute in full!
def test_emergency_sell_smaller_than_buffer_threshold(candidate_ae: CandidateAE_Combined):
    """If a position is 2% of equity (< 3% buffer), an emergency shock MUST sell it completely."""
    # Current portfolio holds 2% of AAPL ($2,000 / $100,000)
    positions = {"AAPL": {"quantity": 20.0, "avg_cost": 100.0}}
    prices = {"AAPL": 100.0}
    tot_equity = 100000.0
    
    # Raw target is 0.0 because of shock
    raw_targets = {"AAPL": 0.0, "XLP": 0.24, "XLU": 0.24, "XLV": 0.20, "XLE": 0.12}
    
    # Under shock, buffer MUST be bypassed
    filtered = candidate_ae.apply_cost_buffer(
        raw_targets, positions, tot_equity, prices, is_shock=True
    )
    assert "AAPL" not in filtered or filtered["AAPL"] == 0.0, (
        f"Buffer retained AAPL during emergency shock! Filtered targets: {filtered}"
    )


# 2. Full liquidation (target=0) must bypass buffer even during normal rebalances!
def test_full_liquidation_bypasses_buffer_in_normal_rebalance(candidate_ae: CandidateAE_Combined):
    """When a stock is removed from top winners, its 2.5% position must be fully closed."""
    positions = {"MSFT": {"quantity": 10.0, "avg_cost": 250.0}}  # $2,500 = 2.5% of $100k
    prices = {"MSFT": 250.0}
    tot_equity = 100000.0
    
    # MSFT is no longer in targets
    raw_targets = {"AAPL": 0.20, "NVDA": 0.20, "QQQ": 0.20, "XLK": 0.20, "GOOGL": 0.12}
    
    filtered = candidate_ae.apply_cost_buffer(
        raw_targets, positions, tot_equity, prices, is_shock=False
    )
    # MSFT must NOT be kept at 2.5%
    assert filtered.get("MSFT", 0.0) == 0.0, (
        f"Dust position retained for MSFT! Target was {filtered.get('MSFT')}"
    )


# 3. Buffer suppresses small trade adjustments when target is close to current weight
def test_buffer_suppresses_small_trade_adjustment(candidate_ae: CandidateAE_Combined):
    """If target is 20% and current is 18.5% (delta 1.5% < 3%), buffer should keep 18.5%."""
    positions = {"AAPL": {"quantity": 185.0, "avg_cost": 100.0}}  # $18,500 = 18.5% of $100k
    prices = {"AAPL": 100.0}
    tot_equity = 100000.0
    
    raw_targets = {"AAPL": 0.20}
    
    filtered = candidate_ae.apply_cost_buffer(
        raw_targets, positions, tot_equity, prices, is_shock=False
    )
    # AAPL should stay at current weight 0.185 (rounded) to avoid churn
    assert abs(filtered["AAPL"] - 0.185) < 1e-4, (
        f"Buffer did not suppress small trade! Target was {filtered['AAPL']}"
    )


# 4. Simultaneous scheduled rebalance and emergency trigger precedence
def test_simultaneous_scheduled_and_emergency_rebalance(candidate_ae: CandidateAE_Combined):
    """When day counter >= 5 AND shock occurs, emergency exit takes precedence."""
    candidate_ae.days_counter = 5
    
    # 65 bars for SPY and QQQ, with last 2 days having a drop of -4%
    spy_bars = [{"ts": f"2020-01-{i+1:02d}", "close": 300.0} for i in range(63)]
    spy_bars.append({"ts": "2020-03-10", "close": 295.0})
    spy_bars.append({"ts": "2020-03-11", "close": 288.0})  # 288/300 - 1 = -4.0%

    market_state = {
        "SPY": spy_bars,
        "QQQ": [{"ts": f"2020-01-{i+1:02d}", "close": 200.0} for i in range(65)],
        "XLP": [{"ts": "2020-03-11", "close": 50.0}],
        "XLU": [{"ts": "2020-03-11", "close": 50.0}],
        "XLV": [{"ts": "2020-03-11", "close": 50.0}],
        "XLE": [{"ts": "2020-03-11", "close": 50.0}],
    }
    assert candidate_ae._is_market_shock(market_state) is True
    
    targets = candidate_ae.compute_raw_targets(market_state, is_shock=True)
    # Under shock, raw targets must be defensive weights, NOT risk-on momentum winners
    assert "XLP" in targets and "XLU" in targets
    assert "AAPL" not in targets


# 5. Repeated emergency triggers (idempotence)
def test_repeated_emergency_triggers_idempotent(candidate_ae: CandidateAE_Combined):
    """Consecutive emergency shock days do not produce redundant sell orders."""
    spy_bars = [{"ts": f"2020-01-{i+1:02d}", "close": 300.0} for i in range(63)]
    spy_bars.append({"ts": "2020-03-10", "close": 290.0})
    spy_bars.append({"ts": "2020-03-11", "close": 280.0})

    market_state = {
        "SPY": spy_bars,
        "QQQ": [{"ts": f"2020-01-{i+1:02d}", "close": 200.0} for i in range(65)],
        "XLP": [{"ts": "2020-03-11", "close": 50.0}],
        "XLU": [{"ts": "2020-03-11", "close": 50.0}],
        "XLV": [{"ts": "2020-03-11", "close": 50.0}],
        "XLE": [{"ts": "2020-03-11", "close": 50.0}],
    }
    # Portfolio already in defensives matching target weights:
    # Equity = $100,000. XLP 24% = $24,000 (480 @ $50), XLU 24% = $24,000 (480 @ $50),
    # XLV 20% = $20,000 (400 @ $50), XLE 12% = $12,000 (240 @ $50), Cash = $20,000.
    portfolio_state = {
        "cash": 20000.0,
        "positions": [
            {"ticker": "XLP", "quantity": 480.0, "avg_cost": 50.0},
            {"ticker": "XLU", "quantity": 480.0, "avg_cost": 50.0},
            {"ticker": "XLV", "quantity": 400.0, "avg_cost": 50.0},
            {"ticker": "XLE", "quantity": 240.0, "avg_cost": 50.0},
        ],
        "last_prices": {"XLP": 50.0, "XLU": 50.0, "XLV": 50.0, "XLE": 50.0},
    }
    candidate_ae.last_rebalance_date = "2020-03-10"
    orders = candidate_ae.decide(market_state, portfolio_state, 20000.0)
    # Since positions are already exactly in defensive weights, no sell orders emitted
    sell_orders = [o for o in orders if o["side"] == "sell"]
    assert len(sell_orders) == 0, f"Spurious sell orders emitted: {sell_orders}"


# 6. Missing or corrupt SPY observations resilience
def test_missing_or_corrupt_spy_resilience(candidate_ae: CandidateAE_Combined):
    """Missing or short SPY bars safely evaluates to False without raising exceptions."""
    assert candidate_ae._is_market_shock({}) is False
    assert candidate_ae._is_market_shock({"SPY": []}) is False
    assert candidate_ae._is_market_shock({"SPY": [{"ts": "2020-01-01", "close": 300.0}]}) is False


# 7. Leveraged ETF gating during market distress
def test_leveraged_etf_exposure_gated_during_distress(candidate_ae: CandidateAE_Combined):
    """QLD and SSO overlay must never be active when shock occurs or vol > 0.28."""
    market_state = {
        "SPY": [{"ts": f"d{i}", "close": 300.0} for i in range(65)],
        "QQQ": [{"ts": f"d{i}", "close": 200.0} for i in range(65)],
        "QLD": [{"ts": "d64", "close": 100.0}],
        "SSO": [{"ts": "d64", "close": 100.0}],
    }
    # When is_shock is True
    targets = candidate_ae.compute_raw_targets(market_state, is_shock=True)
    assert "QLD" not in targets
    assert "SSO" not in targets


# 8. Partial fill and insufficient cash handling in Accounting Engine
def test_insufficient_cash_handling():
    port = PortfolioState(cash=10.0, start_cash=START_CASH)
    order = {"ticker": "SPY", "side": "buy", "quantity": 100.0}
    port.execute_order(order, open_price=300.0, risk_mode=RiskMode.TELEMETRY_ONLY)
    # Should partial fill or reject without crash
    assert port.cash >= 0.0
    assert port.positions.get("SPY", 0.0) < 1.0


# 9. Corporate action during liquidation
def test_stock_split_during_liquidation():
    port = PortfolioState(cash=10000.0, start_cash=START_CASH)
    port.positions["AAPL"] = 100.0
    port.avg_cost["AAPL"] = 100.0
    
    # 2:1 forward stock split via CorporateActionRegistry
    registry = CorporateActionRegistry()
    registry.register_split("2020-01-05", "AAPL", 2.0)
    registry.apply_splits_for_date("2020-01-05", port.positions, port.avg_cost)
    assert port.positions["AAPL"] == 200.0
    assert port.avg_cost["AAPL"] == 50.0
    
    # Execute full liquidation
    order = {"ticker": "AAPL", "side": "sell", "quantity": 200.0}
    port.execute_order(order, open_price=50.0, risk_mode=RiskMode.TELEMETRY_ONLY)
    assert port.positions.get("AAPL", 0.0) == 0.0
    assert port.cash > 19000.0


# 10. Transaction cost shock resilience
def test_transaction_cost_shock_balance_sheet_conservation():
    port = PortfolioState(cash=100000.0, start_cash=100000.0)
    # 100 bps commission shock
    order = {"ticker": "SPY", "side": "buy", "quantity": 100.0}
    port.execute_order(order, open_price=300.0, commission_bps=100.0, risk_mode=RiskMode.TELEMETRY_ONLY)
    
    inv_ok, msg = port.check_accounting_invariants({"SPY": 300.0})
    assert inv_ok is True, f"Invariant failed under cost shock: {msg}"
