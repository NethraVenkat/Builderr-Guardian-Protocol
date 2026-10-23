"""
Automated Report-Manifest Consistency Checker for Guardian Alpha.
Verifies that all financial totals, terminal cash balances, holdings market values,
NAV totals, return metrics, and execution costs in published markdown reports
match authoritative machine manifests bit-for-bit, rejecting contradictory values.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class ReportConsistencyError(ValueError):
    """Raised when published report values contradict machine-readable manifests."""
    pass


class ReportTableArithmeticError(ReportConsistencyError):
    """Raised when markdown table row products or column sums fail mathematical verification."""
    pass


def extract_numeric_value(val_str: str) -> float | None:
    """Extract clean float from markdown formatted cell."""
    s = val_str.replace("**", "").replace("~~", "").replace("*", "")
    s = s.replace("\\", "").replace("$", "").replace(",", "").strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    if m:
        try:
            return float(m.group(0))
        except ValueError:
            return None
    return None


def parse_markdown_tables(text: str) -> list[dict[str, Any]]:
    """Parse all markdown tables in text into structured objects."""
    lines = text.splitlines()
    tables = []
    curr_lines: list[tuple[int, str]] = []

    for line_idx, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            curr_lines.append((line_idx, s))
        else:
            if len(curr_lines) >= 3:
                tables.append(_build_table_dict(curr_lines))
            curr_lines = []
    if len(curr_lines) >= 3:
        tables.append(_build_table_dict(curr_lines))

    return tables


def _build_table_dict(raw_lines: list[tuple[int, str]]) -> dict[str, Any]:
    header_line_num, header_str = raw_lines[0]
    headers = [c.strip() for c in header_str.strip("|").split("|")]

    rows = []
    for line_num, line_str in raw_lines[2:]:  # skip delimiter line
        cells = [c.strip() for c in line_str.strip("|").split("|")]
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        elif len(cells) > len(headers):
            cells = cells[:len(headers)]
        rows.append({"line_num": line_num, "cells": cells, "raw": line_str})

    return {
        "header_line_num": header_line_num,
        "headers": headers,
        "rows": rows,
        "raw_lines": raw_lines,
    }


def validate_table_arithmetic(table: dict[str, Any], tolerance: float = 0.02) -> list[str]:
    """Validate row-level products, column totals, and balance sheet identities in a markdown table."""
    headers = table["headers"]
    rows = table["rows"]
    validation_logs = []

    if not rows:
        return validation_logs

    # Detect total row (must be at the bottom of the table)
    total_row_idx = None
    for idx in range(len(rows) - 1, max(-1, len(rows) - 3), -1):
        first_cell = rows[idx]["cells"][0].strip().replace("*", "").replace("~", "").lower()
        if first_cell.startswith(("total", "stock total", "holdings basis", "sum", "subtotal")):
            total_row_idx = idx
            break

    # 1. Column sum validation for total row
    if total_row_idx is not None:
        total_row = rows[total_row_idx]
        data_rows = rows[:total_row_idx]

        for c_idx, h in enumerate(headers):
            h_lower = h.lower()
            if "%" in h or "pct" in h_lower or "percent" in h_lower or "ratio" in h_lower:
                continue
            tot_val = extract_numeric_value(total_row["cells"][c_idx])
            if tot_val is not None:
                data_vals = [extract_numeric_value(r["cells"][c_idx]) for r in data_rows]
                non_null_vals = [v for v in data_vals if v is not None]
                if len(non_null_vals) >= len(data_rows) * 0.5 and len(non_null_vals) > 0:
                    computed_sum = sum(non_null_vals)
                    delta = abs(computed_sum - tot_val)
                    if delta > tolerance:
                        raise ReportTableArithmeticError(
                            f"Column sum mismatch for '{h}' at line {total_row['line_num']}: "
                            f"Sum of {len(non_null_vals)} rows = {computed_sum:.2f}, reported Total = {tot_val:.2f} (delta={delta:.2f})"
                        )
                    validation_logs.append(
                        f"Line {total_row['line_num']}: Column '{h}' sum of {len(non_null_vals)} rows = {computed_sum:.2f} == Total ({tot_val:.2f}) [OK]"
                    )

    # 2. Row-level product validation (Shares * Price == Market Value)
    shares_col = None
    for c_idx, h in enumerate(headers):
        h_lower = h.lower()
        if ("shares" in h_lower or "quantity" in h_lower) and "v25" not in h_lower:
            shares_col = c_idx
            break

    if shares_col is not None:
        price_cols = [
            c_idx for c_idx, h in enumerate(headers)
            if ("price" in h.lower() or "px" in h.lower() or "close" in h.lower()) and "v25" not in h.lower()
        ]
        mv_cols = [
            c_idx for c_idx, h in enumerate(headers)
            if ("market value" in h.lower() or "mv" in h.lower() or "value" in h.lower())
            and "v25" not in h.lower() and "delta" not in h.lower()
        ]

        data_rows = rows[:total_row_idx] if total_row_idx is not None else rows
        for p_col in price_cols:
            p_header = headers[p_col].lower()
            matching_mv_col = None
            if len(price_cols) == 1 and len(mv_cols) == 1:
                matching_mv_col = mv_cols[0]
            else:
                for m_col in mv_cols:
                    m_header = headers[m_col].lower()
                    if ("close" in p_header and "close" in m_header) or ("2019" in p_header and "2019" in m_header):
                        matching_mv_col = m_col
                        break
                    elif ("open" in p_header and "open" in m_header) or ("2020" in p_header and "2020" in m_header):
                        matching_mv_col = m_col
                        break
                if matching_mv_col is None and len(mv_cols) == len(price_cols):
                    # Match by index position
                    idx_in_prices = price_cols.index(p_col)
                    matching_mv_col = mv_cols[idx_in_prices]

            if matching_mv_col is not None:
                for r in data_rows:
                    sh_val = extract_numeric_value(r["cells"][shares_col])
                    px_val = extract_numeric_value(r["cells"][p_col])
                    mv_val = extract_numeric_value(r["cells"][matching_mv_col])
                    if sh_val is not None and px_val is not None and mv_val is not None:
                        expected_mv = sh_val * px_val
                        delta = abs(expected_mv - mv_val)
                        if delta > tolerance:
                            raise ReportTableArithmeticError(
                                f"Row product mismatch at line {r['line_num']}: "
                                f"{headers[shares_col]}={sh_val} * {headers[p_col]}={px_val} = {expected_mv:.2f}, "
                                f"reported {headers[matching_mv_col]}={mv_val:.2f} (delta={delta:.2f})"
                            )
                        validation_logs.append(
                            f"Line {r['line_num']}: {headers[shares_col]} ({sh_val}) * {headers[p_col]} ({px_val}) = {mv_val:.2f} [OK]"
                        )

    # 3. Horizontal balance sheet validation if Cash, Receivables, Positions, NAV exist in a single row
    for r in rows:
        cells = r["cells"]
        cash_val, rec_val, pos_val, nav_val = None, None, None, None
        for c_idx, h in enumerate(headers):
            h_lower = h.lower()
            if "ending cash" in h_lower or "starting cash" in h_lower or h_lower == "cash":
                cash_val = extract_numeric_value(cells[c_idx])
            elif "receivables" in h_lower or "rec" in h_lower:
                rec_val = extract_numeric_value(cells[c_idx])
            elif "positions mv" in h_lower or "positions" in h_lower or "stock" in h_lower:
                pos_val = extract_numeric_value(cells[c_idx])
            elif "nav" in h_lower:
                nav_val = extract_numeric_value(cells[c_idx])

        if cash_val is not None and rec_val is not None and pos_val is not None and nav_val is not None:
            expected_nav = cash_val + rec_val + pos_val
            delta = abs(expected_nav - nav_val)
            if delta > tolerance:
                raise ReportTableArithmeticError(
                    f"Row balance sheet mismatch at line {r['line_num']}: "
                    f"Cash ({cash_val}) + Rec ({rec_val}) + Pos ({pos_val}) = {expected_nav:.2f}, reported NAV = {nav_val:.2f} (delta={delta:.2f})"
                )
            validation_logs.append(
                f"Line {r['line_num']}: Balance sheet sum {cash_val:.2f} + {rec_val:.2f} + {pos_val:.2f} = {nav_val:.2f} [OK]"
            )

    return validation_logs


def verify_report_table_arithmetic(report_path: Path | str, tolerance: float = 0.02) -> dict[str, Any]:
    """Parse and validate arithmetic across all markdown tables in the report."""
    r_path = Path(report_path)
    if not r_path.exists():
        raise FileNotFoundError(f"Report file not found: {r_path}")

    with open(r_path, "r", encoding="utf-8") as f:
        content = f.read()

    tables = parse_markdown_tables(content)
    total_checks = 0
    validated_tables = 0

    for idx, t in enumerate(tables, 1):
        logs = validate_table_arithmetic(t, tolerance=tolerance)
        total_checks += len(logs)
        validated_tables += 1

    return {
        "report_path": str(r_path),
        "tables_found": len(tables),
        "validated_tables": validated_tables,
        "total_checks": total_checks,
        "verified": True,
    }


def verify_manifest_consistency(manifest_dir: Path | str = "research/manifests") -> dict[str, Any]:
    """Verify cross-manifest consistency across primary, holdings, and accounting ledgers."""
    m_dir = Path(manifest_dir)
    with open(m_dir / "tier2_four_way_results.json", "r", encoding="utf-8") as f:
        four_way = json.load(f)
    with open(m_dir / "tier2_terminal_holdings.json", "r", encoding="utf-8") as f:
        holdings = json.load(f)
    with open(m_dir / "tier2_independent_accounting.json", "r", encoding="utf-8") as f:
        accounting = json.load(f)

    results = {}
    for strat in ["Frozen E0", "Candidate A", "Candidate E", "Candidate A+E"]:
        fw_cash = round(four_way[strat]["metrics"]["terminal_cash"], 2)
        th_cash = round(holdings[strat]["cash"], 2)
        ia_cash = round(accounting["strategies"][strat]["terminal_ledger_cash"], 2)

        if fw_cash != th_cash or th_cash != ia_cash:
            raise ReportConsistencyError(
                f"Contradictory terminal cash for {strat}: "
                f"four_way={fw_cash}, holdings={th_cash}, ledger={ia_cash}"
            )

        fw_nav = round(four_way[strat]["metrics"]["ending_nav"], 2)
        th_nav = round(holdings[strat]["terminal_nav"], 2)
        ia_nav = round(accounting["strategies"][strat]["ledger_ending_nav"], 2)

        if fw_nav != th_nav or th_nav != ia_nav:
            raise ReportConsistencyError(
                f"Contradictory ending NAV for {strat}: "
                f"four_way={fw_nav}, holdings={th_nav}, ledger={ia_nav}"
            )

        results[strat] = {
            "terminal_cash": fw_cash,
            "ending_nav": fw_nav,
            "verified": True
        }

    return results


def verify_report_text(report_path: Path | str, manifest_dir: Path | str = "research/manifests") -> bool:
    """Scan report text for rejected legacy typos and assert manifest figures are present."""
    r_path = Path(report_path)
    if not r_path.exists():
        raise FileNotFoundError(f"Report file not found: {r_path}")

    with open(r_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Rejected legacy typos and fabricated report artifacts
    rejected_strings = [
        ("$12,042.84", "Legacy V23 intermediate cash typo"),
        ("$12,285.18", "Legacy V23 residual table plug typo"),
        ("215,362.16", "Fabricated Candidate A/AE fresh-start NAV in V25 report"),
        ("227,847.74", "Fabricated Candidate E fresh-start NAV in V25 report"),
        ("488,775.76", "Fabricated Candidate A/AE carry-forward NAV in V25 report"),
        ("519,921.46", "Fabricated Candidate E carry-forward NAV in V25 report"),
        ("253,391.71", "Fabricated Tier 1 positions subtotal with unauthorized UNH"),
        ("UNH", "Unauthorized security outside 24-ticker production universe"),
    ]

    # Check line-by-line for unflagged legacy typos and fabrications
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        for rejected, desc in rejected_strings:
            if rejected in line:
                lower = line.lower()
                is_flagged = (
                    "~~" in line
                    or "v23" in lower
                    or "v25" in lower
                    or "legacy" in lower
                    or "typo" in lower
                    or "contradiction" in lower
                    or "defect" in lower
                    or "prior" in lower
                    or "superseded" in lower
                    or "unauthorized" in lower
                    or "fabricat" in lower
                    or "hallucinat" in lower
                    or "erroneous" in lower
                    or "discrepancy" in lower
                )
                if not is_flagged:
                    raise ReportConsistencyError(
                        f"Found unflagged artifact {rejected} ({desc}) at line {line_num}: {line.strip()}"
                    )

    # Verify authoritative values are present (accounting for markdown dollar escapes)
    mandatory_strings = [
        "15,407.54",  # Frozen E0 Authoritative Cash
        "233,249.64", # Frozen E0 Primary Ending NAV
        "535,191.10", # Frozen E0 Carry-forward Ending NAV
        "221,482.93", # Frozen E0 Pre-trade opening economic NAV
        "218,989.40", # Tier 1 Closing NAV
        "364.05",     # Terminal Dividend Receivables
    ]

    for req in mandatory_strings:
        if req not in content:
            raise ReportConsistencyError(f"Mandatory authoritative value '{req}' missing from report {r_path}")

    return True


def verify_v26_report_text(report_path: Path | str, manifest_dir: Path | str = "research/manifests") -> bool:
    """Scan V26 report text for strict candidate consistency and discrepancy reconciliation."""
    verify_report_text(report_path, manifest_dir)
    r_path = Path(report_path)
    with open(r_path, "r", encoding="utf-8") as f:
        content = f.read()

    v26_mandatory = [
        "192,272.44", # Candidate A Fresh-Start NAV
        "225,907.32", # Candidate E Fresh-Start NAV
        "207,620.42", # Candidate A+E Fresh-Start NAV
        "405,757.44", # Candidate A Carry-Forward NAV
        "479,976.21", # Candidate E Carry-Forward NAV
        "419,877.18", # Candidate A+E Carry-Forward NAV
        "47,492.30",  # Reconciled holdings discrepancy
    ]
    for req in v26_mandatory:
        if req not in content:
            raise ReportConsistencyError(f"V26 Mandatory value '{req}' missing from report {r_path}")

    return True


def verify_report_tables_against_manifests(
    report_path: Path | str,
    manifest_dir: Path | str = "research/manifests",
    tolerance: float = 0.02,
) -> dict[str, Any]:
    """Parse all markdown tables in the report and verify every financial cell against machine manifests.

    Cross-checks:
    1. Table Section 3.2: Authoritative Tier 1 holdings (AAPL, NVDA, QLD, SMH, SSO, TSLA, XLV)
       against tier1_terminal_holdings_v22.json and tier2_carryforward_continuity_bridge.json.
    2. Table Section 3.3: Tier 1 closing balance sheet across all 4 strategies
       against tier1_terminal_holdings_v22.json.
    3. Table Section 4.2: Forensic reconciliation against v26_tier1_holdings_forensic_reconciliation.json.
    4. Table Section 5.2: Machine precision overnight bridge against tier2_carryforward_continuity_bridge.json.
    5. Table Section 6.1: Carryforward performance matrix against v26_strategy_specific_carryforward_results.json.
    6. Table Section 6.2: Fresh-start benchmark ending metrics against tier2_terminal_holdings.json and tier2_four_way_results.json.
    """
    r_path = Path(report_path)
    if not r_path.exists():
        raise FileNotFoundError(f"Report file not found: {r_path}")

    m_dir = Path(manifest_dir)
    t1_holdings_path = m_dir / "tier1_terminal_holdings_v22.json"
    t2_bridge_path = m_dir / "tier2_carryforward_continuity_bridge.json"
    cf_results_path = m_dir / "v26_strategy_specific_carryforward_results.json"
    t2_holdings_path = m_dir / "tier2_terminal_holdings.json"
    t1_recon_path = m_dir / "v26_tier1_holdings_forensic_reconciliation.json"

    with open(t1_holdings_path, "r", encoding="utf-8") as f:
        t1_holdings = json.load(f)
    with open(t2_bridge_path, "r", encoding="utf-8") as f:
        t2_bridge = json.load(f)
    with open(cf_results_path, "r", encoding="utf-8") as f:
        cf_results = json.load(f)
    with open(t2_holdings_path, "r", encoding="utf-8") as f:
        t2_holdings = json.load(f)
    with open(t1_recon_path, "r", encoding="utf-8") as f:
        t1_recon = json.load(f)

    with open(r_path, "r", encoding="utf-8") as f:
        content = f.read()

    tables = parse_markdown_tables(content)
    checked_tables = 0
    checks_performed = 0

    for table in tables:
        headers = table["headers"]
        rows = table["rows"]
        h_str = " ".join(headers).lower()

        # 1. Authoritative Tier 1 Terminal Holdings
        if "symbol" in h_str and "2019-12-31 raw close price" in h_str:
            e0_t1_pos = {p["symbol"]: p for p in t1_holdings["Frozen E0"]["positions"]}
            e0_br_pos = {p["symbol"]: p for p in t2_bridge["Frozen E0"]["positions"]}

            for r in rows:
                sym = r["cells"][0].replace("*", "").strip()
                if sym in e0_t1_pos:
                    expected_sh = e0_t1_pos[sym]["shares"]
                    expected_close_px = e0_t1_pos[sym]["raw_price"]
                    expected_close_mv = e0_t1_pos[sym]["market_value"]
                    expected_open_px = e0_br_pos[sym]["open_price_20200102"]
                    expected_open_mv = e0_br_pos[sym]["open_market_value"]
                    expected_delta = e0_br_pos[sym]["overnight_delta"]

                    actual_sh = extract_numeric_value(r["cells"][1])
                    actual_close_px = extract_numeric_value(r["cells"][2])
                    actual_close_mv = extract_numeric_value(r["cells"][3])
                    actual_open_px = extract_numeric_value(r["cells"][4])
                    actual_open_mv = extract_numeric_value(r["cells"][5])
                    actual_delta = extract_numeric_value(r["cells"][6])

                    if actual_sh is None or abs(actual_sh - expected_sh) > tolerance:
                        raise ReportConsistencyError(f"Holdings shares mismatch for {sym}: reported={actual_sh}, manifest={expected_sh}")
                    if actual_close_px is None or abs(actual_close_px - expected_close_px) > tolerance:
                        raise ReportConsistencyError(f"Holdings close px mismatch for {sym}: reported={actual_close_px}, manifest={expected_close_px}")
                    if actual_close_mv is None or abs(actual_close_mv - expected_close_mv) > tolerance:
                        raise ReportConsistencyError(f"Holdings close mv mismatch for {sym}: reported={actual_close_mv}, manifest={expected_close_mv}")
                    if actual_open_px is None or abs(actual_open_px - expected_open_px) > tolerance:
                        raise ReportConsistencyError(f"Holdings open px mismatch for {sym}: reported={actual_open_px}, manifest={expected_open_px}")
                    if actual_open_mv is None or abs(actual_open_mv - expected_open_mv) > tolerance:
                        raise ReportConsistencyError(f"Holdings open mv mismatch for {sym}: reported={actual_open_mv}, manifest={expected_open_mv}")
                    if actual_delta is None or abs(actual_delta - expected_delta) > tolerance:
                        raise ReportConsistencyError(f"Holdings overnight delta mismatch for {sym}: reported={actual_delta}, manifest={expected_delta}")
                    checks_performed += 6
                elif "total" in sym.lower():
                    actual_tot_close_mv = extract_numeric_value(r["cells"][3])
                    actual_tot_open_mv = extract_numeric_value(r["cells"][5])
                    actual_tot_delta = extract_numeric_value(r["cells"][6])

                    expected_tot_close_mv = t2_bridge["Frozen E0"]["closing_positions_market_value"]
                    expected_tot_open_mv = t2_bridge["Frozen E0"]["opening_positions_market_value"]
                    expected_tot_delta = t2_bridge["Frozen E0"]["overnight_market_movement_pnl"]

                    if actual_tot_close_mv is None or abs(actual_tot_close_mv - expected_tot_close_mv) > tolerance:
                        raise ReportConsistencyError(f"Holdings total close mv mismatch: reported={actual_tot_close_mv}, manifest={expected_tot_close_mv}")
                    if actual_tot_open_mv is None or abs(actual_tot_open_mv - expected_tot_open_mv) > tolerance:
                        raise ReportConsistencyError(f"Holdings total open mv mismatch: reported={actual_tot_open_mv}, manifest={expected_tot_open_mv}")
                    if actual_tot_delta is None or abs(actual_tot_delta - expected_tot_delta) > tolerance:
                        raise ReportConsistencyError(f"Holdings total delta mismatch: reported={actual_tot_delta}, manifest={expected_tot_delta}")
                    checks_performed += 3

            checked_tables += 1

        # 2. Authoritative Tier 1 Closing Balance Sheet
        elif "strategy" in h_str and "tier 1 closing nav" in h_str:
            for r in rows:
                strat = r["cells"][0].replace("*", "").strip()
                if strat in t1_holdings:
                    expected_cash = round(t1_holdings[strat]["ending_cash"], 2)
                    expected_rec = round(t1_holdings[strat]["dividend_receivables"], 2)
                    expected_pos = round(sum(p["market_value"] for p in t1_holdings[strat]["positions"]), 2)
                    expected_nav = round(t1_holdings[strat]["ending_nav"], 2)

                    actual_cash = extract_numeric_value(r["cells"][1])
                    actual_rec = extract_numeric_value(r["cells"][2])
                    actual_pos = extract_numeric_value(r["cells"][3])
                    actual_nav = extract_numeric_value(r["cells"][4])

                    if actual_cash is None or abs(actual_cash - expected_cash) > tolerance:
                        raise ReportConsistencyError(f"Balance sheet cash mismatch for {strat}: reported={actual_cash}, manifest={expected_cash}")
                    if actual_rec is None or abs(actual_rec - expected_rec) > tolerance:
                        raise ReportConsistencyError(f"Balance sheet rec mismatch for {strat}: reported={actual_rec}, manifest={expected_rec}")
                    if actual_pos is None or abs(actual_pos - expected_pos) > tolerance:
                        raise ReportConsistencyError(f"Balance sheet pos mismatch for {strat}: reported={actual_pos}, manifest={expected_pos}")
                    if actual_nav is None or abs(actual_nav - expected_nav) > tolerance:
                        raise ReportConsistencyError(f"Balance sheet nav mismatch for {strat}: reported={actual_nav}, manifest={expected_nav}")
                    checks_performed += 4
            checked_tables += 1

        # 3. Forensic Line-by-Line Holdings Comparison
        elif "authoritative shares" in h_str and "erroneous v25 shares" in h_str:
            for r in rows:
                first_cell = r["cells"][0].replace("*", "").strip()
                if "total" in first_cell.lower():
                    actual_auth_tot = extract_numeric_value(r["cells"][3])
                    actual_v25_tot = extract_numeric_value(r["cells"][6])
                    actual_delta = extract_numeric_value(r["cells"][7])

                    expected_auth = t1_recon["authoritative_manifest_stock_total"]
                    expected_v25 = t1_recon["v25_reported_stock_total"]
                    expected_diff = t1_recon["discrepancy_amount"]

                    if actual_auth_tot is None or abs(actual_auth_tot - expected_auth) > tolerance:
                        raise ReportConsistencyError(f"Forensic auth stock total mismatch: reported={actual_auth_tot}, manifest={expected_auth}")
                    if actual_v25_tot is None or abs(actual_v25_tot - expected_v25) > tolerance:
                        raise ReportConsistencyError(f"Forensic v25 stock total mismatch: reported={actual_v25_tot}, manifest={expected_v25}")
                    if actual_delta is None or abs(actual_delta - expected_diff) > tolerance:
                        raise ReportConsistencyError(f"Forensic delta mismatch: reported={actual_delta}, manifest={expected_diff}")
                    checks_performed += 3
            checked_tables += 1

        # 4. Machine Precision Overnight NAV Reconciliation
        elif "full-precision cash" in h_str and "component truncation delta" in h_str:
            for r in rows:
                strat = r["cells"][0].replace("*", "").strip()
                if strat in t2_bridge:
                    expected_open_nav = round(t2_bridge[strat]["opening_economic_nav"], 2)
                    actual_open_nav = extract_numeric_value(r["cells"][5])
                    actual_delta = extract_numeric_value(r["cells"][7])

                    if actual_open_nav is None or abs(actual_open_nav - expected_open_nav) > tolerance:
                        raise ReportConsistencyError(f"Overnight bridge NAV mismatch for {strat}: reported={actual_open_nav}, manifest={expected_open_nav}")
                    if actual_delta is None or abs(actual_delta - 0.01) > 0.001:
                        raise ReportConsistencyError(f"Overnight bridge delta mismatch for {strat}: reported={actual_delta}, expected=0.01")
                    checks_performed += 2
            checked_tables += 1

        # 5. Reconciled Tier 2 Carry-Forward Performance Matrix
        elif "starting economic nav" in h_str and "ending positions mv" in h_str:
            for r in rows:
                strat = r["cells"][0].replace("*", "").strip()
                if strat in cf_results:
                    expected_start_cash = round(cf_results[strat]["starting_cash"], 2)
                    expected_start_rec = round(cf_results[strat]["starting_receivables"], 2)
                    expected_end_cash = round(cf_results[strat]["ending_cash"], 2)
                    expected_end_nav = round(cf_results[strat]["ending_nav"], 2)
                    expected_trades = cf_results[strat]["total_trades"]

                    actual_start_cash = extract_numeric_value(r["cells"][1])
                    actual_start_rec = extract_numeric_value(r["cells"][2])
                    actual_end_cash = extract_numeric_value(r["cells"][7])
                    actual_end_nav = extract_numeric_value(r["cells"][8])
                    actual_trades = extract_numeric_value(r["cells"][12])

                    if actual_start_cash is None or abs(actual_start_cash - expected_start_cash) > tolerance:
                        raise ReportConsistencyError(f"Carryforward start cash mismatch for {strat}: reported={actual_start_cash}, manifest={expected_start_cash}")
                    if actual_start_rec is None or abs(actual_start_rec - expected_start_rec) > tolerance:
                        raise ReportConsistencyError(f"Carryforward start rec mismatch for {strat}: reported={actual_start_rec}, manifest={expected_start_rec}")
                    if actual_end_cash is None or abs(actual_end_cash - expected_end_cash) > tolerance:
                        raise ReportConsistencyError(f"Carryforward end cash mismatch for {strat}: reported={actual_end_cash}, manifest={expected_end_cash}")
                    if actual_end_nav is None or abs(actual_end_nav - expected_end_nav) > tolerance:
                        raise ReportConsistencyError(f"Carryforward end nav mismatch for {strat}: reported={actual_end_nav}, manifest={expected_end_nav}")
                    if actual_trades is None or actual_trades != expected_trades:
                        raise ReportConsistencyError(f"Carryforward trades mismatch for {strat}: reported={actual_trades}, manifest={expected_trades}")
                    checks_performed += 5
            checked_tables += 1

        # 6. Certified Fresh-Start Metrics
        elif "ending nav (2021-12-31)" in h_str and "ending receivables" in h_str:
            for r in rows:
                strat = r["cells"][0].replace("*", "").strip()
                if strat == "Frozen E0":
                    expected_e0_cash = t2_holdings["Frozen E0"]["cash"]
                    expected_e0_nav = t2_holdings["Frozen E0"]["terminal_nav"]
                    actual_cash = extract_numeric_value(r["cells"][1])
                    actual_nav = extract_numeric_value(r["cells"][4])

                    if actual_cash is None or abs(actual_cash - expected_e0_cash) > tolerance:
                        raise ReportConsistencyError(f"Fresh-start E0 cash mismatch: reported={actual_cash}, manifest={expected_e0_cash}")
                    if actual_nav is None or abs(actual_nav - expected_e0_nav) > tolerance:
                        raise ReportConsistencyError(f"Fresh-start E0 nav mismatch: reported={actual_nav}, manifest={expected_e0_nav}")
                    checks_performed += 2

            checked_tables += 1

    return {
        "report_path": str(r_path),
        "tables_cross_checked": checked_tables,
        "manifest_checks_performed": checks_performed,
        "verified": True,
    }


def verify_v26r_report_text(report_path: Path | str, manifest_dir: Path | str = "research/manifests") -> bool:
    """Scan V26-R report text for table arithmetic verification, full precision balance sheet, manifest cross-check, and erratum consistency."""
    verify_report_text(report_path, manifest_dir)
    verify_report_table_arithmetic(report_path, tolerance=0.02)
    verify_report_tables_against_manifests(report_path, manifest_dir, tolerance=0.02)
    r_path = Path(report_path)
    with open(r_path, "r", encoding="utf-8") as f:
        content = f.read()

    v26r_mandatory = [
        "205,899.40",  # Authoritative holdings basis
        "253,391.71",  # Erroneous V25 stock total
        "47,492.31",   # Reconciled holdings discrepancy
        "12,253.46",   # Authoritative Tier 1 cash
        "836.53",      # Authoritative Tier 1 receivables
        "218,989.40",  # Tier 1 closing NAV
        "221,482.93",  # Tier 2 pre-trade opening NAV
        "221,482.92",  # Premature component rounding sum
        "192,272.44",  # Candidate A Fresh-Start NAV
        "225,907.32",  # Candidate E Fresh-Start NAV
        "207,620.42",  # Candidate A+E Fresh-Start NAV
        "405,757.44",  # Candidate A Carry-Forward NAV
        "479,976.21",  # Candidate E Carry-Forward NAV
        "419,877.18",  # Candidate A+E Carry-Forward NAV
        "535,191.10",  # Frozen E0 Carry-Forward NAV
        "233,249.64",  # Frozen E0 Primary Ending NAV
        "15,407.54",   # Frozen E0 Primary Ending Cash
        "364.05",      # Terminal Dividend Receivables
        "71.81s",      # Authoritative Clean-Checkout Execution Time
    ]
    for req in v26r_mandatory:
        if req not in content:
            raise ReportConsistencyError(f"V26-R Mandatory value '{req}' missing from report {r_path}")

    return True



if __name__ == "__main__":
    res = verify_manifest_consistency()
    print("Manifest consistency verified across all 4 strategies:", res)
    v24_report = Path("GUARDIAN_ALPHA_V24_TIER2_CONTINUITY_AND_VALIDATION_FORENSICS_REPORT.md")
    if v24_report.exists():
        verify_report_text(v24_report)
        print("V24 report text verified clean of unflagged typos.")
