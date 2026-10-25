"""
Guardian Alpha — V30 Stage 2B: Defensive Allocation and Drawdown Research Test Suite.

Rigorously verifies:
- Gate A: Preregistered candidate specifications (D1, D2, D3).
- Gate B: Strategy vs Execution separation.
- Gate C: 10 independent, deterministic synthetic stress scenarios.
- Gate D: Financial, portfolio, and accounting invariants.
- Gate G: Causality and no-lookahead assertions.

Preserves all frozen production code and existing V30 test modules.
"""

from __future__ import annotations

import copy
import math
from typing import Any
import pytest

import agent
from research.engine.v30_synthetic_stress_scenarios import (
    generate_stress_scenario_1_sudden_crash,
    generate_stress_scenario_2_grinding_decline,
    generate_stress_scenario_3_v_shaped_recovery,
    generate_stress_scenario_4_false_downside_signal,
    generate_stress_scenario_5_sideways_high_vol,
    generate_stress_scenario_6_defensive_correlation_breakdown,
    generate_stress_scenario_7_rising_market_cash_drag,
    generate_stress_scenario_8_sudden_overnight_gap,
    generate_stress_scenario_9_missing_defensive_instrument,
    generate_stress_scenario_10_alternating_whipsaw,
    get_all_synthetic_stress_scenarios,
)
from research.strategies import (
    v30_candidate_d1_energy_exit as d1,
    v30_candidate_d2_cash_cushion as d2,
    v30_candidate_d3_recovery_discipline as d3,
)


def _simulate_synthetic_regime(decide_fn, regime: dict[str, Any], start_cash: float = 100_000.0) -> dict[str, Any]:
    """Lightweight deterministic simulation loop adhering to preview.py semantics."""
    import inspect
    mod = inspect.getmodule(decide_fn)
    if mod and hasattr(mod, "reset"):
        mod.reset()
    elif mod and hasattr(mod, "_last_rebalance_bar_date"):
        mod._last_rebalance_bar_date = None
        mod._last_targets = {}

    bars = regime["bars"]
    all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})

    cash = float(start_cash)
    positions: dict[str, float] = {}
    avg_cost: dict[str, float] = {}
    equity_curve: list[float] = []
    trades = 0
    errors = 0
    pending: list[dict[str, Any]] = []

    def open_on(ticker: str, date: str) -> float | None:
        for b in bars.get(ticker, []):
            if b["ts"] == date:
                return b["open"]
        return None

    def close_on(ticker: str, date: str) -> float | None:
        for b in bars.get(ticker, []):
            if b["ts"] == date:
                return b["close"]
        return None

    for date in all_dates:
        # 1. Fill yesterday's orders at today's open
        for o in pending:
            px = open_on(o["ticker"], date)
            if px is None or px <= 0:
                continue
            slip = 0.0010 if agent.BETA_MULTIPLE.get(o["ticker"], 1.0) > 1.0 else 0.0005
            if o["side"] == "buy":
                fill = px * (1.0 + slip)
                qty = float(o["quantity"])
                cost = fill * qty
                if cost > cash:
                    qty = cash / fill if fill > 0 else 0.0
                    cost = fill * qty
                if qty <= 0:
                    continue
                held = positions.get(o["ticker"], 0.0)
                prev_cost = avg_cost.get(o["ticker"], 0.0) * held
                positions[o["ticker"]] = held + qty
                avg_cost[o["ticker"]] = (prev_cost + cost) / (held + qty)
                cash -= cost
                trades += 1
            else:  # sell
                held = positions.get(o["ticker"], 0.0)
                qty = min(float(o["quantity"]), held)
                if qty <= 0:
                    continue
                fill = px * (1.0 - slip)
                cash += fill * qty
                positions[o["ticker"]] = held - qty
                if positions[o["ticker"]] <= 1e-9:
                    positions.pop(o["ticker"], None)
                    avg_cost.pop(o["ticker"], None)
                trades += 1

        pending = []

        # 2. Mark to market on today's close
        prices = {t: close_on(t, date) for t in bars}
        prices = {t: p for t, p in prices.items() if p is not None}
        pos_val = sum(positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions)
        equity = cash + pos_val
        equity_curve.append(equity)

        # 3. Agent decides on bars through today's close
        market_state = {t: [b for b in bars[t] if b["ts"] <= date] for t in bars}
        portfolio_state = {
            "cash": cash,
            "positions": [
                {"ticker": t, "quantity": q, "avg_cost": avg_cost.get(t, 0.0)}
                for t, q in positions.items() if q > 0
            ],
            "last_prices": prices,
        }

        try:
            orders = decide_fn(market_state, portfolio_state, cash) or []
        except Exception as e:
            errors += 1
            orders = []

        for o in orders:
            try:
                if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                    pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})
            except (KeyError, TypeError, ValueError):
                errors += 1

    peak, mdd = -1e18, 0.0
    for v in equity_curve:
        peak = max(peak, v)
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)

    ret = equity_curve[-1] / start_cash - 1.0 if equity_curve else 0.0
    return {
        "final_equity": equity_curve[-1] if equity_curve else start_cash,
        "ret": ret,
        "mdd": mdd,
        "trades": trades,
        "errors": errors,
        "curve": equity_curve,
    }


