"""
Guardian Alpha — V30 Stage 2C: Candidate C3 (Volatility-Persistence Gate).

Experiment 2C-03:
Hypothesis:
Single-session volatility spikes above the 0.28 overlay threshold frequently represent
transient noise that causes premature overlay liquidation and churn costs.
Requiring 2 consecutive sessions of adverse volatility (qqq_vol20 >= 0.28) before deactivating
the overlay reduces whipsaw and friction, while preserving immediate emergency exits if
the broader strategy triggers risk-off.

Contract:
- Entry: Requires current session to fully satisfy baseline overlay rules:
  qqq_sma20 > qqq_sma50, qqq_mom20 > 0.0, qqq_vol20 < 0.28.
- Maintenance: If overlay is currently active and trend holds, require 2 consecutive
  sessions of qqq_vol20 >= 0.28 before overlay deactivation.
- Emergency Exit: Immediate exit of overlay and transition to defensive sleeve if
  general risk-off triggers (SPY < SMA50 or QQQ < SMA50 or QQQ vol20 >= 0.35).
- Non-Volatility Trend Exit: Immediate deactivation if QQQ trend breaks (SMA20 <= SMA50 or Mom20 <= 0).
- Pure standard library + agent.py imports (zero modifications to agent.py).
"""

from __future__ import annotations

import math
from typing import Any

import agent

# Preregistered parameters
VOL20_OVERLAY_THRESHOLD = 0.28
CONFIRMATION_SESSIONS_REQUIRED = 2

_last_rebalance_bar_date: str | None = None
_last_targets: dict[str, float] = {}
_adverse_vol_count: int = 0
_overlay_active: bool = False


def reset() -> None:
    """Reset module globals for clean replay evaluation."""
    global _last_rebalance_bar_date, _last_targets, _adverse_vol_count, _overlay_active
    _last_rebalance_bar_date = None
    _last_targets = {}
    _adverse_vol_count = 0
    _overlay_active = False


def _days_since_rebalance(market_state: dict[str, list[dict[str, Any]]]) -> int | None:
    """Calculate trading days since last rebalance date."""
    if _last_rebalance_bar_date is None:
        return None
    bars = market_state.get("SPY") or market_state.get("QQQ") or []
    dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
    if not dates or _last_rebalance_bar_date not in dates:
        return None
    return len(dates) - dates.index(_last_rebalance_bar_date) - 1


def target_weights_c3(market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    """Target weights for Candidate C3 with 2-session volatility persistence confirmation."""
    global _adverse_vol_count, _overlay_active

    spy = agent.closes(market_state.get("SPY"))
    qqq = agent.closes(market_state.get("QQQ"))
    if len(spy) < 50 or len(qqq) < 50:
        _adverse_vol_count = 0
        _overlay_active = False
        return {}

    spy_sma50 = agent.sma(spy, 50)
    qqq_sma50 = agent.sma(qqq, 50)
    qqq_vol20 = agent.realized_vol(qqq, 20)
    
    # 1. Broad Risk-On Gate: If violated, trigger immediate emergency exit
    risk_on = bool(
        spy_sma50 is not None
        and qqq_sma50 is not None
        and qqq_vol20 is not None
        and spy[-1] > spy_sma50
        and qqq[-1] > qqq_sma50
        and qqq_vol20 < 0.35
    )
    if not risk_on:
        # Emergency exit: de-escalate immediately to cash / defensive assets
        _adverse_vol_count = 0
        _overlay_active = False
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
        _adverse_vol_count = 0
        _overlay_active = False
        return agent._scale_caps(agent._risk_off_targets(market_state))

    qqq_sma20 = agent.sma(qqq, 20)
    qqq_mom20 = agent.momentum(qqq, 20)
    
    # 2. Non-volatility trend conditions for overlay
    trend_ok = bool(
        qqq_sma20 is not None
        and qqq_sma50 is not None
        and qqq_mom20 is not None
        and qqq_sma20 > qqq_sma50
        and qqq_mom20 > 0.0
        and agent.closes(market_state.get("QLD"))
        and agent.closes(market_state.get("SSO"))
    )

    if not trend_ok:
        # Non-volatility breakdown: immediate exit
        _adverse_vol_count = 0
        _overlay_active = False
        overlay_on = False
    else:
        # Trend is intact: evaluate volatility persistence
        if qqq_vol20 is not None and qqq_vol20 < VOL20_OVERLAY_THRESHOLD:
            # Calm regime: active and counter cleared
            _adverse_vol_count = 0
            _overlay_active = True
            overlay_on = True
        else:
            # Adverse volatility (vol >= 0.28 or None)
            if _overlay_active:
                _adverse_vol_count += 1
                if _adverse_vol_count < CONFIRMATION_SESSIONS_REQUIRED:
                    # Session 1 of adverse volatility: maintain overlay
                    overlay_on = True
                else:
                    # Confirmed adverse volatility (2+ sessions): exit overlay
                    _overlay_active = False
                    overlay_on = False
            else:
                # Not active: do not enter during adverse volatility
                _adverse_vol_count = 0
                overlay_on = False

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
    """Return long-only buy/sell orders adhering to Candidate C3 rules."""
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

    targets = target_weights_c3(market_state)
    if not targets:
        return []

    prices = agent._market_prices(market_state)
    positions = agent.current_positions(portfolio_state)
    orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
    if orders:
        _last_rebalance_bar_date = latest_date
        _last_targets = targets
    return orders
