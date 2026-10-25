"""
Guardian Alpha — V30 Stage 2D: Independent Mathematical Sizing Oracle.

Provides an independent, high-precision mathematical reference for volatility-aware
position sizing calculations, capacity redistribution, and portfolio constraint enforcement.
Does NOT share code with experimental strategy modules.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import math
from typing import Any

EPSILON = 1e-12
DEFAULT_VOL_FLOOR = 0.05
DEFAULT_POSITION_CAP = 0.24


def compute_pure_inverse_vol_weights(
    volatilities: dict[str, float],
    budget: float,
    floor: float = DEFAULT_VOL_FLOOR,
) -> dict[str, float]:
    """
    Candidate P1 Reference: Pure Inverse-Volatility Sizing.
    raw_w_i = 1.0 / max(vol_i, floor)
    w_i = (raw_w_i / sum(raw_w)) * budget
    """
    if budget <= 0.0 or not volatilities:
        return {}

    # Validate inputs: must be finite and non-negative
    cleaned_vols: dict[str, float] = {}
    for ticker, v in sorted(volatilities.items()):
        if v is None or not math.isfinite(v) or v < 0.0:
            continue
        cleaned_vols[ticker] = max(float(v), floor)

    if not cleaned_vols:
        return {}

    raw_weights = {t: 1.0 / v for t, v in cleaned_vols.items()}
    sum_raw = sum(raw_weights.values())
    if sum_raw <= 0.0:
        return {}

    return {t: (rw / sum_raw) * budget for t, rw in raw_weights.items()}


def compute_capped_inverse_vol_weights(
    volatilities: dict[str, float],
    budget: float,
    cap: float = DEFAULT_POSITION_CAP,
    floor: float = DEFAULT_VOL_FLOOR,
) -> dict[str, float]:
    """
    Candidate P2 Reference: Capped Inverse-Volatility with Capacity Redistribution.
    Strictly enforces w_i <= cap. Excess weight from capped assets is iteratively
    redistributed to uncapped assets proportional to raw inverse volatility.
    If all available assets reach cap, remaining budget is unallocated (cash).
    """
    pure_weights = compute_pure_inverse_vol_weights(volatilities, budget, floor)
    if not pure_weights:
        return {}

    raw_inv_vols = {t: 1.0 / max(float(volatilities[t]), floor) for t in pure_weights}
    weights = dict(pure_weights)
    capped_set: set[str] = set()

    # Iterative deterministic redistribution
    max_iter = len(weights) + 2
    for _ in range(max_iter):
        # Identify newly capped assets
        newly_capped = {t for t, w in weights.items() if w > cap + EPSILON and t not in capped_set}
        if not newly_capped:
            break

        capped_set.update(newly_capped)
        for t in capped_set:
            weights[t] = cap

        uncapped = [t for t in weights if t not in capped_set]
        if not uncapped:
            # All assets capped; remainder held as cash
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

    # Final clamp to eliminate any numerical floating epsilon
    return {t: min(w, cap) for t, w in weights.items()}


def compute_smoothed_volatilities(
    current_vols: dict[str, float],
    prior_vols: dict[str, float] | None,
    alpha: float = 0.5,
) -> dict[str, float]:
    """
    Candidate P3 Reference: Volatility Smoothing across decision dates.
    smoothed_vol_i = alpha * current_vol_i + (1 - alpha) * prior_vol_i
    If prior_vol_i is missing/None, smoothed_vol_i = current_vol_i.
    """
    smoothed: dict[str, float] = {}
    prior = prior_vols or {}

    for t, cv in current_vols.items():
        if cv is None or not math.isfinite(cv) or cv < 0.0:
            continue
        pv = prior.get(t)
        if pv is None or not math.isfinite(pv) or pv < 0.0:
            smoothed[t] = cv
        else:
            smoothed[t] = (alpha * cv) + ((1.0 - alpha) * pv)

    return smoothed


def compute_blended_weights(
    equal_weights: dict[str, float],
    inv_vol_weights: dict[str, float],
    blend: float = 0.5,
) -> dict[str, float]:
    """
    Candidate P4 Reference: Convex Combination of Equal and Inverse-Volatility Weights.
    w_i = blend * equal_w_i + (1 - blend) * inv_vol_w_i
    """
    tickers = sorted(set(equal_weights.keys()) | set(inv_vol_weights.keys()))
    blended: dict[str, float] = {}
    for t in tickers:
        ew = equal_weights.get(t, 0.0)
        ivw = inv_vol_weights.get(t, 0.0)
        blended[t] = (blend * ew) + ((1.0 - blend) * ivw)
    return blended


def verify_weight_invariants(
    weights: dict[str, float],
    budget: float,
    cap: float | None = None,
) -> tuple[bool, str]:
    """
    Adversarial verification of allocation invariants:
    1. All weights non-negative.
    2. Sum of weights <= budget + EPSILON.
    3. Individual weight <= cap + EPSILON (if cap specified).
    """
    total = sum(weights.values())
    if any(w < -EPSILON for w in weights.values()):
        return False, "Negative weight detected"
    if total > budget + 1e-6:
        return False, f"Sum of weights ({total:.6f}) exceeds budget ({budget:.6f})"
    if cap is not None:
        for t, w in weights.items():
            if w > cap + 1e-6:
                return False, f"Asset {t} weight ({w:.6f}) exceeds cap ({cap:.6f})"
    return True, "Valid"