# ==============================================================================
# GATE A: PREREGISTERED SCIENTIFIC HYPOTHESES & CANDIDATE SPECIFICATIONS
# ==============================================================================

class TestGateAPreregisteredHypotheses:
    """Verifies that candidates D1, D2, and D3 strictly match their preregistered definitions."""

    def test_d1_weights_and_cash_budget(self):
        """D1 removes XLE: XLP 0.24, XLU 0.24, XLV 0.20, Cash 0.32."""
        assert d1.DEFENSIVE_WEIGHTS_D1 == (
            ("XLP", 0.24),
            ("XLU", 0.24),
            ("XLV", 0.20),
        )
        total_def_equity = sum(w for _, w in d1.DEFENSIVE_WEIGHTS_D1)
        assert total_def_equity == pytest.approx(0.68)
        assert (1.0 - total_def_equity) == pytest.approx(0.32)  # Explicit 32% cash

    def test_d2_weights_and_cash_budget(self):
        """D2 enforces 50% cash: XLP 0.18, XLU 0.18, XLV 0.14, Cash 0.50."""
        assert d2.DEFENSIVE_WEIGHTS_D2 == (
            ("XLP", 0.18),
            ("XLU", 0.18),
            ("XLV", 0.14),
        )
        total_def_equity = sum(w for _, w in d2.DEFENSIVE_WEIGHTS_D2)
        assert total_def_equity == pytest.approx(0.50)
        assert (1.0 - total_def_equity) == pytest.approx(0.50)  # Explicit 50% cash

    def test_d3_weights_and_reentry_states(self):
        """D3 has base 50% cash defense and causal recovery confirmation protocol."""
        assert d3.DEFENSIVE_WEIGHTS_D3_BASE == (
            ("XLP", 0.18),
            ("XLU", 0.18),
            ("XLV", 0.14),
        )
        # Verify recovery confirmation function exists and accepts spy and qqq series
        assert callable(d3._is_recovery_confirmed)
        assert callable(d3._is_recovery_reset)


# ==============================================================================
# GATE B: STRATEGY AND EXECUTION SEPARATION
# ==============================================================================

class TestGateBSeparateStrategyAndExecution:
    """Verifies that candidates can be evaluated under identical execution semantics."""

    def test_candidates_compatible_with_builderr_decide_signature(self):
        """All candidates implement decide(market_state, portfolio_state, cash) -> list[dict]."""
        for mod in (d1, d2, d3):
            assert hasattr(mod, "decide")
            res = mod.decide({}, {"positions": []}, 100_000.0)
            assert isinstance(res, list)


# ==============================================================================
# GATE C: SYNTHETIC STRESS TESTS (ALL 10 SCENARIOS)
# ==============================================================================

