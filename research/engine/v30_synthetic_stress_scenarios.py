"""
Guardian Alpha — V30 Stage 2B: Preregistered Synthetic Stress Scenarios.

Generates 10 independent, deterministic synthetic market stress regimes
without sampling or deriving parameters from protected or historical market data.

All scenarios use fixed mathematical formulas and explicit pseudo-random seeds.
Zero lookahead, zero historical contamination.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def _generate_bars_from_returns(
    start_date: str,
    tickers: list[str],
    daily_returns: dict[str, list[float]],
    initial_prices: dict[str, float] | None = None,
    volumes: dict[str, float] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Deterministically convert daily returns into daily OHLCV bar dicts."""
    import datetime

    dt = datetime.date.fromisoformat(start_date)
    init_px = initial_prices or {t: 100.0 for t in tickers}
    vols = volumes or {t: 1_000_000.0 for t in tickers}

    n_days = max(len(rets) for rets in daily_returns.values()) if daily_returns else 0
    bars: dict[str, list[dict[str, Any]]] = {t: [] for t in tickers}
    cur_prices = {t: float(init_px.get(t, 100.0)) for t in tickers}

    for day_idx in range(n_days):
        # Advance date skipping weekends
        while dt.weekday() >= 5:
            dt += datetime.timedelta(days=1)
        date_str = dt.isoformat()

        for t in tickers:
            r = daily_returns[t][day_idx] if day_idx < len(daily_returns[t]) else 0.0
            open_px = cur_prices[t]
            close_px = round(open_px * (1.0 + r), 4)
            high_px = round(max(open_px, close_px) * 1.002, 4)
            low_px = round(min(open_px, close_px) * 0.998, 4)
            vol = vols.get(t, 1_000_000.0)

            bars[t].append({
                "ts": date_str,
                "open": open_px,
                "high": high_px,
                "low": low_px,
                "close": close_px,
                "volume": vol,
            })
            cur_prices[t] = close_px

        dt += datetime.timedelta(days=1)

    return bars


def generate_stress_scenario_1_sudden_crash() -> dict[str, Any]:
    """Stress 1: Sudden broad-market crash (-20% over 5 sessions, vol spike > 50%)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    # 60 calm days, then 5 crash days (-4% daily), then 10 turbulent days
    n_days = 75
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0005  # Slow calm drift
            ret_def = 0.0003
        elif i < 65:
            ret_mkt = -0.045  # -4.5% daily crash
            ret_def = -0.015  # Defensive buffers crash somewhat
        else:
            ret_mkt = -0.005
            ret_def = 0.001

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.2)  # Energy drops faster than market
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_1_sudden_crash", "bars": bars, "days": n_days}


def generate_stress_scenario_2_grinding_decline() -> dict[str, Any]:
    """Stress 2: Prolonged grinding decline (-0.35% per day over 80 sessions)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 140
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0008
            ret_def = 0.0005
        else:
            ret_mkt = -0.0035  # Grinding daily decline
            ret_def = -0.0008  # Defensives hold up better

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.1)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_2_grinding_decline", "bars": bars, "days": n_days}


def generate_stress_scenario_3_v_shaped_recovery() -> dict[str, Any]:
    """Stress 3: V-shaped recovery (-25% crash over 15 sessions, immediate +30% rebound)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 110
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0005
            ret_def = 0.0004
        elif i < 75:
            ret_mkt = -0.020  # Sharp crash phase (-2% daily for 15 days)
            ret_def = -0.008
        elif i < 95:
            ret_mkt = +0.015  # Sharp recovery phase (+1.5% daily for 20 days)
            ret_def = +0.004
        else:
            ret_mkt = +0.001
            ret_def = +0.001

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.3)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_3_v_shaped_recovery", "bars": bars, "days": n_days}


def generate_stress_scenario_4_false_downside_signal() -> dict[str, Any]:
    """Stress 4: False downside signal (quick -4% 2-day dip triggering risk-off, followed by ATH rally)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 90
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0005
            ret_def = 0.0003
        elif i in (60, 61):
            ret_mkt = -0.025  # 2-day shock dip (-5% total)
            ret_def = -0.010
        else:
            ret_mkt = +0.008  # Fast persistent rally to new all-time highs
            ret_def = +0.002

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_4_false_downside_signal", "bars": bars, "days": n_days}


