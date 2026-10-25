"""
Guardian Alpha — V30 Stage 2A: Cash-Affordability and Order-Execution Model.

Independent reference implementation of conservative cash-availability, buying-power,
and rebalance order generation rules to prevent simultaneous-order cash-exhaustion,
order rejections, and cascading unheld-position failures under slippage and broker frictions.

Design Invariants:
1. Long-Only: Never generates short sales or negative share quantities.
2. Conservative Buying Power: Never commits more cash than independently verified available.
3. Execution Policy Support:
   - STRICT_SETTLED_CASH: Simultaneous submission / cash account. Buys funded strictly
     by settled cash minus safety reserve. Zero credit for pending sells.
   - SEQUENCED_HAIRCUT: Sells execute before buys with conservative haircuts on sell proceeds
     and buy execution markups.
4. Non-Destructive: Isolated experimental implementation. Frozen agent.py remains untouched.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Any


class ExecutionPolicy(enum.Enum):
    """Execution policy governing cash-availability assumptions."""
    STRICT_SETTLED_CASH = "strict_settled_cash"      # Zero credit for pending sells (simultaneous submission)
    SEQUENCED_HAIRCUT = "sequenced_haircut"          # Sells first with adverse slippage haircuts
    TWO_STAGE_COMMIT = "two_stage_commit"            # Sells executed first, buys staged upon fill confirmation


@dataclass(frozen=True)
class ExecutionConfig:
    """Configuration parameters for cash affordability and order sizing."""
    policy: ExecutionPolicy = ExecutionPolicy.SEQUENCED_HAIRCUT
    sell_haircut: float = 0.10          # 10% haircut on estimated sell proceeds (covers down-gap + slippage)
    buy_markup: float = 0.05            # 5% markup on buy price (covers up-gap + slippage)
    cash_reserve_pct: float = 0.02      # 2% of total equity held as unspendable cash reserve floor
    min_trade_pct: float = 0.015        # 1.5% equity deadband
    commission_bps: float = 0.0         # Brokerage commission in basis points
    max_orders_per_session: int = 45    # Maximum permitted orders per rebalance session


class CashAffordabilityModel:
    """Independent reference model for cash-affordability and buying power."""

    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def compute_available_buying_power(
        self,
        settled_cash: float,
        estimated_sell_proceeds: float,
        total_equity: float,
        committed_buys_notional: float = 0.0,
    ) -> float:
        """
        Compute auditable Available Buying Power (ABP) at order-generation time.

        Formula:
          ABP = max(0.0, C_settled + Credit(sells) - Committed(buys) - C_reserve)
        """
        cash_base = max(float(settled_cash), 0.0)
        reserve_floor = max(total_equity * self.config.cash_reserve_pct, 0.0)

        if self.config.policy == ExecutionPolicy.STRICT_SETTLED_CASH:
            # Under simultaneous submission, pending sell proceeds cannot be spent
            credit_sells = 0.0
        elif self.config.policy == ExecutionPolicy.SEQUENCED_HAIRCUT:
            # Haircut estimated proceeds to absorb negative slippage and price gaps
            haircut_rate = min(max(self.config.sell_haircut, 0.0), 0.50)
            credit_sells = max(estimated_sell_proceeds, 0.0) * (1.0 - haircut_rate)
        elif self.config.policy == ExecutionPolicy.TWO_STAGE_COMMIT:
            # Sells must be confirmed; if unconfirmed at pre-trade, credit is zero
            credit_sells = 0.0
        else:
            credit_sells = 0.0

        available = cash_base + credit_sells - committed_buys_notional - reserve_floor
        return max(available, 0.0)

    def generate_orders(
        self,
        targets: dict[str, float],
        positions: dict[str, dict[str, float]],
        total_equity: float,
        prices: dict[str, float],
        cash_available: float,
    ) -> list[dict[str, Any]]:
        """
        Generate conservative rebalance orders ensuring zero cash exhaustion.

        Guarantees:
        - Sells strictly bounded by current integer positions (no short sales).
        - Buys sized using independently verified available buying power.
        - Buy prices marked up by buy_markup to buffer against adverse execution slippage.
        - Minimum cash reserve floor preserved at all times.
        """
        if total_equity <= 0.0:
            return []

        min_trade = total_equity * self.config.min_trade_pct
        orders: list[dict[str, Any]] = []
        sell_proceeds = 0.0

        # Phase 1: Sells first (remove stale holdings, trim overweight target holdings)
        for ticker, pos in positions.items():
            price = prices.get(ticker)
            if price is None or price <= 0.0 or not math.isfinite(price):
                continue
            qty = pos.get("quantity", 0.0)
            if qty <= 0.0:
                continue

            current_value = qty * price
            target_value = total_equity * targets.get(ticker, 0.0)
            delta = target_value - current_value

            if ticker not in targets:
                # Full liquidation
                sell_qty = int(qty)
                if sell_qty > 0 and current_value >= min_trade:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    sell_proceeds += sell_qty * price
            elif delta < -min_trade:
                # Partial trimming
                sell_qty = min(int(abs(delta) // price), int(qty))
                if sell_qty > 0:
                    orders.append({"ticker": ticker, "side": "sell", "quantity": sell_qty})
                    sell_proceeds += sell_qty * price

        # Phase 2: Compute Available Buying Power (ABP)
        committed_buys = 0.0
        comm_mult = 1.0 + (self.config.commission_bps / 10000.0)
        buy_slip_mult = 1.0 + self.config.buy_markup

        # Sort targets alphabetically for deterministic reproducibility
        for ticker, weight in sorted(targets.items()):
            price = prices.get(ticker)
            if price is None or price <= 0.0 or not math.isfinite(price):
                continue

            current_qty = positions.get(ticker, {}).get("quantity", 0.0)
            current_value = current_qty * price
            target_value = total_equity * weight
            delta = target_value - current_value

            if delta < min_trade:
                continue

            abp = self.compute_available_buying_power(
                settled_cash=cash_available,
                estimated_sell_proceeds=sell_proceeds,
                total_equity=total_equity,
                committed_buys_notional=committed_buys,
            )

            if abp <= 0.0:
                continue

            # Effective cost per share including buy price markup and commission
            effective_share_cost = price * buy_slip_mult * comm_mult
            if effective_share_cost <= 0.0:
                continue

            # Target notional bounded by available buying power
            desired_notional = min(delta, abp)
            buy_qty = int(desired_notional // effective_share_cost)

            if buy_qty > 0:
                orders.append({"ticker": ticker, "side": "buy", "quantity": buy_qty})
                committed_buys += buy_qty * effective_share_cost

        return orders[: self.config.max_orders_per_session]
