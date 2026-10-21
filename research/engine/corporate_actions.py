"""Point-in-Time Corporate Actions Engine.

Handles stock splits (forward/reverse) and cash dividends on their exact ex-dates,
preserving portfolio accounting invariants without requiring retroactive historical price restatements.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StockSplitEvent:
    ex_date: str
    ticker: str
    split_ratio: float  # e.g., 2.0 for 2-for-1 forward split, 0.5 for 1-for-2 reverse split


@dataclass(frozen=True)
class CashDividendEvent:
    ex_date: str
    ticker: str
    amount_per_share: float  # Cash amount in USD per held share


class CorporateActionRegistry:
    """Stores and executes verified corporate action events."""

    def __init__(self) -> None:
        self._splits: dict[str, list[StockSplitEvent]] = {}
        self._dividends: dict[str, list[CashDividendEvent]] = {}

    def register_split(self, ex_date: str, ticker: str, split_ratio: float) -> None:
        if split_ratio <= 0.0:
            raise ValueError(f"Split ratio must be positive, got {split_ratio}")
        event = StockSplitEvent(ex_date=str(ex_date)[:10], ticker=ticker.upper(), split_ratio=float(split_ratio))
        self._splits.setdefault(event.ex_date, []).append(event)

    def register_dividend(self, ex_date: str, ticker: str, amount_per_share: float) -> None:
        if amount_per_share <= 0.0:
            raise ValueError(f"Dividend amount must be positive, got {amount_per_share}")
        event = CashDividendEvent(
            ex_date=str(ex_date)[:10], ticker=ticker.upper(), amount_per_share=float(amount_per_share)
        )
        self._dividends.setdefault(event.ex_date, []).append(event)

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

    def apply_dividends_for_date(
        self,
        date_str: str,
        positions: dict[str, float],
    ) -> tuple[float, list[dict[str, Any]]]:
        """Apply cash dividends occurring on date_str.

        Returns total cash credited and execution logs.
        """
        total_payout = 0.0
        logs: list[dict[str, Any]] = []
        events = self._dividends.get(date_str, [])
        for ev in events:
            sym = ev.ticker
            held = positions.get(sym, 0.0)
            if held > 0.0:
                payout = held * ev.amount_per_share
                total_payout += payout
                logs.append({
                    "action": "cash_dividend",
                    "ticker": sym,
                    "date": date_str,
                    "held_qty": held,
                    "amount_per_share": ev.amount_per_share,
                    "total_payout": payout,
                })
        return total_payout, logs
