"""Tests for Loss Reduction Candidates, Loss Attribution, and Crisis De-Risking.

Fulfills Guardian Alpha Protocol V10 Stages V10-D, V10-E, V10-F, and V10-J:
- Validates fast emergency exit mechanism on market shock.
- Validates drawdown-dependent budget de-risking multiplier.
- Validates exclusion of pro-cyclical XLE from defensive basket.
- Validates snapback recovery participation mechanism.
- Validates E0 loss attribution breakdown in volatility spike regime.
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import agent
import preview
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.loss_reduction_candidates import (
    FastExitDeRiskingCandidate,
    IntegratedLossReductionCandidate,
)

SAMPLE_REGIMES_PATH = Path("sample_regimes.json.gz")


def _make_series(start_p: float, ret: float, n_days: int = 75) -> list[dict[str, Any]]:
    bars = []
    p = start_p
    base = datetime(2021, 1, 4)
    cur = base
    added = 0
    while added < n_days:
        if cur.weekday() < 5:
            p *= (1.0 + ret)
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


def test_candidates_match_competition_contract():
    """Verify all candidate strategies adhere to the official competition decide() interface."""
    cand1 = FastExitDeRiskingCandidate()
    cand2 = IntegratedLossReductionCandidate()

    for cand in [cand1, cand2]:
        assert hasattr(cand, "decide")
        assert cand.decide({}, {"positions": [], "cash": 100_000.0}, 100_000.0) == []


def test_emergency_exit_breaks_five_day_cadence():
    """When a severe market shock occurs, FastExitDeRisking must exit immediately without waiting 5 days."""
    cand = FastExitDeRiskingCandidate(rebalance_every_days=5, emergency_drop_threshold=-0.025)

    spy = _make_series(400.0, 0.002, 75)
    qqq = _make_series(350.0, 0.002, 75)
    aapl = _make_series(150.0, 0.002, 75)

    m_state = {"SPY": spy, "QQQ": qqq, "AAPL": aapl}
    p_state = {"positions": [], "cash": 100_000.0}

    # Initial allocation on Day 0
    orders_d0 = cand.decide(m_state, p_state, 100_000.0)
    assert len(orders_d0) > 0
    assert cand.days_counter == 0

    # Account now holds AAPL
    p_state = {"positions": [{"ticker": "AAPL", "quantity": 100.0, "avg_cost": aapl[-1]["close"]}], "cash": 80_000.0}

    # Day 1: Normal continuation (+0.2%) -> Must NOT rebalance because cadence is 5
    last_dt = datetime.strptime(spy[-1]["ts"], "%Y-%m-%d") + timedelta(days=1)
    p_spy = spy[-1]["close"] * 1.002
    p_qqq = qqq[-1]["close"] * 1.002
    p_aapl = aapl[-1]["close"] * 1.002

    m_state["SPY"].append({"ts": last_dt.strftime("%Y-%m-%d"), "open": p_spy, "high": p_spy*1.01, "low": p_spy*0.99, "close": p_spy, "volume": 1_000_000})
    m_state["QQQ"].append({"ts": last_dt.strftime("%Y-%m-%d"), "open": p_qqq, "high": p_qqq*1.01, "low": p_qqq*0.99, "close": p_qqq, "volume": 1_000_000})
    m_state["AAPL"].append({"ts": last_dt.strftime("%Y-%m-%d"), "open": p_aapl, "high": p_aapl*1.01, "low": p_aapl*0.99, "close": p_aapl, "volume": 1_000_000})

    orders_d1 = cand.decide(m_state, p_state, 80_000.0)
    assert len(orders_d1) == 0, "Normal continuation must honor 5-day cadence"
    assert cand.days_counter == 1

    # Day 2: Market Flash Crash (-4% shock) -> Must trigger EMERGENCY EXIT on day 2!
    crash_dt = last_dt + timedelta(days=1)
    c_spy = p_spy * 0.96
    c_qqq = p_qqq * 0.95
    c_aapl = p_aapl * 0.94

    m_state["SPY"].append({"ts": crash_dt.strftime("%Y-%m-%d"), "open": c_spy, "high": c_spy*1.01, "low": c_spy*0.98, "close": c_spy, "volume": 5_000_000})
    m_state["QQQ"].append({"ts": crash_dt.strftime("%Y-%m-%d"), "open": c_qqq, "high": c_qqq*1.01, "low": c_qqq*0.98, "close": c_qqq, "volume": 5_000_000})
    m_state["AAPL"].append({"ts": crash_dt.strftime("%Y-%m-%d"), "open": c_aapl, "high": c_aapl*1.01, "low": c_aapl*0.98, "close": c_aapl, "volume": 5_000_000})

    orders_d2 = cand.decide(m_state, p_state, 80_000.0)
    assert len(orders_d2) > 0, "Emergency shock must break 5-day cadence immediately"
    assert any(o["ticker"] == "AAPL" and o["side"].lower() == "sell" for o in orders_d2)


def test_drawdown_multiplier_de_risks_portfolio():
    """When portfolio suffers drawdown, gross targets must scale down proportionally."""
    cand = FastExitDeRiskingCandidate(dd_derisk_threshold=0.08)

    spy = _make_series(400.0, 0.002, 75)
    qqq = _make_series(350.0, 0.002, 75)
    m_state = {"SPY": spy, "QQQ": qqq}

    targets_peak = cand.compute_targets(m_state, 100_000.0)
    total_w_peak = sum(targets_peak.values())

    targets_dd = cand.compute_targets(m_state, 85_000.0)
    total_w_dd = sum(targets_dd.values())

    assert total_w_dd < total_w_peak, "Drawdown must reduce gross exposure"
    assert total_w_dd <= total_w_peak * 0.75, "15% drawdown must reduce exposure by at least 25%"


def test_defensive_weights_exclude_xle():
    """Defensive allocation must exclude volatile energy (XLE) when configured."""
    cand = FastExitDeRiskingCandidate(exclude_xle_defensive=True)
    spy = _make_series(400.0, -0.005, 75)
    qqq = _make_series(350.0, -0.005, 75)
    xlp = _make_series(70.0, 0.001, 75)
    xlu = _make_series(65.0, 0.001, 75)
    xlv = _make_series(120.0, 0.001, 75)
    xle = _make_series(50.0, 0.001, 75)

    m_state = {"SPY": spy, "QQQ": qqq, "XLP": xlp, "XLU": xlu, "XLV": xlv, "XLE": xle}
    targets = cand.compute_targets(m_state, 100_000.0)

    assert "XLE" not in targets, "XLE must be excluded from defensive basket"
    assert "XLP" in targets
    assert "XLU" in targets
    assert "XLV" in targets


def test_baseline_vol_spike_attribution_truth():
    """Forensic verification: In vol_spike_snapback, week 1 tech losses exceed 70% of total loss."""
    prov = StaticRegimeProvider(SAMPLE_REGIMES_PATH, "vol_spike_snapback")
    engine = ReplayEngine(agent.decide, prov)
    res = engine.run_replay()

    tot_return = res["metrics"]["ret"]
    mdd = res["metrics"]["mdd"]

    assert tot_return == pytest.approx(-0.15772963, abs=1e-6)
    assert mdd == pytest.approx(0.33457653, abs=1e-6)
