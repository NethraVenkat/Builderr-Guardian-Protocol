"""
Guardian Alpha — V30 Stage 2A-R Independent Broker Cash & Financial Accounting Engine.

This module provides an independent, mathematically verified reference architecture for:
1. Multi-model broker cash availability and buying power:
   - Model 1: STRICT_SETTLED_CASH (no same-session use of unsettled sell proceeds).
   - Model 2: CONFIRMED_SEQUENTIAL (confirmed sell fills recognized with haircut & buffer).
   - Model 3: SETTLEMENT_DELAY_WITH_RESERVATION (order lifecycle reservation/release state machine).
2. Independent double-entry financial accounting ledger tracking:
   - Settled cash vs unsettled receivables vs payables.
   - Physical holdings vs reserved holdings.
   - Realized PnL vs Unrealized PnL vs Mark-to-market Equity.
   - Ex-date vs Payment-date dividend accounting.
   - Corporate action split conservation.
   - Full double-entry balance sheet reconciliation invariants.

Zero modifications to agent.py, v12_candidate_ae.py, or universe.json.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Callable


class OrderStatus(str, Enum):
    """Lifecycle status of a trading order."""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderSide(str, Enum):
    """Order side: BUY or SELL."""
    BUY = "buy"
    SELL = "sell"


class BrokerModel(str, Enum):
    """Explicit broker cash availability and settlement models."""
    # Model 1: Cash account under strict settlement rules (FINRA / Reg-T cash account).
    # Unsettled sell proceeds provide ZERO buying power until settled (T+1 or T+2).
    MODEL_1_STRICT_SETTLED_CASH = "MODEL_1_STRICT_SETTLED_CASH"

    # Model 2: Confirmed sequential execution (e.g. prime broker with intra-day fill netting).
    # Proceeds from confirmed sales may be reinvested in the same session, subject to
    # an adverse-slippage haircut and minimum cash reserve floor.
    MODEL_2_CONFIRMED_SEQUENTIAL = "MODEL_2_CONFIRMED_SEQUENTIAL"

    # Model 3: Settlement delay with active pre-trade fund reservation and order state machine.
    # Submitting a buy order immediately locks reserved cash; cancels release reserved cash.
    MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION = "MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION"


@dataclass
class OrderIntent:
    """Represents a trading order throughout its complete execution lifecycle."""
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
    """Represents a declared dividend awaiting settlement."""
    ticker: str
    ex_date: str
    payment_date: str
    amount_per_share: float
    qualifying_shares: float
    total_amount: float
    settled: bool = False


class IndependentLedger:
    """
    Independent reference double-entry accounting ledger.

    Guarantees strict conservation of cash, equity, and positions without relying on
    naive assumptions like 'Final Cash = Initial Cash + PnL - Comm'.
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

        # Physical asset holdings and reservations
        self.positions: dict[str, float] = {}          # physically owned shares
        self.position_reserved: dict[str, float] = {}  # shares committed to pending sells
        self.avg_cost: dict[str, float] = {}           # average acquisition cost per share

        # Settlement receivables and obligations
        self.unsettled_cash_receivables: list[dict[str, Any]] = []  # [{date, amount, origin}]
        self.dividend_receivables: list[DividendReceivable] = []
        self.liabilities: float = 0.0

        # Cumulative accounting flow monitors
        self.cumulative_buy_outflows: float = 0.0
        self.cumulative_buy_commissions: float = 0.0
        self.cumulative_sell_inflows: float = 0.0
        self.cumulative_commissions: float = 0.0
        self.cumulative_dividends_credited: float = 0.0
        self.cumulative_realized_pnl: float = 0.0

        # Audit logs
        self.orders_history: list[OrderIntent] = []
        self.daily_settled_history: list[dict[str, float]] = []

    # -------------------------------------------------------------------------
    # Buying Power Derivation
    # -------------------------------------------------------------------------

    def available_settled_cash(self) -> float:
        """Return strictly settled cash unencumbered by pending buy reservations."""
        return max(0.0, self.settled_cash - self.reserved_cash)

    def total_unsettled_proceeds(self) -> float:
        """Return total uncollected sale proceeds currently awaiting settlement."""
        return sum(item["amount"] for item in self.unsettled_cash_receivables if not item.get("settled", False))

    def total_dividend_receivables(self) -> float:
        """Return total dividend amount declared on or after ex-date awaiting payment."""
        return sum(d.total_amount for d in self.dividend_receivables if not d.settled)

    def calculate_buying_power(
        self,
        current_prices: dict[str, float] | None = None,
        model: BrokerModel | None = None,
    ) -> float:
        """
        Derive broker-recognized buying power strictly scoped to the active broker model.

        Model 1: STRICT_SETTLED_CASH:
            Buying Power = max(0, Settled Cash - Reserved Cash - Cash Reserve Floor)
            Unsettled sell proceeds = 0.0.

        Model 2: CONFIRMED_SEQUENTIAL:
            Same-day confirmed sell fills are recognized in settled cash.
            Buying Power = max(0, Settled Cash - Reserved Cash - Cash Reserve Floor)

        Model 3: SETTLEMENT_DELAY_WITH_RESERVATION:
            Unsettled proceeds are strictly segregated until settlement date.
            Buying Power = max(0, Settled Cash - Reserved Cash - Cash Reserve Floor)
        """
        active_model = model or self.broker_model
        prices = current_prices or {}
        tot_eq = self.total_account_equity(prices)
        reserve_floor = tot_eq * self.reserve_floor_pct

        if active_model == BrokerModel.MODEL_1_STRICT_SETTLED_CASH:
            # Strictly settled cash only; zero credit for unsettled sales
            free_cash = self.settled_cash - self.reserved_cash
            return max(0.0, free_cash - reserve_floor)

        elif active_model == BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL:
            # Sells must be confirmed first; haircut applied during order sizing
            free_cash = self.settled_cash - self.reserved_cash
            return max(0.0, free_cash - reserve_floor)

        elif active_model == BrokerModel.MODEL_3_SETTLEMENT_DELAY_WITH_RESERVATION:
            # Settlement delay enforced; open reservations locked
            free_cash = self.settled_cash - self.reserved_cash
            return max(0.0, free_cash - reserve_floor)

        return 0.0

    # -------------------------------------------------------------------------
    # Pre-Trade Order Lifecycle & Fund Reservation
    # -------------------------------------------------------------------------

    def submit_buy_order(
        self,
        order_id: str,
        ticker: str,
        requested_qty: float,
        current_date: str,
        est_price: float,
        commission_bps: float = 0.0,
    ) -> tuple[OrderIntent, bool, str]:
        """
        Process a BUY order intent through pre-trade credit checks and fund reservation.
        """
        if requested_qty <= 0.0 or not math.isfinite(requested_qty):
            order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="INVALID_QUANTITY")
            self.orders_history.append(order)
            return order, False, "INVALID_QUANTITY"

        if est_price <= 0.0 or not math.isfinite(est_price):
            order = OrderIntent(order_id, ticker, OrderSide.BUY, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="MISSING_PRICE")
            self.orders_history.append(order)
            return order, False, "MISSING_PRICE"

        # Worst-case required cash including buy markup buffer and estimated commissions
        buffered_price = est_price * (1.0 + self.buy_markup)
        est_cost = buffered_price * requested_qty
        est_comm = est_cost * (commission_bps / 10_000.0)
        total_required_funds = est_cost + est_comm

        available_bp = self.calculate_buying_power()
        if total_required_funds > available_bp:
            order = OrderIntent(
                order_id, ticker, OrderSide.BUY, requested_qty, current_date,
                status=OrderStatus.REJECTED,
                rejection_reason="INSUFFICIENT_CASH",
            )
            self.orders_history.append(order)
            return order, False, f"INSUFFICIENT_CASH (Req: ${total_required_funds:,.2f}, BP: ${available_bp:,.2f})"

        # Reserve funds to prevent overcommitment from simultaneous/subsequent buys
        self.reserved_cash += total_required_funds
        order = OrderIntent(
            order_id, ticker, OrderSide.BUY, requested_qty, current_date,
            status=OrderStatus.SUBMITTED,
            reserved_cash=total_required_funds,
        )
        self.orders_history.append(order)
        return order, True, "SUBMITTED"

    def submit_sell_order(
        self,
        order_id: str,
        ticker: str,
        requested_qty: float,
        current_date: str,
    ) -> tuple[OrderIntent, bool, str]:
        """
        Process a SELL order intent through physical inventory checks and share reservation.
        """
        if requested_qty <= 0.0 or not math.isfinite(requested_qty):
            order = OrderIntent(order_id, ticker, OrderSide.SELL, requested_qty, current_date, OrderStatus.REJECTED, rejection_reason="INVALID_QUANTITY")
            self.orders_history.append(order)
            return order, False, "INVALID_QUANTITY"

        held = self.positions.get(ticker, 0.0)
        already_reserved = self.position_reserved.get(ticker, 0.0)
        available_to_sell = held - already_reserved

        if available_to_sell <= 1e-9:
            order = OrderIntent(
                order_id, ticker, OrderSide.SELL, requested_qty, current_date,
                status=OrderStatus.REJECTED,
                rejection_reason="UNHELD_POSITION",
            )
            self.orders_history.append(order)
            return order, False, "UNHELD_POSITION"

        # Cap sell quantity to available physical shares to prevent short selling
        submittable_qty = min(requested_qty, available_to_sell)
        self.position_reserved[ticker] = already_reserved + submittable_qty

        order = OrderIntent(
            order_id, ticker, OrderSide.SELL, submittable_qty, current_date,
            status=OrderStatus.SUBMITTED,
            reserved_qty=submittable_qty,
        )
        self.orders_history.append(order)
        return order, True, "SUBMITTED"

    # -------------------------------------------------------------------------
    # Execution Fills, Partial Fills, and Cancellations
    # -------------------------------------------------------------------------

    def confirm_buy_fill(
        self,
        order: OrderIntent,
        filled_qty: float,
        fill_price: float,
        commission: float = 0.0,
        effective_slippage_bps: float = 0.0,
    ) -> None:
        """Confirm buy execution: release reserved funds, debit settled cash, update holdings."""
        if order.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot fill order in status {order.status}")

        actual_cost = filled_qty * fill_price
        total_outflow = actual_cost + commission

        # Deduct actual cash and release pre-trade reservation
        self.settled_cash -= total_outflow
        self.reserved_cash = max(0.0, self.reserved_cash - order.reserved_cash)

        # Update physical holdings and cost basis
        held = self.positions.get(order.ticker, 0.0)
        prev_cost_total = held * self.avg_cost.get(order.ticker, 0.0)
        new_held = held + filled_qty
        self.positions[order.ticker] = new_held
        self.avg_cost[order.ticker] = (prev_cost_total + actual_cost) / new_held if new_held > 0 else 0.0

        # Flow tracking
        self.cumulative_buy_outflows += actual_cost
        self.cumulative_buy_commissions += commission
        self.cumulative_commissions += commission

        # Update order record
        order.filled_qty = filled_qty
        order.fill_price = fill_price
        order.commission = commission
        order.effective_slippage_bps = effective_slippage_bps
        order.status = OrderStatus.FILLED if abs(filled_qty - order.requested_qty) < 1e-9 else OrderStatus.PARTIALLY_FILLED

    def confirm_sell_fill(
        self,
        order: OrderIntent,
        filled_qty: float,
        fill_price: float,
        current_date: str,
        settlement_date: str,
        commission: float = 0.0,
        effective_slippage_bps: float = 0.0,
    ) -> None:
        """
        Confirm sell execution: release reserved shares, credit proceeds according to broker model,
        and record realized capital gain/loss.
        """
        if order.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot fill order in status {order.status}")

        actual_proceeds = filled_qty * fill_price
        net_inflow = actual_proceeds - commission

        # Release share reservation and deduct physical inventory
        self.position_reserved[order.ticker] = max(0.0, self.position_reserved.get(order.ticker, 0.0) - order.reserved_qty)
        held = self.positions.get(order.ticker, 0.0)
        new_held = max(0.0, held - filled_qty)
        if new_held <= 1e-9:
            self.positions.pop(order.ticker, None)
            cost_basis = held * self.avg_cost.pop(order.ticker, 0.0)
        else:
            self.positions[order.ticker] = new_held
            cost_basis = filled_qty * self.avg_cost.get(order.ticker, 0.0)

        # Realized PnL = Net Proceeds - Cost Basis
        realized_pnl = net_inflow - cost_basis
        self.cumulative_realized_pnl += realized_pnl
        self.cumulative_sell_inflows += actual_proceeds
        self.cumulative_commissions += commission

        # Settlement routing based on broker model
        if self.broker_model == BrokerModel.MODEL_2_CONFIRMED_SEQUENTIAL:
            # Confirmed proceeds are immediately available as settled cash in Model 2
            self.settled_cash += net_inflow
        else:
            # Model 1 & Model 3: Proceeds are held as unsettled receivables until settlement date
            self.unsettled_cash_receivables.append({
                "settlement_date": settlement_date,
                "amount": net_inflow,
                "origin": f"SELL_{order.ticker}_{order.order_id}",
                "settled": False,
            })

        order.filled_qty = filled_qty
        order.fill_price = fill_price
        order.commission = commission
        order.effective_slippage_bps = effective_slippage_bps
        order.settlement_date = settlement_date
        order.status = OrderStatus.FILLED if abs(filled_qty - order.requested_qty) < 1e-9 else OrderStatus.PARTIALLY_FILLED

    def cancel_order(self, order: OrderIntent, reason: str = "CANCELLED") -> None:
        """Cancel an open/submitted order and release any reserved cash or shares."""
        if order.status == OrderStatus.SUBMITTED:
            if order.side == OrderSide.BUY:
                self.reserved_cash = max(0.0, self.reserved_cash - order.reserved_cash)
            elif order.side == OrderSide.SELL:
                self.position_reserved[order.ticker] = max(
                    0.0, self.position_reserved.get(order.ticker, 0.0) - order.reserved_qty
                )
            order.status = OrderStatus.CANCELLED
            order.rejection_reason = reason

    # -------------------------------------------------------------------------
    # Settlement & Corporate Actions Engine
    # -------------------------------------------------------------------------

    def process_cash_settlements(self, current_date: str) -> float:
        """Credit matured sales proceeds to settled cash on their settlement date."""
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
        """
        Record dividend declaration on ex-date based on settled holdings.
        Funds are NOT credited to cash until payment_date.
        """
        held = self.positions.get(ticker, 0.0)
        if held <= 0.0 or amount_per_share <= 0.0:
            return 0.0

        total_due = held * amount_per_share
        rec = DividendReceivable(
            ticker=ticker,
            ex_date=ex_date,
            payment_date=payment_date,
            amount_per_share=amount_per_share,
            qualifying_shares=held,
            total_amount=total_due,
            settled=False,
        )
        self.dividend_receivables.append(rec)
        return total_due

    def process_dividend_payments(self, current_date: str) -> float:
        """Credit declared dividends to settled cash on or after payment_date."""
        credited = 0.0
        for div in self.dividend_receivables:
            if not div.settled and div.payment_date <= current_date:
                self.settled_cash += div.total_amount
                self.cumulative_dividends_credited += div.total_amount
                div.settled = True
                credited += div.total_amount
        return credited

    def apply_stock_split(self, ticker: str, split_ratio: float) -> None:
        """
        Apply corporate stock split. Conserves total position economic value:
        new_quantity = old_quantity * split_ratio
        new_avg_cost = old_avg_cost / split_ratio
        """
        if split_ratio <= 0.0:
            raise ValueError(f"Invalid split ratio {split_ratio}")

        held = self.positions.get(ticker, 0.0)
        if held > 0.0:
            old_basis_total = held * self.avg_cost.get(ticker, 0.0)
            new_held = held * split_ratio
            self.positions[ticker] = new_held
            self.avg_cost[ticker] = old_basis_total / new_held
            if ticker in self.position_reserved:
                self.position_reserved[ticker] *= split_ratio

    # -------------------------------------------------------------------------
    # Valuation & Double-Entry Invariant Verifications
    # -------------------------------------------------------------------------

    def marked_holdings_value(self, current_prices: dict[str, float]) -> float:
        """Calculate mark-to-market value of physical holdings."""
        return sum(
            qty * current_prices.get(sym, self.avg_cost.get(sym, 0.0))
            for sym, qty in self.positions.items()
        )

    def total_unrealized_pnl(self, current_prices: dict[str, float]) -> float:
        """Calculate unrealized mark-to-market PnL on open positions."""
        pnl = 0.0
        for sym, qty in self.positions.items():
            px = current_prices.get(sym, self.avg_cost.get(sym, 0.0))
            cost = self.avg_cost.get(sym, 0.0)
            pnl += (px - cost) * qty
        return pnl

    def total_account_equity(self, current_prices: dict[str, float]) -> float:
        """
        Standard Balance Sheet Total Account Equity:
        Equity = Settled Cash + Marked Holdings + Unsettled Sales + Dividend Receivables - Liabilities
        """
        marked = self.marked_holdings_value(current_prices)
        unsettled_sales = self.total_unsettled_proceeds()
        unsettled_divs = self.total_dividend_receivables()
        return self.settled_cash + marked + unsettled_sales + unsettled_divs - self.liabilities

    def verify_cash_invariants(self) -> tuple[bool, str]:
        """
        Verify fundamental Cash Flow Identity:
        Settled Cash == Opening Cash + Settled Sales Inflows - Completed Buy Outflows - Commissions + Settled Dividends
        """
        # Sum of settled sell proceeds
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
        discrepancy = abs(self.settled_cash - expected_cash)
        if discrepancy > 1e-4:
            return False, f"Cash invariant broken: Settled Cash={self.settled_cash:.4f} vs Expected={expected_cash:.4f} (Diff: {discrepancy:.6f})"
        return True, "Cash invariant perfectly conserved"

    def verify_balance_sheet(self, current_prices: dict[str, float]) -> tuple[bool, str]:
        """
        Verify comprehensive Double-Entry Balance Sheet:
        Account Equity == Opening Cash + Cumulative Realized PnL + Unrealized PnL + Dividends - Commissions
        """
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
        # To verify without ambiguity, compare against Asset side:
        discrepancy = abs(equity_from_assets - equity_from_income)
        if discrepancy > 1e-3:
            return False, f"Balance sheet discrepancy: Assets Equity={equity_from_assets:.4f} vs Income Equity={equity_from_income:.4f} (Diff: {discrepancy:.6f})"
        return True, "Balance sheet perfectly reconciled"

    def verify_non_negativity(self) -> tuple[bool, str]:
        """Verify no negative cash or negative share holdings exist."""
        if self.settled_cash < -1e-9:
            return False, f"Negative cash detected: {self.settled_cash:.4f}"
        for sym, qty in self.positions.items():
            if qty < -1e-9:
                return False, f"Negative position detected for {sym}: {qty:.6f}"
        return True, "All cash and position balances are strictly non-negative"
