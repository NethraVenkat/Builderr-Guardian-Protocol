"""
Guardian Alpha V30 Stage 2H-B - Independent Decimal Accounting Oracle
Strict Double-Entry Balance Sheet vs Economic Flow Verification
Equation: Equity = Assets - Liabilities
Zero-tolerance verification with Python Decimal (8-place shares, 4-place currency).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
import copy


def to_dec(val) -> Decimal:
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


class DecimalPosition:
    def __init__(self, symbol: str, shares: Decimal = Decimal('0'), cost_basis: Decimal = Decimal('0')):
        self.symbol = symbol
        self.shares = to_dec(shares)
        self.cost_basis = to_dec(cost_basis)  # average cost per share

    def market_value(self, price: Decimal) -> Decimal:
        return (self.shares * to_dec(price)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    def unrealized_pnl(self, price: Decimal) -> Decimal:
        if self.shares == Decimal('0'):
            return Decimal('0.0000')
        return ((to_dec(price) - self.cost_basis) * self.shares).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)


class DecimalAccountingOracle:
    """
    Independent double-entry accounting oracle.
    Strictly verifies:
      Equity (Balance Sheet) = Assets - Liabilities
      Equity (Economic Flow) = Initial Equity + Net External Flows + Realized PnL + Unrealized PnL - Fees + Dividends
    """

    def __init__(self, initial_cash: Decimal = Decimal('100000.0000')):
        self.initial_equity = to_dec(initial_cash)
        self.settled_cash = to_dec(initial_cash)
        self.unsettled_cash_receivables = Decimal('0.0000')
        self.dividend_receivables = Decimal('0.0000')
        
        # Liabilities
        self.trade_payables = Decimal('0.0000')
        self.pending_fee_obligations = Decimal('0.0000')
        
        # Reservations (encumbered settled cash)
        self.buy_reservations = Decimal('0.0000')
        
        # Positions
        self.positions: Dict[str, DecimalPosition] = {}
        
        # Cumulative flow accumulators
        self.external_cash_flows_cum = Decimal('0.0000')
        self.realized_pnl_cum = Decimal('0.0000')
        self.fees_cum = Decimal('0.0000')
        self.dividends_cum = Decimal('0.0000')
        
        # Audit log of transactions
        self.transaction_log: List[dict] = []

    def spendable_cash(self) -> Decimal:
        """Spendable cash is settled cash less active buy reservations."""
        return self.settled_cash - self.buy_reservations

    def reserve_buy(self, reservation_amount: Decimal) -> bool:
        amount = to_dec(reservation_amount)
        if amount > self.spendable_cash():
            return False
        self.buy_reservations += amount
        return True

    def release_reservation(self, reservation_amount: Decimal) -> None:
        amount = to_dec(reservation_amount)
        self.buy_reservations = max(Decimal('0.0000'), self.buy_reservations - amount)

    def execute_buy(
        self,
        symbol: str,
        shares: Decimal,
        price: Decimal,
        slippage_bps: Decimal = Decimal('5.0'),
        fee: Decimal = Decimal('0.0000'),
        reserved_amount: Decimal = Decimal('0.0000')
    ) -> bool:
        shares = to_dec(shares)
        price = to_dec(price)
        slippage_bps = to_dec(slippage_bps)
        fee = to_dec(fee)
        reserved_amount = to_dec(reserved_amount)

        if shares <= Decimal('0') or price <= Decimal('0'):
            self.release_reservation(reserved_amount)
            return False

        gross_cost = (shares * price).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        slippage_cost = (gross_cost * (slippage_bps / Decimal('10000.0'))).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        effective_price = price * (Decimal('1.0') + slippage_bps / Decimal('10000.0'))
        total_cost = gross_cost + slippage_cost + fee

        # Check total cash affordability
        # If cash was reserved, check against settled_cash; otherwise check spendable_cash
        available = self.settled_cash if reserved_amount >= total_cost else (self.spendable_cash() + reserved_amount)
        if total_cost > available:
            self.release_reservation(reserved_amount)
            return False

        # Release reservation
        self.release_reservation(reserved_amount)

        # Deduct cash
        self.settled_cash -= total_cost
        self.fees_cum += fee

        # Update position
        if symbol not in self.positions:
            self.positions[symbol] = DecimalPosition(symbol)
        
        pos = self.positions[symbol]
        total_shares = pos.shares + shares
        total_old_cost = (pos.shares * pos.cost_basis).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        new_effective_cost = gross_cost + slippage_cost
        new_cost_basis = ((total_old_cost + new_effective_cost) / total_shares).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        
        pos.shares = total_shares
        pos.cost_basis = new_cost_basis

        self.transaction_log.append({
            'action': 'BUY',
            'symbol': symbol,
            'shares': float(shares),
            'price': float(price),
            'slippage_cost': float(slippage_cost),
            'fee': float(fee),
            'total_cost': float(total_cost)
        })
        return True

    def execute_sell(
        self,
        symbol: str,
        shares: Decimal,
        price: Decimal,
        slippage_bps: Decimal = Decimal('5.0'),
        fee: Decimal = Decimal('0.0000'),
        settlement_days: int = 0
    ) -> bool:
        shares = to_dec(shares)
        price = to_dec(price)
        slippage_bps = to_dec(slippage_bps)
        fee = to_dec(fee)

        if symbol not in self.positions or self.positions[symbol].shares < shares:
            # Short selling strictly prohibited
            return False

        if shares <= Decimal('0') or price <= Decimal('0'):
            return False

        pos = self.positions[symbol]
        gross_proceeds = (shares * price).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        slippage_reduction = (gross_proceeds * (slippage_bps / Decimal('10000.0'))).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        net_proceeds = gross_proceeds - slippage_reduction - fee

        # Calculate realized PnL against cost basis
        cost_of_sold_shares = (shares * pos.cost_basis).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        realized_gain = (gross_proceeds - slippage_reduction) - cost_of_sold_shares

        # Update position
        pos.shares -= shares
        if pos.shares == Decimal('0'):
            pos.cost_basis = Decimal('0.0000')

        # Accounting for proceeds
        if settlement_days == 0:
            self.settled_cash += net_proceeds
        else:
            self.unsettled_cash_receivables += net_proceeds

        self.fees_cum += fee
        self.realized_pnl_cum += realized_gain

        self.transaction_log.append({
            'action': 'SELL',
            'symbol': symbol,
            'shares': float(shares),
            'price': float(price),
            'slippage_cost': float(slippage_reduction),
            'fee': float(fee),
            'net_proceeds': float(net_proceeds),
            'realized_gain': float(realized_gain),
            'settlement_days': settlement_days
        })
        return True

    def settle_receivable(self, amount: Decimal) -> None:
        amt = to_dec(amount)
        if amt > self.unsettled_cash_receivables:
            amt = self.unsettled_cash_receivables
        self.unsettled_cash_receivables -= amt
        self.settled_cash += amt

    def add_payable(self, amount: Decimal) -> None:
        """Adversarial liability injection (e.g. pending financing / exchange fee audit)."""
        amt = to_dec(amount)
        self.trade_payables += amt
        self.fees_cum += amt

    def pay_payable(self, amount: Decimal) -> bool:
        amt = to_dec(amount)
        if amt > self.settled_cash or amt > self.trade_payables:
            return False
        self.settled_cash -= amt
        self.trade_payables -= amt
        return True

    def process_split(self, symbol: str, split_ratio: Decimal) -> bool:
        ratio = to_dec(split_ratio)
        if symbol not in self.positions or self.positions[symbol].shares <= Decimal('0'):
            return False
        pos = self.positions[symbol]
        pos.shares = (pos.shares * ratio).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        pos.cost_basis = (pos.cost_basis / ratio).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        return True

    def process_dividend(self, symbol: str, per_share: Decimal, payable_delay_days: int = 0) -> bool:
        div = to_dec(per_share)
        if symbol not in self.positions or self.positions[symbol].shares <= Decimal('0'):
            return False
        total_div = (self.positions[symbol].shares * div).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        self.dividends_cum += total_div
        if payable_delay_days == 0:
            self.settled_cash += total_div
        else:
            self.dividend_receivables += total_div
        return True

    def settle_dividend_receivable(self, amount: Decimal) -> None:
        amt = to_dec(amount)
        if amt > self.dividend_receivables:
            amt = self.dividend_receivables
        self.dividend_receivables -= amt
        self.settled_cash += amt

    def total_assets(self, current_prices: Dict[str, Decimal]) -> Decimal:
        holdings_mv = Decimal('0.0000')
        for sym, pos in self.positions.items():
            price = to_dec(current_prices.get(sym, pos.cost_basis))
            holdings_mv += pos.market_value(price)
        return self.settled_cash + self.unsettled_cash_receivables + self.dividend_receivables + holdings_mv

    def total_liabilities(self) -> Decimal:
        return self.trade_payables + self.pending_fee_obligations

    def balance_sheet_equity(self, current_prices: Dict[str, Decimal]) -> Decimal:
        return self.total_assets(current_prices) - self.total_liabilities()

    def economic_flow_equity(self, current_prices: Dict[str, Decimal]) -> Decimal:
        unrealized = Decimal('0.0000')
        for sym, pos in self.positions.items():
            price = to_dec(current_prices.get(sym, pos.cost_basis))
            unrealized += pos.unrealized_pnl(price)
        
        return (
            self.initial_equity
            + self.external_cash_flows_cum
            + self.realized_pnl_cum
            + unrealized
            - self.fees_cum
            + self.dividends_cum
        )

    def verify_accounting_identity(self, current_prices: Dict[str, Decimal]) -> Tuple[bool, Decimal, dict]:
        bs_equity = self.balance_sheet_equity(current_prices)
        flow_equity = self.economic_flow_equity(current_prices)
        residual = (bs_equity - flow_equity).quantize(Decimal('0.0001'))
        
        is_exact = abs(residual) <= Decimal('0.0001')
        diagnostic = {
            'settled_cash': float(self.settled_cash),
            'unsettled_receivables': float(self.unsettled_cash_receivables),
            'dividend_receivables': float(self.dividend_receivables),
            'total_assets': float(self.total_assets(current_prices)),
            'total_liabilities': float(self.total_liabilities()),
            'balance_sheet_equity': float(bs_equity),
            'economic_flow_equity': float(flow_equity),
            'residual': float(residual),
            'is_exact_match': is_exact
        }
        return is_exact, residual, diagnostic
