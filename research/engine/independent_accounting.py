"""
Independent Financial Accounting Verification Engine.
Provides a clean-room, double-entry financial verifier that independently
reconstructs cash, positions, corporate actions, trade execution impact,
realized/unrealized PnL, dividend accruals/settlements, and daily NAV from raw
trade logs and market bars without calling PortfolioState accounting methods.
"""
from __future__ import annotations

import copy
import math
from typing import Any


class AccountingAnomalyDetected(Exception):
    """Raised when an accounting invariant is violated or anomaly detected."""
    pass


class IndependentLedger:
    """
    Independent double-entry accounting ledger that reconciles trading
    executions, corporate actions, and daily balance sheet invariants.
    """

    def __init__(
        self,
        initial_cash: float = 100_000.0,
        slip_equity: float = 0.0005,
        slip_leveraged: float = 0.0010,
        commission_bps: float = 0.0,
    ):
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions: dict[str, float] = {}             # ticker -> share quantity
        self.cost_basis_per_share: dict[str, float] = {}  # ticker -> average purchase cost per share
        self.total_cost_basis: dict[str, float] = {}      # ticker -> total cost basis
        self.dividend_receivables: float = 0.0            # outstanding unpaid dividend entitlements
        self.pending_dividends: list[dict[str, Any]] = [] # [{ticker, amount, payment_date}]
        self.realized_pnl: float = 0.0                    # accumulated realized PnL
        self.total_dividends_credited: float = 0.0        # cash dividends received
        self.total_commissions: float = 0.0               # commissions paid
        self.total_slippage: float = 0.0                  # total slippage paid
        self.slip_equity = slip_equity
        self.slip_leveraged = slip_leveraged
        self.commission_bps = commission_bps

        # Daily snapshots and exception records
        self.daily_snapshots: list[dict[str, Any]] = []
        self.exception_ledger: list[str] = []

    def apply_split(self, date: str, ticker: str, split_ratio: float) -> None:
        """
        Apply stock split on open positions prior to market open.
        Shares are multiplied by split_ratio, cost basis per share divided by split_ratio.
        Total cost basis remains invariant.
        """
        if ticker not in self.positions or self.positions[ticker] <= 0:
            return

        old_qty = self.positions[ticker]
        old_cost_per_share = self.cost_basis_per_share.get(ticker, 0.0)

        if split_ratio <= 0:
            msg = f"[{date}] Invalid split ratio {split_ratio} for {ticker}"
            self.exception_ledger.append(msg)
            raise AccountingAnomalyDetected(msg)

        new_qty = old_qty * split_ratio
        new_cost_per_share = old_cost_per_share / split_ratio

        self.positions[ticker] = new_qty
        self.cost_basis_per_share[ticker] = new_cost_per_share
        self.total_cost_basis[ticker] = new_qty * new_cost_per_share

    def accrue_dividend(self, date: str, ticker: str, amount_per_share: float, payment_date: str) -> None:
        """Accrue dividend entitlement on ex-date based on currently held shares."""
        if ticker not in self.positions or self.positions[ticker] <= 0:
            return

        shares = self.positions[ticker]
        entitlement = shares * amount_per_share
        self.dividend_receivables += entitlement
        self.pending_dividends.append({
            "ticker": ticker,
            "ex_date": date,
            "amount": entitlement,
            "payment_date": payment_date,
        })

    def settle_dividends(self, date: str) -> float:
        """Credit cash on dividend payment date and reduce receivables."""
        settled_cash = 0.0
        remaining_pending = []
        for div in self.pending_dividends:
            if div["payment_date"] <= date:
                amt = div["amount"]
                if (self.dividend_receivables - amt) < -1e-5:
                    msg = f"[{date}] Dividend settlement of ${amt:.2f} exceeds outstanding receivables ${self.dividend_receivables:.2f}"
                    self.exception_ledger.append(msg)
                    raise AccountingAnomalyDetected(msg)
                settled_cash += amt
                self.cash += amt
                self.dividend_receivables -= amt
                self.total_dividends_credited += amt
            else:
                remaining_pending.append(div)
        self.pending_dividends = remaining_pending
        return settled_cash

    def process_fill(
        self,
        date: str,
        ticker: str,
        side: str,
        quantity: float,
        fill_price: float,
        reference_price: float,
        commission: float = 0.0,
    ) -> dict[str, Any]:
        """
        Execute trade fill with exact cash, position, cost basis, and PnL updates.
        """
        qty = float(quantity)
        fill_px = float(fill_price)
        ref_px = float(reference_price)
        comm = float(commission)

        if qty <= 0:
            msg = f"[{date}] Nonpositive fill quantity {qty} for {ticker}"
            self.exception_ledger.append(msg)
            raise AccountingAnomalyDetected(msg)

        slip = abs(qty) * abs(fill_px - ref_px)
        self.total_slippage += slip
        self.total_commissions += comm

        pnl = 0.0

        if side.lower() == "buy":
            total_cost = (fill_px * qty) + comm
            self.cash -= total_cost

            old_qty = self.positions.get(ticker, 0.0)
            old_cost_per_share = self.cost_basis_per_share.get(ticker, 0.0)
            new_qty = old_qty + qty

            if new_qty > 0:
                new_cost_per_share = ((old_qty * old_cost_per_share) + (fill_px * qty)) / new_qty
            else:
                new_cost_per_share = 0.0

            self.positions[ticker] = new_qty
            self.cost_basis_per_share[ticker] = new_cost_per_share
            self.total_cost_basis[ticker] = new_qty * new_cost_per_share

        elif side.lower() == "sell":
            held_qty = self.positions.get(ticker, 0.0)
            if qty > (held_qty + 1e-7):
                msg = f"[{date}] Oversell: selling {qty} shares of {ticker} but only held {held_qty}"
                self.exception_ledger.append(msg)
                raise AccountingAnomalyDetected(msg)

            proceeds = (fill_px * qty) - comm
            self.cash += proceeds

            cost_per_share = self.cost_basis_per_share.get(ticker, 0.0)
            pnl = (fill_px - cost_per_share) * qty - comm
            self.realized_pnl += pnl

            new_qty = max(held_qty - qty, 0.0)
            if new_qty <= 1e-9:
                self.positions[ticker] = 0.0
                self.cost_basis_per_share[ticker] = 0.0
                self.total_cost_basis[ticker] = 0.0
            else:
                self.positions[ticker] = new_qty
                self.total_cost_basis[ticker] = new_qty * cost_per_share

        else:
            msg = f"[{date}] Unknown trade side {side} for {ticker}"
            self.exception_ledger.append(msg)
            raise AccountingAnomalyDetected(msg)

        return {
            "date": date,
            "ticker": ticker,
            "side": side,
            "quantity": qty,
            "fill_price": fill_px,
            "reference_price": ref_px,
            "slippage": slip,
            "commission": comm,
            "realized_pnl": pnl,
        }

    def compute_valuation(self, raw_closes: dict[str, float]) -> dict[str, float]:
        """Compute mark-to-market position values, unrealized PnL, and NAV."""
        positions_market_val = 0.0
        unrealized_pnl = 0.0

        for ticker, qty in self.positions.items():
            if qty > 0:
                px = raw_closes.get(ticker, self.cost_basis_per_share.get(ticker, 0.0))
                mkt_val = qty * px
                cost = qty * self.cost_basis_per_share.get(ticker, 0.0)
                positions_market_val += mkt_val
                unrealized_pnl += (mkt_val - cost)

        total_assets = self.cash + positions_market_val + self.dividend_receivables
        liabilities = 0.0
        nav = total_assets - liabilities

        # Conservation Invariant:
        # NAV == Initial Cash + Realized PnL + Unrealized PnL + Dividends Credited + Receivables - Commissions
        reconstructed_nav = (
            self.initial_cash
            + self.realized_pnl
            + unrealized_pnl
            + self.total_dividends_credited
            + self.dividend_receivables
            - self.total_commissions
        )
        discrepancy = abs(nav - reconstructed_nav)

        return {
            "cash": self.cash,
            "positions_market_val": positions_market_val,
            "dividend_receivables": self.dividend_receivables,
            "nav": nav,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "reconstructed_nav": reconstructed_nav,
            "discrepancy": discrepancy,
        }

    def record_daily_snapshot(self, date: str, raw_closes: dict[str, float]) -> dict[str, Any]:
        """Record daily snapshot and assert balance sheet conservation."""
        val = self.compute_valuation(raw_closes)
        if val["discrepancy"] > 1e-4:
            msg = f"[{date}] Double-entry conservation failure: NAV={val['nav']:.4f} != Reconstructed={val['reconstructed_nav']:.4f} (diff={val['discrepancy']:.6f})"
            self.exception_ledger.append(msg)
            raise AccountingAnomalyDetected(msg)

        snapshot = {
            "date": date,
            "cash": round(self.cash, 4),
            "positions_market_val": round(val["positions_market_val"], 4),
            "dividend_receivables": round(self.dividend_receivables, 4),
            "nav": round(val["nav"], 4),
            "realized_pnl": round(self.realized_pnl, 4),
            "unrealized_pnl": round(val["unrealized_pnl"], 4),
            "total_slippage": round(self.total_slippage, 4),
            "total_commissions": round(self.total_commissions, 4),
            "discrepancy": round(val["discrepancy"], 10),
            "positions": {t: round(q, 4) for t, q in self.positions.items() if q > 0},
        }
        self.daily_snapshots.append(snapshot)
        return snapshot


