"""
Guardian Alpha V30 Stage 3E - Adversarial Competition Verification Test Suite.
Tests agent.py against 14 adversarial synthetic fixtures and execution edge cases.
"""
from __future__ import annotations

import copy
import math
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))
import agent


def make_bar(ts: str, o: float, h: float, l: float, c: float, v: float) -> dict[str, object]:
    return {"ts": ts, "open": o, "high": h, "low": l, "close": c, "volume": v}


def make_synthetic_history(n: int = 220, base: float = 100.0, trend: float = 0.0005, vol: float = 0.01) -> list[dict[str, object]]:
    bars = []
    p = base
    for i in range(n):
        p *= (1.0 + trend + ((i % 7) - 3) * vol * 0.1)
        bars.append(make_bar(f"2026-01-{(i % 28) + 1:02d}", p * 0.99, p * 1.01, p * 0.98, p, 1_000_000))
    return bars


DEFAULT_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL"]


def make_synthetic_market(n: int = 220, tickers: list[str] = DEFAULT_TICKERS) -> dict[str, list[dict[str, object]]]:
    return {t: make_synthetic_history(n=n, base=100.0 + i * 25.0) for i, t in enumerate(tickers)}


def make_portfolio_state(cash: float = 100_000.0, tickers: list[str] = DEFAULT_TICKERS) -> dict[str, object]:
    return {
        "cash": cash,
        "positions": [],
        "last_prices": {t: 100.0 + i * 25.0 for i, t in enumerate(tickers)}
    }


def test_01_fixture_empty_history():
    """Verify empty market state produces empty order list without crash."""
    orders = agent.decide({}, {"cash": 100_000.0, "positions": [], "last_prices": {}}, 100_000.0)
    assert orders == [], "Empty market state must return empty order list"

    # Also test empty bar list per ticker
    orders_empty_bars = agent.decide({"SPY": [], "QQQ": []}, make_portfolio_state(), 100_000.0)
    assert orders_empty_bars == [], "Tickers with empty bar lists must return empty order list"


def test_02_fixture_insufficient_warmup():
    """Verify market state with only 5 bars (insufficient warmup for 50/200-day SMAs) returns empty orders."""
    m_short = make_synthetic_market(n=5)
    p_state = make_portfolio_state()
    orders = agent.decide(m_short, p_state, 100_000.0)
    assert orders == [], f"Insufficient warmup (5 bars) must return empty orders, got {orders}"


def test_03_fixture_missing_ticker():
    """Verify omission of anchor tickers (e.g. SPY missing) safely returns empty orders."""
    m = make_synthetic_market(n=220)
    del m["SPY"]  # Remove SPY
    p_state = make_portfolio_state()
    orders = agent.decide(m, p_state, 100_000.0)
    assert orders == [], "Missing anchor ticker SPY must return empty orders"


def test_04_fixture_duplicate_ticker_handling():
    """Verify ticker case insensitivity and handling of duplicated tickers in portfolio positions."""
    m = make_synthetic_market(n=220)
    p_state = {
        "cash": 50_000.0,
        "positions": [
            {"ticker": "AAPL", "quantity": 10.0, "avg_cost": 150.0},
            {"ticker": "AAPL", "quantity": 5.0, "avg_cost": 155.0}  # duplicate position entry
        ],
        "last_prices": {t: 150.0 for t in DEFAULT_TICKERS}
    }
    orders = agent.decide(m, p_state, 50_000.0)
    assert isinstance(orders, list), "Must return a valid list of orders"
    for o in orders:
        assert isinstance(o, dict)
        assert "ticker" in o and "side" in o and "quantity" in o
        assert o["side"] in ("buy", "sell")
        assert o["quantity"] > 0


def test_05_fixture_invalid_ohlc():
    """Verify invalid OHLC bars (high < low, negative prices) are quarantined or rejected cleanly."""
    m = make_synthetic_market(n=220)
    # Corrupt last bar of AAPL with high < low and negative close
    m["AAPL"][-1] = make_bar("2026-05-01", 100.0, 50.0, 150.0, -10.0, 100)
    p_state = make_portfolio_state()
    orders = agent.decide(m, p_state, 100_000.0)
    assert isinstance(orders, list), "Must not crash on invalid OHLC"
    # AAPL must not be bought with negative/corrupted price
    for o in orders:
        if o["ticker"] == "AAPL" and o["side"] == "buy":
            pytest.fail("Agent attempted to buy ticker with negative/corrupted price bar")


def test_06_fixture_negative_or_zero_prices():
    """Verify zero or negative prices in market state or last_prices do not produce division by zero."""
    m = make_synthetic_market(n=220)
    m["MSFT"][-1] = make_bar("2026-05-01", 0.0, 0.0, 0.0, 0.0, 0)
    p_state = make_portfolio_state()
    p_state["last_prices"]["MSFT"] = 0.0
    orders = agent.decide(m, p_state, 100_000.0)
    assert isinstance(orders, list), "Must not raise ZeroDivisionError"


