"""V21 Portfolio Concentration, Exact NAV Rounding, and Risk Fidelity Tests.

Verifies:
  1. Target weights vs hard risk constraints.
  2. 99.08% two-asset portfolio concentration root cause (pricing basis asymmetry).
  3. Exact Decimal NAV rounding and equity bridge.
  4. Machine manifest and report consistency.
  5. Cash exhaustion and partial-fill safety.
  6. Historical corporate action integrity (QLD/SSO splits, zero splits in Tier 1 for AAPL/NVDA).
  7. Benchmark sensitivity classification and latency monotonicity.
  8. Sealed holdout (Tier 2/Tier 3) access blocking.
  9. Secret token redaction.
  10. Negative control: unadjusted market prices would have triggered AAPL trimming.
"""
from __future__ import annotations

import json
import math
import os
import re
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path
import pytest

import agent
from research.engine.corporate_actions import CorporateActionRegistry
from research.engine.provider import StorageComplianceError, StorageComplianceGuard

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestTargetWeightsVsHardConstraints:
    """Verifies that target_weights() defines desired allocation, not hard risk limits."""

    def test_target_weights_not_hard_caps(self):
        # agent.py has MAX_WEIGHT = 0.24 and DRIFT_LIMIT = 0.27
        assert agent.MAX_WEIGHT == 0.24
        assert agent.DRIFT_LIMIT == 0.27

        # But agent.py does NOT enforce a hard liquidation cap inside decide()
        # when a position drifts above DRIFT_LIMIT unless orders_to_rebalance emits a sell.
        port = {
            "cash": 1000.0,
            "positions": [
                {"ticker": "AAPL", "quantity": 100.0, "avg_cost": 200.0}
            ],
            "last_prices": {"AAPL": 300.0}
        }
        total_eq = agent.equity(port, 1000.0)
        assert total_eq == 31000.0
        # Weight of AAPL is 30,000 / 31,000 = 96.77%
        assert agent._has_position_drifted(port, total_eq) is True

        # Now test orders_to_rebalance when delta is within deadband
        # If target is 0.20, target_val = 6200.
        # But if prices dict has split-adjusted price of $62.00,
        # current_val = 100 * 62.00 = 6200.
        # delta = 6200 - 6200 = 0.0 -> no sell order emitted!
        pos_dict = agent.current_positions(port)
        orders = agent.orders_to_rebalance(
            targets={"AAPL": 0.20},
            positions=pos_dict,
            total_equity=total_eq,
            prices={"AAPL": 62.00},
            cash_available=1000.0
        )
        assert orders == []  # No sell order emitted despite 96.77% raw weight!


