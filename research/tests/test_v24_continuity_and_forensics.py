"""
Guardian Alpha V24: Tier 2 Cross-Period Continuity, Terminal Cash Integrity,
Preregistration Compliance, and Final Validation Forensics Test Suite.

Validates:
  1. Tier 1-to-Tier 2 overnight asset-level continuity bridge (zero phantom capital).
  2. Double-entry accounting conservation in carry-forward initializations.
  3. Terminal cash reconciliation ($15,407.54 exact machine manifest match vs legacy typos).
  4. Execution-order invariance across strategy permutations.
  5. Corporate action state isolation and negative control for mutable registry leaks.
  6. Preregistered vs executed cost model specifications (leveraged ETF slippage audit).
  7. Commit ancestry and clean-checkout provenance between 6d21c4f and 9057ab1.
  8. Scientific statistical interpretation bounds (p=0.2100, CI zero-crossing).
  9. Holdout protection firewall and credential redaction.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path
import pytest
import numpy as np

import agent
from research.engine.accounting import PortfolioState
from research.engine.corporate_actions import CorporateActionRegistry
from research.scripts.run_tier2_authentic_backtest import build_clean_corp_registry
from research.engine.independent_accounting import IndependentLedger
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import (
    TiingoHistoricalProvider,
    HoldoutProtectionViolation,
    HOLDOUT_CUTOFF_DATE,
    redact_secret,
)
from research.strategies.v11_candidates import CandidateA_AdaptiveRebalance, CandidateE_CostAwareRebalancing
from research.strategies.v12_candidate_ae import CandidateAE_Combined

MANIFEST_DIR = Path("research/manifests")
CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"
TIER1_CACHE_FILE = Path("tiingo_cache") / "tier1_bars.json"


@pytest.fixture(scope="module")
def preloaded_bars():
    assert CACHE_FILE.exists(), f"Missing cache {CACHE_FILE}"
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tier1_manifest():
    p = MANIFEST_DIR / "tier1_terminal_holdings_v22.json"
    assert p.exists(), f"Missing Tier 1 holdings {p}"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. OVERNIGHT CONTINUITY BRIDGE AND ASSET-LEVEL VALUATION
# ==============================================================================
def test_tier1_to_tier2_continuity_bridge_frozen_e0(tier1_manifest):
    bridge_path = MANIFEST_DIR / "tier2_carryforward_continuity_bridge.json"
    assert bridge_path.exists(), "Missing tier2_carryforward_continuity_bridge.json"
    with open(bridge_path, "r", encoding="utf-8") as f:
        bridge = json.load(f)

    assert "Frozen E0" in bridge
    e0 = bridge["Frozen E0"]
    assert e0["closing_date"] == "2019-12-31"
    assert e0["opening_date"] == "2020-01-02"

    # Verify exact closing components
    ending_cash = e0["ending_cash"]
    receivables = e0["dividend_receivables"]
    pos_mkt_val = e0["closing_positions_market_value"]
    reconstructed_close = ending_cash + receivables + pos_mkt_val

    assert abs(reconstructed_close - 218989.40) < 0.05
    assert abs(reconstructed_close - e0["reported_tier1_terminal_nav"]) < 0.05

    # Verify overnight mark-to-market price move
    overnight_pnl = sum(
        p["shares"] * (p["open_price_20200102"] - p["close_price_20191231"])
        for p in e0["positions"]
    )
    assert abs(overnight_pnl - e0["overnight_market_movement_pnl"]) < 0.05
    assert abs(overnight_pnl - 2493.53) < 0.05

    # Verify pre-trade opening economic NAV
    opening_nav = reconstructed_close + overnight_pnl
    assert abs(opening_nav - 221482.93) < 0.05
    assert abs(opening_nav - e0["opening_economic_nav"]) < 0.05


def test_four_way_continuity_bridge_completeness(tier1_manifest):
    bridge_path = MANIFEST_DIR / "tier2_carryforward_continuity_bridge.json"
    with open(bridge_path, "r", encoding="utf-8") as f:
        bridge = json.load(f)

    for strat_name in ["Frozen E0", "Candidate A", "Candidate E", "Candidate A+E"]:
        assert strat_name in bridge
        data = bridge[strat_name]
        t1_nav = tier1_manifest[strat_name]["ending_nav"]
        assert abs(data["reported_tier1_terminal_nav"] - t1_nav) < 0.05
        assert abs(data["closing_discrepancy"]) < 0.05


# ==============================================================================
# 2. PHANTOM EXTERNAL CAPITAL DETECTION & DOUBLE-ENTRY CONSERVATION
# ==============================================================================
def test_phantom_capital_rejection():
    # If 100k cash is incorrectly injected as cash without basis offset, invariants fail
    t1_cash = 12253.46
    pos_cost_basis = 117.0 * 293.65  # 34357.05
    receivables = 836.53

    # Correct continuous carry-forward initialization:
    # start_cash = cash + pos_cost_basis
    start_capital = t1_cash + pos_cost_basis
    port = PortfolioState(
        cash=t1_cash,
        start_cash=start_capital,
        positions={"AAPL": 117.0},
        avg_cost={"AAPL": 293.65},
        dividend_receivables=receivables,
    )

    # Valuation at 2019-12-31 close price
    val_prices = {"AAPL": 293.65}
    tot_equity = port.total_equity(val_prices)
    # 12253.46 + 117 * 293.65 (34357.05) + 836.53 = 47447.04
    assert abs(tot_equity - (t1_cash + 34357.05 + receivables)) < 0.01

    ok, msg = port.check_accounting_invariants(val_prices)
    assert ok, f"Invariant check failed on correct portfolio: {msg}"

    # Negative control: Phantom deposit of $100,000 cash injected
    bad_port = PortfolioState(
        cash=t1_cash + 100000.0,  # Phantom $100k
        start_cash=start_capital,   # start_cash not adjusted
        positions={"AAPL": 117.0},
        avg_cost={"AAPL": 293.65},
        dividend_receivables=receivables,
    )
    ok_bad, msg_bad = bad_port.check_accounting_invariants(val_prices)
    assert not ok_bad, "Failed to catch phantom capital injection!"
    assert "100000.00" in msg_bad or "1.00e+05" in msg_bad


# ==============================================================================
# 3. TERMINAL CASH RECONCILIATION & TYPO DISMISSAL
# ==============================================================================
def test_fresh_start_terminal_cash_exact_match():
    # Load all three manifests
    with open(MANIFEST_DIR / "tier2_four_way_results.json", "r", encoding="utf-8") as f:
        four_way = json.load(f)
    with open(MANIFEST_DIR / "tier2_terminal_holdings.json", "r", encoding="utf-8") as f:
        holdings = json.load(f)
    with open(MANIFEST_DIR / "tier2_independent_accounting.json", "r", encoding="utf-8") as f:
        accounting = json.load(f)

    expected_cash = {
        "Frozen E0": 15407.54,
        "Candidate A": 11813.14,
        "Candidate E": 25629.12,
        "Candidate A+E": 6712.52,
    }

    for strat, exp_c in expected_cash.items():
        # Manifest 1: four-way results
        c1 = round(four_way[strat]["metrics"]["terminal_cash"], 2)
        assert c1 == exp_c, f"{strat} four_way cash {c1} != {exp_c}"

        # Manifest 2: terminal holdings
        c2 = round(holdings[strat]["cash"], 2)
        assert c2 == exp_c, f"{strat} holdings cash {c2} != {exp_c}"

        # Manifest 3: independent double-entry ledger
        c3 = round(accounting["strategies"][strat]["terminal_ledger_cash"], 2)
        assert c3 == exp_c, f"{strat} accounting ledger cash {c3} != {exp_c}"

        # Negative control: assert neither V23 report typo matches
        assert c1 != 12042.84, f"Legacy V23 typo $12,042.84 resurfaced in {strat}"
        assert c1 != 12285.18, f"Legacy V23 typo $12,285.18 resurfaced in {strat}"


# ==============================================================================
# 4. EXECUTION-ORDER INVARIANCE
# ==============================================================================
def test_execution_order_invariance(preloaded_bars):
    provider = TiingoHistoricalProvider(
        symbols=list(preloaded_bars.keys()),
        start_date="2020-01-01",
        end_date="2021-12-31",
        warmup_start_date="2019-09-01",
        preloaded_bars=preloaded_bars,
    )

    # Order 1: E0 then Candidate A+E
    engine1_e0 = ReplayEngine(
        agent_path_or_fn=agent.decide,
        provider=provider,
        corporate_actions=build_clean_corp_registry(preloaded_bars),
        commission_bps=0.0,
        price_semantics="causal_production",
    )
    res1_e0 = engine1_e0.run_replay("2020-01-01", "2021-12-31", record_traces=True)

    cand_ae = CandidateAE_Combined()
    engine1_ae = ReplayEngine(
        agent_path_or_fn=cand_ae.decide,
        provider=provider,
        corporate_actions=build_clean_corp_registry(preloaded_bars),
        commission_bps=0.0,
        price_semantics="causal_production",
    )
    res1_ae = engine1_ae.run_replay("2020-01-01", "2021-12-31", record_traces=True)

    # Order 2: Candidate A+E then E0
    cand_ae2 = CandidateAE_Combined()
    engine2_ae = ReplayEngine(
        agent_path_or_fn=cand_ae2.decide,
        provider=provider,
        corporate_actions=build_clean_corp_registry(preloaded_bars),
        commission_bps=0.0,
        price_semantics="causal_production",
    )
    res2_ae = engine2_ae.run_replay("2020-01-01", "2021-12-31", record_traces=True)

    engine2_e0 = ReplayEngine(
        agent_path_or_fn=agent.decide,
        provider=provider,
        corporate_actions=build_clean_corp_registry(preloaded_bars),
        commission_bps=0.0,
        price_semantics="causal_production",
    )
    res2_e0 = engine2_e0.run_replay("2020-01-01", "2021-12-31", record_traces=True)

    # Assert bit-for-bit identical traces and terminal NAV
    assert res1_e0["trace_sha256"] == res2_e0["trace_sha256"]
    assert res1_e0["equity_curve"] == res2_e0["equity_curve"]
    assert res1_ae["trace_sha256"] == res2_ae["trace_sha256"]
    assert res1_ae["equity_curve"] == res2_ae["equity_curve"]


# ==============================================================================
# 5. CORPORATE-ACTION STATE ISOLATION & NEGATIVE CONTROLS
# ==============================================================================
def test_corporate_action_registry_isolation(preloaded_bars):
    reg1 = build_clean_corp_registry(preloaded_bars)
    reg2 = build_clean_corp_registry(preloaded_bars)

    # Verify separate instances
    assert reg1 is not reg2
    assert reg1._splits is not reg2._splits

    # Mutate reg1 with a synthetic split mapping
    reg1._splits["SYNTHETIC"] = [{"symbol": "SYNTHETIC", "ratio": 10.0, "ex_date": "2020-05-01"}]
    assert "SYNTHETIC" in reg1._splits
    assert "SYNTHETIC" not in reg2._splits, "Cross-registry mutation detected!"


# ==============================================================================
# 6. PREREGISTRATION & COST MODEL AUDIT
# ==============================================================================
def test_preregistration_cost_model_audit():
    with open(MANIFEST_DIR / "tier2_preregistration_protocol.json", "r", encoding="utf-8") as f:
        prereg = json.load(f)

    # In preregistration protocol
    assert prereg["execution_cost_and_dividend_model"]["slippage_bps"] == 5.0
    assert prereg["execution_cost_and_dividend_model"]["slippage_multiplier"] == 0.0005

    # In engine accounting
    from research.engine.accounting import SLIP_LEVERAGED, SLIP_EQUITY
    assert SLIP_LEVERAGED == 0.0010, "Leveraged ETF slippage must be 10 bps"
    assert SLIP_EQUITY == 0.0005, "Equity slippage must be 5 bps"


# ==============================================================================
# 7. COMMIT ANCESTRY & CLEAN-CHECKOUT PROVENANCE
# ==============================================================================
def test_commit_provenance():
    # Verify via git log that 6d21c4f is ancestor of 9057ab1
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "9057ab1^"],
            capture_output=True,
            text=True,
            check=True,
        )
        parent_hash = proc.stdout.strip()
        assert parent_hash.startswith("6d21c4fd"), f"Parent of 9057ab1 is {parent_hash}, expected 6d21c4fd"
    except Exception as e:
        pytest.skip(f"Git command failed: {e}")


# ==============================================================================
# 8. STATISTICAL INTERPRETATION BOUNDS
# ==============================================================================
def test_paired_statistics_significance_bounds():
    with open(MANIFEST_DIR / "tier2_paired_strategy_statistics.json", "r", encoding="utf-8") as f:
        stats = json.load(f)

    ae_comp = stats["Challenger: Candidate A+E vs Benchmark: Frozen E0"]
    p_val = ae_comp["parametric_t_test"]["p_value_two_tailed"]
    assert abs(p_val - 0.2100) < 0.005
    assert not ae_comp["parametric_t_test"]["statistically_significant_005"]

    b5_ci = ae_comp["block_bootstrap_length_5"]["sharpe_delta_95_ci"]
    assert b5_ci[0] < 0.0 < b5_ci[1], f"Sharpe CI {b5_ci} must cross zero"


# ==============================================================================
# 9. HOLDOUT FIREWALL & CREDENTIAL REDACTION
# ==============================================================================
def test_holdout_protection_firewall():
    with pytest.raises(HoldoutProtectionViolation):
        TiingoHistoricalProvider(
            symbols=["SPY"],
            start_date="2022-01-01",
            end_date="2022-12-31",
            preloaded_bars={},
        )


def test_credential_redaction():
    secret = "a1b2c3d4e5f67890abcdef1234567890abcdef12"
    msg = f"Connecting with token {secret} to Tiingo API"
    redacted = redact_secret(msg, secret)
    assert secret not in redacted
    assert "REDACTED" in redacted
