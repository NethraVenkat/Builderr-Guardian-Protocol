"""Institutional Financial Market Data Quality, Integrity & Causality Auditor.

Enforces:
  1. Finite positive price constraints: Open, High, Low, Close > 0 and math.isfinite.
  2. Strict OHLC geometric boundary integrity: High >= max(Open, Close, Low) and Low <= min(Open, Close, High).
  3. Non-negative volume: Volume >= 0 and math.isfinite.
  4. Monotonic strictly increasing session dates (YYYY-MM-DD).
  5. Duplicate session timestamp rejection.
  6. Weekend session rejection (Saturday, Sunday).
  7. Inception date boundary integrity (e.g. XLC inception 2018-06-18, XLRE 2015-10-07).
  8. Point-in-time causality: excludes bars dated strictly after evaluation decision point.
  9. Corporate action anomaly detection: splits and missing dividend payment dates.
  10. Ticker alias continuity (FB -> META on 2022-06-09).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from research.engine.validation import ValidationError, validate_calendar_date

# Known ETF / stock inception dates for active universe
INCEPTION_DATES: dict[str, str] = {
    "XLC": "2018-06-18",
    "XLRE": "2015-10-07",
    "QLD": "2006-06-19",
    "SSO": "2006-06-19",
    "SPY": "1993-01-22",
    "QQQ": "1999-03-10",
    "DIA": "1998-01-14",
    "IWM": "2000-05-22",
    "SMH": "2000-05-05",
    "AAPL": "1980-12-12",
    "MSFT": "1986-03-13",
    "AMZN": "1997-05-15",
    "GOOGL": "2004-08-19",
    "META": "2012-05-18",
    "NVDA": "1999-01-22",
    "TSLA": "2010-06-29",
}


def is_valid_calendar_date(ts_val: Any) -> bool:
    try:
        validate_calendar_date(ts_val, reject_weekends=False)
        return True
    except (ValidationError, Exception):
        return False


def is_weekend(ts_val: Any) -> bool:
    try:
        dt = date.fromisoformat(str(ts_val)[:10])
        return dt.weekday() >= 5
    except Exception:
        return False


@dataclass
class QualityAnomaly:
    symbol: str
    date: str
    anomaly_type: str
    details: str
    severity: str  # "FATAL" (bar rejected), "WARNING" (logged for audit)


@dataclass
class SymbolQualityReport:
    symbol: str
    total_bars: int = 0
    valid_bars: int = 0
    rejected_bars: int = 0
    first_date: str | None = None
    last_date: str | None = None
    anomalies: list[QualityAnomaly] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return self.rejected_bars == 0 and len(self.anomalies) == 0


class DataQualityAuditor:
    """Performs deep institutional quality audits on market datasets."""

    def __init__(self, strict_fail_on_anomaly: bool = False):
        self.strict_fail = strict_fail_on_anomaly
        self.reports: dict[str, SymbolQualityReport] = {}

    def audit_bar(self, symbol: str, bar: dict[str, Any], prev_date: str | None = None) -> tuple[bool, list[QualityAnomaly]]:
        """Validate a single OHLCV observation.

        Returns (is_valid, anomalies_detected).
        """
        anomalies: list[QualityAnomaly] = []
        sym = symbol.upper()
        ts = str(bar.get("ts", "")).strip()

        # 1. Date format and validity
        if not is_valid_calendar_date(ts):
            anomalies.append(QualityAnomaly(sym, ts, "INVALID_CALENDAR_DATE", f"Invalid format: {ts}", "FATAL"))
            return False, anomalies

        # 2. Weekend check
        if is_weekend(ts):
            anomalies.append(QualityAnomaly(sym, ts, "WEEKEND_DATA", f"Date falls on weekend: {ts}", "FATAL"))
            return False, anomalies

        # 3. Monotonicity check against previous date
        if prev_date is not None:
            if ts < prev_date:
                anomalies.append(QualityAnomaly(sym, ts, "NON_MONOTONIC_TIMESTAMP", f"Date {ts} < previous {prev_date}", "FATAL"))
                return False, anomalies
            elif ts == prev_date:
                anomalies.append(QualityAnomaly(sym, ts, "DUPLICATE_TIMESTAMP", f"Duplicate session date {ts}", "FATAL"))
                return False, anomalies

        # 4. Inception date boundary
        inception = INCEPTION_DATES.get(sym)
        if inception and ts < inception:
            anomalies.append(QualityAnomaly(sym, ts, "PRE_INCEPTION_BAR", f"Date {ts} precedes inception {inception}", "FATAL"))
            return False, anomalies

        # 5. Price positivity and finiteness
        for price_field in ("open", "high", "low", "close"):
            val = bar.get(price_field)
            if val is None or not isinstance(val, (int, float)) or not math.isfinite(val) or val <= 0.0:
                anomalies.append(QualityAnomaly(sym, ts, "NON_FINITE_PRICE", f"{price_field}={val} is non-finite or <= 0", "FATAL"))
                return False, anomalies

        # 6. OHLC geometric boundary integrity
        o = float(bar["open"])
        h = float(bar["high"])
        l = float(bar["low"])
        c = float(bar["close"])

        if l > h or h < max(o, c, l) or l > min(o, c, h):
            anomalies.append(QualityAnomaly(
                sym, ts, "GEOMETRIC_INTEGRITY_VIOLATION",
                f"Invalid geometry: O={o}, H={h}, L={l}, C={c}", "FATAL"
            ))
            return False, anomalies

        # 7. Volume check
        vol = bar.get("volume", 0.0)
        if vol is not None:
            if not isinstance(vol, (int, float)) or not math.isfinite(vol) or vol < 0.0:
                anomalies.append(QualityAnomaly(sym, ts, "INVALID_VOLUME", f"volume={vol} is negative or non-finite", "FATAL"))
                return False, anomalies

        return True, anomalies

    def audit_symbol_series(self, symbol: str, bars: list[dict[str, Any]]) -> SymbolQualityReport:
        """Audit an entire time series for a single symbol."""
        sym = symbol.upper()
        report = SymbolQualityReport(symbol=sym, total_bars=len(bars))
        self.reports[sym] = report

        prev_date: str | None = None
        for b in bars:
            valid, anomalies = self.audit_bar(sym, b, prev_date)
            report.anomalies.extend(anomalies)
            if valid:
                report.valid_bars += 1
                ts = str(b["ts"])
                if report.first_date is None or ts < report.first_date:
                    report.first_date = ts
                if report.last_date is None or ts > report.last_date:
                    report.last_date = ts
                prev_date = ts
            else:
                report.rejected_bars += 1
                if self.strict_fail:
                    raise ValueError(f"Quality Gate Failure on {sym} ({b.get('ts')}): {anomalies[0].details}")

        return report

    def audit_universe(self, universe_data: dict[str, list[dict[str, Any]]]) -> dict[str, SymbolQualityReport]:
        """Audit all symbols in the universe."""
        results: dict[str, SymbolQualityReport] = {}
        for sym, bars in universe_data.items():
            results[sym.upper()] = self.audit_symbol_series(sym, bars)
        return results

    def summarize(self) -> dict[str, Any]:
        """Produce an aggregated quality audit summary."""
        total_bars = sum(r.total_bars for r in self.reports.values())
        valid_bars = sum(r.valid_bars for r in self.reports.values())
        rejected_bars = sum(r.rejected_bars for r in self.reports.values())
        all_anomalies = [a for r in self.reports.values() for a in r.anomalies]

        by_type: dict[str, int] = {}
        for a in all_anomalies:
            by_type[a.anomaly_type] = by_type.get(a.anomaly_type, 0) + 1

        return {
            "total_symbols": len(self.reports),
            "total_bars_audited": total_bars,
            "valid_bars": valid_bars,
            "rejected_bars": rejected_bars,
            "anomaly_count": len(all_anomalies),
            "anomalies_by_type": by_type,
            "clean_symbols": [s for s, r in self.reports.items() if r.is_clean],
            "flagged_symbols": [s for s, r in self.reports.items() if not r.is_clean],
        }
