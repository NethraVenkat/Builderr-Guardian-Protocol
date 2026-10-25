"""
Guardian Alpha — V30 Stage 2B: Candidate D3 (Recovery and Re-Entry Discipline).

Experiment 2B-03:
Hypothesis:
A deterministic, causal two-stage re-entry protocol reduces cash drag following sharp market
recoveries without premature exposure to false rallies or bull traps.

Contract & Mechanics:
- Base Defensive Sleeve (Stage 0): 50% cash, XLP 0.18, XLU 0.18, XLV 0.14.
- Stage 1 (Recovery Confirmation Filter):
    * Triggered if and only if ALL causal conditions hold:
      1. SPY 5-day return > 0.0 (short-term positive momentum)
      2. SPY close > 10-day SMA (stabilization above short-term trend)
      3. QQQ 5-day return > 0.0 (broad tech market participation)
      4. QQQ 20-day realized volatility < 0.32 (volatility normalization)
    * Allocation: 40% top 2 momentum winners, 30% defensive anchors (XLP 0.15, XLV 0.15), 30% cash.
- Stage 2 (Full Risk-On):
    * Standard E0 rules: SPY > SMA50, QQQ > SMA50, QQQ Vol < 0.35.
- Reset Rule:
    * If SPY closes below its rolling 5-day low, Stage 1 is immediately cancelled,
      resetting fully to Stage 0 (50% cash defense).
- Pure standard library + agent.py imports (zero modifications to agent.py).
"""

from __future__ import annotations

import math
from typing import Any

import agent

DEFENSIVE_WEIGHTS_D3_BASE = (
    ("XLP", 0.18),
    ("XLU", 0.18),
    ("XLV", 0.14),
)

_last_rebalance_bar_date: str | None = None
_last_targets: dict[str, float] = {}
_recovery_stage: int = 0  # 0: deep defensive, 1: recovery transition, 2: full risk-on


def reset() -> None:
    """Reset module globals for clean replay evaluation."""
    global _last_rebalance_bar_date, _last_targets, _recovery_stage
    _last_rebalance_bar_date = None
    _last_targets = {}
    _recovery_stage = 0


def _days_since_rebalance(market_state: dict[str, list[dict[str, Any]]]) -> int | None:
    """Calculate trading days since last rebalance date."""
    if _last_rebalance_bar_date is None:
        return None
    bars = market_state.get("SPY") or market_state.get("QQQ") or []
    dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
    if not dates or _last_rebalance_bar_date not in dates:
        return None
    return len(dates) - dates.index(_last_rebalance_bar_date) - 1


def _is_recovery_confirmed(spy: list[float], qqq: list[float]) -> bool:
    """Causal check for initial recovery confirmation."""
    if len(spy) < 15 or len(qqq) < 25:
        return False

    spy_sma10 = agent.sma(spy, 10)
    qqq_vol20 = agent.realized_vol(qqq, 20)
    if spy_sma10 is None or qqq_vol20 is None:
        return False

    # 1. SPY 5-day return > 0
    spy_ret5 = (spy[-1] / spy[-6]) - 1.0 if len(spy) >= 6 else 0.0
    # 2. QQQ 5-day return > 0
    qqq_ret5 = (qqq[-1] / qqq[-6]) - 1.0 if len(qqq) >= 6 else 0.0

    return (
        spy[-1] > spy_sma10
        and spy_ret5 > 0.0
        and qqq_ret5 > 0.0
        and qqq_vol20 < 0.32
    )


def _is_recovery_reset(spy: list[float]) -> bool:
    """Reset check: if SPY breaks below prior 5-day low, recovery failed."""
    if len(spy) < 6:
        return False
    prior_5d_low = min(spy[-6:-1])
    return spy[-1] < prior_5d_low


def target_weights_d3(market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    """Target weights for Candidate D3."""
    global _recovery_stage
    spy = agent.closes(market_state.get("SPY"))
    qqq = agent.closes(market_state.get("QQQ"))
    if len(spy) < 50 or len(qqq) < 50:
        return {}

    spy_sma50 = agent.sma(spy, 50)
    qqq_sma50 = agent.sma(qqq, 50)
    qqq_vol20 = agent.realized_vol(qqq, 20)

    # 1. Check Full Risk-On (Stage 2)
    full_risk_on = bool(
        spy_sma50 is not None
        and qqq_sma50 is not None
        and qqq_vol20 is not None
        and spy[-1] > spy_sma50
        and qqq[-1] > qqq_sma50
        and qqq_vol20 < 0.35
    )

    if full_risk_on:
        _recovery_stage = 2
        return agent.target_weights(market_state)

    # 2. Check Recovery Reset Condition
    if _recovery_stage == 1 and _is_recovery_reset(spy):
        _recovery_stage = 0

    # 3. Check Recovery Confirmation (Stage 1)
    if _is_recovery_confirmed(spy, qqq):
        _recovery_stage = 1
        # Generate Staged Transition Portfolio:
        # 40% top 2 momentum winners + 30% defensive staples/health + 30% cash
        scored: list[tuple[float, str]] = []
        for ticker in agent.RISK_CANDIDATES:
            vals = agent.closes(market_state.get(ticker))
            if len(vals) < 61:
                continue
            m60 = agent.momentum(vals, 60)
            m20 = agent.momentum(vals, 20)
            tr50 = agent.sma(vals, 50)
            v20 = agent.realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None:
                continue
            tg = vals[-1] / tr50 - 1.0
            sc = (0.55 * m60) + (0.25 * m20) + (0.20 * tg) - (0.15 * v20)
            if sc > 0.0:
                scored.append((sc, ticker))

        scored.sort(reverse=True)
        top2 = [t for _, t in scored[:2]]
        weights: dict[str, float] = {}
        for t in top2:
            weights[t] = 0.20  # 20% each = 40% total
        if agent.closes(market_state.get("XLP")):
            weights["XLP"] = 0.15
        if agent.closes(market_state.get("XLV")):
            weights["XLV"] = 0.15
        return agent._scale_caps(weights)

    # 4. Default: Deep Defensive Risk-Off (Stage 0)
    _recovery_stage = 0
    return agent._scale_caps({
        ticker: weight for ticker, weight in DEFENSIVE_WEIGHTS_D3_BASE
        if agent.closes(market_state.get(ticker))
    })


def decide(
    market_state: dict[str, list[dict[str, Any]]],
    portfolio_state: dict[str, Any],
    cash: float,
) -> list[dict[str, Any]]:
    """Builderr competition contract entrypoint for Candidate D3."""
    global _last_rebalance_bar_date, _last_targets
    if not market_state or not agent._finite_inputs(market_state, portfolio_state, cash):
        return []

    latest_date = agent._latest_bar_date(market_state)
    if latest_date is None:
        return []

    tot_equity = agent.equity(portfolio_state, cash)
    if tot_equity <= 0 or not math.isfinite(tot_equity):
        return []

    days_since = _days_since_rebalance(market_state)
    drifted = agent._has_position_drifted(portfolio_state, tot_equity)
    should_rebalance = (
        _last_rebalance_bar_date is None
        or days_since is None
        or days_since >= agent.REBALANCE_EVERY_DAYS
        or drifted
    )
    if not should_rebalance:
        return []

    targets = target_weights_d3(market_state)
    if not targets:
        return []

    prices = agent._market_prices(market_state)
    positions = agent.current_positions(portfolio_state)
    orders = agent.orders_to_rebalance(targets, positions, tot_equity, prices, cash)

    if orders:
        _last_rebalance_bar_date = latest_date
        _last_targets = targets

    return orders
