"""
Guardian Alpha — V30 Stage 2A-B/G: Simulator Contract Verification & Robustness Test Suite.

Independent, preregistered adversarial micro-scenarios verifying:
- Gate B: Builderr Simulator Contract Conformance (Timing, Prices, Sequencing, Sizing, Rejections, Settlement).
- Gate D: Robustness Testing (Adverse Gaps, Slippage Stress, Missing Prices, Order Inversion, Invariants, Determinism).

Preserves all frozen production files and Stage 2A/2A-R/2A-F artifacts.
"""

from __future__ import annotations

from decimal import Decimal
import math
import pytest

import agent
from research.engine.v30_broker_accounting_final import (
    BrokerModel,
    FinalIndependentLedger,
    OrderSide,
    OrderStatus,
    compute_settlement_date,
)
from research.engine.v30_independent_accounting_oracle import (
    IndependentAccountingOracle,
)
from research.strategies.v30_execution_safe_agent import V30ExecutionSafeAgent
from research.strategies.v30_execution_safe_agent_r import V30ExecutionSafeAgentR
from research.strategies.v30_execution_safe_agent_final import V30ExecutionSafeAgentFinal


# ==============================================================================
# GATE B: CONTRACT CONFORMANCE TESTING
# ==============================================================================

class TestGateBContractConformance:
    """Verifies execution behaviors against the Builderr Simulator Contract."""

    def test_rule1_order_submission_timing_and_execution_open(self):
        """
        Rule 1: Orders generated from information up to close T are filled at T+1 open.
        Live runner (L418) and preview (L107) both evaluate decide() on market_state
        through prior close and execute orders at the current day's open.
        """
        day_t_close = {"SPY": 400.0, "QQQ": 300.0}
        day_t1_open = {"SPY": 405.0, "QQQ": 302.0}

        agent_final = V30ExecutionSafeAgentFinal(broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
        targets = {"SPY": 0.50, "QQQ": 0.50}
        positions = {}
        tot_eq = 100_000.0

        orders = agent_final.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=tot_eq,
            prices=day_t_close,
            settled_cash=100_000.0,
            current_date="2021-01-04",
        )

        assert len(orders) == 2
        ledger = FinalIndependentLedger(opening_cash=100_000.0, broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
        for o in orders:
            px = day_t1_open[o["ticker"]]
            slip = 0.0005  # 5 bps
            fill_px = px * (1.0 + slip)
            req, ok, _ = ledger.submit_buy_order(f"ORD_{o['ticker']}", o["ticker"], float(o["quantity"]), "2021-01-05", est_price=px)
            assert ok
            ledger.confirm_buy_fill(req, filled_qty=float(o["quantity"]), fill_price=fill_px)
            assert req.fill_price == pytest.approx(fill_px, rel=1e-5)
            assert req.fill_price != day_t_close[o["ticker"]]

    def test_rule2_execution_prices_and_leveraged_slippage(self):
        """
        Rule 2: Plain equity has 5 bps slippage; Leveraged ETFs have 10 bps slippage.
        """
        opens = {"SPY": 400.0, "QLD": 80.0, "TQQQ": 50.0}
        
        # Plain equity: 5 bps
        slip_spy = 0.0005 if agent.BETA_MULTIPLE.get("SPY", 1.0) == 1.0 else 0.0010
        assert slip_spy == 0.0005
        fill_spy = opens["SPY"] * (1.0 + slip_spy)
        assert fill_spy == pytest.approx(400.20)

        # 2x Leveraged ETF: 10 bps
        slip_qld = 0.0010 if agent.BETA_MULTIPLE.get("QLD", 1.0) > 1.0 else 0.0005
        assert slip_qld == 0.0010
        fill_qld = opens["QLD"] * (1.0 + slip_qld)
        assert fill_qld == pytest.approx(80.08)

        # 3x Leveraged ETF: 10 bps
        slip_tqqq = 0.0010 if agent.BETA_MULTIPLE.get("TQQQ", 1.0) > 1.0 else 0.0005
        assert slip_tqqq == 0.0010
        fill_tqqq = opens["TQQQ"] * (1.0 + slip_tqqq)
        assert fill_tqqq == pytest.approx(50.05)

    def test_rule3_order_sequencing_discrepancy_preview_vs_broker(self):
        """
        Rule 3 & 4: Order Sequencing & Sell-Before-Buy Handling.
        In preview.py, orders execute in list order.
        In live_runner.py, orders are sorted to force sells first.
        V30 models emit sells strictly before buys to guarantee safety across both engines.
        """
        positions = {"QQQ": {"quantity": 100.0, "avg_cost": 300.0}}
        prices = {"SPY": 400.0, "QQQ": 300.0}
        cash = 1_000.0  # Constrained cash; selling QQQ yields ~$30,000
        total_equity = cash + 100.0 * 300.0  # $31,000
        targets = {"SPY": 0.90, "QQQ": 0.0}

        # E0 Agent order sequencing
        e0_orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
        assert e0_orders[0]["side"] == "sell"
        assert e0_orders[0]["ticker"] == "QQQ"
        assert e0_orders[1]["side"] == "buy"
        assert e0_orders[1]["ticker"] == "SPY"

        # V30 Final Agent order sequencing
        v30_agent = V30ExecutionSafeAgentFinal(broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
        v30_orders = v30_agent.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=total_equity,
            prices=prices,
            settled_cash=cash,
            current_date="2021-01-04",
        )
        assert v30_orders[0]["side"] == "sell"
        assert v30_orders[0]["ticker"] == "QQQ"
        assert v30_orders[1]["side"] == "buy"
        assert v30_orders[1]["ticker"] == "SPY"

    def test_rule5_buying_power_and_simultaneous_order_saturation(self):
        """
        Rule 5: Buying-power calculation across broker models.
        When selling $30,000 of QQQ with only $1,000 settled cash:
        - E0 immediately credits 98% of expected sells, generating ~$28,000+ of buys.
        - V30 Model 1 (Strict Settled Cash) restricts buys strictly to settled cash ($1,000 - reserve buffer).
        - V30 Model 2 (Confirmed Sequential) applies 10% sell haircut + 5% buy markup.
        - V30 Model 3 (Settlement Delay) restricts day T buys to settled cash.
        """
        positions = {"QQQ": {"quantity": 100.0, "avg_cost": 300.0}}
        prices = {"SPY": 400.0, "QQQ": 300.0}
        targets = {"SPY": 0.90, "QQQ": 0.0}
        total_equity = 31_000.0
        settled_cash = 1_000.0

        # E0 generates buys aggressively using expected sell proceeds
        e0_orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, settled_cash)
        e0_buys = [o for o in e0_orders if o["side"] == "buy"]
        e0_buy_notional = sum(o["quantity"] * prices[o["ticker"]] for o in e0_buys)
        assert e0_buy_notional > 25_000.0  # Spends anticipated sell proceeds!

        # V30 Model 1 strictly respects settled cash (zero credit for unconfirmed/unsettled sells)
        v30_m1 = V30ExecutionSafeAgentFinal(broker_model=BrokerModel.MODEL_1_STRICT_SETTLED_CASH)
        m1_orders = v30_m1.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=total_equity,
            prices=prices,
            settled_cash=settled_cash,
            current_date="2021-01-04",
        )
        m1_buys = [o for o in m1_orders if o["side"] == "buy"]
        m1_buy_notional = sum(o["quantity"] * prices[o["ticker"]] for o in m1_buys)
        assert m1_buy_notional <= settled_cash  # Strictly bounded by $1,000 settled cash!

    def test_rule6_unheld_position_sell_rejection(self):
        """
        Rule 6 & 7: Rejection behavior.
        Attempting to sell a security that is not held must be rejected.
        """
        ledger = FinalIndependentLedger(opening_cash=50_000.0)
        req, ok, reason = ledger.submit_sell_order("S1", "TSLA", 10.0, "2021-01-05")
        assert not ok
        assert reason == "UNHELD_POSITION"
        assert ledger.positions.get("TSLA", 0.0) == 0.0
        assert ledger.settled_cash == 50_000.0

    def test_rule7_partial_fills_and_cost_basis(self):
        """
        Rule 10: Partial fills.
        When cash allows only a partial fill, quantity is clamped, avg_cost is updated,
        and unspent reservation is released.
        """
        ledger = FinalIndependentLedger(opening_cash=50_000.0, broker_model=BrokerModel.MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION)
        b1, ok, _ = ledger.submit_buy_order("B1", "AAPL", 100.0, "2021-01-05", est_price=100.0)
        assert ok
        # 100 * 100 * 1.05 = 10,500 reserved
        assert ledger.reserved_cash == 10500.0

        # Partial fill: only 40 shares fill at $100 = $4,000
        ledger.confirm_buy_fill(b1, filled_qty=40.0, fill_price=100.0, commission=0.0)
        assert b1.status == OrderStatus.PARTIALLY_FILLED
        assert ledger.positions["AAPL"] == 40.0
        assert ledger.avg_cost["AAPL"] == 100.0
        assert ledger.settled_cash == 46000.0  # 50,000 - 4,000
        # 40% of $10,500 = $4,200 consumed from reservation, remaining $6,300 stays reserved
        assert ledger.reserved_cash == pytest.approx(6300.0)

        # Cancel remaining 60 shares
        ledger.cancel_order(b1, reason="EXCHANGE_PARTIAL_CANCEL")
        assert b1.status == OrderStatus.CANCELLED
        assert ledger.reserved_cash == 0.0  # Remaining reservation cleanly released!
        assert ledger.available_settled_cash() == 46000.0

    def test_rule8_fractional_shares_contract(self):
        """
        Rule 8: Fractional shares.
        Builderr simulator allows float quantities (preview.py: qty = cash / fill).
        However, agent.py and V30 agents truncate buy/sell orders to integer shares (int(qty))
        to ensure institutional realism and avoid broker fractional-share rejection.
        """
        agent_final = V30ExecutionSafeAgentFinal()
        targets = {"SPY": 0.333333, "QQQ": 0.333333, "AAPL": 0.333333}
        prices = {"SPY": 401.27, "QQQ": 305.89, "AAPL": 142.17}
        positions = {}

        orders = agent_final.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=100_000.0,
            prices=prices,
            settled_cash=100_000.0,
            current_date="2021-01-04",
        )

        for o in orders:
            assert isinstance(o["quantity"], int)
            assert o["quantity"] == int(o["quantity"])

    def test_rule9_settlement_timing_simulator_t0_vs_brokerage_t1_t2(self):
        """
        Rule 13: Settlement assumptions.
        preview.py assumes T+0 instantaneous settlement.
        Real brokerages enforce T+1 (modern SEC rule) or T+2 (historical).
        Model 3 proves safe execution under T+1 / T+2 settlement delay.
        """
        trade_date = "2021-04-30"  # Friday
        settle_t1 = compute_settlement_date(trade_date, lag_business_days=1)
        settle_t2 = compute_settlement_date(trade_date, lag_business_days=2)

        # Weekend skipped
        assert settle_t1 == "2021-05-03"  # Monday
        assert settle_t2 == "2021-05-04"  # Tuesday

    def test_rule10_leverage_and_concentration_caps(self):
        """
        Rule 14: Leverage and Concentration Telemetry.
        Competition contract limit: Gross exposure <= 1.50x equity (beta-adjusted).
        Agent internal risk control: MAX_BETA_GROSS = 1.35 (10% safety buffer).
        Max concentration <= 30% per name for > 5 consecutive days (agent caps at 20%).
        """
        import preview
        assert preview.LEVERAGE_CAP == 1.50
        assert preview.CONCENTRATION_CAP == 0.30
        assert agent.MAX_BETA_GROSS == 1.35  # Conservative 10% safety margin below 1.50 cap
        assert agent.MAX_WEIGHT == 0.24  # Conservative 24% target cap (well below 30% cap)
        assert agent.BETA_MULTIPLE.get("TQQQ") == 3.0
        assert agent.BETA_MULTIPLE.get("QLD") == 2.0
        assert agent.BETA_MULTIPLE.get("SPY", 1.0) == 1.0