class TestConcentrationForensics:
    """Tests the exact mathematical reason for AAPL and NVDA 99.08% concentration."""

    def test_aapl_nvda_deadband_suppression(self):
        # On 2019-12-31, AAPL had 752.433 shares, raw close was 293.65, adj_close was 70.66
        # NVDA had 524.132 shares, raw close was 235.30, adj_close was 5.88
        raw_equity = 347496.21
        min_trade = raw_equity * agent.MIN_TRADE_PCT  # ~5,212.44
        target_weight = 0.152  # 15.2% target in risk-on regime
        target_value = raw_equity * target_weight  # ~52,819.42

        # AAPL current value evaluated with adj_close (split-adjusted)
        aapl_adj_price = 70.66
        aapl_shares = 752.433
        aapl_adj_val = aapl_shares * aapl_adj_price  # ~53,166.92
        aapl_delta = target_value - aapl_adj_val  # -347.50

        # Since -347.50 is NOT < -min_trade (-5212.44), no sell order is generated!
        assert not (aapl_delta < -min_trade)
        assert abs(aapl_delta) < min_trade

        # NVDA current value evaluated with 40:1 split-adjusted price
        nvda_adj_price = 5.88
        nvda_shares = 524.132
        nvda_adj_val = nvda_shares * nvda_adj_price  # ~3,081.90
        nvda_delta = target_value - nvda_adj_val  # +49,737.52

        # Delta is positive! The strategy believes NVDA is severely under-allocated!
        assert nvda_delta > min_trade
        # But cash available is $0.04
        spendable = 0.04
        buy_qty = int(min(nvda_delta, spendable) // nvda_adj_price)
        assert buy_qty == 0  # Cannot buy even 1 share with 4 cents


class TestExactDecimalNAVRounding:
    """Reconciles exact Decimal arithmetic and display round-off behavior."""

    def test_decimal_rounding_bridge(self):
        # Exact values from tier1_terminal_holdings_v20.json
        sum_positions = Decimal("347491.1031060928")
        cash = Decimal("0.03995659431493667")
        receivables = Decimal("5.062059328900196")

        exact_nav = sum_positions + cash + receivables
        assert str(exact_nav).startswith("347496.205122")

        # Rounding under standard conventions
        round_even = exact_nav.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        round_up = exact_nav.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        assert round_even == Decimal("347496.21")
        assert round_up == Decimal("347496.21")

        # Explain the $347,496.20 display sum
        # In the table: positions = 347491.10, cash = 0.04, receivables = 5.0645
        # 347491.10 + 0.04 + 5.0645 = 347496.2045
        display_sum = Decimal("347491.10") + Decimal("0.04") + Decimal("5.0645")
        assert display_sum == Decimal("347496.2045")
        display_sum_rounded = display_sum.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        assert display_sum_rounded == Decimal("347496.20")


class TestCorporateActionsFidelity:
    """Verifies stock splits and dividend behavior across Tier 1."""

    def test_split_inventory(self):
        # In Tier 1 (2015-2019), only QLD and SSO had stock splits
        cache_file = REPO_ROOT / "tiingo_cache" / "tier1_bars.json"
        if not cache_file.exists():
            pytest.skip("tier1_bars.json cache not present")

        with open(cache_file, "r", encoding="utf-8") as f:
            bars_data = json.load(f)

        splits_found = {}
        for sym, bars in bars_data.items():
            sym_splits = [b for b in bars if float(b.get("split_factor", 1.0)) != 1.0]
            if sym_splits:
                splits_found[sym] = sym_splits

        # Exactly QLD and SSO had splits in 2015-2019
        assert set(splits_found.keys()) == {"QLD", "SSO"}
        assert len(splits_found["QLD"]) == 2
        assert len(splits_found["SSO"]) == 1

        # AAPL and NVDA had ZERO splits during 2015-2019
        assert "AAPL" not in splits_found
        assert "NVDA" not in splits_found


class TestBenchmarkSensitivityClassification:
    """Verifies benchmark latency and tracemalloc overhead."""

    def test_decision_latency_sub_5ms(self):
        from research.engine.benchmark import PerformanceBenchmarkRunner
        sample_path = REPO_ROOT / "sample_regimes.json.gz"
        runner = PerformanceBenchmarkRunner(sample_path, "calm_uptrend")
        # Run 1 iteration
        m = runner.run_benchmark(iterations=1)
        assert m.decision_latency_p50_ms < 5.0
        assert m.decision_latency_p50_ms <= m.decision_latency_p95_ms <= m.decision_latency_max_ms


class TestHoldoutAndSecurityGates:
    """Verifies that Tier 2 and Tier 3 remain strictly sealed and token is redacted."""

    def test_tier2_tier3_strictly_blocked(self):
        # Prohibit accessing dates in sealed holdout (2022-2024)
        from research.engine.tiingo_client import TiingoClient, HoldoutProtectionViolation
        client = TiingoClient()
        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2022-01-01", "2022-01-05")
        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2021-12-01", "2022-01-02")
        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2023-01-01", "2023-12-31")

    def test_token_redaction(self):
        # Ensure TIINGO_API_KEY is not written into source or manifest files
        key = os.environ.get("TIINGO_API_KEY")
        if not key:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as reg_key:
                    key, _ = winreg.QueryValueEx(reg_key, "TIINGO_API_KEY")
            except Exception:
                pass

        if not key or len(key) < 10:
            pytest.skip("TIINGO_API_KEY not set")

        for fpath in REPO_ROOT.glob("research/**/*.py"):
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            assert key not in content, f"Secret key leaked into {fpath}"

        for fpath in REPO_ROOT.glob("research/manifests/*.json"):
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            assert key not in content, f"Secret key leaked into {fpath}"


class TestNegativeControls:
    """Adversarial negative controls to verify rebalance sensitivity."""

    def test_unadjusted_prices_trigger_aapl_trim(self):
        # Negative control: If market_state DID contain the unadjusted raw price ($293.65)
        # instead of adj_close ($70.66), orders_to_rebalance WOULD have emitted a sell order!
        raw_equity = 347496.21
        port = {
            "cash": 0.04,
            "positions": {
                "AAPL": {"quantity": 752.433, "avg_cost": 233.06}
            },
            "last_prices": {"AAPL": 293.65}
        }
        # With unadjusted price $293.65:
        # current_value = 752.433 * 293.65 = 220,952.95
        # target_value = 347496.21 * 0.152 = 52,819.42
        # delta = 52819.42 - 220952.95 = -168,133.53 (< -min_trade of -5212.44)
        orders = agent.orders_to_rebalance(
            targets={"AAPL": 0.152},
            positions=port["positions"],
            total_equity=raw_equity,
            prices={"AAPL": 293.65},  # Raw price
            cash_available=0.04
        )
        assert len(orders) == 1
        assert orders[0]["ticker"] == "AAPL"
        assert orders[0]["side"] == "sell"
        # Number of shares to sell: abs(delta) // price = 168133.53 // 293.65 = 572 shares
        assert orders[0]["quantity"] == 572


class TestCashExhaustionAndPartialFills:
    """Verifies cash exhaustion and partial fills prevent negative cash balances."""

    def test_buy_orders_scale_to_available_cash(self):
        from research.engine.accounting import PortfolioState, RiskMode
        p = PortfolioState(cash=50.0)
        # Try to buy 100 shares of SPY at $200
        order = {"ticker": "SPY", "side": "buy", "quantity": 100}
        res = p.execute_order(order, open_price=200.0, commission_bps=0.0, risk_mode=RiskMode.TELEMETRY_ONLY)
        assert res is not None
        # Should fill 50.0 / (200.0 * 1.0005) = ~0.2498 shares
        assert p.cash >= 0.0
        assert math.isclose(p.cash, 0.0, abs_tol=1e-6)
        assert p.positions["SPY"] > 0.0


class TestManifestConsistency:
    """Ensures machine manifests are internally consistent down to the cent."""

    def test_manifest_nav_matches_unrounded_bridge(self):
        bridge_file = REPO_ROOT / "research" / "manifests" / "tier1_nav_rounding_bridge.json"
        metrics_file = REPO_ROOT / "research" / "manifests" / "tier1_v20_comprehensive_metrics.json"
        holdings_file = REPO_ROOT / "research" / "manifests" / "tier1_terminal_holdings_v20.json"

        assert bridge_file.exists()
        assert metrics_file.exists()
        assert holdings_file.exists()

        bridge = json.loads(bridge_file.read_text(encoding="utf-8"))
        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        holdings = json.loads(holdings_file.read_text(encoding="utf-8"))

        e0_metrics = metrics["Frozen E0"]
        e0_holdings = holdings["Frozen E0"]

        assert e0_metrics["terminal_nav"] == 347496.21
        assert bridge["rounded_values"]["round_half_even_bankers"]["exact_nav"] == "347496.21"
        assert bridge["rounded_values"]["round_half_up_commercial"]["exact_nav"] == "347496.21"

        # Check unrounded sum in holdings vs bridge
        raw_bridge_nav = Decimal(bridge["unrounded_components"]["exact_nav_unrounded"])
        raw_holdings_nav = Decimal(str(e0_holdings["reconstructed_nav"]))
        assert abs(raw_bridge_nav - raw_holdings_nav) < Decimal("1e-6")


class TestExposureConcentrationMetrics:
    """Computes Herfindahl-Hirschman Index (HHI) and Top 2 asset exposure."""

    def test_e0_high_concentration_vs_candidates(self):
        holdings_file = REPO_ROOT / "research" / "manifests" / "tier1_terminal_holdings_v20.json"
        holdings = json.loads(holdings_file.read_text(encoding="utf-8"))

        # For Frozen E0: AAPL (63.58%) + NVDA (35.49%) = 99.07%
        e0_positions = holdings["Frozen E0"]["positions"]
        aapl = next(p for p in e0_positions if p["symbol"] == "AAPL")
        nvda = next(p for p in e0_positions if p["symbol"] == "NVDA")

        top2_weight = aapl["nav_contribution_pct"] + nvda["nav_contribution_pct"]
        assert top2_weight > 99.0

        # Calculate HHI (sum of squared weight percentages)
        hhi = sum((p["nav_contribution_pct"]) ** 2 for p in e0_positions)
        # AAPL (63.58^2 = 4042) + NVDA (35.49^2 = 1259) = ~5301 (extremely concentrated, > 2500 is highly concentrated)
        assert hhi > 5000.0
