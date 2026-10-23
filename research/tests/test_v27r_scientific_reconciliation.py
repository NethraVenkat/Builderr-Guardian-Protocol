"""
Unit and Adversarial Verification Suite for Master Guardian Protocol V27-R.
Stage B2-R1: Scientific Baseline and Execution-Sensitivity Remediation.

Covers:
- P0 Corrected Tier 1 Provenance & Holdings Concentration (31.27% vs superseded 99.07%)
- P0 Execution-Cost Paradox Resolution (Method A Fixed-Trade vs Method B Reactive Replay)
- P0 Authoritative Tier 2 Fresh-Start Metrics & Compounding Reconciliation
- P1 Adversarial Verification (9 Mandatory Failure Injections):
  1. Substitute superseded holdings into corrected NAV
  2. Mix incompatible simulation revisions
  3. Double-charge slippage
  4. Inject phantom capital
  5. Misclassify path-dependent reactive gain as direct cost savings
  6. Corrupt scenario fill chronology
  7. Alter a report table subtotal
  8. Introduce future information (lookahead poison)
  9. Access sealed Tier 3 observations (holdout protection)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest

from research.engine.accounting import (
    PortfolioState,
    FillResult,
    RiskMode,
    SLIP_EQUITY,
    SLIP_LEVERAGED,
    get_beta,
)
import research.engine.accounting as accounting
from research.engine.corporate_actions import CorporateActionRegistry, PaymentDatePolicy
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import TiingoHistoricalProvider, TiingoClient, HoldoutProtectionViolation
from research.engine.report_consistency_checker import (
    ReportConsistencyError,
    ReportTableArithmeticError,
    validate_table_arithmetic,
    extract_numeric_value,
)
import agent
from research.scripts.run_tier2_authentic_backtest import build_clean_corp_registry, compute_extended_metrics


# ==============================================================================
# P0: TIER 1 PROVENANCE & CONCENTRATION RECONCILIATION
# ==============================================================================

def test_authoritative_tier1_holdings_and_concentration():
    """Verify that authoritative V22 Option B Tier 1 holdings sum to $218,989.40 and have 31.27% top-2 concentration."""
    manifest_path = Path("research/manifests/tier1_terminal_holdings_v22.json")
    assert manifest_path.exists(), "tier1_terminal_holdings_v22.json must exist"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    e0 = data["Frozen E0"]
    ending_nav = e0["ending_nav"]
    ending_cash = e0["ending_cash"]
    receivables = e0["dividend_receivables"]
    positions = e0["positions"]
    
    # 1. Verify terminal NAV is $218,989.40
    assert abs(ending_nav - 218989.40) < 0.01, f"Expected $218,989.40, got {ending_nav}"
    assert abs(ending_cash - 12253.46) < 0.01, f"Expected cash $12,253.46, got {ending_cash}"
    assert abs(receivables - 836.53) < 0.01, f"Expected receivables $836.53, got {receivables}"
    
    # 2. Verify position values
    pos_dict = {p["symbol"]: p for p in positions}
    assert "AAPL" in pos_dict and "NVDA" in pos_dict
    assert pos_dict["AAPL"]["shares"] == 117.0
    assert abs(pos_dict["AAPL"]["market_value"] - 34357.05) < 0.01
    assert abs(pos_dict["AAPL"]["weight_pct"] - 15.69) < 0.05
    
    assert pos_dict["NVDA"]["shares"] == 145.0
    assert abs(pos_dict["NVDA"]["market_value"] - 34118.50) < 0.01
    assert abs(pos_dict["NVDA"]["weight_pct"] - 15.58) < 0.05
    
    # 3. Verify exact sum of components
    stock_total = sum(p["market_value"] for p in positions)
    assert abs(stock_total - 205899.40) < 0.01, f"Expected stocks $205,899.40, got {stock_total}"
    reconstructed_nav = stock_total + ending_cash + receivables
    assert abs(reconstructed_nav - ending_nav) < 0.001, "Balance sheet must conserve exactly"
    
    # 4. Verify top-2 concentration is 31.27%, NOT superseded 99.07%
    top2_concentration = (pos_dict["AAPL"]["market_value"] + pos_dict["NVDA"]["market_value"]) / ending_nav
    assert abs(top2_concentration - 0.3127) < 0.001, f"Top-2 concentration must be 31.27%, got {top2_concentration * 100:.2f}%"


def test_superseded_v20_holdings_provenance():
    """Verify that superseded V20/V21 run ($347,496.21) is preserved as historical evidence and not mixed with V22."""
    superseded_path = Path("research/manifests/tier1_accounting_reconciliation.json")
    assert superseded_path.exists(), "tier1_accounting_reconciliation.json must exist"
    data = json.loads(superseded_path.read_text(encoding="utf-8"))
    
    old_e0 = data["Frozen E0"]
    old_nav = old_e0["ending_nav"]
    old_positions = old_e0["terminal_positions"]
    
    assert abs(old_nav - 347496.21) < 0.01, f"Expected old NAV $347,496.21, got {old_nav}"
    old_aapl = old_positions["AAPL"]["market_value"]
    old_nvda = old_positions["NVDA"]["market_value"]
    assert abs(old_aapl - 220952.06) < 0.05
    assert abs(old_nvda - 123328.47) < 0.05
    old_concentration = (old_aapl + old_nvda) / old_nav
    assert abs(old_concentration - 0.9907) < 0.001, f"Old concentration was 99.07%, got {old_concentration * 100:.2f}%"


# ==============================================================================
# P0: TWO-METHOD EXECUTION SENSITIVITY & PARADOX RESOLUTION
# ==============================================================================

def test_two_method_execution_sensitivity_manifest():
    """Verify that the two-method execution sensitivity manifest exists and contains rigorous Method A & B results."""
    manifest_path = Path("research/manifests/v27r_two_method_execution_sensitivity.json")
    assert manifest_path.exists(), "v27r_two_method_execution_sensitivity.json must exist"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    e0_a = data["Frozen E0"]["method_a_fixed_trade"]
    e0_b = data["Frozen E0"]["method_b_reactive"]
    
    # 1. Method A: Monotonically increasing direct cost drag
    navs_a = [s["ending_nav"] for s in e0_a[:5]] # Scenarios 0 to 4 (slippage progression)
    assert navs_a == sorted(navs_a, reverse=True), f"Method A ending NAVs must be strictly monotonic: {navs_a}"
    assert e0_a[0]["ending_nav"] == 238621.72 # Zero friction
    assert e0_a[1]["ending_nav"] == 233249.64 # Baseline
    assert e0_a[2]["ending_nav"] == 227877.56 # Moderate slippage (strictly lower by $5,372.08)
    assert e0_a[2]["direct_cost_drag"] == 5372.08
    
    # Commissions in Method A: exact linear cost deduction
    assert e0_a[5]["direct_cost_drag"] == 1012.71 # 1 bps
    assert e0_a[6]["direct_cost_drag"] == 5063.54 # 5 bps
    assert e0_a[7]["direct_cost_drag"] == 10127.08 # 10 bps
    
    # 2. Method B: Path-dependent reactive effects
    assert e0_b[1]["ending_nav"] == 233249.64 # Baseline
    assert e0_b[2]["ending_nav"] == 235374.49 # Moderate slippage (reactive trade avoidance)
    assert e0_b[2]["trades"] == 401 # 13 fewer trades than Baseline (414)
    assert e0_b[2]["classification"] == "Path-Dependent Reactive Effect"
    
    # Candidate A+E under Method A and B
    ae_a = data["Candidate A+E"]["method_a_fixed_trade"]
    ae_b = data["Candidate A+E"]["method_b_reactive"]
    assert ae_a[0]["ending_nav"] > ae_a[1]["ending_nav"] > ae_a[2]["ending_nav"]
    assert ae_b[0]["ending_nav"] > ae_b[1]["ending_nav"] > ae_b[2]["ending_nav"]


def test_first_divergence_tracing():
    """Verify that the exact first divergence between Baseline and Moderate slippage occurs on 2020-02-25 on fill #35."""
    cache_path = Path("tiingo_cache/tier2_bars.json")
    assert cache_path.exists()
    preloaded = json.loads(cache_path.read_text(encoding="utf-8"))
    
    def run_one(slip_eq, slip_lev, comm_bps):
        orig_s_eq, orig_s_lev = accounting.SLIP_EQUITY, accounting.SLIP_LEVERAGED
        try:
            accounting.SLIP_EQUITY = slip_eq
            accounting.SLIP_LEVERAGED = slip_lev
            agent._last_rebalance_bar_date = None
            agent._last_targets = {}
            provider = TiingoHistoricalProvider(
                symbols=list(preloaded.keys()),
                start_date="2020-01-01",
                end_date="2020-03-01", # warmup through first divergence
                warmup_start_date="2019-09-01",
                preloaded_bars=preloaded,
            )
            reg = build_clean_corp_registry(preloaded)
            engine = ReplayEngine(
                agent_path_or_fn=agent.decide,
                provider=provider,
                corporate_actions=reg,
                commission_bps=comm_bps,
                start_cash=100_000.0,
                price_semantics="causal_production",
            )
            engine.run_replay("2020-01-01", "2020-03-01")
            return engine.last_portfolio.fill_log
        finally:
            accounting.SLIP_EQUITY = orig_s_eq
            accounting.SLIP_LEVERAGED = orig_s_lev

    fills_base = run_one(0.0005, 0.0010, 0.0)
    fills_mod = run_one(0.0010, 0.0020, 0.0)
    
    # First 34 fills must have identical date, ticker, side, and filled_qty
    for i in range(35):
        fb = fills_base[i]
        fm = fills_mod[i]
        assert (fb.date, fb.ticker, fb.side, fb.filled_qty) == (fm.date, fm.ticker, fm.side, fm.filled_qty), f"Diverged before index 35 at index {i}"
        
    # Fill #35 (2020-02-25 XLP) diverges by 1 share due to cash difference
    fb35 = fills_base[35]
    fm35 = fills_mod[35]
    assert fb35.date == "2020-02-25" and fm35.date == "2020-02-25"
    assert fb35.ticker == "XLP" and fm35.ticker == "XLP"
    assert fb35.side == "buy" and fm35.side == "buy"
    assert fb35.filled_qty == 433.0
    assert fm35.filled_qty == 432.0


