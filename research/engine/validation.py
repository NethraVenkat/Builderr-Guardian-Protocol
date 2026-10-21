"""Strict Market Data Validation Layer.

Enforces legitimate calendar dates, strict chronological monotonicity,
finite positive OHLC values, geometric price boundary integrity,
nonnegative volume, duplicate exclusion, and point-in-time future bar rejection.
"""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any


class ValidationError(ValueError):
    """Raised when market data fails structural, physical or temporal invariants."""


def validate_calendar_date(ts_val: Any, reject_weekends: bool = False) -> str:
    """Validate and normalize an ISO date string to YYYY-MM-DD.

    Rejects invalid calendar dates (e.g. 2026-02-30, 2026-13-45) and optionally
    rejects weekend dates (Saturday/Sunday).
    """
    if ts_val is None:
        raise ValidationError("Timestamp cannot be None")
    s = str(ts_val).strip()
    if len(s) < 10:
        raise ValidationError(f"Timestamp too short to represent YYYY-MM-DD: {ts_val!r}")
    date_part = s[:10]
    try:
        dt = date.fromisoformat(date_part)
    except ValueError as e:
        raise ValidationError(f"Invalid calendar date {date_part!r}: {e}") from e

    # Year must be reasonable (1970 to 2050 for current financial context)
    if not (1970 <= dt.year <= 2050):
        raise ValidationError(f"Calendar year {dt.year} outside valid epoch range [1970, 2050]")

    if reject_weekends and dt.weekday() >= 5:
        day_name = "Saturday" if dt.weekday() == 5 else "Sunday"
        raise ValidationError(f"Date {date_part} falls on a weekend ({day_name})")

    return date_part


def validate_bar(bar: dict[str, Any], ticker: str | None = None) -> dict[str, Any]:
    """Validate a single OHLCV bar dictionary.

    Invariants enforced:
      1. Required fields: ts, open, high, low, close, volume.
      2. Valid calendar date for ts.
      3. Finite, strictly positive prices: open, high, low, close > 0.
      4. Geometric bounds: low <= open <= high, low <= close <= high, low <= high.
      5. Finite, non-negative volume: volume >= 0.
    """
    sym_tag = f"[{ticker}] " if ticker else ""
    if not isinstance(bar, dict):
        raise ValidationError(f"{sym_tag}Bar must be a dictionary, got {type(bar).__name__}")

    for field in ("ts", "open", "high", "low", "close"):
        if field not in bar:
            raise ValidationError(f"{sym_tag}Missing required bar field: {field!r}")

    ts = validate_calendar_date(bar["ts"])

    try:
        o = float(bar["open"])
        h = float(bar["high"])
        l = float(bar["low"])
        c = float(bar["close"])
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{sym_tag}Non-numeric price field on {ts}: {e}") from e

    for name, val in (("open", o), ("high", h), ("low", l), ("close", c)):
        if not math.isfinite(val):
            raise ValidationError(f"{sym_tag}Price {name} on {ts} is non-finite: {val}")
        if val <= 0.0:
            raise ValidationError(f"{sym_tag}Price {name} on {ts} is non-positive: {val}")

    if l > h:
        raise ValidationError(f"{sym_tag}Price low ({l}) > high ({h}) on {ts}")
    if o < l or o > h:
        raise ValidationError(f"{sym_tag}Open ({o}) outside [low={l}, high={h}] on {ts}")
    if c < l or c > h:
        raise ValidationError(f"{sym_tag}Close ({c}) outside [low={l}, high={h}] on {ts}")

    vol_raw = bar.get("volume", 0)
    try:
        v = float(vol_raw)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{sym_tag}Non-numeric volume on {ts}: {vol_raw!r}") from e

    if not math.isfinite(v):
        raise ValidationError(f"{sym_tag}Volume on {ts} is non-finite: {v}")
    if v < 0.0:
        raise ValidationError(f"{sym_tag}Volume on {ts} is negative: {v}")

    return {
        "ts": ts,
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": int(v) if v.is_integer() else v,
    }


def validate_series(
    bars: list[dict[str, Any]],
    ticker: str | None = None,
    asof_date: str | None = None,
    strict_future_rejection: bool = True,
) -> list[dict[str, Any]]:
    """Validate a chronological series of OHLCV bars.

    Invariants enforced:
      1. Every bar passes validate_bar.
      2. Strictly increasing timestamps: ts_i < ts_{i+1} (no duplicates, no reversals).
      3. If asof_date is provided and strict_future_rejection is True, any bar with
         ts > asof_date raises ValidationError immediately.
      4. If asof_date is provided and strict_future_rejection is False, future bars
         are excluded from the output.
    """
    sym_tag = f"[{ticker}] " if ticker else ""
    if not isinstance(bars, (list, tuple)):
        raise ValidationError(f"{sym_tag}Bars series must be a list or tuple, got {type(bars).__name__}")

    if asof_date is not None:
        asof_date = validate_calendar_date(asof_date)

    validated: list[dict[str, Any]] = []
    last_date: str | None = None

    for idx, raw_bar in enumerate(bars):
        clean_bar = validate_bar(raw_bar, ticker=ticker)
        cur_date = clean_bar["ts"]

        if last_date is not None:
            if cur_date == last_date:
                raise ValidationError(f"{sym_tag}Duplicate timestamp detected at index {idx}: {cur_date}")
            if cur_date < last_date:
                raise ValidationError(
                    f"{sym_tag}Non-monotonic chronological ordering at index {idx}: {cur_date} < {last_date}"
                )

        if asof_date is not None and cur_date > asof_date:
            if strict_future_rejection:
                raise ValidationError(
                    f"{sym_tag}Future timestamp violation: bar date {cur_date} > asof decision cutoff {asof_date}"
                )
            # If not strict rejection, stop appending future bars
            break

        validated.append(clean_bar)
        last_date = cur_date

    return validated


def validate_market_state(
    market_state: dict[str, list[dict[str, Any]]],
    asof_date: str | None = None,
    strict_future_rejection: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Validate an entire market_state mapping of ticker -> bars."""
    if not isinstance(market_state, dict):
        raise ValidationError(f"market_state must be a dict, got {type(market_state).__name__}")

    clean_state: dict[str, list[dict[str, Any]]] = {}
    for ticker, bars in market_state.items():
        sym = str(ticker).strip().upper()
        clean_state[sym] = validate_series(
            bars or [],
            ticker=sym,
            asof_date=asof_date,
            strict_future_rejection=strict_future_rejection,
        )
    return clean_state
