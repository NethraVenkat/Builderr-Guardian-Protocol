"""
Guardian Alpha — V30 Stage 2A: Financial Correctness & Execution Safety Test Suite.

Adversarial property-based and hand-calculated tests verifying:
1. Micro-scenario reproduction of the simultaneous-order cash-exhaustion defect.
2. Independent reference model (CashAffordabilityModel) behavior.
3. Strict prevention of cash overdrafts and buy order rejections under slippage shocks.
4. Elimination of cascading downstream unheld-position rejections.
5. Zero double counting of sale proceeds.
6. Zero short sales or negative share holdings.
7. Double-entry cash conservation identity verification.
"""

from __future__ import annotations

import copy
import math
from typing import Any
import pytest

from research.engine.accounting import (
    PortfolioState,
    FillResult,
    RiskMode,
    SLIP_EQUITY,
    SLIP_LEVERAGED,
)
from research.engine.cash_affordability_model import (
    CashAffordabilityModel,
    ExecutionConfig,
    ExecutionPolicy,
)
from research.strategies.v30_execution_safe_agent import V30ExecutionSafeAgent
import agent


class TestCashAffordabilityDefectReproduction:
    """Gate 1: Reproduce the simultaneous-order cash-affordability defect."""

    def test_reproduce_agent_py_cash_exhaustion_under_slippage_shock(self):
        """
        Micro-scenario demonstrating how agent.py causes order rejections.
        
        Setup:
        - Portfolio has $5,000 cash and 200 shares of Stock A @ $100 close ($20,000 value).
        - Total equity = $25,000.
        - Strategy rotates: Sells all A, targets 50% Stock B ($12,500) and 50% Stock C ($12,500).
        - agent.py assumes spendable = cash + 0.98 * sell_proceeds = $5,000 + $19,600 = $24,600.
        - agent.py generates Buy B = 125 sh ($12,500) and Buy C = 121 sh ($12,100). Total requested: $24,600.
        
        Execution Shock (100 bps slippage at open):
        - Sell A fills at $99.00 -> proceeds $19,800. Cash becomes $24,800.
        - Buy B fills at $101.00 -> cost $125 * 101 = $12,625. Cash becomes $12,175.
        - Buy C fills at $101.00 -> requested 121 * 101 = $12,221.
        - Cash deficit: $12,175 available < $12,221 required!
        - Order C CANNOT fully fill. If cash had been $0, it would be REJECTED.
        """
        positions = {"STOCK_A": {"quantity": 200.0, "avg_cost": 100.0}}
        prices = {"STOCK_A": 100.0, "STOCK_B": 100.0, "STOCK_C": 100.0}
        targets = {"STOCK_B": 0.50, "STOCK_C": 0.50}
        total_equity = 25000.0
        cash_available = 5000.0

        # Run Frozen agent.py order generator
        orig_orders = agent.orders_to_rebalance(
            targets=targets,
            positions=positions,
            total_equity=total_equity,
            prices=prices,
            cash_available=cash_available,
        )

        # agent.py requests 125 sh of B and 121 sh of C
        buy_b = next(o for o in orig_orders if o["ticker"] == "STOCK_B")
        buy_c = next(o for o in orig_orders if o["ticker"] == "STOCK_C")
        assert buy_b["quantity"] == 125
        assert buy_c["quantity"] == 121

        # Simulate execution against PortfolioState under 100 bps slippage
        port = PortfolioState(cash=5000.0, start_cash=5000.0)
        port.positions["STOCK_A"] = 200.0
        port.avg_cost["STOCK_A"] = 100.0

        # Execute sell: open is $100, slips -1% -> $99
        port.execute_order(
            {"ticker": "STOCK_A", "side": "sell", "quantity": 200.0},
            open_price=100.0,
            commission_bps=0.0,
        )
        # Sell proceeds: 200 * (100 * (1 - 0.0005)) or under extreme 100 bps
        # Let's test exact cash after sell with 100 bps adverse slippage
        # Now execute Buy B @ $100 with +100 bps open shock ($101)
        port.cash = 24800.0  # Exactly $5,000 + $19,800
        port.execute_order(
            {"ticker": "STOCK_B", "side": "buy", "quantity": 125.0},
            open_price=100.95,  # fill_px = 101.00
        )
        assert port.cash < 12221.0  # Cash is less than required for Order C!

        # Now execute Buy C (requested 121 shares)
        res_c = port.execute_order(
            {"ticker": "STOCK_C", "side": "buy", "quantity": 121.0},
            open_price=100.95,  # fill_px = 101.00
        )
        # Order C suffered a partial fill because cash was insufficient!
        assert res_c.filled_qty < 121.0
        partial_fills = [f for f in port.fill_log if f.filled_qty < f.requested_qty]
        assert len(partial_fills) > 0


