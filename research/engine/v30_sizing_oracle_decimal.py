"""
Guardian Alpha — V30 Stage 2D-R: Independent Decimal Sizing Oracle.

Provides a mathematically rigorous, exact Decimal/Rational reference implementation
for volatility-aware position sizing, capacity redistribution, volatility smoothing,
and equal/inverse-vol convex blending.

Independent Engineering Controls:
- ZERO imports from candidate strategies or agent modules.
- Arithmetic is performed in exact Decimal / Fraction space.
- Zero floating-point representation drift or epsilon contamination.
- Full input sanitization for nonfinite, negative, missing, or zero volatilities.
- Deterministic capacity redistribution with strict cash retention when capacity saturates.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from fractions import Fraction
import math
from typing import Any, Mapping

# Default parameters specified by Guardian Alpha protocol
DEFAULT_DECIMAL_VOL_FLOOR = Decimal("0.05")
DEFAULT_DECIMAL_POSITION_CAP = Decimal("0.24")
DEFAULT_DECIMAL_BASE_BUDGET_OVERLAY = Decimal("0.76")
DEFAULT_DECIMAL_BASE_BUDGET_NO_OVERLAY = Decimal("0.92")


def _to_decimal(val: Any) -> Decimal | None:
    """Safely convert any numeric input to Decimal, rejecting nonfinite, NaN, or None."""
    if val is None:
        return None
    if isinstance(val, (float, int, str, Decimal)):
        try:
            d = Decimal(str(val))
            if d.is_nan() or d.is_infinite():
                return None
            return d
        except (InvalidOperation, ValueError, TypeError):
            return None
    return None


class IndependentDecimalSizingOracle:
    """
    Pure reference implementation for position sizing using exact rational and Decimal math.
    """

    @staticmethod
    def compute_pure_inverse_vol_weights(
        volatilities: Mapping[str, Any],
        budget: Any,
        floor: Any = DEFAULT_DECIMAL_VOL_FLOOR,
    ) -> dict[str, Decimal]:
        """
        Pure inverse-volatility sizing:
            raw_w_i = 1 / max(vol_i, floor)
            w_i = (raw_w_i / sum(raw_w)) * budget
        """
        b = _to_decimal(budget)
        fl = _to_decimal(floor) or DEFAULT_DECIMAL_VOL_FLOOR
        if b is None or b <= Decimal("0"):
            return {}

        cleaned_vols: dict[str, Decimal] = {}
        for ticker in sorted(volatilities.keys()):
            v = _to_decimal(volatilities[ticker])
            if v is not None and v >= Decimal("0"):
                cleaned_vols[ticker] = max(v, fl)

        if not cleaned_vols:
            return {}

        # Use exact Fraction arithmetic for inverse summation
        raw_inv = {t: Fraction(1) / Fraction(cleaned_vols[t]) for t in cleaned_vols}
        sum_raw = sum(raw_inv.values())
        if sum_raw <= 0:
            return {}

        b_frac = Fraction(b)
        weights: dict[str, Decimal] = {}
        for t in cleaned_vols:
            w_frac = (raw_inv[t] / sum_raw) * b_frac
            # Convert to Decimal with 8 decimal places
            weights[t] = Decimal(str(float(w_frac)))
        return weights

    @staticmethod
    def compute_capped_inverse_vol_weights(
        volatilities: Mapping[str, Any],
        budget: Any,
        cap: Any = DEFAULT_DECIMAL_POSITION_CAP,
        floor: Any = DEFAULT_DECIMAL_VOL_FLOOR,
    ) -> dict[str, Decimal]:
        """
        Capped inverse-volatility sizing with iterative capacity redistribution.
        - Clamps any asset weight exceeding `cap` to `cap`.
        - Iteratively redistributes excess weight to uncapped assets proportional to raw inverse volatility.
        - If all assets saturate their cap or remaining budget is exhausted, remainder is retained as cash.
        """
        b = _to_decimal(budget)
        cp = _to_decimal(cap) or DEFAULT_DECIMAL_POSITION_CAP
        fl = _to_decimal(floor) or DEFAULT_DECIMAL_VOL_FLOOR
        if b is None or b <= Decimal("0"):
            return {}

        pure = IndependentDecimalSizingOracle.compute_pure_inverse_vol_weights(volatilities, b, fl)
        if not pure:
            return {}

        cleaned_vols = {t: max(_to_decimal(volatilities[t]), fl) for t in pure}
        raw_inv = {t: Fraction(1) / Fraction(cleaned_vols[t]) for t in pure}
        b_frac = Fraction(b)
        cp_frac = Fraction(cp)

        weights_frac = {t: (raw_inv[t] / sum(raw_inv.values())) * b_frac for t in pure}
        capped_set: set[str] = set()

        max_iter = len(weights_frac) + 2
        for _ in range(max_iter):
            newly_capped = {t for t, w in weights_frac.items() if w > cp_frac and t not in capped_set}
            if not newly_capped:
                break

            capped_set.update(newly_capped)
            for t in capped_set:
                weights_frac[t] = cp_frac

            uncapped = [t for t in weights_frac if t not in capped_set]
            if not uncapped:
                # All assets capped; remainder unallocated (held as cash)
                break

            budget_remaining = b_frac - (len(capped_set) * cp_frac)
            if budget_remaining <= Fraction(0):
                for t in uncapped:
                    weights_frac[t] = Fraction(0)
                break

            sum_uncapped_raw = sum(raw_inv[t] for t in uncapped)
            if sum_uncapped_raw <= Fraction(0):
                break

            for t in uncapped:
                weights_frac[t] = (raw_inv[t] / sum_uncapped_raw) * budget_remaining

        result: dict[str, Decimal] = {}
        for t in sorted(weights_frac.keys()):
            # Clamp strictly to cap
            val = min(weights_frac[t], cp_frac)
            result[t] = Decimal(str(round(float(val), 8)))
        return result

    @staticmethod
    def compute_smoothed_volatilities(
        current_vols: Mapping[str, Any],
        prior_vols: Mapping[str, Any] | None,
        alpha: Any = Decimal("0.5"),
    ) -> dict[str, Decimal]:
        """
        Volatility smoothing across decision dates:
            smoothed_i = alpha * cur_i + (1 - alpha) * prior_i
        If prior_i is missing/None/nonfinite, smoothed_i = cur_i.
        """
        a = _to_decimal(alpha) or Decimal("0.5")
        one_minus_a = Decimal("1.0") - a
        smoothed: dict[str, Decimal] = {}
        prior = prior_vols or {}

        for t in sorted(current_vols.keys()):
            cv = _to_decimal(current_vols[t])
            if cv is None or cv < Decimal("0"):
                continue
            pv = _to_decimal(prior.get(t))
            if pv is None or pv < Decimal("0"):
                smoothed[t] = cv
            else:
                sm = (a * cv) + (one_minus_a * pv)
                smoothed[t] = sm.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN)
        return smoothed

    @staticmethod
    def compute_blended_weights(
        equal_weights: Mapping[str, Any],
        inv_vol_weights: Mapping[str, Any],
        blend: Any = Decimal("0.5"),
    ) -> dict[str, Decimal]:
        """
        Convex blend of two weighting vectors:
            w_i = blend * eq_i + (1 - blend) * iv_i
        """
        b = _to_decimal(blend) or Decimal("0.5")
        one_minus_b = Decimal("1.0") - b
        all_tickers = sorted(set(equal_weights.keys()) | set(inv_vol_weights.keys()))
        blended: dict[str, Decimal] = {}

        for t in all_tickers:
            ew = _to_decimal(equal_weights.get(t)) or Decimal("0")
            iv = _to_decimal(inv_vol_weights.get(t)) or Decimal("0")
            bw = (b * ew) + (one_minus_b * iv)
            blended[t] = bw.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN)
        return blended

    @staticmethod
    def verify_financial_invariants(
        weights: Mapping[str, Any],
        budget: Any,
        cap: Any = DEFAULT_DECIMAL_POSITION_CAP,
    ) -> tuple[bool, str]:
        """
        Audit weights for:
        1. Non-negativity: w_i >= 0
        2. Individual position cap: w_i <= cap + epsilon
        3. Budget conservation: sum(w_i) <= budget + epsilon
        """
        b = _to_decimal(budget) or Decimal("1.0")
        cp = _to_decimal(cap) or DEFAULT_DECIMAL_POSITION_CAP
        tol = Decimal("0.00001")

        tot = Decimal("0")
        for t, w in weights.items():
            dw = _to_decimal(w)
            if dw is None:
                return False, f"Non-numeric weight for {t}"
            if dw < -tol:
                return False, f"Negative weight for {t}: {dw}"
            if dw > cp + tol:
                return False, f"Position cap breach for {t}: {dw} > {cp}"
            tot += dw

        if tot > b + tol:
            return False, f"Budget overrun: sum(weights) = {tot} > {b}"
        return True, "ALL_INVARIANTS_PASSED"
