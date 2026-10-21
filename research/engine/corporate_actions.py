"""Point-in-Time Corporate Actions Engine with Full Lifecycle Accounting.

Supports:
  1. Stock splits (forward and reverse) on ex-date before market open.
  2. Cash dividends with distinct Ex-Date, Record Date, and Payment Date:
     - On Ex-Date: creates Dividend Receivable entitlement without immediate cash.
     - On Payment Date: converts Dividend Receivable into spendable Cash.
     - Compatibility Mode: optional instant cash credit on ex-date for preview.py parity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class MissingPaymentDateError(ValueError):
    """Raised when dividend payment_date is missing and policy is REJECT."""
    pass


class PaymentDatePolicy(str, Enum):
    """Explicit policy for handling dividends with missing payment dates."""
    REJECT = "REJECT"                             # Strict research gate: raises MissingPaymentDateError
    IMPUTE_SETTLEMENT_LAG = "IMPUTE_SETTLEMENT_LAG"   # Documented proxy: ex_date + 14 calendar days, audit logged
    EX_DATE_COMPATIBILITY = "EX_DATE_COMPATIBILITY"   # Legacy / preview.py parity mode: ex_date = payment_date


@dataclass(frozen=True)
class StockSplitEvent:
    ex_date: str
    ticker: str
    split_ratio: float  # e.g., 2.0 for 2-for-1 forward split, 0.5 for 1-for-2 reverse split


@dataclass(frozen=True)
class CashDividendEvent:
    ex_date: str          # Date stock trades ex-dividend (ownership cutoff)
    record_date: str      # Date company finalizes eligible shareholders
    payment_date: str     # Date cash is actually credited to broker account
    ticker: str
    amount_per_share: float  # Cash dividend per share in USD


@dataclass
class DividendReceivable:
    ticker: str
    ex_date: str
    payment_date: str
    held_qty: float
    amount_per_share: float
    total_amount: float


class CorporateActionRegistry:
    """Manages verified corporate actions across the investment lifecycle."""

    def __init__(
        self,
        instant_credit_compatibility: bool = False,
        payment_date_policy: PaymentDatePolicy | None = None,
    ) -> None:
        self.instant_credit_compatibility = instant_credit_compatibility
        if payment_date_policy is not None:
            self.payment_date_policy = payment_date_policy
        elif instant_credit_compatibility:
            self.payment_date_policy = PaymentDatePolicy.EX_DATE_COMPATIBILITY
        else:
            self.payment_date_policy = PaymentDatePolicy.REJECT
        self._splits: dict[str, list[StockSplitEvent]] = {}
        self._dividends_by_ex: dict[str, list[CashDividendEvent]] = {}
        self._dividends_by_pay: dict[str, list[CashDividendEvent]] = {}
        self.receivables: list[DividendReceivable] = []
        self.imputation_audit_log: list[dict[str, Any]] = []

    def register_split(self, ex_date: str, ticker: str, split_ratio: float) -> None:
        if split_ratio <= 0.0:
            raise ValueError(f"Split ratio must be positive, got {split_ratio}")
        event = StockSplitEvent(ex_date=str(ex_date)[:10], ticker=ticker.upper(), split_ratio=float(split_ratio))
        existing = self._splits.setdefault(event.ex_date, [])
        if event not in existing:
            existing.append(event)

    def register_dividend(
        self,
        ex_date: str,
        ticker: str,
        amount_per_share: float,
        record_date: str | None = None,
        payment_date: str | None = None,
        policy: PaymentDatePolicy | None = None,
    ) -> None:
        if amount_per_share <= 0.0:
            raise ValueError(f"Dividend amount must be positive, got {amount_per_share}")
        ex_d = str(ex_date)[:10]
        rec_d = str(record_date)[:10] if record_date else ex_d

        effective_policy = policy or self.payment_date_policy

        if payment_date is not None and str(payment_date).strip() != "":
            pay_d = str(payment_date)[:10]
        else:
            # Payment date is missing - handle via explicit policy rather than silent substitution
            if effective_policy == PaymentDatePolicy.REJECT:
                raise MissingPaymentDateError(
                    f"Missing payment date for {ticker} dividend on ex-date {ex_d}. "
                    f"Silent substitution of ex-date as payment date is prohibited under PaymentDatePolicy.REJECT."
                )
            elif effective_policy == PaymentDatePolicy.IMPUTE_SETTLEMENT_LAG:
                dt = datetime.strptime(ex_d, "%Y-%m-%d") + timedelta(days=14)
                pay_d = dt.strftime("%Y-%m-%d")
                self.imputation_audit_log.append({
                    "warning": "UNVERIFIED_PAYMENT_DATE_IMPUTATION",
                    "ticker": ticker.upper(),
                    "ex_date": ex_d,
                    "imputed_payment_date": pay_d,
                    "method": "SETTLEMENT_LAG_14D",
                })
            elif effective_policy == PaymentDatePolicy.EX_DATE_COMPATIBILITY:
                pay_d = ex_d
                self.imputation_audit_log.append({
                    "warning": "EX_DATE_COMPATIBILITY_IMPUTATION",
                    "ticker": ticker.upper(),
                    "ex_date": ex_d,
                    "imputed_payment_date": pay_d,
                    "method": "EX_DATE_EQUIVALENCE",
                })
            else:
                raise ValueError(f"Unknown PaymentDatePolicy: {effective_policy}")

        event = CashDividendEvent(
            ex_date=ex_d,
            record_date=rec_d,
            payment_date=pay_d,
            ticker=ticker.upper(),
            amount_per_share=float(amount_per_share),
        )
        existing_ex = self._dividends_by_ex.setdefault(event.ex_date, [])
        if event not in existing_ex:
            existing_ex.append(event)
        existing_pay = self._dividends_by_pay.setdefault(event.payment_date, [])
        if event not in existing_pay:
            existing_pay.append(event)

    def apply_splits_for_date(
        self,
        date_str: str,
        positions: dict[str, float],
        avg_cost: dict[str, float],
    ) -> list[dict[str, Any]]:
        """Apply stock splits occurring on date_str before trading open.

        Updates positions and avg_cost in-place.
        Invariant: held_quantity * avg_cost remains constant before slippage/fees.
        """
        logs: list[dict[str, Any]] = []
        events = self._splits.get(date_str, [])
        for ev in events:
            sym = ev.ticker
            if sym in positions and positions[sym] > 0.0:
                old_qty = positions[sym]
                old_cost = avg_cost.get(sym, 0.0)
                new_qty = old_qty * ev.split_ratio
                new_cost = old_cost / ev.split_ratio if ev.split_ratio > 0 else old_cost

                positions[sym] = new_qty
                avg_cost[sym] = new_cost
                logs.append({
                    "action": "stock_split",
                    "ticker": sym,
                    "date": date_str,
                    "ratio": ev.split_ratio,
                    "old_qty": old_qty,
                    "new_qty": new_qty,
                    "old_cost": old_cost,
                    "new_cost": new_cost,
                })
        return logs

    def process_dividends_for_date(
        self,
        date_str: str,
        positions: dict[str, float],
    ) -> tuple[float, float, list[dict[str, Any]]]:
        """Process dividends for date_str.

        Returns:
          (cash_credited_today, new_receivables_booked_today, logs)
        """
        logs: list[dict[str, Any]] = []
        cash_credited = 0.0
        new_receivables = 0.0

        # Step 1: Handle Ex-Dates occurring today
        for ev in self._dividends_by_ex.get(date_str, []):
            held = positions.get(ev.ticker, 0.0)
            if held > 0.0:
                payout = held * ev.amount_per_share
                # If payment date is today or compatibility mode is enabled, credit cash immediately
                if self.instant_credit_compatibility or ev.payment_date <= date_str:
                    cash_credited += payout
                    logs.append({
                        "action": "cash_dividend",
                        "ticker": ev.ticker,
                        "date": date_str,
                        "held_qty": held,
                        "amount_per_share": ev.amount_per_share,
                        "total_payout": payout,
                        "cash_credited": payout,
                    })
                else:
                    # Entitlement booked as dividend receivable on balance sheet
                    rec = DividendReceivable(
                        ticker=ev.ticker,
                        ex_date=ev.ex_date,
                        payment_date=ev.payment_date,
                        held_qty=held,
                        amount_per_share=ev.amount_per_share,
                        total_amount=payout,
                    )
                    self.receivables.append(rec)
                    new_receivables += payout
                    logs.append({
                        "action": "dividend_entitlement_booked",
                        "ticker": ev.ticker,
                        "ex_date": date_str,
                        "payment_date": ev.payment_date,
                        "held_qty": held,
                        "amount_per_share": ev.amount_per_share,
                        "total_payout": payout,
                        "receivable_booked": payout,
                    })

        # Step 2: On Payment Date, convert previously booked Receivables into spendable Cash
        remaining_receivables: list[DividendReceivable] = []
        for rec in self.receivables:
            if rec.payment_date <= date_str:
                cash_credited += rec.total_amount
                logs.append({
                    "action": "dividend_receivable_paid",
                    "ticker": rec.ticker,
                    "ex_date": rec.ex_date,
                    "payment_date": date_str,
                    "total_payout": rec.total_amount,
                    "cash_credited": rec.total_amount,
                })
            else:
                remaining_receivables.append(rec)
        self.receivables = remaining_receivables

        return cash_credited, new_receivables, logs

    def apply_dividends_for_date(
        self,
        date_str: str,
        positions: dict[str, float],
    ) -> tuple[float, list[dict[str, Any]]]:
        """Backward-compatible interface returning (cash_credited, logs)."""
        cash_credited, _, logs = self.process_dividends_for_date(date_str, positions)
        return cash_credited, logs

    def total_outstanding_receivables(self) -> float:
        """Total dividend receivables awaiting cash payment on the balance sheet."""
        return sum(rec.total_amount for rec in self.receivables)