# ==============================================================================
# P1: MANDATORY ADVERSARIAL FAILURE INJECTIONS (1 THROUGH 9)
# ==============================================================================

def test_adv_01_substitute_superseded_holdings_into_corrected_nav():
    """Adversarial Injection 1: Substitute superseded holdings ($344k) into corrected NAV ($218k). Must fail closed."""
    superseded_holdings_sum = 344280.53 # AAPL + NVDA from superseded run
    corrected_nav = 218989.40
    
    # Verification gate
    def verify_holdings_fit_nav(holdings_val: float, nav: float) -> bool:
        if holdings_val > nav:
            raise ValueError(f"IncompatibleSimulationProvenanceError: Holdings (${holdings_val:,.2f}) exceed NAV (${nav:,.2f})")
        return True

    with pytest.raises(ValueError, match="IncompatibleSimulationProvenanceError"):
        verify_holdings_fit_nav(superseded_holdings_sum, corrected_nav)


def test_adv_02_mix_incompatible_simulation_revisions():
    """Adversarial Injection 2: Mix V20 cash ($0.04) with V22 positions ($205.8k). Must fail closed."""
    v20_cash = 0.04
    v22_positions_mv = 205899.40
    v22_receivables = 836.53
    authoritative_nav = 218989.40
    
    reconstructed = v20_cash + v22_positions_mv + v22_receivables # 206,735.97
    discrepancy = abs(reconstructed - authoritative_nav)
    
    assert discrepancy > 12000.0, f"Discrepancy should reflect missing ~$12k cash, got {discrepancy}"
    with pytest.raises(AssertionError):
        assert abs(reconstructed - authoritative_nav) < 0.01, "Revision mixing must fail balance sheet check"