def reconstruct_independent_ledger(
    timeline: list[str],
    preloaded_bars: dict[str, list[dict[str, Any]]],
    fill_log: list[Any],
    corp_registry: Any,
    initial_cash: float = 100_000.0,
    commission_bps: float = 0.0,
) -> IndependentLedger:
    """
    Reconstruct the full historical backtest timeline day-by-day from scratch.
    """
    ledger = IndependentLedger(
        initial_cash=initial_cash,
        commission_bps=commission_bps,
    )

    # Group fills by date
    fills_by_date: dict[str, list[Any]] = {}
    for f in fill_log:
        d = f.get("date") if isinstance(f, dict) else getattr(f, "date", None)
        if d:
            fills_by_date.setdefault(d, []).append(f)

    # Pre-index closes by date for O(1) daily lookup
    closes_by_date: dict[str, dict[str, float]] = {}
    for sym, bars in preloaded_bars.items():
        for b in bars:
            ts = b["ts"]
            closes_by_date.setdefault(ts, {})[sym] = b.get("raw_close", b["close"])

    # Extract corporate actions
    div_actions: dict[str, list[tuple[str, float, str]]] = {}
    split_actions: dict[str, list[tuple[str, float]]] = {}

    for sym, bars in preloaded_bars.items():
        for b in bars:
            ts = b["ts"]
            div_val = float(b.get("div_cash", 0.0))
            if div_val > 0.0:
                from research.engine.corporate_actions import compute_business_day_settlement
                pay_dt = compute_business_day_settlement(ts, 10)
                div_actions.setdefault(ts, []).append((sym, div_val, pay_dt))

            split_val = float(b.get("split_factor", 1.0))
            if split_val != 1.0:
                split_actions.setdefault(ts, []).append((sym, split_val))

    for current_date in timeline:
        # 1. Corporate actions prior to market open
        # Apply splits
        for sym, ratio in split_actions.get(current_date, []):
            ledger.apply_split(current_date, sym, ratio)

        # Accrue ex-date dividends
        for sym, div_cash, pay_dt in div_actions.get(current_date, []):
            ledger.accrue_dividend(current_date, sym, div_cash, pay_dt)

        # Settle pending dividends
        ledger.settle_dividends(current_date)

        # 2. Market Open: Execute fills for today
        today_fills = fills_by_date.get(current_date, [])
        for f in today_fills:
            ticker = f["ticker"] if isinstance(f, dict) else getattr(f, "ticker")
            side = f["side"] if isinstance(f, dict) else getattr(f, "side")
            qty = f.get("filled_qty", f.get("quantity")) if isinstance(f, dict) else getattr(f, "filled_qty")
            fill_px = f["fill_price"] if isinstance(f, dict) else getattr(f, "fill_price")
            open_px = f.get("open_price", fill_px) if isinstance(f, dict) else getattr(f, "open_price", fill_px)
            comm = f.get("commission", 0.0) if isinstance(f, dict) else getattr(f, "commission", 0.0)

            ledger.process_fill(
                date=current_date,
                ticker=ticker,
                side=side,
                quantity=qty,
                fill_price=fill_px,
                reference_price=open_px,
                commission=comm,
            )

        # 3. Market Close: Mark to market valuation
        raw_closes = closes_by_date.get(current_date, {})

        # Snapshot and assert conservation
        ledger.record_daily_snapshot(current_date, raw_closes)

    return ledger


