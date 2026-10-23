"""
Guardian Alpha Protocol V26-R: Report Table Arithmetic Verifier and Mutation Suite.
Stage B2-Q Remediation: Automated Verification of Published Markdown Financial Tables.

Verifies:
  1. Exact mathematical reconstruction of all holdings rows, quantities, prices, and sums.
  2. Sub-penny component rounding analysis across all 4 strategies.
  3. Parameterized mutation tests that deliberately alter share quantity, price, row subtotal, and grand total.
  4. Detection of omitted rows, unauthorized securities, and balance-sheet mismatches.
"""
from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path
import pytest

from research.engine.accounting import (
    AUTHORIZED_UNIVERSE,
    UnauthorizedSecurityError,
    validate_and_extract_carryforward_state,
)
from research.engine.report_consistency_checker import (
    ReportTableArithmeticError,
    ReportConsistencyError,
    extract_numeric_value,
    parse_markdown_tables,
    validate_table_arithmetic,
    verify_report_table_arithmetic,
    verify_report_tables_against_manifests,
    verify_v26r_report_text,
)

MANIFEST_DIR = Path("research/manifests")
CACHE_DIR = Path("tiingo_cache")


@pytest.fixture(scope="module")
def tier1_holdings():
    p = MANIFEST_DIR / "tier1_terminal_holdings_v22.json"
    assert p.exists(), f"Missing {p}"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tier2_bridge():
    p = MANIFEST_DIR / "tier2_carryforward_continuity_bridge.json"
    assert p.exists(), f"Missing {p}"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. TABLE PARSING INTEGRITY
# ==============================================================================
def test_parse_markdown_tables_basic():
    sample = """
# Header
Some intro text.

| Symbol | Shares | Price | Value |
| :--- | :--- | :--- | :--- |
| AAPL | 10.0 | $150.00 | $1,500.00 |
| MSFT | 5.0 | $300.00 | $1,500.00 |
| Total | — | — | **$3,000.00** |

End text.
"""
    tables = parse_markdown_tables(sample)
    assert len(tables) == 1
    t = tables[0]
    assert t["headers"] == ["Symbol", "Shares", "Price", "Value"]
    assert len(t["rows"]) == 3
    logs = validate_table_arithmetic(t)
    assert len(logs) >= 3


# ==============================================================================
# 2. AUTHORITATIVE MACHINE MANIFEST ARITHMETIC (ALL 4 STRATEGIES)
# ==============================================================================
@pytest.mark.parametrize("strat_name", ["Frozen E0", "Candidate A", "Candidate E", "Candidate A+E"])
def test_authoritative_manifest_exact_arithmetic(tier1_holdings, tier2_bridge, strat_name):
    t1_strat = tier1_holdings[strat_name]
    bridge_strat = tier2_bridge[strat_name]

    cash = Decimal(str(t1_strat["ending_cash"]))
    rec = Decimal(str(t1_strat["dividend_receivables"]))
    positions = t1_strat["positions"]

    # 1. Closing positions exact row product & sum
    calc_close_pos_sum = Decimal("0")
    for p in positions:
        sh = Decimal(str(p["shares"]))
        px = Decimal(str(p["raw_price"]))
        mv = Decimal(str(p["market_value"]))
        assert round(sh * px, 2) == round(mv, 2), f"Manifest row product mismatch for {p['symbol']} in {strat_name}"
        calc_close_pos_sum += mv

    # 2. Closing total NAV balance sheet
    unrounded_closing_nav = calc_close_pos_sum + cash + rec
    reported_closing_nav = Decimal(str(t1_strat["ending_nav"]))
    assert round(unrounded_closing_nav, 2) == round(reported_closing_nav, 2)

    # 3. Opening positions exact row product & sum
    bridge_positions = bridge_strat["positions"]
    calc_open_pos_sum = Decimal("0")
    for bp in bridge_positions:
        sh = Decimal(str(bp["shares"]))
        open_px = Decimal(str(bp["open_price_20200102"]))
        open_mv = Decimal(str(bp["open_market_value"]))
        assert round(sh * open_px, 2) == round(open_mv, 2), f"Bridge open product mismatch for {bp['symbol']}"
        calc_open_pos_sum += open_mv

    # 4. Opening economic NAV balance sheet
    unrounded_opening_nav = calc_open_pos_sum + cash + rec
    reported_opening_nav = Decimal(str(bridge_strat["opening_economic_nav"]))
    assert round(unrounded_opening_nav, 2) == round(reported_opening_nav, 2)