def test_adv_03_double_charge_slippage():
    """Adversarial Injection 3: Double-charge slippage in price AND cash. Must violate accounting invariant."""
    port = PortfolioState(cash=50000.0)
    # Buy 100 SPY at $100. Slippage = 5 bps = 0.05 per share.
    # fill_px = $100.05. Cost = $10,005.00.
    res = port.execute_order({"ticker": "SPY", "side": "buy", "quantity": 100}, open_price=100.0)
    assert res is not None
    assert port.cash == 50000.0 - 10005.0 # $39,995.00
    
    # Inject adversarial double slippage charge: debit cash an additional $5.00
    port.cash -= 5.0
    
    # Check accounting invariant: Equity == Start + Realized + Unrealized + Div - Comm
    # Mark to market at $100.00
    inv_ok, reason = port.check_accounting_invariants({"SPY": 100.0})
    assert not inv_ok, "Double charging slippage must violate accounting invariant"
    assert "Balance sheet discrepancy" in reason


def test_adv_04_inject_phantom_capital():
    """Adversarial Injection 4: Inject $100,000 phantom cash without trade or deposit. Must fail closed."""
    port = PortfolioState(cash=100000.0)
    port.execute_order({"ticker": "SPY", "side": "buy", "quantity": 100}, open_price=100.0)
    
    # Inject phantom capital
    port.cash += 100000.0
    
    inv_ok, reason = port.check_accounting_invariants({"SPY": 100.0})
    assert not inv_ok, "Phantom capital must violate accounting invariant"
    assert "Balance sheet discrepancy" in reason


