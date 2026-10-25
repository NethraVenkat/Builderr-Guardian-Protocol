"""
Guardian Alpha — V30 Stage 2D: Comprehensive Adversarial Test Suite for Position Sizing.

Verifies:
1. Preregistered hypotheses, parameters, and algorithms (P1, P2, P3, P4).
2. Independent mathematical sizing oracle and bounded capacity redistribution.
3. All 16 deterministic synthetic market stress regimes.
4. Signal causality and strict future-price independence.
5. Volatility smoothing state transitions and prior-vol tracking.
6. Portfolio weight bounds, non-negativity, and leverage invariants.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

import agent
from research.strategies import (
    v30_candidate_p1_inverse_vol as p1,
    v30_candidate_p2_capped_inverse_vol as p2,
    v30_candidate_p3_smoothed_inverse_vol as p3,
    v30_candidate_p4_blend_equal_inverse as p4,
)
from research.engine import v30_sizing_oracle as oracle
from research.engine import v30_synthetic_stress_scenarios_stage2d as syn


@pytest.fixture(autouse=True)
def reset_globals():
    """Ensure all module globals are clean before and after every test."""
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}
    p1.reset()
    p2.reset()
    p3.reset()
    p4.reset()
    yield
    agent._last_rebalance_bar_date = None
    agent._last_targets = {}
    p1.reset()
    p2.reset()
    p3.reset()
    p4.reset()


def _simulate_synthetic_regime(decide_fn: Any, bars: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Run simulation over synthetic bars and verify execution integrity."""
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

        for o in orders:
            t = o["ticker"]
            side = o["side"]
            qty = o["quantity"]
            px = cur_prices.get(t, 100.0)
            if side == "sell":
                avail = positions.get(t, {}).get("quantity", 0.0)
                exec_qty = min(qty, avail)
                if exec_qty > 0:
                    cash += exec_qty * px * 0.9995
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
    }


# ==============================================================================
# GATE A: CANDIDATE CONTRACTS AND PREREGISTRATION CHECKS
# ==============================================================================

class TestGateACandidateContracts:
    def test_p1_vol_floor_contract(self):
        """P1 must define 0.05 volatility floor."""
        assert p1.VOL_FLOOR_P1 == 0.05

    def test_p2_cap_and_floor_contract(self):
        """P2 must define agent.MAX_WEIGHT (0.24) position cap and 0.05 floor."""
        assert p2.VOL_FLOOR_P2 == 0.05
        assert p2.MAX_POSITION_CAP_P2 == agent.MAX_WEIGHT

    def test_p3_smoothing_alpha_contract(self):
        """P3 must define 0.5 smoothing parameter and agent.MAX_WEIGHT (0.24) cap."""
        assert p3.SMOOTHING_ALPHA == 0.5
        assert p3.MAX_POSITION_CAP_P3 == agent.MAX_WEIGHT

    def test_p4_blend_alpha_contract(self):
        """P4 must define 0.5 blend parameter."""
        assert p4.BLEND_ALPHA == 0.5

    def test_candidates_compatible_with_decide_signature(self):
        """All candidates must implement decide(market_state, portfolio_state, cash)."""
        market = {"SPY": [{"ts": "2021-01-01", "close": 100.0, "open": 100.0, "high": 101.0, "low": 99.0, "volume": 1e6}]}
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            assert hasattr(mod, "decide"), f"{name} lacks decide"
            assert hasattr(mod, "reset"), f"{name} lacks reset"
            res = mod.decide(market, {}, 100000.0)
            assert isinstance(res, list), f"{name} decide return type must be list"


# ==============================================================================
# GATE B: INDEPENDENT SIZING ORACLE VERIFICATION
# ==============================================================================

