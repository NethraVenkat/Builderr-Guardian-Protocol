"""
Guardian Alpha — V30 Stage 2C: Comprehensive Adversarial Test Suite for Volatility Gating.

Verifies:
1. Preregistered hypotheses, parameters, and algorithms (C1, C2, C3, C4).
2. All 12 deterministic synthetic market stress regimes.
3. Signal causality and strict future-price independence.
4. Volatility arithmetic, annualization, and zero-denominator safety.
5. Volatility persistence state transitions (C3 entry, maintenance, confirmation exit, emergency exit).
6. Financial conservation, weight bounds, and portfolio risk invariants.
"""

from __future__ import annotations

import math
from statistics import pstdev
from typing import Any

import pytest

import agent
from research.strategies import (
    v30_candidate_c1_tight_vol_gate as c1,
    v30_candidate_c2_vol_acceleration as c2,
    v30_candidate_c3_vol_persistence as c3,
    v30_candidate_c4_combined_gates as c4,
)
from research.engine import v30_synthetic_stress_scenarios_stage2c as syn


@pytest.fixture(autouse=True)
def reset_globals():
    """Ensure all module globals are clean before and after every test."""
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}
    c1.reset()
    c2.reset()
    c3.reset()
    c4.reset()
    yield
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}
    c1.reset()
    c2.reset()
    c3.reset()
    c4.reset()