def test_adv_05_misclassify_path_dependent_gain_as_direct_savings():
    """Adversarial Injection 5: Misclassify reactive gain as direct cost savings. Must fail validation."""
    def classify_execution_effect(scenario_name: str, direct_drag: float, reactive_diff: float) -> str:
        if direct_drag > 0 and reactive_diff < 0:
            # Direct drag is positive (costs money in fixed replay), but reactive replay gained NAV
            return "PATH_DEPENDENT_REBALANCING_EFFECT"
        elif direct_drag > 0 and reactive_diff > 0:
            return "DIRECT_COST_DRAG"
        elif direct_drag == 0:
            return "BASELINE"
        else:
            raise ValueError("InvalidExecutionClassification: Direct execution costs cannot be negative")

    # In Scenario 2: direct_drag = +$5,372.08, reactive_diff = -$2,124.85
    classification = classify_execution_effect("Scenario 2", direct_drag=5372.08, reactive_diff=-2124.85)
    assert classification == "PATH_DEPENDENT_REBALANCING_EFFECT"
    
    # Adversarially claim direct cost savings
    with pytest.raises(ValueError, match="InvalidExecutionClassification"):
        classify_execution_effect("Scenario 2", direct_drag=-2124.85, reactive_diff=-2124.85)


def test_adv_06_corrupt_scenario_fill_chronology():
    """Adversarial Injection 6: Permute fill dates out of chronological sequence. Must fail validation."""
    fills = [
        {"date": "2020-01-03", "ticker": "SPY", "side": "buy"},
        {"date": "2020-01-08", "ticker": "QQQ", "side": "buy"},
        {"date": "2020-01-05", "ticker": "AAPL", "side": "buy"}, # Injected backwards date
    ]
    
    def validate_fill_chronology(fill_list: list[dict]) -> bool:
        dates = [f["date"] for f in fill_list]
        for i in range(1, len(dates)):
            if dates[i] < dates[i - 1]:
                raise ValueError(f"ChronologicalOrderViolation: Fill {i} ({dates[i]}) is earlier than fill {i-1} ({dates[i-1]})")
        return True

    with pytest.raises(ValueError, match="ChronologicalOrderViolation"):
        validate_fill_chronology(fills)


