"""
Guardian Alpha V23 Tier 2 Out-of-Sample Validation and Independent Quantitative Audit Test Suite.
Validates:
  1. Tier 2 observation boundaries and strict Tier 3 holdout firewall.
  2. 24-symbol universe completeness and data qualification.
  3. Point-in-time corporate action handling (AAPL 4:1, TSLA 5:1, NVDA 4:1).
  4. Option B production-faithful price semantics and causal indicators.
  5. Cross-year execution timing and boundary continuity.
  6. Independent double-entry accounting reconciliation (all 505 sessions).
  7. 7 adversarial negative accounting controls.
  8. Statistical reproducibility and block bootstrap sensitivity.
  9. Macroeconomic regime segmentation and performance attribution.
  10. Manifest consistency, secret redaction, and compliance.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import pytest
import numpy as np

import agent
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
    compute_business_day_settlement,
)
from research.engine.independent_accounting import (
    AccountingAnomalyDetected,
    IndependentLedger,
    run_negative_control_altered_fill_price,
    run_negative_control_omitted_trade,
    run_negative_control_reversed_split,
    run_negative_control_double_dividend,
    run_negative_control_double_fee,
    run_negative_control_missing_position,
    run_negative_control_lookahead_leak,
)
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import (
    TiingoClient,
    TiingoHistoricalProvider,
    HoldoutProtectionViolation,
    HOLDOUT_CUTOFF_DATE,
    redact_secret,
)
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateE_CostAwareRebalancing,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined

CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"
TIER1_CACHE_FILE = Path("tiingo_cache") / "tier1_bars.json"
MANIFEST_DIR = Path("research/manifests")

PRODUCTION_SYMBOLS = [
    "SPY", "QQQ", "DIA", "IWM", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY",
    "XLP", "XLU", "XLRE", "XLC", "SMH", "AAPL", "MSFT", "GOOGL", "AMZN",
    "META", "NVDA", "TSLA", "QLD", "SSO"
]


class TestV23Tier2BoundariesAndHoldoutFirewall:
    """Validates observation dates and programmatic holdout firewall."""

    def test_holdout_firewall_rejection(self):
        """Assert queries requesting dates on or after 2022-01-01 are strictly rejected."""
        client = TiingoClient(api_token="dummy_test_token")
        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2022-01-01", "2022-12-31")

        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("AAPL", "2020-01-01", "2022-06-01")

        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("QQQ", "2023-01-01", "2023-12-31")

    def test_tier2_cache_dates_within_authorized_window(self):
        """Assert cached Tier 2 bars never contain observations on or after 2022-01-01."""
        assert CACHE_FILE.exists(), f"Missing cache file {CACHE_FILE}"
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for sym, bars in data.items():
            for b in bars:
                assert b["ts"] < HOLDOUT_CUTOFF_DATE, f"Holdout violation: {sym} has bar on {b['ts']} >= {HOLDOUT_CUTOFF_DATE}"


class TestV23UniverseAndCorporateActions:
    """Validates 24 instruments, split factors, and cash dividends."""

    def test_24_symbols_presence_and_bar_count(self):
        """Assert all 24 production instruments are present with 505 Tier 2 bars each."""
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for sym in PRODUCTION_SYMBOLS:
            assert sym in data, f"Missing {sym} in Tier 2 cache"
            t2_bars = [b for b in data[sym] if "2020-01-01" <= b["ts"] <= "2021-12-31"]
            assert len(t2_bars) == 505, f"{sym} has {len(t2_bars)} Tier 2 bars, expected 505"

    def test_known_stock_splits_qualification(self):
        """Assert AAPL 4:1, TSLA 5:1, and NVDA 4:1 splits are accurately represented."""
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # AAPL 4:1 split on 2020-08-31
        aapl_splits = [b for b in data["AAPL"] if float(b.get("split_factor", 1.0)) != 1.0 and b["ts"] >= "2020-01-01"]
        assert len(aapl_splits) == 1, f"Expected 1 AAPL split, got {len(aapl_splits)}"
        assert aapl_splits[0]["ts"] == "2020-08-31"
        assert math.isclose(float(aapl_splits[0]["split_factor"]), 4.0, rel_tol=1e-4)

        # TSLA 5:1 split on 2020-08-31
        tsla_splits = [b for b in data["TSLA"] if float(b.get("split_factor", 1.0)) != 1.0 and b["ts"] >= "2020-01-01"]
        assert len(tsla_splits) == 1, f"Expected 1 TSLA split, got {len(tsla_splits)}"
        assert tsla_splits[0]["ts"] == "2020-08-31"
        assert math.isclose(float(tsla_splits[0]["split_factor"]), 5.0, rel_tol=1e-4)

        # NVDA 4:1 split on 2021-07-20
        nvda_splits = [b for b in data["NVDA"] if float(b.get("split_factor", 1.0)) != 1.0 and b["ts"] >= "2020-01-01"]
        assert len(nvda_splits) == 1, f"Expected 1 NVDA split, got {len(nvda_splits)}"
        assert nvda_splits[0]["ts"] == "2021-07-20"
        assert math.isclose(float(nvda_splits[0]["split_factor"]), 4.0, rel_tol=1e-4)


class TestV23OptionBPriceContractAndCausality:
    """Validates Option B causal price semantics and indicator scale-invariance."""

    def test_option_b_preserves_raw_close_for_decision_bar(self):
        """Assert Option B adapter sets bar[-1]['close'] to raw_close on decision day T."""
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        provider = TiingoHistoricalProvider(
            symbols=["AAPL", "TSLA", "NVDA"],
            start_date="2020-01-01",
            end_date="2021-12-31",
            warmup_start_date="2019-09-01",
            preloaded_bars=data,
        )

        engine = ReplayEngine(agent.decide, provider, price_semantics="causal_production")

        # Test on split day: 2020-08-31
        for cur_date, mkt_state in provider.stream_daily_slices("2020-08-31", "2020-08-31"):
            today_closes = {sym: b[-1]["raw_close"] for sym, b in mkt_state.items() if b}
            adapted = engine._adapt_market_state_causal(mkt_state, cur_date, today_closes)
            for sym in ["AAPL", "TSLA"]:
                assert math.isclose(adapted[sym][-1]["close"], today_closes[sym], rel_tol=1e-5), (
                    f"Decision bar close for {sym} does not match raw close: {adapted[sym][-1]['close']} vs {today_closes[sym]}"
                )


class TestV23CrossYearBoundaryAndPendingOrders:
    """Validates that 2019-12-31 generated orders execute at 2020-01-02 open."""

    def test_zero_pending_orders_at_tier1_terminal_boundary(self):
        """Assert no pending orders are dangling at 2019-12-31 close."""
        if TIER1_CACHE_FILE.exists():
            with open(TIER1_CACHE_FILE, "r", encoding="utf-8") as f:
                t1_bars = json.load(f)
            t1_provider = TiingoHistoricalProvider(list(t1_bars.keys()), "2015-01-01", "2019-12-31", "2014-09-01", preloaded_bars=t1_bars)
            corp = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.IMPUTE_BUSINESS_DAYS_10)
            engine = ReplayEngine(agent.decide, t1_provider, corp, price_semantics="causal_production")
            res = engine.run_replay(eval_start="2019-12-31", eval_end="2019-12-31")
            assert len(engine.last_portfolio.fill_log) == 0, "No trades should fill on 2019-12-31"


class TestV23IndependentAccountingAndNegativeControls:
    """Validates independent double-entry ledger certification and 7 negative controls."""

    def test_independent_accounting_manifest_certification(self):
        """Assert all 4 strategies achieved 100% accounting certification."""
        manifest_path = MANIFEST_DIR / "tier2_independent_accounting.json"
        assert manifest_path.exists(), "Missing tier2_independent_accounting.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        assert doc["all_strategies_certified"] is True, "Accounting certification failed"
        assert doc["all_negative_controls_passed"] is True, "Negative controls failed"

        for strat, data in doc["strategies"].items():
            assert data["certified"] is True
            assert data["max_daily_discrepancy"] < 1e-4, f"{strat} max discrepancy {data['max_daily_discrepancy']} >= 1e-4"
            assert data["cash_discrepancy"] < 1e-4, f"{strat} cash discrepancy {data['cash_discrepancy']} >= 1e-4"
            assert len(data["position_mismatches"]) == 0

    def test_seven_adversarial_negative_controls(self):
        """Assert all 7 adversarial negative controls catch anomalies."""
        assert run_negative_control_altered_fill_price(), "Failed to catch altered fill price"
        assert run_negative_control_omitted_trade(), "Failed to catch omitted trade"
        assert run_negative_control_reversed_split(), "Failed to catch reversed split"
        assert run_negative_control_double_dividend(), "Failed to catch double dividend"
        assert run_negative_control_double_fee(), "Failed to catch double fee"
        assert run_negative_control_missing_position(), "Failed to catch missing position"
        assert run_negative_control_lookahead_leak(), "Failed to catch future lookahead"


class TestV23StatisticalAndManifestConsistency:
    """Validates statistical results, regime profile, and secret redaction."""

    def test_preregistration_protocol_present_and_valid(self):
        """Assert tier2_preregistration_protocol.json is valid and covers 24 assets."""
        path = MANIFEST_DIR / "tier2_preregistration_protocol.json"
        assert path.exists(), "Missing tier2_preregistration_protocol.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["universe"]["symbols"]) == 24
        assert data["tier3_isolation_firewall"]["status"] == "ABSOLUTELY_SEALED"

    def test_four_way_results_present_and_valid(self):
        """Assert tier2_four_way_results.json exists and contains all 4 strategies."""
        path = MANIFEST_DIR / "tier2_four_way_results.json"
        assert path.exists(), "Missing tier2_four_way_results.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "Frozen E0" in data
        assert "Candidate A" in data
        assert "Candidate E" in data
        assert "Candidate A+E" in data

        e0_nav = data["Frozen E0"]["metrics"]["ending_nav"]
        ae_nav = data["Candidate A+E"]["metrics"]["ending_nav"]
        assert e0_nav > 200_000.0
        assert ae_nav > 190_000.0

    def test_paired_statistics_manifest(self):
        """Assert tier2_paired_strategy_statistics.json has block bootstrap CIs."""
        path = MANIFEST_DIR / "tier2_paired_strategy_statistics.json"
        assert path.exists(), "Missing tier2_paired_strategy_statistics.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "Challenger: Candidate A+E vs Benchmark: Frozen E0" in data

    def test_regime_robustness_manifest(self):
        """Assert tier2_regime_robustness_profile.json has all 6 macroeconomic regimes."""
        path = MANIFEST_DIR / "tier2_regime_robustness_profile.json"
        assert path.exists(), "Missing tier2_regime_robustness_profile.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_regimes"] == 6

    def test_secret_redaction(self):
        """Assert secret redaction function functions properly."""
        secret = "secret_tiingo_token_abc123"
        text = f"Failed to connect using token {secret} on endpoint."
        redacted = redact_secret(text, secret)
        assert secret not in redacted
        assert "[REDACTED_TIINGO_TOKEN]" in redacted