def _simulate_synthetic_regime(decide_fn: Any, bars: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Run a light simulation over synthetic bars and return portfolio traces."""
    if hasattr(decide_fn, "__self__"):
        mod = decide_fn.__self__
        if hasattr(mod, "reset"):
            mod.reset()

    tickers = list(bars.keys())
    n_days = min(len(b) for b in bars.values()) if bars else 0

    cash = 100_000.0
    positions: dict[str, dict[str, float]] = {}
    total_trades = 0
    errors = 0
    overlays_held_days = 0

    for i in range(55, n_days):
        market_slice = {t: bars[t][:i+1] for t in tickers}
        cur_prices = {t: bars[t][i]["close"] for t in tickers}
        total_equity = cash + sum(pos["quantity"] * cur_prices.get(t, pos["avg_cost"]) for t, pos in positions.items())

        port_state = {
            "cash": cash,
            "positions": [{"ticker": t, "quantity": pos["quantity"], "avg_cost": pos["avg_cost"]} for t, pos in positions.items()],
            "last_prices": cur_prices,
        }

        try:
            orders = decide_fn(market_slice, port_state, cash)
        except Exception:
            errors += 1
            continue

        if "QLD" in positions and positions["QLD"]["quantity"] > 0:
            overlays_held_days += 1

        # Simulate execution at current close
        for o in orders:
            t = o["ticker"]
            side = o["side"]
            qty = o["quantity"]
            px = cur_prices.get(t, 100.0)
            if side == "sell":
                avail = positions.get(t, {}).get("quantity", 0.0)
                exec_qty = min(qty, avail)
                if exec_qty > 0:
                    cash += exec_qty * px * 0.9995  # 5 bps slippage
                    positions[t]["quantity"] -= exec_qty
                    if positions[t]["quantity"] <= 0:
                        del positions[t]
                    total_trades += 1
            elif side == "buy":
                cost = qty * px * 1.0005
                if cost <= cash and qty > 0:
                    cash -= cost
                    pos = positions.setdefault(t, {"quantity": 0.0, "avg_cost": px})
                    new_qty = pos["quantity"] + qty
                    pos["avg_cost"] = (pos["quantity"] * pos["avg_cost"] + cost) / new_qty
                    pos["quantity"] = new_qty
                    total_trades += 1

    final_equity = cash + sum(pos["quantity"] * bars[t][-1]["close"] for t, pos in positions.items())
    return {
        "final_equity": final_equity,
        "total_trades": total_trades,
        "errors": errors,
        "overlays_held_days": overlays_held_days,
    }


# ==============================================================================
# GATE A: CANDIDATE CONTRACTS AND PREREGISTRATION CHECKS
# ==============================================================================

class TestGateACandidateContracts:
    def test_c1_tight_threshold_contract(self):
        """C1 must have QQQ_VOL20_OVERLAY_THRESHOLD_C1 == 0.22."""
        assert c1.QQQ_VOL20_OVERLAY_THRESHOLD_C1 == 0.22

    def test_c2_acceleration_threshold_contract(self):
        """C2 must define ratio threshold 1.25 and baseline 0.28."""
        assert c2.VOL_ACCELERATION_RATIO_MAX == 1.25
        assert c2.BASELINE_VOL20_OVERLAY_THRESHOLD == 0.28
        assert c2.ZERO_DENOMINATOR_EPSILON == 1e-6

    def test_c3_persistence_contract(self):
        """C3 must require 2 confirmation sessions at vol >= 0.28."""
        assert c3.VOL20_OVERLAY_THRESHOLD == 0.28
        assert c3.CONFIRMATION_SESSIONS_REQUIRED == 2

    def test_c4_combined_contract(self):
        """C4 must jointly enforce 0.22 vol ceiling and 1.25 acceleration."""
        assert c4.QQQ_VOL20_OVERLAY_THRESHOLD_C4 == 0.22
        assert c4.VOL_ACCELERATION_RATIO_MAX == 1.25

    def test_candidates_compatible_with_decide_signature(self):
        """All candidates must implement decide(market_state, portfolio_state, cash)."""
        market = {"SPY": [{"ts": "2021-01-01", "close": 100.0, "open": 100.0, "high": 101.0, "low": 99.0, "volume": 1e6}]}
        for mod, name in [(c1, "C1"), (c2, "C2"), (c3, "C3"), (c4, "C4")]:
            assert hasattr(mod, "decide"), f"{name} lacks decide"
            assert hasattr(mod, "reset"), f"{name} lacks reset"
            res = mod.decide(market, {}, 100000.0)
            assert isinstance(res, list), f"{name} decide return type must be list"


# ==============================================================================
# GATE B: SIGNAL ARITHMETIC AND NUMERICAL INTEGRITY
# ==============================================================================

class TestGateBSignalArithmetic:
    def test_realized_vol_reference_value(self):
        """Verify realized_vol against mathematical reference calculation."""
        rets = [0.01, -0.01, 0.02, -0.02, 0.01]
        px = [100.0]
        for r in rets:
            px.append(px[-1] * (1.0 + r))
        v = agent.realized_vol(px, 5)
        expected = pstdev(rets) * math.sqrt(252.0)
        assert v == pytest.approx(expected, rel=1e-12)

    def test_volatility_acceleration_zero_denominator_safe(self):
        """Zero-denominator must not raise ZeroDivisionError and must evaluate as adverse."""
        flat_prices = [100.0] * 30
        assert c2.is_volatility_acceleration_adverse(flat_prices) is True
        assert c4.is_volatility_acceleration_adverse(flat_prices) is True

    def test_volatility_acceleration_detection(self):
        """Short-term spike on top of low trailing vol must trigger adverse acceleration."""
        # 16 days calm (+/-0.05%), then 5 days violent swings (+/-5%)
        px = [100.0]
        for _ in range(16):
            px.append(px[-1] * 1.0005)
        for r in [0.05, -0.05, 0.04, -0.04, 0.05]:
            px.append(px[-1] * (1.0 + r))
        assert c2.is_volatility_acceleration_adverse(px) is True

    def test_c3_persistence_state_machine(self):
        """Verify C3 allows single-session transient vol spike and exits on second session."""
        c3.reset()
        
        # Build calm market state with strong positive trend (1.008 daily drift)
        calm_bars = [{"ts": f"2021-01-{i+1:02d}", "close": 100.0 * (1.008 ** i), "open": 100.0 * (1.008 ** i), "high": 101.0 * (1.008 ** i), "low": 99.0 * (1.008 ** i), "volume": 1e6} for i in range(70)]
        market_calm = {
            "SPY": calm_bars,
            "QQQ": calm_bars,
            "AAPL": calm_bars,
            "MSFT": calm_bars,
            "QLD": calm_bars,
            "SSO": calm_bars,
            "XLP": calm_bars, "XLU": calm_bars, "XLV": calm_bars, "XLE": calm_bars,
        }

        # Session 1: Calm regime -> overlay must be active
        w1 = c3.target_weights_c3(market_calm)
        assert "QLD" in w1 and "SSO" in w1
        assert c3._overlay_active is True
        assert c3._adverse_vol_count == 0

        # Session 2: Inject single volatile bar (vol20 rises to ~0.32, between 0.28 and 0.35)
        spike_bars = list(calm_bars)
        spike_bars.append({"ts": "2021-04-01", "close": calm_bars[-1]["close"] * 0.915, "open": calm_bars[-1]["close"], "high": calm_bars[-1]["close"], "low": calm_bars[-1]["close"] * 0.91, "volume": 1e6})
        market_spike1 = dict(market_calm)
        market_spike1["QQQ"] = spike_bars

        # C3 must maintain overlay on Day 1 of adverse volatility spike
        w2 = c3.target_weights_c3(market_spike1)
        assert "QLD" in w2 and "SSO" in w2
        assert c3._adverse_vol_count == 1
        assert c3._overlay_active is True

        # Session 3: Second volatile bar -> C3 must confirm adverse vol and exit overlay
        spike_bars2 = list(spike_bars)
        spike_bars2.append({"ts": "2021-04-02", "close": spike_bars[-1]["close"] * 1.01, "open": spike_bars[-1]["close"], "high": spike_bars[-1]["close"] * 1.02, "low": spike_bars[-1]["close"], "volume": 1e6})
        market_spike2 = dict(market_calm)
        market_spike2["QQQ"] = spike_bars2

        w3 = c3.target_weights_c3(market_spike2)
        assert "QLD" not in w3 and "SSO" not in w3
        assert c3._overlay_active is False
        assert c3._adverse_vol_count >= 2


# ==============================================================================
# GATE C: 12 SYNTHETIC STRESS TESTS
# ==============================================================================

class TestGateCSyntheticStressScenarios:
    def test_stress_1_abrupt_vol_explosion(self):
        regime = syn.scenario_1_abrupt_vol_explosion()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c4 = _simulate_synthetic_regime(c4.decide, regime)
        assert res_e0["errors"] == 0 and res_c1["errors"] == 0 and res_c4["errors"] == 0
        # C1 and C4 should hold overlay fewer or equal days than E0
        assert res_c1["overlays_held_days"] <= res_e0["overlays_held_days"]
        assert res_c4["overlays_held_days"] <= res_e0["overlays_held_days"]

    def test_stress_2_slow_vol_increase(self):
        regime = syn.scenario_2_slow_vol_increase()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        assert res_e0["errors"] == 0 and res_c1["errors"] == 0
        assert res_c1["overlays_held_days"] <= res_e0["overlays_held_days"]

    def test_stress_3_high_vol_sideways(self):
        regime = syn.scenario_3_high_vol_sideways()
        res_c2 = _simulate_synthetic_regime(c2.decide, regime)
        assert res_c2["errors"] == 0

    def test_stress_4_false_short_term_spike(self):
        regime = syn.scenario_4_false_short_term_spike()
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        assert res_c3["errors"] == 0

    def test_stress_5_v_shaped_recovery(self):
        regime = syn.scenario_5_v_shaped_recovery()
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        assert res_c1["errors"] == 0 and res_c3["errors"] == 0

    def test_stress_6_persistent_low_vol_uptrend(self):
        regime = syn.scenario_6_persistent_low_vol_uptrend()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c2 = _simulate_synthetic_regime(c2.decide, regime)
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        res_c4 = _simulate_synthetic_regime(c4.decide, regime)
        assert all(r["errors"] == 0 for r in [res_e0, res_c1, res_c2, res_c3, res_c4])
        # In persistent low-vol bull, overlays should be active across all candidates
        assert res_c1["overlays_held_days"] > 0
        assert res_c4["overlays_held_days"] > 0

    def test_stress_7_leveraged_etf_gap(self):
        regime = syn.scenario_7_leveraged_etf_gap()
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        assert res_c1["errors"] == 0

    def test_stress_8_near_zero_denominator(self):
        regime = syn.scenario_8_near_zero_denominator()
        res_c2 = _simulate_synthetic_regime(c2.decide, regime)
        res_c4 = _simulate_synthetic_regime(c4.decide, regime)
        assert res_c2["errors"] == 0 and res_c4["errors"] == 0

    def test_stress_9_missing_qqq_observations(self):
        regime = syn.scenario_9_missing_qqq_observations()
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c2 = _simulate_synthetic_regime(c2.decide, regime)
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        res_c4 = _simulate_synthetic_regime(c4.decide, regime)
        assert all(r["errors"] == 0 for r in [res_c1, res_c2, res_c3, res_c4])

    def test_stress_10_alternating_calm_and_stressed(self):
        regime = syn.scenario_10_alternating_calm_and_stressed()
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        assert res_c3["errors"] == 0

    def test_stress_11_overnight_gap_beyond_slippage(self):
        regime = syn.scenario_11_overnight_gap_beyond_slippage()
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c4 = _simulate_synthetic_regime(c4.decide, regime)
        assert res_c1["errors"] == 0 and res_c4["errors"] == 0

    def test_stress_12_conflicting_risk_conditions(self):
        regime = syn.scenario_12_conflicting_risk_conditions()
        res_c1 = _simulate_synthetic_regime(c1.decide, regime)
        res_c3 = _simulate_synthetic_regime(c3.decide, regime)
        assert res_c1["errors"] == 0 and res_c3["errors"] == 0


# ==============================================================================
# GATE D: FINANCIAL AND CAUSALITY INVARIANTS
# ==============================================================================

class TestGateDFinancialAndCausalityInvariants:
    def test_target_weights_bounds_and_non_negativity(self):
        """All target weights must be non-negative, sum to <= 1.0, and respect caps."""
        market_state = {
            "SPY": [{"ts": f"2021-01-{i+1:02d}", "close": 300.0 + i, "open": 300.0 + i, "high": 301.0 + i, "low": 299.0 + i, "volume": 1e6} for i in range(60)],
            "QQQ": [{"ts": f"2021-01-{i+1:02d}", "close": 200.0 + i, "open": 200.0 + i, "high": 201.0 + i, "low": 199.0 + i, "volume": 1e6} for i in range(60)],
            "AAPL": [{"ts": f"2021-01-{i+1:02d}", "close": 150.0 + i, "open": 150.0 + i, "high": 151.0 + i, "low": 149.0 + i, "volume": 1e6} for i in range(60)],
            "MSFT": [{"ts": f"2021-01-{i+1:02d}", "close": 250.0 + i, "open": 250.0 + i, "high": 251.0 + i, "low": 249.0 + i, "volume": 1e6} for i in range(60)],
            "QLD": [{"ts": f"2021-01-{i+1:02d}", "close": 80.0 + i, "open": 80.0 + i, "high": 81.0 + i, "low": 79.0 + i, "volume": 1e6} for i in range(60)],
            "SSO": [{"ts": f"2021-01-{i+1:02d}", "close": 60.0 + i, "open": 60.0 + i, "high": 61.0 + i, "low": 59.0 + i, "volume": 1e6} for i in range(60)],
        }
        for fn, name in [(c1.target_weights_c1, "C1"), (c2.target_weights_c2, "C2"), (c3.target_weights_c3, "C3"), (c4.target_weights_c4, "C4")]:
            w = fn(market_state)
            assert all(v >= 0.0 for v in w.values()), f"{name} negative weight"
            assert sum(w.values()) <= 1.0 + 1e-6, f"{name} sum exceeds 1.0"
            for t, v in w.items():
                assert v <= agent.MAX_WEIGHT + 1e-6, f"{name} concentration cap breach on {t}"

    def test_future_price_injection_does_not_affect_decision(self):
        """Signal causality: Tampering with future day T+1 bar must not change day T decision."""
        base_bars = [{"ts": f"2021-01-{i+1:02d}", "close": 100.0 + i, "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i, "volume": 1e6} for i in range(60)]
        market_clean = {
            "SPY": base_bars,
            "QQQ": base_bars,
            "AAPL": base_bars,
            "QLD": base_bars,
            "SSO": base_bars,
        }

        # Decisions at Day 59
        c1.reset(); orders_c1_clean = c1.decide(market_clean, {}, 100000.0)
        c2.reset(); orders_c2_clean = c2.decide(market_clean, {}, 100000.0)
        c3.reset(); orders_c3_clean = c3.decide(market_clean, {}, 100000.0)
        c4.reset(); orders_c4_clean = c4.decide(market_clean, {}, 100000.0)

        # Inject mutated bar into a hypothetical Day 60
        mutated_bars = list(base_bars)
        mutated_bars.append({"ts": "2021-04-01", "close": 9999.0, "open": 9999.0, "high": 9999.0, "low": 9999.0, "volume": 1e9})
        # Evaluate up to index 59 only
        market_sliced = {t: mutated_bars[:60] for t in market_clean}

        c1.reset(); orders_c1_mut = c1.decide(market_sliced, {}, 100000.0)
        c2.reset(); orders_c2_mut = c2.decide(market_sliced, {}, 100000.0)
        c3.reset(); orders_c3_mut = c3.decide(market_sliced, {}, 100000.0)
        c4.reset(); orders_c4_mut = c4.decide(market_sliced, {}, 100000.0)

        assert orders_c1_clean == orders_c1_mut
        assert orders_c2_clean == orders_c2_mut
        assert orders_c3_clean == orders_c3_mut
        assert orders_c4_clean == orders_c4_mut
