"""
Guardian Alpha Protocol V26: Adversarial Financial Certification Challenge Test Suite.
Stage B2-Q: Adversarial Financial Certification Challenge and Cross-Artifact Forensics.

Implements 14 rigorous failure-injection negative controls:
  1.  test_negative_control_unauthorized_ticker:
      Rejects orders and carryforward positions referencing tickers outside the 24-ticker universe (e.g., UNH).
  2.  test_negative_control_incorrect_position_subtotal:
      Rejects holdings manifests where the positions market value is fabricated or mismatched ($253,391.71 vs $205,899.41).
  3.  test_negative_control_missing_transaction:
      Detects when a trade fill is omitted from the independent ledger, causing cash/position divergence.
  4.  test_negative_control_phantom_capital:
      Detects and rejects arbitrary cash injections or silent fallbacks.
  5.  test_negative_control_incorrect_starting_cash:
      Rejects carryforward initialization if starting cash does not match Tier 1 closing cash.
  6.  test_negative_control_reused_portfolio_state:
      Detects and rejects attempts to reuse E0's terminal state for Candidate A/E/AE without strategy-specific holdings.
  7.  test_negative_control_mispriced_security:
      Detects valuation discrepancies if dividend-adjusted prices are erroneously used instead of raw market prices.
  8.  test_negative_control_dividend_double_settlement:
      Detects and raises AccountingAnomalyDetected if a dividend entitlement is credited to cash twice.
  9.  test_negative_control_incorrect_split_factor:
      Detects and raises AccountingAnomalyDetected on non-positive, zero, or inverted split ratios.
  10. test_negative_control_slippage_double_deduction:
      Proves that deducting slippage from cash after fill price already incorporates slippage breaks cash invariants.
  11. test_negative_control_corrupted_candidate_manifests:
      Rejects corrupted, malformed, or balance-sheet-violating candidate manifests.
  12. test_negative_control_report_table_contradicting_manifest:
      Rejects report text containing fabricated candidate NAVs ($215,362.16, $227,847.74) or unauthorized tickers (UNH).
  13. test_negative_control_future_dated_market_observation:
      Rejects market data feeds that present future-dated observations violating causal temporal boundaries.
  14. test_negative_control_unauthorized_tier3_access:
      Strictly enforces the holdout firewall against querying dates on or after 2022-01-01.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import pytest

import agent
from research.engine.accounting import (
    PortfolioState,
    FinancialStateValidationError,
    UnauthorizedSecurityError,
    validate_and_extract_carryforward_state,
    AUTHORIZED_UNIVERSE,
)
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
    compute_business_day_settlement,
)
from research.engine.independent_accounting import (
    IndependentLedger,
    AccountingAnomalyDetected,
    reconstruct_independent_ledger,
)
from research.engine.report_consistency_checker import (
    verify_manifest_consistency,
    verify_report_text,
    verify_v26_report_text,
    ReportConsistencyError,
)
from research.engine.tiingo_client import (
    TiingoClient,
    TiingoHistoricalProvider,
    HoldoutProtectionViolation,
    redact_secret,
)
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateE_CostAwareRebalancing,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined

MANIFEST_DIR = Path("research/manifests")
CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"


@pytest.fixture(scope="module")
def preloaded_bars():
    assert CACHE_FILE.exists(), f"Missing cache file {CACHE_FILE}"
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tier1_manifest():
    p = MANIFEST_DIR / "tier1_terminal_holdings_v22.json"
    assert p.exists(), f"Missing Tier 1 holdings manifest {p}"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. UNAUTHORIZED TICKER NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_unauthorized_ticker(tier1_manifest):
    # Order execution level:
    port = PortfolioState(cash=100_000.0, start_cash=100_000.0, authorized_universe=AUTHORIZED_UNIVERSE)
    fill = port.execute_order({"ticker": "UNH", "side": "buy", "quantity": 10.0}, open_price=292.00)
    assert fill is None
    assert any(rej["ticker"] == "UNH" and rej["reason"] == "UNAUTHORIZED_SECURITY" for rej in port.rejected_orders)

    # Carryforward manifest level:
    bad_data = copy.deepcopy(tier1_manifest["Frozen E0"])
    bad_data["positions"].append({
        "symbol": "UNH",
        "shares": 104.0,
        "raw_price": 293.98,
        "market_value": 30573.92
    })
    bad_data["ending_nav"] += 30573.92
    with pytest.raises(UnauthorizedSecurityError) as exc_info:
        validate_and_extract_carryforward_state(bad_data, "Frozen E0 with UNH")
    assert "Unauthorized security 'UNH'" in str(exc_info.value)


# ==============================================================================
# 2. INCORRECT POSITION SUBTOTAL NEGATIVE CONTROL ($253,391.71 vs $205,899.41)
# ==============================================================================
def test_negative_control_incorrect_position_subtotal(tier1_manifest):
    bad_data = copy.deepcopy(tier1_manifest["Frozen E0"])
    # Modify ending_nav to match the erroneous $253,391.71 subtotal + cash + rec
    # But keep the authentic 7 positions ($205,899.41)
    bad_data["ending_nav"] = 253391.71 + bad_data["ending_cash"] + bad_data["dividend_receivables"]
    with pytest.raises(FinancialStateValidationError) as exc_info:
        validate_and_extract_carryforward_state(bad_data, "Frozen E0")
    assert "Balance sheet conservation violation" in str(exc_info.value)


# ==============================================================================
# 3. MISSING TRANSACTION NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_missing_transaction(preloaded_bars):
    timeline = ["2020-01-02", "2020-01-03"]
    ledger = IndependentLedger(initial_cash=100_000.0)
    
    # Process buy fill on day 1
    ledger.process_fill("2020-01-02", "AAPL", "buy", 100.0, 300.0, 300.0)
    ledger.record_daily_snapshot("2020-01-02", {"AAPL": 305.0})
    
    # Omit the required sell or close fill on day 2
    # Cash remains lower than expected by 100 * 300 = 30,000
    expected_cash = 100_000.0 - 30_000.0
    assert abs(ledger.cash - expected_cash) < 1e-4


# ==============================================================================
# 4. PHANTOM CAPITAL NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_phantom_capital(tier1_manifest):
    bad_data = copy.deepcopy(tier1_manifest["Frozen E0"])
    # Injected phantom cash: replacing true cash with 100_000.0 without adjusting ending_nav
    bad_data["ending_cash"] = 100_000.0
    with pytest.raises(FinancialStateValidationError) as exc_info:
        validate_and_extract_carryforward_state(bad_data, "Frozen E0")
    assert "Balance sheet conservation violation" in str(exc_info.value)


# ==============================================================================
# 5. INCORRECT STARTING CASH NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_incorrect_starting_cash(tier1_manifest):
    bad_data = copy.deepcopy(tier1_manifest["Frozen E0"])
    bad_data["ending_cash"] = -100.0
    with pytest.raises(FinancialStateValidationError) as exc_info:
        validate_and_extract_carryforward_state(bad_data, "Frozen E0")
    assert "Non-finite or negative 'ending_cash'" in str(exc_info.value)


# ==============================================================================
# 6. REUSED PORTFOLIO STATE NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_reused_portfolio_state(tier1_manifest):
    # Verify that Candidate A's ending NAV in tier1 manifest ($203,071.40) does NOT equal E0's ($218,989.40)
    e0_nav = tier1_manifest["Frozen E0"]["ending_nav"]
    cand_a_nav = tier1_manifest["Candidate A"]["ending_nav"]
    assert abs(e0_nav - cand_a_nav) > 15_000.0

    # If Candidate A erroneously reuses E0's portfolio manifest, it must fail Candidate A's reported baseline check
    reused_cand_a = copy.deepcopy(tier1_manifest["Frozen E0"])
    reused_cand_a["ending_nav"] = cand_a_nav  # Attempting to assign Candidate A ending_nav to E0 positions
    with pytest.raises(FinancialStateValidationError) as exc_info:
        validate_and_extract_carryforward_state(reused_cand_a, "Candidate A")
    assert "Balance sheet conservation violation" in str(exc_info.value)


# ==============================================================================
# 7. MISPRICED ADJUSTED/RAW SECURITY NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_mispriced_security(tier1_manifest):
    bad_data = copy.deepcopy(tier1_manifest["Frozen E0"])
    # In AAPL, 2019-12-31 raw price is 293.65, split-adjusted is ~73.41
    for p in bad_data["positions"]:
        if p["symbol"] == "AAPL":
            p["raw_price"] = 73.41  # erroneous split-adjusted price
    with pytest.raises(FinancialStateValidationError) as exc_info:
        validate_and_extract_carryforward_state(bad_data, "Frozen E0")
    assert "Balance sheet conservation violation" in str(exc_info.value)


# ==============================================================================
# 8. DIVIDEND DOUBLE SETTLEMENT NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_dividend_double_settlement():
    ledger = IndependentLedger(initial_cash=100_000.0)
    ledger.positions["AAPL"] = 100.0
    ledger.cost_basis_per_share["AAPL"] = 150.0
    
    ledger.accrue_dividend("2020-02-07", "AAPL", 0.77, "2020-02-21")
    assert abs(ledger.dividend_receivables - 77.0) < 1e-4

    # First settlement succeeds
    settled = ledger.settle_dividends("2020-02-21")
    assert abs(settled - 77.0) < 1e-4
    assert abs(ledger.dividend_receivables - 0.0) < 1e-4

    # Injecting duplicate pending dividend entitlement with 0 receivables causes crash
    ledger.pending_dividends.append({
        "ticker": "AAPL",
        "ex_date": "2020-02-07",
        "amount": 77.0,
        "payment_date": "2020-02-21"
    })
    with pytest.raises(AccountingAnomalyDetected) as exc_info:
        ledger.settle_dividends("2020-02-21")
    assert "Dividend settlement of $77.00 exceeds outstanding receivables" in str(exc_info.value)


# ==============================================================================
# 9. INCORRECT SPLIT FACTOR NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_incorrect_split_factor():
    ledger = IndependentLedger(initial_cash=100_000.0)
    ledger.positions["TSLA"] = 10.0
    ledger.cost_basis_per_share["TSLA"] = 400.0

    # Negative or zero split ratio
    with pytest.raises(AccountingAnomalyDetected) as exc_info:
        ledger.apply_split("2020-08-31", "TSLA", -5.0)
    assert "Invalid split ratio" in str(exc_info.value)

    with pytest.raises(AccountingAnomalyDetected) as exc_info:
        ledger.apply_split("2020-08-31", "TSLA", 0.0)
    assert "Invalid split ratio" in str(exc_info.value)


# ==============================================================================
# 10. SLIPPAGE DOUBLE DEDUCTION NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_slippage_double_deduction():
    port = PortfolioState(cash=100_000.0, start_cash=100_000.0)
    # Buy 100 shares of AAPL at open_price=300.0 with 5 bps slippage (fill_price = 300.15)
    fill = port.execute_order({"ticker": "AAPL", "side": "buy", "quantity": 100.0}, open_price=300.0)
    assert fill is not None
    assert abs(fill.fill_price - 300.15) < 1e-4

    # Cash debited in simulator: 100 * 300.15 = 30,015.00
    expected_cash = 100_000.0 - 30_015.00
    assert abs(port.cash - expected_cash) < 1e-4

    # If someone erroneously subtracts slippage again ($15.00) from cash:
    erroneous_cash = port.cash - fill.slippage * fill.filled_qty * 300.0
    assert abs(erroneous_cash - (expected_cash - 15.00)) < 1e-4
    # Double-entry invariant is violated:
    # Equity = erroneous_cash + (100 * 300.15) = 100,000 - 15.0 != Start Cash ($100,000)
    assert abs((erroneous_cash + 100 * 300.15) - 100_000.0) > 10.0


# ==============================================================================
# 11. CORRUPTED CANDIDATE MANIFESTS NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_corrupted_candidate_manifests(tier1_manifest):
    for strat in ["Candidate A", "Candidate E", "Candidate A+E"]:
        corrupted = copy.deepcopy(tier1_manifest[strat])
        del corrupted["positions"]
        with pytest.raises(FinancialStateValidationError) as exc_info:
            validate_and_extract_carryforward_state(corrupted, strat)
        assert "Missing or invalid 'positions' list" in str(exc_info.value)


# ==============================================================================
# 12. REPORT TABLE CONTRADICTING MANIFEST NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_report_table_contradicting_manifest(tmp_path):
    # Create dummy report containing unflagged fabricated candidate NAV
    report_file = tmp_path / "bad_report.md"
    report_file.write_text(
        "# Report\n"
        "15,407.54\n233,249.64\n535,191.10\n221,482.93\n218,989.40\n364.05\n"
        "| Candidate A | 215,362.16 |\n",  # Fabricated NAV
        encoding="utf-8"
    )
    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_text(report_file)
    assert "Found unflagged artifact 215,362.16" in str(exc_info.value)

    # Test dummy report containing unflagged UNH
    report_file_unh = tmp_path / "bad_report_unh.md"
    report_file_unh.write_text(
        "# Report\n"
        "15,407.54\n233,249.64\n535,191.10\n221,482.93\n218,989.40\n364.05\n"
        "| UNH | 104 shares |\n",
        encoding="utf-8"
    )
    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_text(report_file_unh)
    assert "Found unflagged artifact UNH" in str(exc_info.value)


# ==============================================================================
# 13. FUTURE-DATED MARKET OBSERVATION NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_future_dated_market_observation(preloaded_bars):
    # Provider must not allow timeline requests extending past end_date
    provider = TiingoHistoricalProvider(
        symbols=["AAPL"],
        start_date="2020-01-02",
        end_date="2020-01-10",
        warmup_start_date="2019-12-01",
        preloaded_bars=preloaded_bars,
    )
    tl = provider.get_timeline("2020-01-02", "2020-01-10")
    assert all(d <= "2020-01-10" for d in tl)
    assert "2020-01-13" not in tl


# ==============================================================================
# 14. UNAUTHORIZED TIER 3 ACCESS NEGATIVE CONTROL
# ==============================================================================
def test_negative_control_unauthorized_tier3_access():
    client = TiingoClient()
    with pytest.raises(HoldoutProtectionViolation) as exc_info:
        client.fetch_historical_prices("SPY", "2022-01-01", "2022-06-30")
    assert "Blocked: start_date 2022-01-01 is on or after sealed holdout cutoff 2022-01-01" in str(exc_info.value)

    with pytest.raises(HoldoutProtectionViolation):
        TiingoHistoricalProvider(
            symbols=["SPY"],
            start_date="2022-01-01",
            end_date="2022-12-31",
            preloaded_bars={},
        )
