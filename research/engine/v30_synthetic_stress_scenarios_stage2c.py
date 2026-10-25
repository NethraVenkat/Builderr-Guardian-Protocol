"""
Guardian Alpha — V30 Stage 2C: Synthetic Stress Scenarios for Volatility Gates.

Generates 12 independent, deterministic synthetic market stress regimes
without sampling or deriving parameters from protected or historical market data.

All scenarios use fixed mathematical formulas and explicit pseudo-random seeds.
Zero lookahead, zero historical contamination.
"""

from __future__ import annotations

import datetime
import math
from typing import Any

STANDARD_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]


def _generate_bars_from_returns(
    start_date: str,
    tickers: list[str],
    daily_returns: dict[str, list[float]],
    initial_prices: dict[str, float] | None = None,
    volumes: dict[str, float] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Deterministically convert daily returns into daily OHLCV bar dicts."""
    dt = datetime.date.fromisoformat(start_date)
    init_px = initial_prices or {t: 100.0 for t in tickers}
    vols = volumes or {t: 1_000_000.0 for t in tickers}

    n_days = max(len(rets) for rets in daily_returns.values()) if daily_returns else 0
    bars: dict[str, list[dict[str, Any]]] = {t: [] for t in tickers}
    cur_prices = {t: float(init_px.get(t, 100.0)) for t in tickers}

    for i in range(n_days):
        while dt.weekday() >= 5:  # Skip weekends
            dt += datetime.timedelta(days=1)

        date_str = dt.isoformat()
        for t in tickers:
            rets = daily_returns.get(t, [])
            ret = rets[i] if i < len(rets) else 0.0
            prev_px = cur_prices[t]
            close_px = max(prev_px * (1.0 + ret), 0.01)
            open_px = prev_px
            high_px = max(open_px, close_px) * 1.002
            low_px = min(open_px, close_px) * 0.998
            vol = vols.get(t, 1_000_000.0)

            bars[t].append({
                "ts": date_str,
                "open": round(open_px, 4),
                "high": round(high_px, 4),
                "low": round(low_px, 4),
                "close": round(close_px, 4),
                "volume": vol,
            })
            cur_prices[t] = close_px

        dt += datetime.timedelta(days=1)

    return bars


def scenario_1_abrupt_vol_explosion() -> dict[str, list[dict[str, Any]]]:
    """1. Abrupt volatility explosion: 60 calm days (vol ~0.10) followed by 5 violent days (+/-5% daily swings)."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 60:
            r_mkt = 0.0008
            r_qld = 0.0016
        else:
            # Alternating violent days
            r_mkt = -0.05 if i % 2 == 1 else 0.04
            r_qld = r_mkt * 2.0
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.3)
        rets["QLD"].append(r_qld)
        rets["SSO"].append(r_qld)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_2_slow_vol_increase() -> dict[str, list[dict[str, Any]]]:
    """2. Slow volatility increase: Volatility drifts upward from 0.12 to 0.32 over 40 sessions."""
    n = 90
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 50:
            scale = 0.005
        else:
            scale = 0.005 + (i - 50) * 0.0006  # Gradually expanding dispersion
        # Deterministic pseudo-sine wave
        r_mkt = 0.0005 + scale * math.sin(i * 1.5)
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.4)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_3_high_vol_sideways() -> dict[str, list[dict[str, Any]]]:
    """3. High-volatility sideways market: Persistent oscillating market (vol ~0.30) around zero return."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 55:
            r_mkt = 0.001
        else:
            r_mkt = 0.025 * (1 if i % 2 == 0 else -1)
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.3)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_4_false_short_term_spike() -> dict[str, list[dict[str, Any]]]:
    """4. False short-term volatility spike: Single day outlier (-3.5% then +3.5%) in an otherwise calm market."""
    n = 70
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i == 62:
            r_mkt = -0.035  # Isolated one-day shock
        elif i == 63:
            r_mkt = 0.035   # Immediate rebound
        else:
            r_mkt = 0.0006  # Calm
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.2)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_5_v_shaped_recovery() -> dict[str, list[dict[str, Any]]]:
    """5. V-shaped recovery: 4-day sharp drop (-3% daily) followed by 4-day surge (+3% daily)."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 55:
            r_mkt = 0.0008
        elif i < 59:
            r_mkt = -0.03
        elif i < 63:
            r_mkt = 0.03
        else:
            r_mkt = 0.0005
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.3)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_6_persistent_low_vol_uptrend() -> dict[str, list[dict[str, Any]]]:
    """6. Persistent low-volatility uptrend: Unbroken smooth bull market (vol ~0.08)."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r_mkt = 0.0012
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.5)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_7_leveraged_etf_gap() -> dict[str, list[dict[str, Any]]]:
    """7. Leveraged ETF gap against the position: QLD/SSO experience an adverse tracking gap (-8% vs -3% index)."""
    n = 70
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i == 60:
            r_mkt = -0.03
            r_qld = -0.08  # Extreme gap
        else:
            r_mkt = 0.0007
            r_qld = r_mkt * 2.0
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.3)
        rets["QLD"].append(r_qld)
        rets["SSO"].append(r_qld)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_8_near_zero_denominator() -> dict[str, list[dict[str, Any]]]:
    """8. Volatility ratio denominator near zero: 25 completely flat sessions (sigma_20 = 0.0)."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i >= 50:
            r_mkt = 0.0  # Zero movement -> zero volatility
        else:
            r_mkt = 0.0005
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt)
        rets["QLD"].append(r_mkt)
        rets["SSO"].append(r_mkt)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_9_missing_qqq_observations() -> dict[str, list[dict[str, Any]]]:
    """9. Missing QQQ observations: Market has bars for SPY/equities but QQQ data stream is truncated/missing."""
    base = scenario_6_persistent_low_vol_uptrend()
    # Remove last 10 bars of QQQ
    base["QQQ"] = base["QQQ"][:50]
    return base


def scenario_10_alternating_calm_and_stressed() -> dict[str, list[dict[str, Any]]]:
    """10. Alternating calm and stressed sessions: Volatility whipsaws across 0.28 every 2 sessions."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 55:
            r_mkt = 0.0008
        else:
            cycle = (i - 55) % 4
            r_mkt = 0.028 if cycle in (0, 1) else 0.0002
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.3)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_11_overnight_gap_beyond_slippage() -> dict[str, list[dict[str, Any]]]:
    """11. Overnight gap beyond modeled slippage: Massive overnight gap of -12% on Day 62."""
    n = 70
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i == 62:
            r_mkt = -0.12
            r_qld = -0.24
        else:
            r_mkt = 0.0008
            r_qld = 0.0016
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.4)
        rets["QLD"].append(r_qld)
        rets["SSO"].append(r_qld)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_12_conflicting_risk_conditions() -> dict[str, list[dict[str, Any]]]:
    """12. Conflicting risk-on and risk-off conditions: QQQ is in a strong uptrend, but SPY drops below SMA50."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 55:
            r_spy = 0.0006
            r_qqq = 0.0010
        else:
            r_spy = -0.015  # SPY breakdown below SMA50
            r_qqq = 0.0015   # QQQ continuing uptrend
        rets["SPY"].append(r_spy)
        rets["QQQ"].append(r_qqq)
        for t in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_qqq)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_spy * 0.5)
        rets["QLD"].append(r_qqq * 2.0)
        rets["SSO"].append(r_spy * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)