# ==============================================================================
# 3. COMPONENT-LEVEL ROUNDING INVARIANT (FINDING 3 PROOF)
# ==============================================================================
@pytest.mark.parametrize("strat_name", ["Frozen E0", "Candidate A", "Candidate E", "Candidate A+E"])
def test_component_rounding_invariant(tier1_holdings, tier2_bridge, strat_name):
    """Prove that summing rounded components yields exactly 1 cent less than rounding unrounded sum."""
    t1_strat = tier1_holdings[strat_name]
    bridge_strat = tier2_bridge[strat_name]

    cash_unrounded = Decimal(str(t1_strat["ending_cash"]))
    rec_unrounded = Decimal(str(t1_strat["dividend_receivables"]))
    open_pos_unrounded = Decimal(str(bridge_strat["opening_positions_market_value"]))

    unrounded_sum = cash_unrounded + rec_unrounded + open_pos_unrounded
    rounded_nav = round(unrounded_sum, 2)

    # Sum of prematurely rounded individual components
    cash_rounded = round(cash_unrounded, 2)
    rec_rounded = round(rec_unrounded, 2)
    pos_rounded = round(open_pos_unrounded, 2)
    sum_of_rounded_components = cash_rounded + rec_rounded + pos_rounded

    # The 1-cent rounding invariant holds universally across all 4 strategies
    delta = rounded_nav - sum_of_rounded_components
    assert delta == Decimal("0.01"), (
        f"Expected exactly 1 cent delta between rounded unrounded sum ({rounded_nav}) "
        f"and sum of rounded components ({sum_of_rounded_components}) for {strat_name}"
    )


# ==============================================================================
# 4. PARAMETERIZED MUTATION TESTS: DELIBERATE FAULT INJECTION
# ==============================================================================
SAMPLE_VALID_TABLE = """
| Symbol | Shares Held | 2019-12-31 Close Price | 2019-12-31 Market Value |
| :--- | :--- | :--- | :--- |
| AAPL | 117.0 | $293.65 | $34,357.05 |
| NVDA | 145.0 | $235.30 | $34,118.50 |
| QLD | 200.0 | $121.89 | $24,378.00 |
| SMH | 227.0 | $141.41 | $32,100.07 |
| SSO | 98.0 | $150.84 | $14,782.32 |
| TSLA | 80.0 | $418.33 | $33,466.40 |
| XLV | 321.0 | $101.86 | $32,697.06 |
| Total | — | — | **$205,899.40** |
"""


def test_valid_sample_table_passes():
    tables = parse_markdown_tables(SAMPLE_VALID_TABLE)
    assert len(tables) == 1
    logs = validate_table_arithmetic(tables[0])
    assert len(logs) == 8  # 1 column sum + 7 row products


@pytest.mark.parametrize("delta_shares", [+1.0, -1.0, +0.5, -0.5])
def test_mutation_alter_single_share_quantity(delta_shares):
    # Alter AAPL shares from 117.0 to 117.0 + delta
    mutated = SAMPLE_VALID_TABLE.replace("AAPL | 117.0 |", f"AAPL | {117.0 + delta_shares:.1f} |")
    tables = parse_markdown_tables(mutated)
    with pytest.raises(ReportTableArithmeticError) as exc_info:
        validate_table_arithmetic(tables[0])
    assert "Row product mismatch" in str(exc_info.value)