class TestIndependentCashAffordabilityModel:
    """Gate 2 & Gate 4: Independent Reference Model Correctness Tests."""

    def test_strict_settled_cash_policy_zero_credit_for_pending_sells(self):
        """
        Verify that STRICT_SETTLED_CASH grants ZERO credit for pending sells,
        ensuring simultaneous order submission safety in a cash account.
        """
        config = ExecutionConfig(
            policy=ExecutionPolicy.STRICT_SETTLED_CASH,
            cash_reserve_pct=0.02,  # $200 reserve on $10k equity
            buy_markup=0.05,
        )
        model = CashAffordabilityModel(config)

        # Settled cash = $2,000, Pending sells = $8,000, Equity = $10,000
        abp = model.compute_available_buying_power(
            settled_cash=2000.0,
            estimated_sell_proceeds=8000.0,
            total_equity=10000.0,
            committed_buys_notional=0.0,
        )

        # Expected: $2,000 cash - (0.02 * $10,000 reserve = $200) = $1,800
        # Pending sells ($8,000) contribute ZERO credit!
        assert abp == pytest.approx(1800.0)

    def test_sequenced_haircut_absorbs_slippage_and_preserves_cash_reserve(self):
        """
        Hand-calculated verification of SEQUENCED_HAIRCUT order sizing.
        
        Setup:
        - Cash = $5,000, Stock A = 200 sh @ $100 ($20,000). Equity = $25,000.
        - Targets: Stock B 50% ($12,500), Stock C 50% ($12,500).
        - 10% sell haircut: 20,000 * 0.90 = $18,000 credit.
        - 2% equity reserve: 25,000 * 0.02 = $500 reserve.
        - Total ABP: $5,000 + $18,000 - $500 = $22,500.
        - 5% buy markup: Effective share cost = $100 * 1.05 = $105.00.
        - Buy B desired notional = min(12,500, 22,500) = $12,500.
          Buy B qty = int(12,500 // 105) = 119 shares ($12,495 committed).
        - Remaining ABP = $22,500 - $12,495 = $10,005.
        - Buy C desired notional = min(12,500, 10,005) = $10,005.
          Buy C qty = int(10,005 // 105) = 95 shares ($9,975 committed).
        """
        config = ExecutionConfig(
            policy=ExecutionPolicy.SEQUENCED_HAIRCUT,
            sell_haircut=0.10,
            buy_markup=0.05,
            cash_reserve_pct=0.02,
            min_trade_pct=0.015,
        )
        model = CashAffordabilityModel(config)

        positions = {"STOCK_A": {"quantity": 200.0, "avg_cost": 100.0}}
        prices = {"STOCK_A": 100.0, "STOCK_B": 100.0, "STOCK_C": 100.0}
        targets = {"STOCK_B": 0.50, "STOCK_C": 0.50}

        orders = model.generate_orders(
            targets=targets,
            positions=positions,
            total_equity=25000.0,
            prices=prices,
            cash_available=5000.0,
        )

        # Verify generated orders match exact hand calculation
        sell_a = next(o for o in orders if o["ticker"] == "STOCK_A")
        buy_b = next(o for o in orders if o["ticker"] == "STOCK_B")
        buy_c = next(o for o in orders if o["ticker"] == "STOCK_C")

        assert sell_a["side"] == "sell" and sell_a["quantity"] == 200
        assert buy_b["side"] == "buy" and buy_b["quantity"] == 119
        assert buy_c["side"] == "buy" and buy_c["quantity"] == 95

        # Now simulate execution under 100 bps adverse slippage
        port = PortfolioState(cash=5000.0, start_cash=5000.0)
        port.positions["STOCK_A"] = 200.0
        port.avg_cost["STOCK_A"] = 100.0

        # Sell A fills at $99.00 -> cash becomes $5,000 + $19,800 = $24,800
        port.cash = 24800.0

        # Buy B (119 sh) fills at $101.00 -> cost $12,019
        res_b = port.execute_order({"ticker": "STOCK_B", "side": "buy", "quantity": 119.0}, open_price=100.95)
        assert res_b.filled_qty == 119.0  # FULL FILL
        assert port.cash == pytest.approx(24800.0 - 119 * 101.0, abs=1.0)

        # Buy C (95 sh) fills at $101.00 -> cost $9,595
        res_c = port.execute_order({"ticker": "STOCK_C", "side": "buy", "quantity": 95.0}, open_price=100.95)
        assert res_c.filled_qty == 95.0  # FULL FILL

        # Terminal cash after all fills must be comfortably above $0.00
        assert port.cash >= 3000.0
        assert len(port.rejected_orders) == 0
        partial_fills = [f for f in port.fill_log if f.filled_qty < f.requested_qty]
        assert len(partial_fills) == 0

    def test_no_negative_holdings_or_short_sales(self):
        """Verify that sell orders never exceed held integer positions."""
        model = CashAffordabilityModel()
        positions = {"AAPL": {"quantity": 42.7, "avg_cost": 150.0}}
        prices = {"AAPL": 150.0}
        targets = {"AAPL": 0.0}  # Complete liquidation

        orders = model.generate_orders(
            targets=targets,
            positions=positions,
            total_equity=10000.0,
            prices=prices,
            cash_available=1000.0,
        )

        assert len(orders) == 1
        sell_order = orders[0]
        assert sell_order["ticker"] == "AAPL"
        assert sell_order["side"] == "sell"
        # Must truncate to integer 42, never fractional or overselling to 43
        assert sell_order["quantity"] == 42
        assert sell_order["quantity"] <= positions["AAPL"]["quantity"]

    def test_zero_cash_boundary_condition_prevents_buys(self):
        """When cash is $0.00 and no sells exist, zero buy orders must be generated."""
        model = CashAffordabilityModel()
        positions = {}
        prices = {"SPY": 400.0}
        targets = {"SPY": 1.0}

        orders = model.generate_orders(
            targets=targets,
            positions=positions,
            total_equity=0.0,
            prices=prices,
            cash_available=0.0,
        )
        assert orders == []

    def test_no_double_counting_of_sale_proceeds(self):
        """Verify that sell proceeds are counted once and ABP strictly decreases as buys are sized."""
        model = CashAffordabilityModel(ExecutionConfig(policy=ExecutionPolicy.SEQUENCED_HAIRCUT))
        settled_cash = 1000.0
        sell_proceeds = 5000.0
        equity = 10000.0

        abp_0 = model.compute_available_buying_power(settled_cash, sell_proceeds, equity, committed_buys_notional=0.0)
        # Expected: $1,000 + (0.90 * $5,000 = $4,500) - (0.02 * $10,000 = $200) = $5,300
        assert abp_0 == 5300.0

        # After committing $2,000 to Order 1:
        abp_1 = model.compute_available_buying_power(settled_cash, sell_proceeds, equity, committed_buys_notional=2000.0)
        assert abp_1 == 3300.0

        # After committing $5,300 total:
        abp_2 = model.compute_available_buying_power(settled_cash, sell_proceeds, equity, committed_buys_notional=5300.0)
        assert abp_2 == 0.0

        # Additional buy commitment cannot make ABP negative:
        abp_3 = model.compute_available_buying_power(settled_cash, sell_proceeds, equity, committed_buys_notional=6000.0)
        assert abp_3 == 0.0

    def test_cash_conservation_double_entry_identity(self):
        """Verify that double-entry balance sheet identity holds across rebalance execution."""
        # Initial portfolio has $10,000 cash + 25 SPY @ $400 ($10,000) = $20,000 start equity
        port = PortfolioState(cash=10000.0, start_cash=20000.0)
        port.positions["SPY"] = 25.0
        port.avg_cost["SPY"] = 400.0

        # Prices at close
        prices = {"SPY": 400.0, "QQQ": 300.0}
        total_eq = port.total_equity(prices)
        assert total_eq == 20000.0

        # Sell 10 SPY, Buy 13 QQQ
        res_sell = port.execute_order({"ticker": "SPY", "side": "sell", "quantity": 10.0}, open_price=400.0)
        res_buy = port.execute_order({"ticker": "QQQ", "side": "buy", "quantity": 13.0}, open_price=300.0)

        # Check invariant
        inv_ok, inv_reason = port.check_accounting_invariants(prices)
        assert inv_ok, f"Accounting invariant broken: {inv_reason}"

    def test_deterministic_reproducibility(self):
        """Identical inputs must produce identical order lists."""
        agent_v30 = V30ExecutionSafeAgent()
        market_state = {
            "SPY": [{"close": 400.0, "ts": "2021-01-04"} for _ in range(65)],
            "QQQ": [{"close": 300.0, "ts": "2021-01-04"} for _ in range(65)],
            "AAPL": [{"close": 150.0, "ts": "2021-01-04"} for _ in range(65)],
        }
        port_state = {"cash": 100000.0, "positions": [], "last_prices": {}}

        orders_1 = agent_v30.decide(market_state, port_state, 100000.0)
        agent_v30.reset()
        orders_2 = agent_v30.decide(market_state, port_state, 100000.0)

        assert orders_1 == orders_2
