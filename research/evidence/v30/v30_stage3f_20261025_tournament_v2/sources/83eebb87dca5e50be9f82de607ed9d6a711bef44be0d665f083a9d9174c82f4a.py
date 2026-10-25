"""
Guardian Alpha — V30 Stage 2A-F Final Hardened Broker Accounting Engine.

This module provides the final, hardened execution-safety and broker settlement architecture,
correcting partial-fill fund reservation release, multi-status cancellations,
and business-day settlement calendars.

All changes are non-invasive and located strictly in this new file.
Zero modifications to agent.py, v12_candidate_ae.py, universe.json, or Stage 2A/2A-R files.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
from typing import Any, Callable


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class BrokerModel(str, Enum):
    MODEL_1_STRICT_SETTLED_CASH = "MODEL_1_STRICT_SETTLED_CASH"
    MODEL_2_CONFIRMED_SEQUENTIAL = "MODEL_2_CONFIRMED_SEQUENTIAL"
    MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION = "MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION"


def compute_settlement_date(trade_date_str: str, lag_business_days: int = 1) -> str:
    """
    Calculate contractual settlement date skipping weekends.
    Standard US equity settlement convention (T+1 since May 2024, historically T+2).
    """
    dt = datetime.strptime(trade_date_str[:10], "%Y-%m-%d")
    added = 0
    while added < lag_business_days:
        dt += timedelta(days=1)
        # 5 is Saturday, 6 is Sunday
        if dt.weekday() < 5:
            added += 1
    return dt.strftime("%Y-%m-%d")


@dataclass
class OrderIntent:
    order_id: str
    ticker: str
    side: OrderSide
    requested_qty: float
    created_date: str
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: float = 0.0
    fill_price: float = 0.0
    commission: float = 0.0
    effective_slippage_bps: float = 0.0
    reserved_cash: float = 0.0
    reserved_qty: float = 0.0
    rejection_reason: str | None = None
    settlement_date: str | None = None


@dataclass
class DividendReceivable:
    ticker: str
    ex_date: str
    payment_date: str
    amount_per_share: float
    qualifying_shares: float
    total_amount: float
    settled: bool = False


class FinalIndependentLedger:
    """
    Final institutional double-entry financial ledger with proportional
    fund reservation and business-day settlement guarantees.
    """

    def __init__(
        self,
        opening_cash: float = 100_000.0,
        settlement_delay_days: int = 1,
        broker_model: BrokerModel = BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL,
        sell_proceeds_haircut: float = 0.10,
        buy_slippage_markup: float = 0.05,
        cash_reserve_floor_pct: float = 0.02,
    ) -> None:
        self.opening_cash: float = float(opening_cash)
        self.settled_cash: float = float(opening_cash)
        self.reserved_cash: float = 0.0
        self.settlement_delay_days: int = settlement_delay_days
        self.broker_model: BrokerModel = broker_model
        self.sell_haircut: float = sell_proceeds_haircut
        self.buy_markup: float = buy_slippage_markup
        self.reserve_floor_pct: float = cash_reserve_floor_pct

        # Holdings: physically owned vs committed to open sell orders
        self.positions: dict[str, float] = {}
        self.position_reserved: dict[str, float] = {}
        self.avg_cost: dict[str, float] = {}

        # Receivables & obligations
        self.unsettled_cash_receivables: list[dict[str, Any]] = []
        self.dividend_receivables: list[DividendReceivable] = []
        self.liabilities: float = 0.0

        # Flow tracking
        self.cumulative_buy_outflows: float = 0.0
        self.cumulative_buy_commissions: float = 0.0
        self.cumulative_sell_inflows: float = 0.0
        self.cumulative_commissions: float = 0.0
        self.cumulative_dividends_credited: float = 0.0
        self.cumulative_realized_pnl: float = 0.0

        self.orders_history: list[OrderIntent] = []

    def available_settled_cash(self) -> float:
        return max(0.0, self.settled_cash - self.reserved_cash)

    def total_unsettled_proceeds(self) -> float:
        return sum(item["amount"] for item in self.unsettled_cash_receivables if not item.get("settled", False))

    def total_dividend_receivables(self) -> float:
        return sum(d.total_amount for d in self.dividend_receivables if not d.settled)

    def calculate_buying_power(
        self,
        current_prices: dict[str, float] | None = None,
        model: BrokerModel | None = None,
    ) -> float:
        active_model = model or self.broker_model
        prices = current_prices or {}
        tot_eq = self.total_account_equity(prices)
        reserve_floor = tot_eq * self.reserve_floor_pct

        free_cash = self.settled_cash - self.reserved_cash
        return max(0.0, free_cash - reserve_floor)

    def submit_buy_order(
        self,
        order_id: str,
        ticker: str,
        requested_qty: float,
        current_date: str,
        est_price: float,
        commission_bps: float = 0.0,
    ) -> tuple[OrderIntent, bool, str]:
        if requested_qty <= 0.0 or not math.isfinite(requested_qty):
            order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="INVALID_QUANTITY")
            self.orders_history.append(order)
            return order, False, "INVALID_QUANTITY"

        if est_price <= 0.0 or not math.isfinite(est_price):
            order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="MISSING_PRICE")
            self.orders_history.append(order)
            return order, False, "MISSING_PRICE"

        buffered_price = est_price * (1.0 + self.buy_markup)
        est_cost = buffered_price * requested_qty
        est_comm = est_cost * (commission_bps / 10_000.0)
        total_required = est_cost + est_comm

        available_bp = self.calculate_buying_power()
        if total_required > available_bp:
            order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="INSUFFICIENT_CASH")
            self.orders_history.append(order)
            return order, False, f"INSUFFICIENT_CASH (Req: ${total_required:,.2f}, BP: ${available_bp:,.2f})"

        # Lock funds
        self.reserved_cash += total_required
        order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.SUBMITTED, reserved_cash=total_required)
        self.orders_history.append(order)
        return order, True, "SUBMITTED"

    def submit_sell_order(
        self,
        order_id: str,
        ticker: str,
        requested_qty: float,
        current_date: str,
    ) -> tuple[OrderIntent, bool, str]:
        if requested_qty <= 0.0 or not math.isfinite(requested_qty):
            order = OrderIntent(order_id, ticker, OrderSide.SELL, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="INVALID_QUANTITY")
            self.orders_history.append(order)
            return order, False, "INVALID_QUANTITY"

        held = self.positions.get(ticker, 0.0)
        already_reserved = self.position_reserved.get(ticker, 0.0)
        available_to_sell = held - already_reserved

        if available_to_sell <= 1e-9:
            order = OrderIntent(order_id, ticker, OrderSide.SELL, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="UNHELD_POSITION")
            self.orders_history.append(order)
            return order, False, "UNHELD_POSITION"

        submittable = min(requested_qty, available_to_sell)
        self.position_reserved[ticker] = already_reserved + submittable
        order = OrderIntent(order_id, ticker, OrderSide.SELL, submittable, current_date, OrderStatus.SUBMITTED, reserved_qty=submittable)
        self.orders_history.append(order)
        return order, True, "SUBMITTED"

    def confirm_buy_fill(
        self,
        order: OrderIntent,
        filled_qty: float,
        fill_price: float,
        commission: float = 0.0,
        effective_slippage_bps: float = 0.0,
    ) -> None:
        """
        Confirm buy fill with PROPORTIONAL reservation release.
        If partially filled, only the proportional reserved cash is released.
        """
        if order.status not in (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"Cannot fill order in status {order.status}")

        actual_cost = filled_qty * fill_price
        total_outflow = actual_cost + commission

        # Proportional reservation release
        if order.requested_qty > 0.0:
            consumed_reservation = order.reserved_cash * (filled_qty / order.requested_qty)
        else:
            consumed_reservation = order.reserved_cash

        self.settled_cash -= total_outflow
        self.reserved_cash = max(0.0, self.reserved_cash - consumed_reservation)
        order.reserved_cash = max(0.0, order.reserved_cash - consumed_reservation)

        # Update physical holdings
        held = self.positions.get(order.ticker, 0.0)
        prev_basis = held * self.avg_cost.get(order.ticker, 0.0)
        new_held = held + filled_qty
        self.positions[order.ticker] = new_held
        self.avg_cost[order.ticker] = (prev_basis + actual_cost) / new_held if new_held > 0 else 0.0

        self.cumulative_buy_outflows += actual_cost
        self.cumulative_buy_commissions += commission
        self.cumulative_commissions += commission

        order.filled_qty += filled_qty
        order.fill_price = fill_price
        order.commission += commission
        order.effective_slippage_bps = effective_slippage_bps
        order.status = OrderStatus.FILLED if abs(order.filled_qty - order.requested_qty) < 1e-9 else OrderStatus.PARTIALLY_FILLED

    def confirm_sell_fill(
        self,
        order: OrderIntent,
        filled_qty: float,
        fill_price: float,
        current_date: str,
        settlement_date: str | None = None,
        commission: float = 0.0,
        effective_slippage_bps: float = 0.0,
    ) -> None:
        if order.status not in (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"Cannot fill order in status {order.status}")

        actual_proceeds = filled_qty * fill_price
        net_inflow = actual_proceeds - commission

        # Release reserved shares
        self.position_reserved[order.ticker] = max(
            0.0, self.position_reserved.get(order.ticker, 0.0) - filled_qty
        )
        order.reserved_qty = max(0.0, order.reserved_qty - filled_qty)

        held = self.positions.get(order.ticker, 0.0)
        new_held = max(0.0, held - filled_qty)
        cost_basis = filled_qty * self.avg_cost.get(order.ticker, 0.0)
        if new_held <= 1e-9:
            self.positions.pop(order.ticker, None)
            self.avg_cost.pop(order.ticker, None)
        else:
            self.positions[order.ticker] = new_held

        realized_pnl = net_inflow - cost_basis
        self.cumulative_realized_pnl += realized_pnl
        self.cumulative_sell_inflows += actual_proceeds
        self.cumulative_commissions += commission

        settle_dt = settlement_date or compute_settlement_date(current_date, self.settlement_delay_days)

        if self.broker_model == BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL:
            self.settled_cash += net_inflow
        else:
            self.unsettled_cash_receivables.append({
                "settlement_date": settle_dt,
                "amount": net_inflow,
                "origin": f"SELL_{order.ticker}_{order.order_id}",
                "settled": False,
            })

        order.filled_qty += filled_qty
        order.fill_price = fill_price
        order.commission += commission
        order.effective_slippage_bps = effective_slippage_bps
        order.settlement_date = settle_dt
        order.status = OrderStatus.FILLED if abs(order.filled_qty - order.requested_qty) < 1e-9 else OrderStatus.PARTIALLY_FILLED

    def cancel_order(self, order: OrderIntent, reason: str = "CANCELLED") -> None:
        """
        Cancel order: safely releases remaining reserved cash or shares,
        supporting both SUBMITTED and PARTIALLY_FILLED orders.
        """
        if order.status in (OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED):
            if order.side == OrderSide.BUY:
                self.reserved_cash = max(0.0, self.reserved_cash - order.reserved_cash)
                order.reserved_cash = 0.0
            elif order.side == OrderSide.SELL:
                self.position_reserved[order.ticker] = max(
                    0.0, self.position_reserved.get(order.ticker, 0.0) - order.reserved_qty
                )
                order.reserved_qty = 0.0
            order.status = OrderStatus.CANCELLED
            order.rejection_reason = reason

    def process_cash_settlements(self, current_date: str) -> float:
        credited = 0.0
        for rec in self.unsettled_cash_receivables:
            if not rec.get("settled", False) and rec["settlement_date"] <= current_date:
                self.settled_cash += rec["amount"]
                rec["settled"] = True
                credited += rec["amount"]
        return credited

    def record_dividend_ex_date(
        self,
        ticker: str,
        ex_date: str,
        payment_date: str,
        amount_per_share: float,
    ) -> float:
        held = self.positions.get(ticker, 0.0)
        if held <= 0.0 or amount_per_share <= 0.0:
            return 0.0
        total_due = held * amount_per_share
        self.dividend_receivables.append(
            DividendReceivable(ticker, ex_date, payment_date, amount_per_share, held, total_due, False)
        )
        return total_due

    def process_dividend_payments(self, current_date: str) -> float:
        credited = 0.0
        for div in self.dividend_receivables:
            if not div.settled and div.payment_date <= current_date:
                self.settled_cash += div.total_amount
                self.cumulative_dividends_credited += div.total_amount
                div.settled = True
                credited += div.total_amount
        return credited

    def apply_stock_split(self, ticker: str, split_ratio: float) -> None:
        if split_ratio <= 0.0:
            raise ValueError(f"Invalid split ratio {split_ratio}")
        held = self.positions.get(ticker, 0.0)
        if held > 0.0:
            old_basis = held * self.avg_cost.get(ticker, 0.0)
            new_held = held * split_ratio
            self.positions[ticker] = new_held
            self.avg_cost[ticker] = old_basis / new_held
            if ticker in self.position_reserved:
                self.position_reserved[ticker] *= split_ratio

    def marked_holdings_value(self, current_prices: dict[str, float]) -> float:
        return sum(
            qty * current_prices.get(sym, self.avg_cost.get(sym, 0.0))
            for sym, qty in self.positions.items()
        )

    def total_unrealized_pnl(self, current_prices: dict[str, float]) -> float:
        pnl = 0.0
        for sym, qty in self.positions.items():
            px = current_prices.get(sym, self.avg_cost.get(sym, 0.0))
            cost = self.avg_cost.get(sym, 0.0)
            pnl += (px - cost) * qty
        return pnl

    def total_account_equity(self, current_prices: dict[str, float]) -> float:
        marked = self.marked_holdings_value(current_prices)
        unsettled_sales = self.total_unsettled_proceeds()
        unsettled_divs = self.total_dividend_receivables()
        return self.settled_cash + marked + unsettled_sales + unsettled_divs - self.liabilities

    def verify_cash_invariants(self) -> tuple[bool, str]:
        settled_sales = self.cumulative_sell_inflows if self.broker_model == BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL else sum(
            rec["amount"] for rec in self.unsettled_cash_receivables if rec.get("settled", False)
        )
        expected_cash = (
            self.opening_cash
            + settled_sales
            - self.cumulative_buy_outflows
            - self.cumulative_commissions
            + self.cumulative_dividends_credited
        )
        diff = abs(self.settled_cash - expected_cash)
        if diff > 1e-4:
            return False, f"Cash Invariant Mismatch: Settled={self.settled_cash:.4f} vs Expected={expected_cash:.4f} (Diff: {diff:.6f})"
        return True, "Cash invariant strictly conserved"

    def verify_balance_sheet(self, current_prices: dict[str, float]) -> tuple[bool, str]:
        equity_from_assets = self.total_account_equity(current_prices)
        unrealized = self.total_unrealized_pnl(current_prices)
        total_dividends = self.cumulative_dividends_credited + self.total_dividend_receivables()

        equity_from_income = (
            self.opening_cash
            + self.cumulative_realized_pnl
            + unrealized
            + total_dividends
            - self.cumulative_buy_commissions
        )
        diff = abs(equity_from_assets - equity_from_income)
        if diff > 1e-3:
            return False, f"Balance Sheet Mismatch: Assets={equity_from_assets:.4f} vs Income={equity_from_income:.4f} (Diff: {diff:.6f})"
        return True, "Balance sheet perfectly reconciled"

    def verify_non_negativity(self) -> tuple[bool, str]:
        if self.settled_cash < -1e-9:
            return False, f"Negative cash detected: {self.settled_cash:.4f}"
        for sym, qty in self.positions.items():
            if qty < -1e-9:
                return False, f"Negative position for {sym}: {qty:.6f}"
        return True, "Strict non-negativity conserved"
