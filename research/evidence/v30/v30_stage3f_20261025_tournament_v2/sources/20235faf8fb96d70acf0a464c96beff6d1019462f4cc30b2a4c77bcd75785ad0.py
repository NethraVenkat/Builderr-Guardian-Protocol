"""
Guardian Alpha — V30 Stage 2D: Candidate P3 (Smoothed Inverse-Volatility Sizing).

Experiment 2D-P3:
Hypothesis:
Smoothing trailing volatility across consecutive eligible decision dates:
smoothed_vol_i = 0.5 * vol20_i(current) + 0.5 * vol20_i(prior)
dampens short-term volatility estimation noise, reducing sizing turnover and
preventing erratic weight adjustments between rebalance cycles.

Contract:
- Risk-On Asset Selection: 100% identical to Frozen E0 (top 5 ranked momentum winners).
- Weighting: Capped inverse smoothed-volatility with capacity redistribution.
- Smoothing: 50% current decision date vol, 50% prior eligible decision date vol (or 100% current if prior missing).
- Position Cap: Strict MAX_WEIGHT = 0.25.
- Base Budget: 0.76 if leveraged overlay active (QLD 0.11, SSO 0.07), else 0.92.
- Defensive Sleeve: 100% identical to Frozen E0.
- Pure standard library + agent.py imports (zero modifications to agent.py).
"""

from __future__ import annotations

import math
from typing import Any

import agent

VOL_FLOOR_P3 = 0.05
MAX_POSITION_CAP_P3 = agent.MAX_WEIGHT  # 0.25
SMOOTHING_ALPHA = 0.5

_last_rebalance_bar_date: str | None = None
_last_targets: dict[str, float] = {}
_prior_decision_vols: dict[str, float] = {}


def reset() -> None:
    """Reset module globals for clean replay evaluation."""
    global _last_rebalance_bar_date, _last_targets, _prior_decision_vols
    _last_rebalance_bar_date = None
    _last_targets = {}
    _prior_decision_vols = {}


def _days_since_rebalance(market_state: dict[str, list[dict[str, Any]]]) -> int | None:
    """Calculate trading days since last rebalance date."""
    if _last_rebalance_bar_date is None:
        return None
    bars = market_state.get("SPY") or market_state.get("QQQ") or []
    dates = [str(b.get("ts", i))[:10] for i, b in enumerate(bars)]
    if not dates or _last_rebalance_bar_date not in dates:
        return None
    return len(dates) - dates.index(_last_rebalance_bar_date) - 1


def _distribute_capped_inverse_vol(
    vols: dict[str, float],
    budget: float,
    cap: float = MAX_POSITION_CAP_P3,
    floor: float = VOL_FLOOR_P3,
) -> dict[str, float]:
    """Iteratively distribute budget with per-position cap and proportional redistribution."""
    if budget <= 0.0 or not vols:
        return {}

    raw_inv_vols = {t: 1.0 / max(vols[t], floor) for t in vols}
    sum_raw = sum(raw_inv_vols.values())
    if sum_raw <= 0.0:
        return {}

    weights = {t: (raw_inv_vols[t] / sum_raw) * budget for t in vols}
    capped_set: set[str] = set()

    max_iter = len(weights) + 2
    for _ in range(max_iter):
        newly_capped = {t for t, w in weights.items() if w > cap + 1e-12 and t not in capped_set}
        if not newly_capped:
            break

        capped_set.update(newly_capped)
        for t in capped_set:
            weights[t] = cap

        uncapped = [t for t in weights if t not in capped_set]
        if not uncapped:
            break

        budget_remaining = budget - (len(capped_set) * cap)
        if budget_remaining <= 0.0:
            for t in uncapped:
                weights[t] = 0.0
            break

        sum_uncapped_raw = sum(raw_inv_vols[t] for t in uncapped)
        if sum_uncapped_raw <= 0.0:
            break

        for t in uncapped:
            weights[t] = (raw_inv_vols[t] / sum_uncapped_raw) * budget_remaining

    return {t: min(w, cap) for t, w in weights.items()}


def target_weights_p3(market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    """Target weights for Candidate P3 with smoothed inverse-volatility weighting."""
    global _prior_decision_vols

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
    vols: dict[str, float] = {}
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
            vols[ticker] = vol20

    scored.sort(reverse=True)
    winners = [ticker for _, ticker in scored[:5]]
    if not winners:
        return agent._scale_caps(agent._risk_off_targets(market_state))

    qqq_sma20 = agent.sma(qqq, 20)
    qqq_mom20 = agent.momentum(qqq, 20)
    overlay_on = bool(
        qqq_sma20 is not None
        and qqq_sma50 is not None
        and qqq_mom20 is not None
        and qqq_sma20 > qqq_sma50
        and qqq_mom20 > 0.0
        and qqq_vol20 < 0.28
        and agent.closes(market_state.get("QLD"))
        and agent.closes(market_state.get("SSO"))
    )

    base_budget = 0.76 if overlay_on else 0.92

    # P3: Compute smoothed volatility
    smoothed_vols: dict[str, float] = {}
    for t in winners:
        cv = vols[t]
        pv = _prior_decision_vols.get(t)
        if pv is None or not math.isfinite(pv):
            sv = cv
        else:
            sv = (SMOOTHING_ALPHA * cv) + ((1.0 - SMOOTHING_ALPHA) * pv)
        smoothed_vols[t] = sv
        # Cache for next decision date
        _prior_decision_vols[t] = cv

    weights = _distribute_capped_inverse_vol(smoothed_vols, base_budget, MAX_POSITION_CAP_P3, VOL_FLOOR_P3)

    if overlay_on:
        weights["QLD"] = 0.11
        weights["SSO"] = 0.07

    return agent._scale_caps(weights)


def decide(
    market_state: dict,
    portfolio_state: dict | None = None,
    cash: float | None = None,
) -> list[dict[str, Any]]:
    """Return long-only buy/sell orders adhering to Candidate P3 rules."""
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

    targets = target_weights_p3(market_state)
    if not targets:
        return []

    prices = agent._market_prices(market_state)
    positions = agent.current_positions(portfolio_state)
    orders = agent.orders_to_rebalance(targets, positions, total_equity, prices, cash)
    if orders:
        _last_rebalance_bar_date = latest_date
        _last_targets = targets
    return orders
