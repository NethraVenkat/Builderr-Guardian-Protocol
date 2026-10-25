"""
Guardian Alpha — V30 Stage 2A-F Independent Accounting Oracle.

AN INDEPENDENT REFERENCE ACCOUNTING ORACLE USING EXACT DECIMAL ARITHMETIC.
CRITICAL INTEGRITY RULE:
This oracle DOES NOT import, inherit, or reuse any code from
research/engine/v30_broker_accounting_r.py or cash_affordability_model.py.

All arithmetic is evaluated using Python's `decimal.Decimal` with explicit
quantization to eliminate IEEE 754 floating-point rounding artifacts.

Tracks:
1. Settled cash vs Unsettled cash receivables vs Trade payables.
2. Reserved buying power vs Available free cash.
3. Actual positions, cost bases, and completed fills.
4. Transaction fees and commissions.
5. Dividends: declared, accrued (receivable on ex-date), and paid (cash on pay-date).
6. Corporate actions: stock split basis and quantity conservation.
7. Realized P&L vs Unrealized mark-to-market P&L.
8. Total Balance-Sheet Equity vs Independently Accumulated Economic Flows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_DOWN
from enum import Enum
import math
from typing import Any


def to_dec(val: float | int | str | Decimal) -> Decimal:
    """Convert input to exact Decimal."""
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


class OracleOrderStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OracleOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class OraclePosition:
    ticker: str
    quantity: Decimal = Decimal("0")
    total_cost_basis: Decimal = Decimal("0")

    @property
    def avg_cost_per_share(self) -> Decimal:
        if self.quantity <= Decimal("0"):
            return Decimal("0")
        return (self.total_cost_basis / self.quantity).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN)


@dataclass
class OracleDividend:
    ticker: str
    ex_date: str
    payment_date: str
    amount_per_share: Decimal
    qualifying_shares: Decimal
    total_amount: Decimal
    settled: bool = False


@dataclass
class OracleSettlementReceivable:
    receivable_id: str
    settlement_date: str
    amount: Decimal
    origin: str
    settled: bool = False


class IndependentAccountingOracle:
    """
    Independent double-entry accounting oracle for micro-transaction verification.
    """

    def __init__(
        self,
        opening_cash: Decimal | str | float = "100000.00",
        buy_slippage_buffer_pct: Decimal | str | float = "0.05",
        cash_reserve_floor_pct: Decimal | str | float = "0.02",
    ) -> None:
        self.opening_cash: Decimal = to_dec(opening_cash)
        self.settled_cash: Decimal = to_dec(opening_cash)
        self.reserved_cash: Decimal = Decimal("0")
        self.trade_payables: Decimal = Decimal("0")

        self.buy_buffer_pct: Decimal = to_dec(buy_slippage_buffer_pct)
        self.reserve_floor_pct: Decimal = to_dec(cash_reserve_floor_pct)

        # Holdings: ticker -> OraclePosition
        self.positions: dict[str, OraclePosition] = {}
        self.shares_reserved: dict[str, Decimal] = {}

        # Receivables
        self.unsettled_sales: list[OracleSettlementReceivable] = []
        self.dividends: list[OracleDividend] = []

        # Flow tracking
        self.cumulative_cash_credits: Decimal = Decimal("0")
        self.cumulative_cash_debits: Decimal = Decimal("0")
        self.cumulative_buy_outflows: Decimal = Decimal("0")
        self.cumulative_sell_inflows: Decimal = Decimal("0")
        self.cumulative_commissions: Decimal = Decimal("0")
        self.cumulative_buy_commissions: Decimal = Decimal("0")
        self.cumulative_dividends_credited: Decimal = Decimal("0")
        self.cumulative_realized_pnl: Decimal = Decimal("0")

    # -------------------------------------------------------------------------
    # Balance Sheet and Flow Queries
    # -------------------------------------------------------------------------

    def total_unsettled_sales(self) -> Decimal:
        return sum((r.amount for r in self.unsettled_sales if not r.settled), Decimal("0"))

    def total_dividend_receivables(self) -> Decimal:
        return sum((d.total_amount for d in self.dividends if not d.settled), Decimal("0"))

    def marked_holdings_value(self, market_prices: dict[str, Decimal | str | float]) -> Decimal:
        total = Decimal("0")
        for sym, pos in self.positions.items():
            if pos.quantity > Decimal("0"):
                px = to_dec(market_prices.get(sym, pos.avg_cost_per_share))
                total += pos.quantity * px
        return total

    def total_unrealized_pnl(self, market_prices: dict[str, Decimal | str | float]) -> Decimal:
        total = Decimal("0")
        for sym, pos in self.positions.items():
            if pos.quantity > Decimal("0"):
                px = to_dec(market_prices.get(sym, pos.avg_cost_per_share))
                total += (px - pos.avg_cost_per_share) * pos.quantity
        return total

    def balance_sheet_equity(self, market_prices: dict[str, Decimal | str | float]) -> Decimal:
        """
        Assets Equity: Settled Cash + Marked Holdings + Unsettled Sales + Dividend Receivables - Trade Payables.
        """
        marked = self.marked_holdings_value(market_prices)
        unsettled_sales = self.total_unsettled_sales()
        unsettled_divs = self.total_dividend_receivables()
        return self.settled_cash + marked + unsettled_sales + unsettled_divs - self.trade_payables

    def economic_flow_equity(self, market_prices: dict[str, Decimal | str | float]) -> Decimal:
        """
        Income Equity: Opening Cash + Realized PnL + Unrealized PnL + Total Dividends - Buy Commissions.
        """
        unrealized = self.total_unrealized_pnl(market_prices)
        total_dividends = self.cumulative_dividends_credited + self.total_dividend_receivables()
        return (
            self.opening_cash
            + self.cumulative_realized_pnl
            + unrealized
            + total_dividends
            - self.cumulative_buy_commissions
        )

    def available_buying_power(self, total_equity: Decimal | str | float) -> Decimal:
        tot_eq = to_dec(total_equity)
        reserve_floor = tot_eq * self.reserve_floor_pct
        free_cash = self.settled_cash - self.reserved_cash
        return max(Decimal("0"), free_cash - reserve_floor)

    # -------------------------------------------------------------------------
    # Order Lifecycle State Machine
    # -------------------------------------------------------------------------

    def submit_buy(
        self,
        order_id: str,
        ticker: str,
        quantity: Decimal | str | float,
        price: Decimal | str | float,
        total_equity: Decimal | str | float,
        commission_bps: Decimal | str | float = "0.0",
    ) -> tuple[bool, str, Decimal]:
        qty = to_dec(quantity)
        px = to_dec(price)
        comm_bps = to_dec(commission_bps)

        if qty <= Decimal("0") or px <= Decimal("0"):
            return False, "INVALID_INPUT", Decimal("0")

        # Buffered price absorbs adverse execution slippage
        buffered_px = px * (Decimal("1") + self.buy_buffer_pct)
        est_cost = qty * buffered_px
        est_comm = est_cost * (comm_bps / Decimal("10000"))
        required_funds = est_cost + est_comm

        bp = self.available_buying_power(total_equity)
        if required_funds > bp:
            return False, f"INSUFFICIENT_BUYING_POWER (Req: {required_funds}, Avail: {bp})", Decimal("0")

        # Lock funds
        self.reserved_cash += required_funds
        return True, "SUBMITTED", required_funds

    def submit_sell(
        self,
        order_id: str,
        ticker: str,
        quantity: Decimal | str | float,
    ) -> tuple[bool, str, Decimal]:
        qty = to_dec(quantity)
        if qty <= Decimal("0"):
            return False, "INVALID_QUANTITY", Decimal("0")

        held = self.positions.get(ticker, OraclePosition(ticker)).quantity
        already_reserved = self.shares_reserved.get(ticker, Decimal("0"))
        available_to_sell = held - already_reserved

        if available_to_sell <= Decimal("0"):
            return False, "UNHELD_POSITION", Decimal("0")

        submittable = min(qty, available_to_sell)
        self.shares_reserved[ticker] = already_reserved + submittable
        return True, "SUBMITTED", submittable

    def execute_buy_fill(
        self,
        ticker: str,
        requested_qty: Decimal | str | float,
        filled_qty: Decimal | str | float,
        fill_price: Decimal | str | float,
        total_reserved_for_order: Decimal | str | float,
        commission: Decimal | str | float = "0.0",
    ) -> None:
        req_q = to_dec(requested_qty)
        fill_q = to_dec(filled_qty)
        fill_px = to_dec(fill_price)
        comm = to_dec(commission)
        tot_reserved = to_dec(total_reserved_for_order)

        cost = fill_q * fill_px
        outflow = cost + comm

        # Proportional reserved funds release:
        # If order fills in full: releases entire reservation.
        # If partial fill: releases the portion consumed by fill_q.
        if req_q > Decimal("0"):
            consumed_reservation = tot_reserved * (fill_q / req_q)
        else:
            consumed_reservation = tot_reserved
        self.reserved_cash = max(Decimal("0"), self.reserved_cash - consumed_reservation)

        # Debit settled cash
        self.settled_cash -= outflow
        self.cumulative_cash_debits += outflow
        self.cumulative_buy_outflows += cost
        self.cumulative_commissions += comm
        self.cumulative_buy_commissions += comm

        # Update physical holdings
        pos = self.positions.setdefault(ticker, OraclePosition(ticker))
        pos.quantity += fill_q
        pos.total_cost_basis += cost

    def cancel_unexecuted_buy_reservation(
        self,
        unexecuted_reserved_funds: Decimal | str | float,
    ) -> None:
        unexec = to_dec(unexecuted_reserved_funds)
        self.reserved_cash = max(Decimal("0"), self.reserved_cash - unexec)

    def execute_sell_fill(
        self,
        ticker: str,
        filled_qty: Decimal | str | float,
        fill_price: Decimal | str | float,
        settlement_date: str,
        commission: Decimal | str | float = "0.0",
        same_day_settlement: bool = False,
    ) -> Decimal:
        fill_q = to_dec(filled_qty)
        fill_px = to_dec(fill_price)
        comm = to_dec(commission)

        gross_proceeds = fill_q * fill_px
        net_proceeds = gross_proceeds - comm

        # Release shares reserved and deduct holdings
        self.shares_reserved[ticker] = max(Decimal("0"), self.shares_reserved.get(ticker, Decimal("0")) - fill_q)
        pos = self.positions.get(ticker)
        if not pos or pos.quantity < fill_q:
            raise ValueError(f"Oracle cannot sell {fill_q} shares of {ticker}; holds only {pos.quantity if pos else 0}")

        # Realized PnL: Net Proceeds - Pro-rata Cost Basis
        cost_of_sold = pos.avg_cost_per_share * fill_q
        pos.quantity -= fill_q
        pos.total_cost_basis = max(Decimal("0"), pos.total_cost_basis - cost_of_sold)
        if pos.quantity == Decimal("0"):
            pos.total_cost_basis = Decimal("0")

        realized_pnl = net_proceeds - cost_of_sold
        self.cumulative_realized_pnl += realized_pnl
        self.cumulative_sell_inflows += gross_proceeds
        self.cumulative_commissions += comm

        if same_day_settlement:
            self.settled_cash += net_proceeds
            self.cumulative_cash_credits += net_proceeds
        else:
            self.unsettled_sales.append(
                OracleSettlementReceivable(
                    receivable_id=f"SELL_{ticker}",
                    settlement_date=settlement_date,
                    amount=net_proceeds,
                    origin=f"SELL_{ticker}",
                    settled=False,
                )
            )

        return realized_pnl

    def process_sales_settlement(self, current_date: str) -> Decimal:
        matured = Decimal("0")
        for rec in self.unsettled_sales:
            if not rec.settled and rec.settlement_date <= current_date:
                self.settled_cash += rec.amount
                self.cumulative_cash_credits += rec.amount
                rec.settled = True
                matured += rec.amount
        return matured

    def declare_dividend(
        self,
        ticker: str,
        ex_date: str,
        payment_date: str,
        amount_per_share: Decimal | str | float,
    ) -> Decimal:
        amt = to_dec(amount_per_share)
        pos = self.positions.get(ticker)
        if not pos or pos.quantity <= Decimal("0"):
            return Decimal("0")

        total_due = pos.quantity * amt
        self.dividends.append(
            OracleDividend(
                ticker=ticker,
                ex_date=ex_date,
                payment_date=payment_date,
                amount_per_share=amt,
                qualifying_shares=pos.quantity,
                total_amount=total_due,
                settled=False,
            )
        )
        return total_due

    def process_dividend_payment(self, current_date: str) -> Decimal:
        paid = Decimal("0")
        for div in self.dividends:
            if not div.settled and div.payment_date <= current_date:
                self.settled_cash += div.total_amount
                self.cumulative_cash_credits += div.total_amount
                self.cumulative_dividends_credited += div.total_amount
                div.settled = True
                paid += div.total_amount
        return paid

    def execute_stock_split(self, ticker: str, split_ratio: Decimal | str | float) -> None:
        ratio = to_dec(split_ratio)
        if ratio <= Decimal("0"):
            raise ValueError(f"Invalid split ratio {ratio}")

        pos = self.positions.get(ticker)
        if pos and pos.quantity > Decimal("0"):
            # Conservation: total cost basis remains exactly unchanged
            pos.quantity = pos.quantity * ratio
            if ticker in self.shares_reserved:
                self.shares_reserved[ticker] = self.shares_reserved[ticker] * ratio

    # -------------------------------------------------------------------------
    # Invariant Verifications
    # -------------------------------------------------------------------------

    def verify_all_invariants(self, market_prices: dict[str, Decimal | str | float]) -> tuple[bool, str]:
        # 1. Cash flow equation
        expected_cash = self.opening_cash + self.cumulative_cash_credits - self.cumulative_cash_debits
        if self.settled_cash != expected_cash:
            return False, f"Cash Flow Invariant Broken: Actual={self.settled_cash} vs Expected={expected_cash}"

        # 2. Balance sheet equality
        bs_equity = self.balance_sheet_equity(market_prices)
        flow_equity = self.economic_flow_equity(market_prices)
        if bs_equity != flow_equity:
            return False, f"Balance Sheet Discrepancy: BalanceSheet={bs_equity} vs FlowEquity={flow_equity} (Diff: {bs_equity - flow_equity})"

        # 3. Non-negativity
        if self.settled_cash < Decimal("0"):
            return False, f"Negative cash detected: {self.settled_cash}"
        for sym, pos in self.positions.items():
            if pos.quantity < Decimal("0"):
                return False, f"Negative position for {sym}: {pos.quantity}"

        return True, "ALL INVARIANTS CONSERVED EXACTLY"