@pytest.mark.parametrize("delta_price", [+0.05, -0.05, +1.00, -1.00])
def test_mutation_alter_single_price(delta_price):
    # Alter NVDA price from $235.30 to $235.30 + delta
    mutated = SAMPLE_VALID_TABLE.replace("$235.30 |", f"${235.30 + delta_price:.2f} |")
    tables = parse_markdown_tables(mutated)
    with pytest.raises(ReportTableArithmeticError) as exc_info:
        validate_table_arithmetic(tables[0])
    assert "Row product mismatch" in str(exc_info.value)


@pytest.mark.parametrize("delta_mv", [+1.00, -1.00, +10.00, -10.00])
def test_mutation_alter_single_row_market_value(delta_mv):
    # Alter QLD market value from $24,378.00 to $24,378.00 + delta
    mutated = SAMPLE_VALID_TABLE.replace("$24,378.00", f"${24378.00 + delta_mv:.2f}")
    tables = parse_markdown_tables(mutated)
    with pytest.raises(ReportTableArithmeticError) as exc_info:
        validate_table_arithmetic(tables[0])
    # Fails column sum or row product
    assert ("Column sum mismatch" in str(exc_info.value) or "Row product mismatch" in str(exc_info.value))


@pytest.mark.parametrize("delta_total", [+1.00, -1.00, +1000.00, -1000.00])
def test_mutation_alter_grand_total(delta_total):
    # Alter Total from $205,899.40 to $205,899.40 + delta
    mutated = SAMPLE_VALID_TABLE.replace("**$205,899.40**", f"**${205899.40 + delta_total:,.2f}**")
    tables = parse_markdown_tables(mutated)
    with pytest.raises(ReportTableArithmeticError) as exc_info:
        validate_table_arithmetic(tables[0])
    assert "Column sum mismatch" in str(exc_info.value)


def test_mutation_omitted_row():
    # Omit XLV row but keep the $205,899.40 total
    lines = [line for line in SAMPLE_VALID_TABLE.splitlines() if "XLV" not in line]
    mutated = "\n".join(lines)
    tables = parse_markdown_tables(mutated)
    with pytest.raises(ReportTableArithmeticError) as exc_info:
        validate_table_arithmetic(tables[0])
    assert "Column sum mismatch" in str(exc_info.value)


def test_mutation_unauthorized_ticker_in_manifest():
    # Attempting to add UNH to carryforward state must fail
    manifest_holdings = {
        "symbol": "UNH",
        "shares": 104.0,
        "raw_price": 293.98,
        "market_value": 30573.92,
    }
    dummy_strat = {
        "ending_cash": 10000.0,
        "dividend_receivables": 0.0,
        "ending_nav": 40573.92,
        "positions": [manifest_holdings],
    }
    with pytest.raises(UnauthorizedSecurityError) as exc_info:
        validate_and_extract_carryforward_state(dummy_strat, "Test Strategy")
    assert "Unauthorized security 'UNH'" in str(exc_info.value)


# ==============================================================================
# 5. RECONCILIATION OF HISTORICAL V25 ARITHMETIC TABLE
# ==============================================================================
def test_historical_v25_table_internal_arithmetic():
    """Verify that the 7 stocks in the original V25 Section 6 table DID sum to $253,391.71."""
    v25_md = """
| Ticker | Shares Held | 2019-12-31 Close | 2019-12-31 Market Value |
| :--- | :--- | :--- | :--- |
| AAPL | 42.0 | $293.65 | $12,333.30 |
| NVDA | 133.0 | $235.30 | $31,294.90 |
| MSFT | 172.0 | $157.70 | $27,124.40 |
| UNH | 104.0 | $293.98 | $30,573.92 |
| AMZN | 29.0 | $1,847.84 | $53,587.36 |
| QLD | 818.0 | $70.52 | $57,685.36 |
| SSO | 593.0 | $68.79 | $40,792.47 |
| Stock Total | — | — | **$253,391.71** |
"""
    tables = parse_markdown_tables(v25_md)
    assert len(tables) == 1
    # Internal arithmetic is consistent
    logs = validate_table_arithmetic(tables[0])
    assert len(logs) == 8


