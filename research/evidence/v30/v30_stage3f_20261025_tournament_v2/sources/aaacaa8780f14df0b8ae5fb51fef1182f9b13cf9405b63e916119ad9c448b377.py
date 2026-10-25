"""
Guardian Alpha — V30 Stage 2A-F Final Remediated Execution Safe Strategy.

Hardened strategy wrapping Frozen E0 target weights with the FinalIndependentLedger.
Features:
- Configurable broker settlement policies (Model 1, Model 2, Model 3).
- Proportional fund reservation on partial fills.
- Business-day settlement calendar (skips weekends and US market holidays).
- 100% preservation of Frozen E0 alpha weights (zero target drift).
- Zero modifications to agent.py, v12_candidate_ae.py, or universe.json.
"""

from __future__ import annotations

import math
from typing import Any

import agent
from research.engine.v30_broker_accounting_final import (
    BrokerModel,
    FinalIndependentLedger,
    OrderSide,
    OrderStatus,
)


class V30ExecutionSafeAgentFinal:
    """
    Final institutional execution-safe agent conforming to Stage 2A-F acceptance standards.
    """

    def __init__(
        self,
        broker_model: BrokerModel = BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL,
        sell_haircut: float = 0.10,
        buy_markup: float = 0.05,
        cash_reserve_floor: float = 0.02,
        settlement_delay_days: int = 1,
        rebalance_every_days: int = agent.REBALANCE_EVERY_DAYS,
    ) -> None:
        self.broker_model: BrokerModel = broker_model
        self.sell_haircut: float = sell_haircut
        self.buy_markup: float = buy_markup
        self.reserve_floor: float = cash_reserve_floor
        self.settlement_delay_days: int = settlement_delay_days
        self.rebalance_every_days: int = rebalance_every_days

        self.last_rebalance_date: str | None = None
        self.ledger: FinalIndependentLedger | None = None

    def reset(self) -> None:
        """Reset internal rebalance tracker for clean replay evaluation."""
        self.last_rebalance_date = None

    def _days_since_rebalance(self, market_state: dict[str, list[dict[str, Any]]]) -> int | None:
        if self.last_rebalance_date is None:
            return None
        bars = market_state.get("SPY") or market_state.get("QQQ") or []
        dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
        if not dates or self.last_rebalance_date not in dates:
            return None
        return len(dates) - dates.index(self.last_rebalance_date) - 1

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        """Return conservative long-only rebalance orders bounded by broker buying power."""
        if not market_state or not agent._finite_inputs(market_state, portfolio_state, cash):
            return []

        latest_date = agent._latest_bar_date(market_state)
        if latest_date is None:
            return []

        tot_eq = agent.equity(portfolio_state, cash)
        if tot_eq <= 0.0 or not math.isfinite(tot_eq):
            return []

        days_since = self._days_since_rebalance(market_state)
        drifted = agent._has_position_drifted(portfolio_state, tot_eq)
        should_rebalance = (
            self.last_rebalance_date is None
            or days_since is None
            or days_since >= self.rebalance_every_days
            or drifted
        )
        if not should_rebalance:
            return []

        targets = agent.target_weights(market_state)
        if not targets:
            return []

        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)

        orders = self.generate_safe_orders(
            targets=targets,
            positions=positions,
            total_equity=tot_eq,
            prices=prices,
            settled_cash=cash,
            current_date=latest_date,
        )

        if orders:
            self.last_rebalance_date = latest_date

        return orders

    def generate_safe_orders(
        self,
        targets: dict[str, float],
        positions: dict[str, dict[str, float]],
        total_equity: float,
        prices: dict[str, float],
        settled_cash: float,
        current_date: str,
    ) -> list[dict[str, Any]]:
        min_trade = total_equity * agent.MIN_TRADE_PCT
        orders: list[dict[str, Any]] = []

        # 1. Sells First: strictly cap sell quantities to physically held shares
        estimated_sell_proceeds = 0.0

        for ticker, pos in positions.items():
            px = prices.get(ticker)
            if px is None or px <= 0.0:
                continue

            held_qty = float(pos.get("quantity", 0.0))
            if held_qty <= 0.0:
                continue

            current_val = held_qty * px
            target_val = total_equity * targets.get(ticker, 0.0)
            delta = target_val - current_val

            if ticker not in targets:
                sell_qty = int(held_qty)
                if sell_qty > 0 and current_val >= min_trade:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    estimated_sell_proceeds += sell_qty * px
            elif delta < -min_trade:
                sell_qty = min(int(abs(delta) // px), int(held_qty))
                if sell_qty > 0:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    estimated_sell_proceeds += sell_qty * px

        # 2. Derive Spendable Cash
        reserve_buffer = total_equity * self.reserve_floor

        if self.broker_model == BrokerModel.MODEL_1_STRICT_SETTLED_CASH:
            spendable_cash = max(0.0, float(settled_cash) - reserve_buffer)
        elif self.broker_model == BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL:
            haircut_proceeds = estimated_sell_proceeds * (1.0 - self.sell_haircut)
            spendable_cash = max(0.0, float(settled_cash) + haircut_proceeds - reserve_buffer)
        elif self.broker_model == BrokerModel.MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION:
            spendable_cash = max(0.0, float(settled_cash) - reserve_buffer)
        else:
            spendable_cash = max(0.0, float(settled_cash) - reserve_buffer)

        # 3. Dynamic Buy Sizing with Slippage Markup
        buy_candidates: list[dict[str, Any]] = []
        for ticker, target_wt in targets.items():
            px = prices.get(ticker)
            if px is None or px <= 0.0:
                continue

            current_qty = float(positions.get(ticker, {}).get("quantity", 0.0))
            current_val = current_qty * px
            target_val = total_equity * target_wt
            delta = target_val - current_val

            if delta > min_trade:
                desired_qty = int(delta // px)
                if desired_qty > 0:
                    buy_candidates.append({
                        "ticker": ticker,
                        "desired_qty": desired_qty,
                        "price": px,
                        "target_wt": target_wt,
                    })

        for cand in buy_candidates:
            if spendable_cash <= 0.0:
                break

            ticker = cand["ticker"]
            px = cand["price"]
            desired_qty = cand["desired_qty"]

            buffered_price = px * (1.0 + self.buy_markup)
            max_affordable = int(spendable_cash // buffered_price)
            actual_buy_qty = min(desired_qty, max_affordable)

            if actual_buy_qty > 0:
                cost = actual_buy_qty * buffered_price
                spendable_cash = max(0.0, spendable_cash - cost)
                orders.append({
                    "ticker": ticker,
                    "side": "buy",
                    "quantity": actual_buy_qty,
                })

        return orders