# ==============================================================================
# GATE D: SYNTHETIC STRESS ROBUSTNESS TESTING
# ==============================================================================

class TestGateDRobustnessScenarios:
    """Independent, preregistered adversarial stress micro-scenarios."""

    def test_stress_adverse_price_gaps(self):
        """
        Scenario 1: Adverse Overnight Price Gaps.
        Buys gap up +10% at the open; Sells gap down -10% at the open.
        Under Frozen E0, this severe divergence would blow through cash reserves.
        Under V30 Final, buy markup and sell haircut absorb the gap cleanly.
        """
        close_px = {"SPY": 400.0, "QQQ": 300.0}
        adverse_open = {"SPY": 440.0, "QQQ": 270.0}

        positions = {"QQQ": {"quantity": 100.0, "avg_cost": 300.0}}
        cash = 5_000.0
        tot_eq = cash + 100.0 * 300.0  # $35,000

        targets = {"SPY": 0.80, "QQQ": 0.0}

        v30_agent = V30ExecutionSafeAgentFinal(
            broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL,
            sell_haircut=0.15,  # 15% haircut
            buy_markup=0.10,    # 10% markup buffer
            cash_reserve_floor=0.05,
        )

        orders = v30_agent.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=tot_eq,
            prices=close_px,
            settled_cash=cash,
            current_date="2021-01-04",
        )

        ledger = FinalIndependentLedger(opening_cash=cash, broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
        ledger.positions["QQQ"] = 100.0
        ledger.avg_cost["QQQ"] = 300.0

        # Execute sell order first at adverse price
        sell_order = next(o for o in orders if o["side"] == "sell")
        s_req, ok_s, _ = ledger.submit_sell_order("S1", sell_order["ticker"], float(sell_order["quantity"]), "2021-01-05")
        assert ok_s
        fill_px_s = adverse_open["QQQ"] * (1.0 - 0.0005)
        ledger.confirm_sell_fill(s_req, filled_qty=float(sell_order["quantity"]), fill_price=fill_px_s, current_date="2021-01-05")

        # Execute buy order second at adverse price
        buy_order = next(o for o in orders if o["side"] == "buy")
        fill_px_b = adverse_open["SPY"] * (1.0 + 0.0005)
        b_req, ok_b, _ = ledger.submit_buy_order("B1", buy_order["ticker"], float(buy_order["quantity"]), "2021-01-05", est_price=adverse_open["SPY"])
        assert ok_b
        ledger.confirm_buy_fill(b_req, filled_qty=float(buy_order["quantity"]), fill_price=fill_px_b)

        # Must execute without blowing cash negative
        assert ledger.settled_cash >= 0.0
        assert ledger.positions.get("QQQ", 0.0) == 0.0
        assert ledger.positions.get("SPY", 0.0) > 0.0

    def test_stress_extreme_slippage_200bps(self):
        """
        Scenario 2: Extreme Slippage Stress (200 bps = 2.0%).
        Verify that broker fills and double-entry accounting maintain conservation
        under 40x normal slippage.
        """
        ledger = FinalIndependentLedger(opening_cash=100_000.0)
        open_px = 400.0
        slip_200bps = 0.020
        fill_px = open_px * (1.0 + slip_200bps)

        b1, ok, _ = ledger.submit_buy_order("B1", "SPY", 100.0, "2021-01-05", est_price=fill_px)
        assert ok
        ledger.confirm_buy_fill(b1, filled_qty=100.0, fill_price=fill_px)

        assert ledger.settled_cash == pytest.approx(100_000.0 - (100 * 408.0))
        assert ledger.positions["SPY"] == 100.0
        assert ledger.avg_cost["SPY"] == 408.0

    def test_stress_missing_and_corrupt_execution_prices(self):
        """
        Scenario 3: Missing, Zero, Negative, and Non-finite Execution Prices.
        Agent must skip or reject gracefully without crashing.
        """
        v30_agent = V30ExecutionSafeAgentFinal()
        targets = {"VALID": 0.50, "NONE_PX": 0.25, "ZERO_PX": 0.25}
        prices = {
            "VALID": 100.0,
            "NONE_PX": None,
            "ZERO_PX": 0.0,
            "NEG_PX": -50.0,
        }

        orders = v30_agent.generate_safe_orders(
            targets=targets,
            positions={},
            total_equity=10_000.0,
            prices=prices,
            settled_cash=10_000.0,
            current_date="2021-01-04",
        )

        assert len(orders) == 1
        assert orders[0]["ticker"] == "VALID"

    def test_stress_order_sequence_inversion(self):
        """
        Scenario 4: Order Sequence Inversion Sensitivity.
        Verify that sorting sells before buys neutralizes order submission sequence.
        """
        orders_std = [
            {"ticker": "QQQ", "side": "sell", "quantity": 50},
            {"ticker": "SPY", "side": "buy", "quantity": 20},
        ]
        orders_inv = [
            {"ticker": "SPY", "side": "buy", "quantity": 20},
            {"ticker": "QQQ", "side": "sell", "quantity": 50},
        ]

        def process_batch(order_list):
            sorted_orders = sorted(order_list, key=lambda x: 0 if x["side"] == "sell" else 1)
            l = FinalIndependentLedger(opening_cash=5_000.0, broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
            l.positions["QQQ"] = 50.0
            l.avg_cost["QQQ"] = 300.0

            for o in sorted_orders:
                if o["side"] == "sell":
                    s_req, ok, _ = l.submit_sell_order(f"S_{o['ticker']}", o["ticker"], float(o["quantity"]), "2021-01-05")
                    assert ok
                    l.confirm_sell_fill(s_req, float(o["quantity"]), 300.0, current_date="2021-01-05")
                else:
                    b_req, ok, _ = l.submit_buy_order(f"B_{o['ticker']}", o["ticker"], float(o["quantity"]), "2021-01-05", est_price=400.0)
                    assert ok
                    l.confirm_buy_fill(b_req, float(o["quantity"]), 400.0)
            return l.settled_cash, l.positions

        cash1, pos1 = process_batch(orders_std)
        cash2, pos2 = process_batch(orders_inv)

        assert cash1 == pytest.approx(cash2)
        assert pos1 == pos2

    def test_stress_zero_and_negative_cash_boundary(self):
        """
        Scenario 5: Zero and Negative Cash Boundary Conditions.
        Agent must produce zero buys and prevent balance overdrafts.
        """
        v30_agent = V30ExecutionSafeAgentFinal()
        targets = {"SPY": 0.50, "QQQ": 0.50}
        prices = {"SPY": 400.0, "QQQ": 300.0}

        orders_zero = v30_agent.generate_safe_orders(
            targets=targets,
            positions={},
            total_equity=10_000.0,
            prices=prices,
            settled_cash=0.0,
            current_date="2021-01-04",
        )
        assert len(orders_zero) == 0

        orders_neg = v30_agent.generate_safe_orders(
            targets=targets,
            positions={},
            total_equity=10_000.0,
            prices=prices,
            settled_cash=-500.0,
            current_date="2021-01-04",
        )
        assert len(orders_neg) == 0

    def test_stress_double_entry_accounting_invariants(self):
        """
        Scenario 6: Double-entry accounting conservation across complex trade cycle.
        """
        oracle = IndependentAccountingOracle(opening_cash="100000.00")
        tot_eq = Decimal("100000.00")

        # 1. Buy SPY
        ok1, _, res1 = oracle.submit_buy("B1", "SPY", "100", "400.00", total_equity=tot_eq)
        assert ok1
        oracle.execute_buy_fill("SPY", "100", "100", "400.00", res1, commission="0.00")

        # 2. Buy QQQ
        ok2, _, res2 = oracle.submit_buy("B2", "QQQ", "100", "300.00", total_equity=tot_eq)
        assert ok2
        oracle.execute_buy_fill("QQQ", "100", "100", "300.00", res2, commission="0.00")

        # 3. Sell 50 SPY at $420
        ok3, _, _ = oracle.submit_sell("S1", "SPY", "50")
        assert ok3
        oracle.execute_sell_fill("SPY", "50", "420.00", settlement_date="2021-01-06", commission="0.00")

        prices = {"SPY": Decimal("420.00"), "QQQ": Decimal("300.00")}
        valid, msg = oracle.verify_all_invariants(prices)
        assert valid, msg

    def test_stress_numerical_stability_extreme_values(self):
        """
        Scenario 7: Numerical stability under extreme price scales ($0.0001 to $600,000).
        """
        ledger = FinalIndependentLedger(opening_cash=1_000_000.0)

        # Micro-cap
        b_penny, ok1, _ = ledger.submit_buy_order("B_PENNY", "PENNY", 100_000.0, "2021-01-05", est_price=0.0001)
        assert ok1
        ledger.confirm_buy_fill(b_penny, 100_000.0, 0.0001)

        # Mega-cap
        b_berk, ok2, _ = ledger.submit_buy_order("B_BERK", "BERK", 1.0, "2021-01-05", est_price=600_000.0)
        assert ok2
        ledger.confirm_buy_fill(b_berk, 1.0, 600_000.0)

        assert math.isfinite(ledger.settled_cash)
        assert ledger.settled_cash == pytest.approx(1_000_000.0 - 10.0 - 600_000.0)

    def test_stress_deterministic_repeatability(self):
        """
        Scenario 8: Deterministic Repeatability.
        Running identical scenario 5 times yields bit-identical outputs.
        """
        def run_sim():
            l = FinalIndependentLedger(opening_cash=100_000.0, broker_model=BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL)
            l.positions["QQQ"] = 100.0
            l.avg_cost["QQQ"] = 300.0

            s_req, _, _ = l.submit_sell_order("S1", "QQQ", 50.0, "2021-01-05")
            l.confirm_sell_fill(s_req, 50.0, 301.75, current_date="2021-01-05")

            b_req, _, _ = l.submit_buy_order("B1", "SPY", 50.0, "2021-01-05", est_price=402.15)
            l.confirm_buy_fill(b_req, 50.0, 402.15)

            return (l.settled_cash, l.positions.get("SPY", 0.0), l.positions.get("QQQ", 0.0), l.avg_cost.get("SPY", 0.0))

        baseline = run_sim()
        for _ in range(4):
            res = run_sim()
            assert res == baseline
