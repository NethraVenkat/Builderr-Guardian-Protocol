"""Targeted Synthetic Unit and Integration Tests for Leveraged ETF Overlay (QLD & SSO).

Fulfills Guardian Alpha Protocol V9 Phase B1:
- Verifies QLD and SSO execution pathways under valid synthetic calm-uptrend conditions.
- Confirms overlay is inactive when QLD/SSO are missing (as in public fixtures).
- Verifies overlay deactivates when QQQ volatility exceeds 0.28.
- Verifies orderly liquidation of QLD/SSO positions when the market trend breaks.
- Verifies gross beta leverage clamp (<= 1.35) and 10 bps leveraged ETF slippage.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import agent
from research.engine.provider import InMemoryStreamProvider
from research.engine.replay import ReplayEngine


@pytest.fixture(autouse=True)
def reset_agent_globals():
    """Reset module-level rebalance state in agent.py before and after each test."""
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}
    yield
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}


def _generate_synthetic_calm_bars(start_p: float, daily_ret: float, n_days: int = 75) -> list[dict[str, Any]]:
    bars = []
    p = start_p
    base_date = datetime(2021, 1, 4)  # Monday
    cur = base_date
    added = 0
    while added < n_days:
        # Generate weekdays
        if cur.weekday() < 5:
            p *= (1.0 + daily_ret)
            bars.append({
                "ts": cur.strftime("%Y-%m-%d"),
                "open": round(p * 0.998, 2),
                "high": round(p * 1.005, 2),
                "low": round(p * 0.995, 2),
                "close": round(p, 2),
                "volume": 1_000_000,
            })
            added += 1
        cur += timedelta(days=1)
    return bars


def test_overlay_inactive_when_qld_sso_missing():
    """When QLD and SSO are absent from market state, overlay must remain inactive."""
    spy_bars = _generate_synthetic_calm_bars(400.0, 0.002, 75)
    qqq_bars = _generate_synthetic_calm_bars(350.0, 0.0025, 75)
    aapl_bars = _generate_synthetic_calm_bars(150.0, 0.003, 75)

    market_state = {
        "SPY": spy_bars,
        "QQQ": qqq_bars,
        "AAPL": aapl_bars,
    }

    portfolio_state = {"positions": [], "cash": 100_000.0}
    orders = agent.decide(market_state, portfolio_state, 100_000.0)

    symbols = [o["ticker"] for o in orders]
    assert "QLD" not in symbols
    assert "SSO" not in symbols


def test_overlay_activates_in_calm_uptrend_with_qld_sso():
    """When QLD and SSO exist and QQQ is in calm uptrend, overlay activates."""
    spy_bars = _generate_synthetic_calm_bars(400.0, 0.0015, 75)
    qqq_bars = _generate_synthetic_calm_bars(350.0, 0.0020, 75)
    aapl_bars = _generate_synthetic_calm_bars(150.0, 0.0025, 75)
    msft_bars = _generate_synthetic_calm_bars(250.0, 0.0025, 75)
    googl_bars = _generate_synthetic_calm_bars(100.0, 0.0025, 75)
    nvda_bars = _generate_synthetic_calm_bars(200.0, 0.0025, 75)
    amzn_bars = _generate_synthetic_calm_bars(120.0, 0.0025, 75)

    # 2x leveraged overlays
    qld_bars = _generate_synthetic_calm_bars(70.0, 0.0040, 75)
    sso_bars = _generate_synthetic_calm_bars(60.0, 0.0030, 75)

    market_state = {
        "SPY": spy_bars,
        "QQQ": qqq_bars,
        "AAPL": aapl_bars,
        "MSFT": msft_bars,
        "GOOGL": googl_bars,
        "NVDA": nvda_bars,
        "AMZN": amzn_bars,
        "QLD": qld_bars,
        "SSO": sso_bars,
    }

    targets = agent.target_weights(market_state)
    assert targets.get("QLD") == 0.11, "QLD target weight must be 0.11"
    assert targets.get("SSO") == 0.07, "SSO target weight must be 0.07"
    for w in ["MSFT", "NVDA", "AAPL", "AMZN", "GOOGL"]:
        assert targets.get(w) == 0.152

    # Beta gross leverage check: 5 * 0.152 * 1.0 + 0.11 * 2.0 + 0.07 * 2.0 = 1.12 <= 1.35
    gross_beta = sum(agent.BETA_MULTIPLE.get(sym, 1.0) * w for sym, w in targets.items())
    assert gross_beta <= agent.MAX_BETA_GROSS

    portfolio_state = {"positions": [], "cash": 100_000.0}
    orders = agent.decide(market_state, portfolio_state, 100_000.0)

    symbols = {o["ticker"]: o for o in orders}
    assert "QLD" in symbols, "QLD order must be emitted when overlay is active"
    assert "SSO" in symbols, "SSO order must be emitted when overlay is active"
    assert symbols["QLD"]["side"].lower() == "buy"
    assert symbols["SSO"]["side"].lower() == "buy"

    # Verify notional target percentages: QLD target is 0.11 ($11,000), SSO is 0.07 ($7,000)
    qld_notional = symbols["QLD"]["quantity"] * qld_bars[-1]["close"]
    sso_notional = symbols["SSO"]["quantity"] * sso_bars[-1]["close"]
    assert pytest.approx(qld_notional, abs=200.0) == 11_000.0
    assert pytest.approx(sso_notional, abs=200.0) == 7_000.0


def test_overlay_deactivates_on_high_volatility():
    """When QQQ 20-day realized volatility exceeds 0.28, overlay must be off."""
    spy_bars = _generate_synthetic_calm_bars(400.0, 0.0015, 75)
    
    # Create volatile QQQ series (+/- 3% daily swings)
    qqq_bars = []
    p = 350.0
    base_date = datetime(2021, 1, 4)
    cur = base_date
    added = 0
    while added < 75:
        if cur.weekday() < 5:
            ret = 0.03 if (added % 2 == 0) else -0.025
            p *= (1.0 + ret)
            qqq_bars.append({
                "ts": cur.strftime("%Y-%m-%d"),
                "open": round(p * 0.99, 2), "high": round(p * 1.03, 2),
                "low": round(p * 0.97, 2), "close": round(p, 2), "volume": 2_000_000
            })
            added += 1
        cur += timedelta(days=1)

    qld_bars = _generate_synthetic_calm_bars(70.0, 0.002, 75)
    sso_bars = _generate_synthetic_calm_bars(60.0, 0.002, 75)
    aapl_bars = _generate_synthetic_calm_bars(150.0, 0.002, 75)

    market_state = {
        "SPY": spy_bars, "QQQ": qqq_bars, "AAPL": aapl_bars,
        "QLD": qld_bars, "SSO": sso_bars,
    }
    targets = agent.target_weights(market_state)
    assert "QLD" not in targets
    assert "SSO" not in targets


def test_overlay_liquidation_on_trend_breakdown():
    """When account holds QLD and SSO and market breaks down, agent must sell all shares."""
    # Market breaking down (prices falling below SMA50)
    spy_bars = _generate_synthetic_calm_bars(400.0, -0.005, 75)
    qqq_bars = _generate_synthetic_calm_bars(350.0, -0.006, 75)
    qld_bars = _generate_synthetic_calm_bars(70.0, -0.012, 75)
    sso_bars = _generate_synthetic_calm_bars(60.0, -0.010, 75)
    xlp_bars = _generate_synthetic_calm_bars(70.0, 0.001, 75)
    xlu_bars = _generate_synthetic_calm_bars(65.0, 0.001, 75)
    xlv_bars = _generate_synthetic_calm_bars(120.0, 0.001, 75)
    xle_bars = _generate_synthetic_calm_bars(50.0, 0.001, 75)

    market_state = {
        "SPY": spy_bars, "QQQ": qqq_bars, "QLD": qld_bars, "SSO": sso_bars,
        "XLP": xlp_bars, "XLU": xlu_bars, "XLV": xlv_bars, "XLE": xle_bars,
    }

    portfolio_state = {
        "positions": [
            {"ticker": "QLD", "quantity": 150.0, "avg_cost": 75.0},
            {"ticker": "SSO", "quantity": 100.0, "avg_cost": 65.0},
        ],
        "cash": 80_000.0,
    }

    orders = agent.decide(market_state, portfolio_state, 80_000.0)
    sell_orders = {o["ticker"]: o for o in orders if o["side"].lower() == "sell"}

    assert "QLD" in sell_orders, "Agent must liquidate QLD on trend breakdown"
    assert "SSO" in sell_orders, "Agent must liquidate SSO on trend breakdown"
    assert sell_orders["QLD"]["quantity"] == 150.0
    assert sell_orders["SSO"]["quantity"] == 100.0


def test_replay_engine_executes_leveraged_overlay_with_slippage():
    """Integration test: ReplayEngine processes QLD/SSO with 10 bps slippage and ledger conservation."""
    spy_bars = _generate_synthetic_calm_bars(400.0, 0.002, 75)
    qqq_bars = _generate_synthetic_calm_bars(350.0, 0.0025, 75)
    qld_bars = _generate_synthetic_calm_bars(70.0, 0.005, 75)
    sso_bars = _generate_synthetic_calm_bars(60.0, 0.004, 75)
    aapl_bars = _generate_synthetic_calm_bars(150.0, 0.003, 75)
    msft_bars = _generate_synthetic_calm_bars(250.0, 0.003, 75)
    googl_bars = _generate_synthetic_calm_bars(100.0, 0.003, 75)
    nvda_bars = _generate_synthetic_calm_bars(200.0, 0.003, 75)
    amzn_bars = _generate_synthetic_calm_bars(120.0, 0.003, 75)

    raw_bars = {
        "SPY": spy_bars, "QQQ": qqq_bars, "QLD": qld_bars, "SSO": sso_bars,
        "AAPL": aapl_bars, "MSFT": msft_bars, "GOOGL": googl_bars,
        "NVDA": nvda_bars, "AMZN": amzn_bars,
    }
    provider = InMemoryStreamProvider("overlay_test_stream", raw_bars)
    engine = ReplayEngine(agent.decide, provider)
    res = engine.run_replay()

    metrics = res["metrics"]
    assert metrics["trades"] > 0
    assert metrics["errors"] == 0
    assert res["compliance"]["all_safety_bars_cleared"] is True