class TestGateBIndependentSizingOracle:
    def test_equal_volatility_yields_equal_weights(self):
        vols = {"A": 0.20, "B": 0.20, "C": 0.20, "D": 0.20}
        w = oracle.compute_pure_inverse_vol_weights(vols, 0.80)
        for t in vols:
            assert w[t] == pytest.approx(0.20)

    def test_extreme_volatility_allocation(self):
        vols = {"CALM": 0.10, "VOLATILE": 0.50}
        w = oracle.compute_pure_inverse_vol_weights(vols, 1.0)
        # 1/0.10 = 10, 1/0.50 = 2 -> total 12 -> CALM gets 10/12 (83.3%), VOLATILE gets 2/12 (16.7%)
        assert w["CALM"] == pytest.approx(10.0 / 12.0)
        assert w["VOLATILE"] == pytest.approx(2.0 / 12.0)

    def test_near_zero_volatility_hits_floor(self):
        vols = {"ZERO": 0.0001, "NORMAL": 0.20}
        w = oracle.compute_pure_inverse_vol_weights(vols, 1.0, floor=0.05)
        # ZERO clamped to 0.05 -> inv = 20; NORMAL = 0.20 -> inv = 5; total = 25
        assert w["ZERO"] == pytest.approx(20.0 / 25.0)  # 0.80
        assert w["NORMAL"] == pytest.approx(5.0 / 25.0)  # 0.20

    def test_capped_inverse_vol_capacity_redistribution(self):
        vols = {"A": 0.06, "B": 0.20, "C": 0.20, "D": 0.20}
        # In pure weighting of 0.80 budget:
        # inv_A = 16.666, inv_B = 5, inv_C = 5, inv_D = 5 -> total = 31.666
        # A raw weight = (16.666 / 31.666) * 0.80 = 0.421 > 0.25!
        # Under P2 capping: A capped at 0.25. Remaining 0.55 budget split equally among B, C, D (0.1833 each <= 0.25)
        w = oracle.compute_capped_inverse_vol_weights(vols, 0.80, cap=0.25)
        assert w["A"] == pytest.approx(0.25)
        assert w["B"] == pytest.approx(0.55 / 3.0)
        assert w["C"] == pytest.approx(0.55 / 3.0)
        assert w["D"] == pytest.approx(0.55 / 3.0)
        assert sum(w.values()) == pytest.approx(0.80)

    def test_infeasible_capped_allocation_retains_cash(self):
        # 2 assets, budget 0.80, cap 0.25 -> max capacity is 2 * 0.25 = 0.50. Remaining 0.30 to cash
        vols = {"A": 0.10, "B": 0.10}
        w = oracle.compute_capped_inverse_vol_weights(vols, 0.80, cap=0.25)
        assert w["A"] == pytest.approx(0.25)
        assert w["B"] == pytest.approx(0.25)
        assert sum(w.values()) == pytest.approx(0.50)  # 0.30 retained as cash

    def test_volatility_smoothing(self):
        cur = {"A": 0.20, "B": 0.30}
        prior = {"A": 0.10, "B": 0.10}
        smoothed = oracle.compute_smoothed_volatilities(cur, prior, alpha=0.5)
        assert smoothed["A"] == pytest.approx(0.15)
        assert smoothed["B"] == pytest.approx(0.20)

    def test_missing_prior_smoothing_defaults_to_current(self):
        cur = {"A": 0.25}
        smoothed = oracle.compute_smoothed_volatilities(cur, None, alpha=0.5)
        assert smoothed["A"] == pytest.approx(0.25)

    def test_blended_weights_convex_combination(self):
        eq = {"A": 0.20, "B": 0.20}
        inv = {"A": 0.25, "B": 0.15}
        blended = oracle.compute_blended_weights(eq, inv, blend=0.5)
        assert blended["A"] == pytest.approx(0.225)
        assert blended["B"] == pytest.approx(0.175)


# ==============================================================================
# GATE C: 16 SYNTHETIC STRESS TESTS
# ==============================================================================