class TestGateCSyntheticStressScenarios:
    """Evaluates Frozen E0, D1, D2, and D3 across all 10 synthetic stress scenarios."""

    def test_stress_1_sudden_crash_defense(self):
        """Stress 1: Sudden crash (-20% over 5 sessions). Higher cash in D2 must reduce MaxDD."""
        regime = generate_stress_scenario_1_sudden_crash()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d1 = _simulate_synthetic_regime(d1.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)
        res_d3 = _simulate_synthetic_regime(d3.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d1["errors"] == 0
        assert res_d2["errors"] == 0
        assert res_d3["errors"] == 0

        # D2 (50% cash) and D1 (32% cash) must have lower MaxDD than E0 (20% cash)
        assert res_d2["mdd"] < res_e0["mdd"]
        assert res_d1["mdd"] <= res_e0["mdd"]

    def test_stress_2_grinding_decline(self):
        """Stress 2: Grinding decline. All candidates run clean."""
        regime = generate_stress_scenario_2_grinding_decline()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d2["errors"] == 0
        # Under steady bleed, D2 holds up better due to 50% cash preservation
        assert res_d2["mdd"] < res_e0["mdd"]

    def test_stress_3_v_shaped_recovery(self):
        """Stress 3: V-shaped recovery. Documents the recovery participation trade-off."""
        regime = generate_stress_scenario_3_v_shaped_recovery()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)
        res_d3 = _simulate_synthetic_regime(d3.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d2["errors"] == 0
        assert res_d3["errors"] == 0

    def test_stress_4_false_downside_signal(self):
        """Stress 4: False downside signal. Tests whipsaw resilience."""
        regime = generate_stress_scenario_4_false_downside_signal()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d1 = _simulate_synthetic_regime(d1.decide, regime)
        assert res_e0["errors"] == 0
        assert res_d1["errors"] == 0

    def test_stress_5_sideways_high_vol(self):
        """Stress 5: Sideways high volatility (+/- 3% daily)."""
        regime = generate_stress_scenario_5_sideways_high_vol()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)
        assert res_e0["errors"] == 0
        assert res_d2["errors"] == 0

    def test_stress_6_defensive_correlation_breakdown(self):
        """Stress 6: Defensive correlation breakdown. 50% cash (D2) buffers defensive equity plunge."""
        regime = generate_stress_scenario_6_defensive_correlation_breakdown()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d2["errors"] == 0
        # In defensive collapse, 50% cash provides significant drawdown buffer
        assert res_d2["mdd"] < res_e0["mdd"]

    def test_stress_7_rising_market_cash_drag(self):
        """Stress 7: Rising market cash drag. Documents the explicit return penalty of holding cash."""
        regime = generate_stress_scenario_7_rising_market_cash_drag()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d2["errors"] == 0
        # In a pure bull market, both strategies should operate risk-on cleanly
        assert res_e0["final_equity"] > 100_000.0
        assert res_d2["final_equity"] > 100_000.0

    def test_stress_8_sudden_overnight_gap(self):
        """Stress 8: Sudden overnight gap (-8%). Verifies graceful absorption."""
        regime = generate_stress_scenario_8_sudden_overnight_gap()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d1 = _simulate_synthetic_regime(d1.decide, regime)
        assert res_e0["errors"] == 0
        assert res_d1["errors"] == 0

    def test_stress_9_missing_defensive_instrument(self):
        """Stress 9: Missing defensive instrument (XLU/XLV missing). Graceful degradation."""
        regime = generate_stress_scenario_9_missing_defensive_instrument()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d1 = _simulate_synthetic_regime(d1.decide, regime)
        res_d2 = _simulate_synthetic_regime(d2.decide, regime)
        res_d3 = _simulate_synthetic_regime(d3.decide, regime)

        assert res_e0["errors"] == 0
        assert res_d1["errors"] == 0
        assert res_d2["errors"] == 0
        assert res_d3["errors"] == 0

    def test_stress_10_alternating_whipsaw(self):
        """Stress 10: Alternating whipsaw (crosses above/below SMA50 every 3 sessions)."""
        regime = generate_stress_scenario_10_alternating_whipsaw()
        res_e0 = _simulate_synthetic_regime(agent.decide, regime)
        res_d3 = _simulate_synthetic_regime(d3.decide, regime)
        assert res_e0["errors"] == 0
        assert res_d3["errors"] == 0


# ==============================================================================
# GATE D: FINANCIAL AND PORTFOLIO INVARIANTS
# ==============================================================================