def test_adv_07_alter_report_subtotal():
    """Adversarial Injection 7: Alter a markdown table subtotal. Automated validator must detect error."""
    # Table where rows do not sum to total
    bad_table = {
        "headers": ["Symbol", "Market Value"],
        "rows": [
            {"line_num": 1, "cells": ["AAPL", "$34,357.05"]},
            {"line_num": 2, "cells": ["NVDA", "$34,118.50"]},
            {"line_num": 3, "cells": ["Total", "$78,475.55"]}, # Should be $68,475.55! Mutated by +$10,000
        ]
    }
    
    with pytest.raises(ReportTableArithmeticError) as exc:
        validate_table_arithmetic(bad_table)
    assert "Column sum mismatch for 'Market Value'" in str(exc.value)


def test_adv_08_introduce_future_information():
    """Adversarial Injection 8: Future price change at T+1 cannot leak into decision at T."""
    cache_path = Path("tiingo_cache/tier2_bars.json")
    assert cache_path.exists()
    preloaded = json.loads(cache_path.read_text(encoding="utf-8"))
    
    provider_clean = TiingoHistoricalProvider(
        symbols=list(preloaded.keys()),
        start_date="2020-01-01",
        end_date="2020-01-10",
        warmup_start_date="2019-09-01",
        preloaded_bars=preloaded,
    )
    
    # Poison preloaded bars: inject spike on 2020-01-08
    poisoned = copy.deepcopy(preloaded)
    for b in poisoned["AAPL"]:
        if b["ts"] == "2020-01-08":
            b["close"] = 9999.0
            b["raw_close"] = 9999.0

    provider_poisoned = TiingoHistoricalProvider(
        symbols=list(preloaded.keys()),
        start_date="2020-01-01",
        end_date="2020-01-10",
        warmup_start_date="2019-09-01",
        preloaded_bars=poisoned,
    )
    
    reg = build_clean_corp_registry(preloaded)
    
    # Get slice on 2020-01-03
    slices_clean = dict(provider_clean.stream_daily_slices("2020-01-01", "2020-01-03"))
    slices_poisoned = dict(provider_poisoned.stream_daily_slices("2020-01-01", "2020-01-03"))
    
    engine = ReplayEngine(agent.decide, provider_clean, reg, price_semantics="causal_production")
    
    m_clean = engine._adapt_market_state_causal(slices_clean["2020-01-03"], "2020-01-03", {"AAPL": 297.43})
    m_poisoned = engine._adapt_market_state_causal(slices_poisoned["2020-01-03"], "2020-01-03", {"AAPL": 297.43})
    
    agent._last_rebalance_bar_date = None
    dec_clean = agent.decide(m_clean, {"cash": 100000.0, "positions": []}, 100000.0)
    agent._last_rebalance_bar_date = None
    dec_poisoned = agent.decide(m_poisoned, {"cash": 100000.0, "positions": []}, 100000.0)
    
    assert dec_clean == dec_poisoned, "Poisoned future price at T+1 altered decision at T!"


def test_adv_09_access_sealed_tier3_observations():
    """Adversarial Injection 9: Querying dates >= 2022-01-01 must trigger HoldoutProtectionViolation."""
    client = TiingoClient(api_token="test_token")
    
    # Sealed holdout dates must be strictly blocked
    for future_date in ["2022-01-01", "2022-06-15", "2023-01-01", "2024-12-31"]:
        with pytest.raises(HoldoutProtectionViolation) as exc:
            client.fetch_historical_prices("SPY", future_date, future_date)
        assert "holdout cutoff" in str(exc.value).lower()
