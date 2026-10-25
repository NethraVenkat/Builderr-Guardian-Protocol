"""
Guardian Alpha — V30 Stage 2D: Synthetic Stress Scenarios for Position Sizing.

Generates 16 independent, deterministic synthetic market stress regimes
specifically targeting volatility-aware position sizing, concentration capping,
volatility estimation lag, and capacity redistribution.

All scenarios use fixed mathematical formulas and explicit pseudo-random seeds.
Zero lookahead, zero historical contamination.
"""

from __future__ import annotations

import datetime
import math
from typing import Any

STANDARD_TICKERS = [
    "SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL",
    "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"
]


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


def scenario_1_calm_low_vol_bull() -> dict[str, list[dict[str, Any]]]:
    """1. Calm low-volatility bull: All assets drift upward with low volatility (~8%)."""
    n = 80
    rets = {t: [0.0010 for _ in range(n)] for t in STANDARD_TICKERS}
    rets["QLD"] = [0.0020 for _ in range(n)]
    rets["SSO"] = [0.0020 for _ in range(n)]
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_2_broad_market_crash() -> dict[str, list[dict[str, Any]]]:
    """2. Broad-market crash: 60 calm days, then -25% crash over 5 sessions."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r_mkt = 0.0008 if i < 60 else -0.05
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.4)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_3_high_vol_rebound() -> dict[str, list[dict[str, Any]]]:
    """3. High-volatility rebound: Crash followed by turbulent +3% daily snapback."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 55:
            r = 0.0007
        elif i < 62:
            r = -0.04
        else:
            r = 0.03
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r * 0.3)
        rets["QLD"].append(r * 2.0)
        rets["SSO"].append(r * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_4_defensive_vol_spike() -> dict[str, list[dict[str, Any]]]:
    """4. Defensive asset volatility spike: Broad market calm, but defensive sectors swing +/-4%."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r_mkt = 0.0008
        r_def = 0.04 if i % 2 == 0 else -0.04
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_def)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_5_low_vol_asset_crash() -> dict[str, list[dict[str, Any]]]:
    """5. Low-volatility asset crash: An asset with lowest vol (AAPL) experiences an unexpected sudden -15% drop."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        for t in STANDARD_TICKERS:
            rets[t].append(0.0008)
        if i == 65:
            rets["AAPL"][-1] = -0.15  # Specific crash in supposedly calm asset
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_6_correlated_selloff() -> dict[str, list[dict[str, Any]]]:
    """6. Correlated cross-asset selloff: All correlations go to 1.0 during -12% correction."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r = 0.0008 if i < 60 else -0.03
        for t in STANDARD_TICKERS:
            rets[t].append(r)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_7_sharp_vol_regime_reversal() -> dict[str, list[dict[str, Any]]]:
    """7. Sharp volatility regime reversal: Calm market instantly shifts to high vol (+/-3.5%)."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r = 0.0008 if i < 60 else (0.035 if i % 2 == 0 else -0.035)
        for t in STANDARD_TICKERS:
            rets[t].append(r)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_8_prolonged_sideways() -> dict[str, list[dict[str, Any]]]:
    """8. Prolonged sideways market: 80 sessions of mean-reverting chop (+/-0.5%)."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r = 0.005 if i % 2 == 0 else -0.005
        for t in STANDARD_TICKERS:
            rets[t].append(r)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_9_missing_ticker_data() -> dict[str, list[dict[str, Any]]]:
    """9. Missing individual ticker data: MSFT stops reporting prices after session 55."""
    base = scenario_1_calm_low_vol_bull()
    base["MSFT"] = base["MSFT"][:55]
    return base


def scenario_10_high_concentration_pressure() -> dict[str, list[dict[str, Any]]]:
    """10. High concentration pressure: One asset (AAPL) has vol 0.05 while all others have vol 0.40."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        # AAPL flat smooth climb
        rets["AAPL"].append(0.0010)
        # Others volatile
        r_other = 0.025 if i % 2 == 0 else -0.023
        for t in ["MSFT", "NVDA", "AMZN", "GOOGL", "SPY", "QQQ", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]:
            rets[t].append(r_other)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_11_leveraged_etf_gap() -> dict[str, list[dict[str, Any]]]:
    """11. Leveraged ETF gap: QLD drops -10% overnight on session 62 while index drops -2%."""
    n = 70
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r = 0.0008
        for t in STANDARD_TICKERS:
            rets[t].append(r)
        if i == 62:
            rets["QLD"][-1] = -0.10
            rets["SSO"][-1] = -0.10
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_12_slippage_underfill() -> dict[str, list[dict[str, Any]]]:
    """12. Slippage-driven underfill: High volume divergence simulating execution stress."""
    n = 75
    rets = {t: [0.0010 for _ in range(n)] for t in STANDARD_TICKERS}
    vols = {t: 50_000.0 for t in STANDARD_TICKERS}  # Illiquid
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets, volumes=vols)


def scenario_13_simultaneous_rebalance() -> dict[str, list[dict[str, Any]]]:
    """13. Simultaneous sell and buy basket: Ranking completely flips winners on Day 60."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        if i < 60:
            rets["AAPL"].append(0.003)
            rets["MSFT"].append(0.003)
            rets["NVDA"].append(0.000)
            rets["AMZN"].append(0.000)
        else:
            rets["AAPL"].append(-0.002)
            rets["MSFT"].append(-0.002)
            rets["NVDA"].append(0.004)
            rets["AMZN"].append(0.004)
        for t in ["SPY", "QQQ", "GOOGL", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]:
            rets[t].append(0.001)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_14_frequent_vol_rank_reversals() -> dict[str, list[dict[str, Any]]]:
    """14. Frequent volatility rank reversals: Assets swap low/high volatility status every 5 days."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        phase = (i // 5) % 2
        r_aapl = 0.001 if phase == 0 else (0.025 if i % 2 == 0 else -0.023)
        r_msft = 0.001 if phase == 1 else (0.025 if i % 2 == 0 else -0.023)
        rets["AAPL"].append(r_aapl)
        rets["MSFT"].append(r_msft)
        for t in ["SPY", "QQQ", "NVDA", "AMZN", "GOOGL", "XLP", "XLU", "XLV", "XLE", "QLD", "SSO"]:
            rets[t].append(0.001)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_15_risk_on_to_off_transition() -> dict[str, list[dict[str, Any]]]:
    """15. Risk-on to risk-off transition: SPY and QQQ break below SMA50 on session 65."""
    n = 75
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r_mkt = 0.0008 if i < 62 else -0.025
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "QLD", "SSO"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(0.0003 if i < 62 else -0.005)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)


def scenario_16_risk_off_to_on_recovery() -> dict[str, list[dict[str, Any]]]:
    """16. Risk-off to risk-on recovery: Market starts in risk-off and crosses above SMA50 on session 65."""
    n = 80
    rets = {t: [] for t in STANDARD_TICKERS}
    for i in range(n):
        r_mkt = -0.002 if i < 50 else 0.004  # Recovery ramp
        for t in ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
            rets[t].append(r_mkt)
        for t in ["XLP", "XLU", "XLV", "XLE"]:
            rets[t].append(r_mkt * 0.4)
        rets["QLD"].append(r_mkt * 2.0)
        rets["SSO"].append(r_mkt * 2.0)
    return _generate_bars_from_returns("2021-01-04", STANDARD_TICKERS, rets)