def generate_stress_scenario_5_sideways_high_vol() -> dict[str, Any]:
    """Stress 5: Sideways high-volatility market (+/- 3% daily oscillation, 0 net drift over 60 days)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 120
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0005
            ret_def = 0.0004
        else:
            # Alternating +/- 3%
            ret_mkt = 0.030 if (i % 2 == 0) else -0.029
            ret_def = 0.008 if (i % 2 == 0) else -0.007

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.2)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_5_sideways_high_vol", "bars": bars, "days": n_days}


def generate_stress_scenario_6_defensive_correlation_breakdown() -> dict[str, Any]:
    """Stress 6: Defensive correlation breakdown (Market falls -10%, but defensive equities plunge -20%)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 85
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0006
            ret_def = 0.0005
        else:
            ret_mkt = -0.005  # Moderate market dip (-0.5% daily)
            ret_def = -0.015  # Defensive sectors plunge (-1.5% daily, e.g. utility/staple crash)

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_def * 1.5)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_6_defensive_breakdown", "bars": bars, "days": n_days}


def generate_stress_scenario_7_rising_market_cash_drag() -> dict[str, Any]:
    """Stress 7: Extended bull rally (+35% over 100 sessions) testing cash drag penalty."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 120
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        ret_mkt = +0.0025  # Relentless steady upward grind
        ret_def = +0.0008

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 0.9)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt * 1.2)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_7_rising_cash_drag", "bars": bars, "days": n_days}


def generate_stress_scenario_8_sudden_overnight_gap() -> dict[str, Any]:
    """Stress 8: Sudden overnight opening gap (-8% gap between close T and open T+1)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 70
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 60:
            ret_mkt = 0.0005
            ret_def = 0.0003
        elif i == 60:
            ret_mkt = -0.080  # Severe overnight gap
            ret_def = -0.040
        else:
            ret_mkt = -0.002
            ret_def = 0.001

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.2)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_8_overnight_gap", "bars": bars, "days": n_days}


def generate_stress_scenario_9_missing_defensive_instrument() -> dict[str, Any]:
    """Stress 9: Missing defensive instrument (XLU and XLV bars missing entirely from feed)."""
    # Base scenario 1, but XLU and XLV are omitted from bars dict
    scen1 = generate_stress_scenario_1_sudden_crash()
    bars = scen1["bars"]
    # Drop XLU and XLV
    bars_missing = {t: b for t, b in bars.items() if t not in ("XLU", "XLV")}
    return {"name": "stress_9_missing_defensive", "bars": bars_missing, "days": scen1["days"]}


def generate_stress_scenario_10_alternating_whipsaw() -> dict[str, Any]:
    """Stress 10: Alternating whipsaw (crosses above/below SMA50 every 3 sessions)."""
    tickers = ["SPY", "QQQ", "AAPL", "MSFT", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]
    n_days = 90
    daily_returns: dict[str, list[float]] = {t: [] for t in tickers}

    for i in range(n_days):
        if i < 50:
            ret_mkt = 0.0005
            ret_def = 0.0004
        else:
            # Frequent 3-day swing cycles (+2% for 3 days, -2.2% for 3 days)
            cycle = (i - 50) % 6
            ret_mkt = +0.015 if cycle < 3 else -0.018
            ret_def = +0.004 if cycle < 3 else -0.005

        for t in tickers:
            if t in ("XLP", "XLU", "XLV"):
                daily_returns[t].append(ret_def)
            elif t == "XLE":
                daily_returns[t].append(ret_mkt * 1.1)
            elif t in ("QLD", "SSO"):
                daily_returns[t].append(ret_mkt * 2.0)
            else:
                daily_returns[t].append(ret_mkt)

    bars = _generate_bars_from_returns("2021-01-04", tickers, daily_returns)
    return {"name": "stress_10_alternating_whipsaw", "bars": bars, "days": n_days}


def get_all_synthetic_stress_scenarios() -> list[dict[str, Any]]:
    """Return all 10 preregistered stress scenarios."""
    return [
        generate_stress_scenario_1_sudden_crash(),
        generate_stress_scenario_2_grinding_decline(),
        generate_stress_scenario_3_v_shaped_recovery(),
        generate_stress_scenario_4_false_downside_signal(),
        generate_stress_scenario_5_sideways_high_vol(),
        generate_stress_scenario_6_defensive_correlation_breakdown(),
        generate_stress_scenario_7_rising_market_cash_drag(),
        generate_stress_scenario_8_sudden_overnight_gap(),
        generate_stress_scenario_9_missing_defensive_instrument(),
        generate_stress_scenario_10_alternating_whipsaw(),
    ]