# ==============================================================================
# SEVEN ADVERSARIAL NEGATIVE CONTROLS FOR INDEPENDENT VERIFIER
# ==============================================================================

def run_negative_control_altered_fill_price() -> bool:
    """1. Injects altered fill price where cash is debited differently from position cost."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    # Buy 100 shares of AAPL at $150
    ledger.process_fill("2015-01-05", "AAPL", "buy", 100.0, fill_price=150.0, reference_price=150.0)
    # Tamper cash by debiting an extra $500 (as if fill price was $155 instead of $150)
    ledger.cash -= 500.0
    try:
        ledger.record_daily_snapshot("2015-01-05", {"AAPL": 150.0})
        return False  # Failed to catch
    except AccountingAnomalyDetected:
        return True  # Correctly caught!


def run_negative_control_omitted_trade() -> bool:
    """2. Injects omitted buy transaction; subsequent sell attempts to sell unheld shares."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    # Buy omitted!
    try:
        # Sell 50 shares of AAPL without having bought
        ledger.process_fill("2015-01-06", "AAPL", "sell", 50.0, fill_price=155.0, reference_price=155.0)
        return False
    except AccountingAnomalyDetected:
        return True  # Correctly caught oversell!


def run_negative_control_reversed_split() -> bool:
    """3. Injects invalid/reversed split ratio."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    ledger.process_fill("2015-01-05", "QLD", "buy", 100.0, fill_price=50.0, reference_price=50.0)
    try:
        ledger.apply_split("2015-01-06", "QLD", split_ratio=-2.0)
        return False
    except AccountingAnomalyDetected:
        return True  # Correctly rejected invalid split ratio!


def run_negative_control_double_dividend() -> bool:
    """4. Injects double dividend credit on settlement date."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    ledger.process_fill("2015-01-05", "SPY", "buy", 100.0, fill_price=200.0, reference_price=200.0)
    ledger.accrue_dividend("2015-01-05", "SPY", 1.0, "2015-01-15")
    # Tamper pending dividend list by duplicating it
    ledger.pending_dividends.append(copy.deepcopy(ledger.pending_dividends[0]))
    try:
        ledger.settle_dividends("2015-01-15")
        ledger.record_daily_snapshot("2015-01-15", {"SPY": 200.0})
        return False
    except AccountingAnomalyDetected:
        return True  # Correctly caught double dividend!


