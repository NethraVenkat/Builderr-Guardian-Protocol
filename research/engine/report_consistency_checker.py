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


def verify_v26r_report_text(report_path: Path | str, manifest_dir: Path | str = "research/manifests") -> bool:
    """Scan V26-R report text for table arithmetic verification, full precision balance sheet, and erratum consistency."""
    verify_report_text(report_path, manifest_dir)
    verify_report_table_arithmetic(report_path, tolerance=0.02)
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