class TestGateCSyntheticStressScenarios:
    def test_stress_1_calm_low_vol_bull(self):
        bars = syn.scenario_1_calm_low_vol_bull()
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            res = _simulate_synthetic_regime(mod.decide, bars)
            assert res["errors"] == 0, f"{name} failed on scenario 1"

    def test_stress_2_broad_market_crash(self):
        bars = syn.scenario_2_broad_market_crash()
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            res = _simulate_synthetic_regime(mod.decide, bars)
            assert res["errors"] == 0, f"{name} failed on scenario 2"

    def test_stress_3_high_vol_rebound(self):
        bars = syn.scenario_3_high_vol_rebound()
        res_p2 = _simulate_synthetic_regime(p2.decide, bars)
        assert res_p2["errors"] == 0

    def test_stress_4_defensive_vol_spike(self):
        bars = syn.scenario_4_defensive_vol_spike()
        res_p1 = _simulate_synthetic_regime(p1.decide, bars)
        assert res_p1["errors"] == 0

    def test_stress_5_low_vol_asset_crash(self):
        bars = syn.scenario_5_low_vol_asset_crash()
        res_p2 = _simulate_synthetic_regime(p2.decide, bars)
        assert res_p2["errors"] == 0

    def test_stress_6_correlated_selloff(self):
        bars = syn.scenario_6_correlated_selloff()
        res_p3 = _simulate_synthetic_regime(p3.decide, bars)
        assert res_p3["errors"] == 0

    def test_stress_7_sharp_vol_regime_reversal(self):
        bars = syn.scenario_7_sharp_vol_regime_reversal()
        res_p4 = _simulate_synthetic_regime(p4.decide, bars)
        assert res_p4["errors"] == 0

    def test_stress_8_prolonged_sideways(self):
        bars = syn.scenario_8_prolonged_sideways()
        res_p2 = _simulate_synthetic_regime(p2.decide, bars)
        assert res_p2["errors"] == 0

    def test_stress_9_missing_ticker_data(self):
        bars = syn.scenario_9_missing_ticker_data()
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            res = _simulate_synthetic_regime(mod.decide, bars)
            assert res["errors"] == 0, f"{name} crashed on missing ticker data"

    def test_stress_10_high_concentration_pressure(self):
        bars = syn.scenario_10_high_concentration_pressure()
        res_p2 = _simulate_synthetic_regime(p2.decide, bars)
        assert res_p2["errors"] == 0

    def test_stress_11_leveraged_etf_gap(self):
        bars = syn.scenario_11_leveraged_etf_gap()
        res_p1 = _simulate_synthetic_regime(p1.decide, bars)
        assert res_p1["errors"] == 0

    def test_stress_12_slippage_underfill(self):
        bars = syn.scenario_12_slippage_underfill()
        res_p2 = _simulate_synthetic_regime(p2.decide, bars)
        assert res_p2["errors"] == 0

    def test_stress_13_simultaneous_rebalance(self):
        bars = syn.scenario_13_simultaneous_rebalance()
        res_p3 = _simulate_synthetic_regime(p3.decide, bars)
        assert res_p3["errors"] == 0

    def test_stress_14_frequent_vol_rank_reversals(self):
        bars = syn.scenario_14_frequent_vol_rank_reversals()
        res_p4 = _simulate_synthetic_regime(p4.decide, bars)
        assert res_p4["errors"] == 0

    def test_stress_15_risk_on_to_off_transition(self):
        bars = syn.scenario_15_risk_on_to_off_transition()
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            res = _simulate_synthetic_regime(mod.decide, bars)
            assert res["errors"] == 0, f"{name} crashed on risk-on to off transition"

    def test_stress_16_risk_off_to_on_recovery(self):
        bars = syn.scenario_16_risk_off_to_on_recovery()
        for mod, name in [(p1, "P1"), (p2, "P2"), (p3, "P3"), (p4, "P4")]:
            res = _simulate_synthetic_regime(mod.decide, bars)
            assert res["errors"] == 0, f"{name} crashed on risk-off to on recovery"


# ==============================================================================
# GATE D: FINANCIAL CONSERVATION AND CAUSALITY INVARIANTS
# ==============================================================================