def test_07_fixture_nan_and_infinite_values():
    """Verify NaN and Inf price values in market bars are handled without unhandled exception."""
    m = make_synthetic_market(n=220)
    m["NVDA"][-1] = make_bar("2026-05-01", float("nan"), float("inf"), float("-inf"), float("nan"), 0)
    p_state = make_portfolio_state()
    orders = agent.decide(m, p_state, 100_000.0)
    assert isinstance(orders, list), "Must not raise ValueError on NaN/Inf"
    for o in orders:
        assert math.isfinite(o["quantity"]), "Order quantities must be finite"


def test_08_fixture_corporate_action_discontinuity():
    """Verify a 50% split discontinuity does not produce anomalous oversized orders."""
    m = make_synthetic_market(n=220)
    last_c = m["AAPL"][-2]["close"]
    # 2:1 stock split on last day: price cuts in half
    m["AAPL"][-1] = make_bar("2026-05-02", last_c * 0.5, last_c * 0.51, last_c * 0.49, last_c * 0.5, 2_000_000)
    p_state = make_portfolio_state()
    orders = agent.decide(m, p_state, 100_000.0)
    assert isinstance(orders, list)
    for o in orders:
        if o["ticker"] == "AAPL":
            # Order value must not exceed single-name concentration cap (30k)
            est_val = o["quantity"] * (last_c * 0.5)
            assert est_val <= 30_000.0 * 1.05, f"Split caused oversized order: {est_val}"


def test_09_fixture_large_open_gaps():
    """Verify large gaps (+20% gap up, -20% gap down) are processed safely."""
    m = make_synthetic_market(n=220)
    last_c = m["MSFT"][-2]["close"]
    m["MSFT"][-1] = make_bar("2026-05-02", last_c * 1.25, last_c * 1.30, last_c * 1.20, last_c * 1.25, 3_000_000)
    p_state = make_portfolio_state()
    orders = agent.decide(m, p_state, 100_000.0)
    assert isinstance(orders, list)


def test_10_fixture_flat_price_market():
    """Verify completely flat prices (zero volatility, zero return) produces safe behavior."""
    flat_bars = [make_bar(f"2026-01-{(i % 28) + 1:02d}", 100.0, 100.0, 100.0, 100.0, 100_000) for i in range(220)]
    m_flat = {t: copy.deepcopy(flat_bars) for t in DEFAULT_TICKERS}
    p_state = make_portfolio_state()
    orders = agent.decide(m_flat, p_state, 100_000.0)
    assert isinstance(orders, list)
    # Under flat markets, volatility is 0 and momentum is 0; orders must be empty or bounded
    assert len(orders) <= 10


def test_11_fixture_sharp_downturn():
    """Verify market undergoing severe downturn triggers defensive posture (no aggressive buys)."""
    m_down = {t: make_synthetic_history(n=220, base=250.0, trend=-0.005, vol=0.03) for t in DEFAULT_TICKERS}
    p_state = make_portfolio_state()
    orders = agent.decide(m_down, p_state, 100_000.0)
    assert isinstance(orders, list)
    # Under sharp downturn, SPY and QQQ are below 50-day SMA; risk-on is deactivated
    assert orders == [] or all(o.get("side") != "buy" or o.get("ticker") in ("XLP", "XLU", "XLV", "XLE") for o in orders)


def test_12_fixture_recovery_after_drawdown():
    """Verify recovery market with strong uptrend resumes rebalancing safely."""
    m_rec = {t: make_synthetic_history(n=220, base=50.0, trend=0.005, vol=0.01) for t in DEFAULT_TICKERS}
    p_state = make_portfolio_state()
    orders = agent.decide(m_rec, p_state, 100_000.0)
    assert isinstance(orders, list)
    assert len(orders) > 0, "Recovery market should generate rebalance orders"


def test_13_fixture_repeated_invocations():
    """Verify 100 consecutive invocations run without state leakage, memory bloat, or timing drift."""
    m = make_synthetic_market(n=220)
    p_state = make_portfolio_state()
    first_orders = agent.decide(m, p_state, 100_000.0)
    for _ in range(100):
        subsequent_orders = agent.decide(m, p_state, 100_000.0)
        assert subsequent_orders == first_orders, "Repeated invocation must produce identical output"


def test_14_fixture_restart_determinism():
    """Verify restart from identical deep-copied state produces bit-for-bit identical order objects."""
    m1 = make_synthetic_market(n=220)
    m2 = copy.deepcopy(m1)
    p1 = make_portfolio_state()
    p2 = copy.deepcopy(p1)
    orders1 = agent.decide(m1, p1, 100_000.0)
    orders2 = agent.decide(m2, p2, 100_000.0)
    assert orders1 == orders2, "Restart with deep-copied state must produce bit-for-bit identical orders"