def run_negative_control_double_fee() -> bool:
    """5. Injects fee charged twice against cash."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    # Buy with $10 commission, but debit cash by $20
    ledger.process_fill("2015-01-05", "AAPL", "buy", 100.0, fill_price=150.0, reference_price=150.0, commission=10.0)
    ledger.cash -= 10.0  # Extra second fee charge
    try:
        ledger.record_daily_snapshot("2015-01-05", {"AAPL": 150.0})
        return False
    except AccountingAnomalyDetected:
        return True  # Correctly caught double fee!


def run_negative_control_missing_position() -> bool:
    """6. Injects missing/dropped position from ledger valuation."""
    ledger = IndependentLedger(initial_cash=100_000.0)
    ledger.process_fill("2015-01-05", "AAPL", "buy", 100.0, fill_price=150.0, reference_price=150.0)
    # Drop AAPL position from positions map
    del ledger.positions["AAPL"]
    try:
        ledger.record_daily_snapshot("2015-01-05", {"AAPL": 150.0})
        return False
    except AccountingAnomalyDetected:
        return True  # Correctly caught dropped position!


def run_negative_control_lookahead_leak() -> bool:
    """7. Injects future bar into point-in-time slice; caught by causal assertion."""
    from research.engine.validation import validate_market_state, ValidationError
    # Provide bar dated 2021-06-15 in a 2015 stream
    bad_state = {
        "SPY": [
            {"ts": "2015-01-05", "open": 200.0, "high": 205.0, "low": 199.0, "close": 201.0, "volume": 1e6},
            {"ts": "2021-06-15", "open": 400.0, "high": 405.0, "low": 399.0, "close": 402.0, "volume": 1e6},
        ]
    }
    try:
        validate_market_state(bad_state, asof_date="2015-01-05", strict_future_rejection=True)
        return False
    except (ValidationError, ValueError):
        return True  # Correctly caught future lookahead!