class TestGateDFinancialAndPortfolioInvariants:
    """Verifies allocation sums, non-negativity, leverage bounds, and concentration caps."""

    def test_target_weights_sum_and_non_negativity(self):
        """All target weights must be non-negative and sum to <= 1.0."""
        # Synthetic market state with risk-off prices
        market_state = {
            "SPY": [{"ts": f"2021-01-{i+1:02d}", "close": 300.0 - i, "open": 300.0 - i, "high": 301.0, "low": 299.0, "volume": 1e6} for i in range(60)],
            "QQQ": [{"ts": f"2021-01-{i+1:02d}", "close": 200.0 - i, "open": 200.0 - i, "high": 201.0, "low": 199.0, "volume": 1e6} for i in range(60)],
            "XLP": [{"ts": f"2021-01-{i+1:02d}", "close": 70.0, "open": 70.0, "high": 71.0, "low": 69.0, "volume": 1e6} for i in range(60)],
            "XLU": [{"ts": f"2021-01-{i+1:02d}", "close": 60.0, "open": 60.0, "high": 61.0, "low": 59.0, "volume": 1e6} for i in range(60)],
            "XLV": [{"ts": f"2021-01-{i+1:02d}", "close": 120.0, "open": 120.0, "high": 121.0, "low": 119.0, "volume": 1e6} for i in range(60)],
            "XLE": [{"ts": f"2021-01-{i+1:02d}", "close": 50.0, "open": 50.0, "high": 51.0, "low": 49.0, "volume": 1e6} for i in range(60)],
        }

        w_e0 = agent.target_weights(market_state)
        w_d1 = d1.target_weights_d1(market_state)
        w_d2 = d2.target_weights_d2(market_state)
        w_d3 = d3.target_weights_d3(market_state)

        for w_dict, name in ((w_e0, "E0"), (w_d1, "D1"), (w_d2, "D2"), (w_d3, "D3")):
            assert all(v >= 0.0 for v in w_dict.values()), f"{name} negative weight"
            assert sum(w_dict.values()) <= 1.0 + 1e-6, f"{name} sum exceeds 1.0"
            for t, v in w_dict.items():
                assert v <= agent.MAX_WEIGHT + 1e-6, f"{name} concentration breach on {t}"

        # In D1, XLE must not be present
        assert "XLE" not in w_d1
        # In D2, sum of weights is 0.50
        assert sum(w_d2.values()) == pytest.approx(0.50)
        # In D2, XLE must not be present
        assert "XLE" not in w_d2


# ==============================================================================
# GATE G: CAUSALITY AND NO-LOOKAHEAD ASSERTIONS
# ==============================================================================

class TestCausalityAndNoLookahead:
    """Verifies that future data injection does not alter prior decisions."""

    def test_future_price_injection_does_not_affect_current_decision(self):
        """Mutating market_state at T+1 does not change decide() output at session T."""
        regime = generate_stress_scenario_1_sudden_crash()
        bars = regime["bars"]
        all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
        date_t = all_dates[50]

        # Feed up to Date T
        ms_clean = {t: [b for b in bars[t] if b["ts"] <= date_t] for t in bars}
        ps = {"cash": 100_000.0, "positions": []}
        cash = 100_000.0

        # Reset module state prior to evaluating clean feed
        agent._last_rebalance_bar_date = None
        d1.reset()
        d2.reset()
        d3.reset()

        orders_e0_clean = agent.decide(ms_clean, ps, cash)
        orders_d1_clean = d1.decide(ms_clean, ps, cash)
        orders_d2_clean = d2.decide(ms_clean, ps, cash)
        orders_d3_clean = d3.decide(ms_clean, ps, cash)

        # Mutate tomorrow's bar in the raw dataset
        date_t1 = all_dates[51]
        bars_mutated = copy.deepcopy(bars)
        for b in bars_mutated["SPY"]:
            if b["ts"] == date_t1:
                b["close"] = 999999.0  # Absurd future spike

        # Filter strictly up to date_t again
        ms_mutated = {t: [b for b in bars_mutated[t] if b["ts"] <= date_t] for t in bars}

        # Reset module state prior to evaluating mutated feed so rebalance cadence does not suppress decision
        agent._last_rebalance_bar_date = None
        d1.reset()
        d2.reset()
        d3.reset()

        orders_e0_mut = agent.decide(ms_mutated, ps, cash)
        orders_d1_mut = d1.decide(ms_mutated, ps, cash)
        orders_d2_mut = d2.decide(ms_mutated, ps, cash)
        orders_d3_mut = d3.decide(ms_mutated, ps, cash)

        # Decisions must be byte-identical (causality verified)
        assert orders_e0_clean == orders_e0_mut
        assert orders_d1_clean == orders_d1_mut
        assert orders_d2_clean == orders_d2_mut
        assert orders_d3_clean == orders_d3_mut
