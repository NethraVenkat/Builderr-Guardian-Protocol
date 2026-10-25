"""
Guardian Alpha — V30 Stage 2C: Candidate C4 (Prespecified Combined Volatility Gates).

Experiment 2C-04:
Hypothesis:
Jointly enforcing a tightened volatility ceiling (sigma_20 < 0.22) AND an acceleration barrier
(sigma_5 / sigma_20 <= 1.25) creates an orthogonal defense against both elevated baseline volatility
and rapid volatility explosions, providing maximal drawdown suppression for leveraged exposure.

Contract:
- Leveraged Overlay Gate: Jointly requires:
  1. qqq_vol20 < 0.22 (from Candidate C1)
  2. sigma_5 / sigma_20 <= 1.25 (from Candidate C2)
  3. QQQ trend: SMA20 > SMA50 and Mom20 > 0.0
- Zero-denominator / missing-data handling: If sigma_20 <= 1e-6 or sigma_20 is None or sigma_5 is None: overlay blocked.
- Risk-On Base Sleeve: Identical to Frozen E0.
- Defensive Sleeve: Identical to Frozen E0.
- Pure standard library + agent.py imports (zero modifications to agent.py).
"""

from __future__ import annotations

import math
from typing import Any

import agent

# Preregistered parameters
QQQ_VOL20_OVERLAY_THRESHOLD_C4 = 0.22
VOL_ACCELERATION_RATIO_MAX = 1.25
ZERO_DENOMINATOR_EPSILON = 1e-6

_last_rebalance_bar_date: str | None = None
_last_targets: dict[str, float] = {}


def reset() -> None:
    """Reset module globals for clean replay evaluation."""
    global _last_rebalance_bar_date, _last_targets
    _last_rebalance_bar_date = None
    _last_targets = {}


def _days_since_rebalance(market_state: dict[str, list[dict[str, Any]]]) -> int | None:
    """Calculate trading days since last rebalance date."""
    if _last_rebalance_bar_date is None:
        return None
    bars = market_state.get("SPY") or market_state.get("QQQ") or []
    dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
    if not dates or _last_rebalance_bar_date not in dates:
        return None
    return len(dates) - dates.index(_last_rebalance_bar_date) - 1


def is_volatility_acceleration_adverse(qqq_closes: list[float]) -> bool:
    """
    Check if short-term volatility is expanding relative to medium-term volatility.
    Returns True if adverse (acceleration exceeds 1.25 or undefined), False if calm/safe.
    """
    if len(qqq_closes) < 21:
        return True

    vol5 = agent.realized_vol(qqq_closes, 5)
    vol20 = agent.realized_vol(qqq_closes, 20)

    if vol5 is None or vol20 is None or vol20 <= ZERO_DENOMINATOR_EPSILON:
        return True

    ratio = vol5 / vol20
    return ratio > VOL_ACCELERATION_RATIO_MAX


def target_weights_c4(market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    """Target weights for Candidate C4 combining tightened vol ceiling and acceleration barrier."""
    spy = agent.closes(market_state.get("SPY"))
    qqq = agent.closes(market_state.get("QQQ"))
    if len(spy) < 50 or len(qqq) < 50:
        return {}

    spy_sma50 = agent.sma(spy, 50)
    qqq_sma50 = agent.sma(qqq, 50)
    qqq_vol20 = agent.realized_vol(qqq, 20)
    risk_on = bool(
        spy_sma50 is not None
        and qqq_sma50 is not None
        and qqq_vol20 is not None
        and spy[-1] > spy_sma50
        and qqq[-1] > qqq_sma50
        and qqq_vol20 < 0.35
    )
    if not risk_on:
        return agent._scale_caps(agent._risk_off_targets(market_state))

    scored: list[tuple[float, str]] = []
    for ticker in agent.RISK_CANDIDATES:
        values = agent.closes(market_state.get(ticker))
        if len(values) < 61:
            continue
        mom60 = agent.momentum(values, 60)
        mom20 = agent.momentum(values, 20)
        trend50 = agent.sma(values, 50)
        vol20 = agent.realized_vol(values, 20)
        if mom60 is None or mom20 is None or trend50 is None or vol20 is None:
            continue
        trend_gap = values[-1] / trend50 - 1.0
        score = (0.55 * mom60) + (0.25 * mom20) + (0.20 * trend_gap) - (0.15 * vol20)
        if score > 0.0:
            scored.append((score, ticker))

    scored.sort(reverse=True)
    winners = [ticker for _, ticker in scored[:5]]
    if not winners:
        return agent._scale_caps(agent._risk_off_targets(market_state))

    qqq_sma20 = agent.sma(qqq, 20)
    qqq_mom20 = agent.momentum(qqq, 20)
    
    # C4 Gating: QQQ Trend + Tightened Vol < 0.22 + Vol Acceleration <= 1.25
    vol_accel_adverse = is_volatility_acceleration_adverse(qqq)
    overlay_on = bool(
        qqq_sma20 is not None
        and qqq_sma50 is not None
        and qqq_mom20 is not None
        and qqq_vol20 is not None
        and qqq_sma20 > qqq_sma50
        and qqq_mom20 > 0.0
        and qqq_vol20 < QQQ_VOL20_OVERLAY_THRESHOLD_C4
        and not vol_accel_adverse
        and agent.closes(market_state.get("QLD"))
        and agent.closes(market_state.get("SSO"))
    )

    weights: dict[str, float] = {}
    base_budget = 0.76 if overlay_on else 0.92
    per_winner = min(agent.MAX_WEIGHT - 0.02, base_budget / len(winners))
    for ticker in winners:
        weights[ticker] = per_winner

    if overlay_on:
        weights["QLD"] = 0.11
        weights["SSO"] = 0.07

    return agent._scale_caps(weights)


def decide(
    market_state: dict,
    portfolio_state: dict | None = None,
    cash: float | None = None,
) -> list[dict[str, Any]]:
    """Return long-only buy/sell orders adhering to Candidate C4 rules."""
    global _last_rebalance_bar_date, _last_targets

    if portfolio_state is None:
        portfolio_state = {}
    if cash is None:
        cash = float(portfolio_state.get("cash", 0.0))

    if not market_state or not agent._finite_inputs(market_state, portfolio_state, cash):
        return []

    latest_date = agent._latest_bar_date(market_state)
    if latest_date is None:
        return []

    total_equity = agent.equity(portfolio_state, cash)
    days_since = _days_since_rebalance(market_state)
    drifted = agent._has_position_drifted(portfolio_state, total_equity)
    should_rebalance = (
        _last_rebalance_bar_date is None
        or days_since is None
        or days_since >= agent.REBALANCE_EVERY_DAYS
        or drifted
    )
    if not should_rebalance:
        return []

    targets = target_weights_c4(market_state)
    if not targets:
        return []

    prices = agent._market_prices(market_state)
    positions = agent.current_positions(portfolio_state)
    orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
    if orders:
        _last_rebalance_bar_date = latest_date
        _last_targets = targets
    return orders