# ==============================================================================
# 6. STRATEGY-SPECIFIC BALANCE SHEET HORIZONTAL VALIDATION
# ==============================================================================
def test_strategy_balance_sheet_table_validation():
    sample_bs_table = """
| Strategy | Starting Cash | Starting Receivables | Starting Positions MV | Starting Economic NAV |
| :--- | :--- | :--- | :--- | :--- |
| Frozen E0 | $12,253.46 | $836.53 | $208,392.93 | $221,482.92 |
| Candidate A | $11,973.28 | $1,607.01 | $191,784.79 | $205,365.08 |
| Candidate E | $9,597.57 | $2,227.17 | $201,391.75 | $213,216.49 |
| Candidate A+E | $8,688.77 | $2,799.39 | $186,459.66 | $197,947.82 |
"""
    tables = parse_markdown_tables(sample_bs_table)
    assert len(tables) == 1
    logs = validate_table_arithmetic(tables[0])
    assert len(logs) == 4


# ==============================================================================
# 7. MANIFEST CROSS-CHECK & REPORT MUTATION TESTS
# ==============================================================================
def test_v26r_report_tables_against_manifests_success():
    """Verify published V26-R report tables against machine manifests."""
    report_path = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md")
    assert report_path.exists()
    res = verify_report_tables_against_manifests(report_path)
    assert res["tables_cross_checked"] == 6
    assert res["manifest_checks_performed"] >= 90
    assert res["verified"] is True


def test_v26r_full_report_text_verification():
    """Verify that full gating validator passes on the published V26-R report."""
    report_path = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md")
    assert verify_v26r_report_text(report_path) is True


def test_manifest_crosscheck_mutation_share_quantity(tmp_path):
    """Mutating a share quantity in Table 1 triggers ReportConsistencyError against manifest."""
    original = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md").read_text(encoding="utf-8")
    mutated = original.replace("AAPL** | 117.0 |", "AAPL** | 118.0 |")
    mut_file = tmp_path / "mutated_report.md"
    mut_file.write_text(mutated, encoding="utf-8")

    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_tables_against_manifests(mut_file)
    assert "Holdings shares mismatch for AAPL" in str(exc_info.value)


def test_manifest_crosscheck_mutation_close_price(tmp_path):
    """Mutating a close price in Table 1 triggers ReportConsistencyError against manifest."""
    original = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md").read_text(encoding="utf-8")
    mutated = original.replace("NVDA** | 145.0 | \\$235.30 |", "NVDA** | 145.0 | \\$240.00 |")
    mut_file = tmp_path / "mutated_report.md"
    mut_file.write_text(mutated, encoding="utf-8")

    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_tables_against_manifests(mut_file)
    assert "Holdings close px mismatch for NVDA" in str(exc_info.value)


def test_manifest_crosscheck_mutation_cash(tmp_path):
    """Mutating ending cash in Section 3.3 balance sheet triggers ReportConsistencyError against manifest."""
    original = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md").read_text(encoding="utf-8")
    mutated = original.replace("Frozen E0** | \\$12,253.46 |", "Frozen E0** | \\$12,000.00 |")
    mut_file = tmp_path / "mutated_report.md"
    mut_file.write_text(mutated, encoding="utf-8")

    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_tables_against_manifests(mut_file)
    assert "Balance sheet cash mismatch for Frozen E0" in str(exc_info.value)


def test_manifest_crosscheck_mutation_carryforward_nav(tmp_path):
    """Mutating carryforward ending NAV in Section 6.1 triggers ReportConsistencyError against manifest."""
    original = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md").read_text(encoding="utf-8")
    mutated = original.replace("**\\$535,191.10** | 55.43%", "**\\$530,000.00** | 55.43%")
    mut_file = tmp_path / "mutated_report.md"
    mut_file.write_text(mutated, encoding="utf-8")

    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_tables_against_manifests(mut_file)
    assert "Carryforward end nav mismatch for Frozen E0" in str(exc_info.value)