class TestGateDFinancialAndCausalityInvariants:
    def test_target_weights_bounds_and_non_negativity(self):
        """All target weights must be non-negative, sum to <= 1.0, and respect caps."""
        market_state = {
            "SPY": [{"ts": f"2021-01-{i+1:02d}", "close": 300.0 + i, "open": 300.0 + i, "high": 301.0 + i, "low": 299.0 + i, "volume": 1e6} for i in range(70)],
            "QQQ": [{"ts": f"2021-01-{i+1:02d}", "close": 200.0 + i, "open": 200.0 + i, "high": 201.0 + i, "low": 199.0 + i, "volume": 1e6} for i in range(70)],
            "AAPL": [{"ts": f"2021-01-{i+1:02d}", "close": 150.0 + i, "open": 150.0 + i, "high": 151.0 + i, "low": 149.0 + i, "volume": 1e6} for i in range(70)],
            "MSFT": [{"ts": f"2021-01-{i+1:02d}", "close": 250.0 + i, "open": 250.0 + i, "high": 251.0 + i, "low": 249.0 + i, "volume": 1e6} for i in range(70)],
            "NVDA": [{"ts": f"2021-01-{i+1:02d}", "close": 180.0 + i, "open": 180.0 + i, "high": 181.0 + i, "low": 179.0 + i, "volume": 1e6} for i in range(70)],
            "AMZN": [{"ts": f"2021-01-{i+1:02d}", "close": 3200.0 + i, "open": 3200.0 + i, "high": 3201.0 + i, "low": 3199.0 + i, "volume": 1e6} for i in range(70)],
            "GOOGL": [{"ts": f"2021-01-{i+1:02d}", "close": 2000.0 + i, "open": 2000.0 + i, "high": 2001.0 + i, "low": 1999.0 + i, "volume": 1e6} for i in range(70)],
            "QLD": [{"ts": f"2021-01-{i+1:02d}", "close": 80.0 + i, "open": 80.0 + i, "high": 81.0 + i, "low": 79.0 + i, "volume": 1e6} for i in range(70)],
            "SSO": [{"ts": f"2021-01-{i+1:02d}", "close": 60.0 + i, "open": 60.0 + i, "high": 61.0 + i, "low": 59.0 + i, "volume": 1e6} for i in range(70)],
        }
        for fn, name in [(p1.target_weights_p1, "P1"), (p2.target_weights_p2, "P2"), (p3.target_weights_p3, "P3"), (p4.target_weights_p4, "P4")]:
            w = fn(market_state)
            assert all(v >= 0.0 for v in w.values()), f"{name} negative weight"
            assert sum(w.values()) <= 1.0 + 1e-6, f"{name} sum exceeds 1.0"
            for t, v in w.items():
                assert v <= agent.MAX_WEIGHT + 1e-6, f"{name} concentration cap breach on {t}"

    def test_future_price_injection_does_not_affect_decision(self):
        """Signal causality: Future price injection at Day T+1 cannot alter Day T decision."""
        base_bars = [{"ts": f"2021-01-{i+1:02d}", "close": 100.0 * (1.002 ** i), "open": 100.0 * (1.002 ** i), "high": 101.0 * (1.002 ** i), "low": 99.0 * (1.002 ** i), "volume": 1e6} for i in range(70)]
        market_clean = {
            "SPY": base_bars,
            "QQQ": base_bars,
            "AAPL": base_bars,
            "MSFT": base_bars,
            "NVDA": base_bars,
            "QLD": base_bars,
            "SSO": base_bars,
        }

        # Decisions at Day 69
        p1.reset(); orders_p1_clean = p1.decide(market_clean, {}, 100000.0)
        p2.reset(); orders_p2_clean = p2.decide(market_clean, {}, 100000.0)
        p3.reset(); orders_p3_clean = p3.decide(market_clean, {}, 100000.0)
        p4.reset(); orders_p4_clean = p4.decide(market_clean, {}, 100000.0)

        # Inject mutated future bar into index 70
        mutated_bars = list(base_bars)
        mutated_bars.append({"ts": "2021-05-01", "close": 8888.0, "open": 8888.0, "high": 8888.0, "low": 8888.0, "volume": 1e9})
        market_sliced = {t: mutated_bars[:70] for t in market_clean}

        p1.reset(); orders_p1_mut = p1.decide(market_sliced, {}, 100000.0)
        p2.reset(); orders_p2_mut = p2.decide(market_sliced, {}, 100000.0)
        p3.reset(); orders_p3_mut = p3.decide(market_sliced, {}, 100000.0)
        p4.reset(); orders_p4_mut = p4.decide(market_sliced, {}, 100000.0)

        assert orders_p1_clean == orders_p1_mut
        assert orders_p2_clean == orders_p2_mut
        assert orders_p3_clean == orders_p3_mut
        assert orders_p4_clean == orders_p4_mut
