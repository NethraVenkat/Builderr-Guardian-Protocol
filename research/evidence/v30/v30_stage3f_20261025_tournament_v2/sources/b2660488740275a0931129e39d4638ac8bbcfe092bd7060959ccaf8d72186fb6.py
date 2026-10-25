"""
Guardian Alpha — V30 Stage 2A: Execution-Safe Agent Candidate.

Integrates the independent CashAffordabilityModel with Frozen E0 signal generation
to eliminate cash-exhaustion buy order rejections and downstream unheld-position sell rejections.

DO NOT OVERWRITE OR MUTATE agent.py.
This is a dedicated experimental research candidate residing in research/strategies/.
"""

from __future__ import annotations

from typing import Any

import agent
from research.engine.cash_affordability_model import (
    CashAffordabilityModel,
    ExecutionConfig,
    ExecutionPolicy,
)

REBALANCE_EVERY_DAYS = 5


class V30ExecutionSafeAgent:
    """Experimental Candidate: Frozen E0 signals with Conservative Cash-Affordability Execution."""

    def __init__(
        self,
        execution_config: ExecutionConfig | None = None,
        rebalance_every_days: int = REBALANCE_EVERY_DAYS,
    ) -> None:
        self.config = execution_config or ExecutionConfig(
            policy=ExecutionPolicy.SEQUENCED_HAIRCUT,
            sell_haircut=0.10,
            buy_markup=0.05,
            cash_reserve_pct=0.02,
            min_trade_pct=0.015,
        )
        self.model = CashAffordabilityModel(self.config)
        self.rebalance_every_days = rebalance_every_days
        self._last_rebalance_bar_date: str | None = None
        self._last_targets: dict[str, float] = {}

    def reset(self) -> None:
        """Reset internal state for clean replay isolation."""
        self._last_rebalance_bar_date = None
        self._last_targets = {}

    def _days_since_rebalance(self, market_state: dict[str, list[dict[str, Any]]]) -> int | None:
        if self._last_rebalance_bar_date is None:
            return None
        bars = market_state.get("SPY") or market_state.get("QQQ") or []
        dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
        if not dates or self._last_rebalance_bar_date not in dates:
            return None
        return len(dates) - dates.index(self._last_rebalance_bar_date) - 1

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        """Return conservative long-only rebalance orders."""
        if not market_state or not agent._finite_inputs(market_state, portfolio_state, cash):
            return []

        latest_date = agent._latest_bar_date(market_state)
        if latest_date is None:
            return []

        total_equity = agent.equity(portfolio_state, cash)
        days_since = self._days_since_rebalance(market_state)
        drifted = agent._has_position_drifted(portfolio_state, total_equity)

        should_rebalance = (
            self._last_rebalance_bar_date is None
            or days_since is None
            or days_since >= self.rebalance_every_days
            or drifted
        )
        if not should_rebalance:
            return []

        # Use identical Frozen E0 signal targets
        targets = agent.target_weights(market_state)
        if not targets:
            return []

        prices = agent._market_prices(market_state)
        positions = agent.current_positions(portfolio_state)

        # Generate orders using the independent CashAffordabilityModel
        orders = self.model.generate_orders(
            targets=targets,
            positions=positions,
            total_equity=total_equity,
            prices=prices,
            cash_available=cash,
        )

        if orders:
            self._last_rebalance_bar_date = latest_date
            self._last_targets = targets

        return orders


# Stateless module-level singleton instance for ReplayEngine compatibility
_default_v30_agent = V30ExecutionSafeAgent()


def decide(
    market_state: dict[str, list[dict[str, Any]]],
    portfolio_state: dict[str, Any],
    cash: float,
) -> list[dict[str, Any]]:
    """Builderr competition contract entrypoint for V30 Execution-Safe Agent."""
    return _default_v30_agent.decide(market_state, portfolio_state, cash)
