"""Deterministic Portfolio Accounting, Pre-Trade Risk Enforcement & PnL Lifecycle.

Provides:
  1. Double-entry accounting tracking Cash, Positions, Dividend Receivables, Realized PnL,
     Unrealized PnL, Commissions, and Total Equity.
  2. Double-entry balance sheet invariant verification:
     Total Equity == Start Cash + Realized PnL + Unrealized PnL + Dividends - Commissions.
  3. Pre-trade Active Risk Enforcement Gates (Leverage <= 1.50x, Concentration <= 30%, Max Trades <= 50)
     strictly distinguished from post-hoc Passive Telemetry.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

BETA_3X = {"TQQQ", "SOXL", "UPRO", "SPXL", "TNA", "FAS", "TECL", "LABU", "CURE", "DRN", "UDOW", "NAIL"}
BETA_2X = {"QLD", "SSO", "DDM", "ROM", "UWM", "AGQ"}

SLIP_EQUITY = 0.0005     # 5 bps
SLIP_LEVERAGED = 0.0010  # 10 bps
LEVERAGE_CAP = 1.50
CONCENTRATION_CAP = 0.30
CATASTROPHE_DD = 0.50
MAX_TRADES_PER_DAY = 50
START_CASH = 100_000.0


class RiskMode(str, Enum):
    """Distinguishes passive measurement from active execution gating."""
    TELEMETRY_ONLY = "telemetry_only"        # Measures breaches post-close; does not alter orders (preview.py mode)
    ACTIVE_ENFORCEMENT = "active_enforcement"  # Pre-trade checks reject or clamp orders exceeding caps (live_runner mode)


class FinancialStateValidationError(ValueError):
    """Raised when portfolio state fields are missing, malformed, negative, or fail balance sheet conservation."""
    pass


def get_beta(ticker: str) -> float:
    t = ticker.upper()
    if t in BETA_3X:
        return 3.0
    if t in BETA_2X:
        return 2.0
    return 1.0


@dataclass
class FillResult:
    ticker: str
    side: str
    requested_qty: float
    filled_qty: float
    fill_price: float
    slippage: float
    notional: float
    commission: float
    realized_pnl: float = 0.0
    rejected: bool = False
    rejection_reason: str | None = None
    date: str = ""
    open_price: float = 0.0


@dataclass
class PortfolioState:
    cash: float = START_CASH
    start_cash: float = START_CASH
    positions: dict[str, float] = field(default_factory=dict)       # ticker -> held qty
    avg_cost: dict[str, float] = field(default_factory=dict)        # ticker -> average purchase cost
    dividend_receivables: float = 0.0                               # unpaid dividend entitlement asset
    realized_pnl: float = 0.0                                       # accumulated gross realized PnL from closed sells
    total_dividends_credited: float = 0.0                           # cash dividends paid into account
    total_commissions: float = 0.0                                  # accumulated transaction fees
    trades_today: int = 0                                           # daily trade counter for 50 trades/day rule
    trade_count: int = 0                                            # total trade counter across simulation
    equity_curve: list[float] = field(default_factory=list)
    peak_gross: float = 0.0                                         # Preview.py compatibility (beta-weighted)
    peak_gross_notional: float = 0.0                                # Genuine gross notional leverage: sum(|V|) / equity
    peak_beta_adjusted: float = 0.0                                 # Beta-adjusted exposure: sum(|V| * beta) / equity
    peak_conc: float = 0.0
    conc_streak: dict[str, int] = field(default_factory=dict)
    max_conc_streak: int = 0
    fill_log: list[FillResult] = field(default_factory=list)
    rejected_orders: list[dict[str, Any]] = field(default_factory=list)

    def total_positions_value(self, current_prices: dict[str, float]) -> float:
        return sum(
            self.positions.get(t, 0.0) * current_prices.get(t, self.avg_cost.get(t, 0.0))
            for t in self.positions
            if self.positions.get(t, 0.0) > 0.0
        )

    def unrealized_pnl(self, current_prices: dict[str, float]) -> float:
        """Mark-to-market unrealized PnL on open positions."""
        total = 0.0
        for t, q in self.positions.items():
            if q > 0.0:
                cost = self.avg_cost.get(t, 0.0)
                px = current_prices.get(t, cost)
                total += (px - cost) * q
        return total

    def total_equity(self, current_prices: dict[str, float]) -> float:
        """Comprehensive balance sheet equity including cash, positions and receivables."""
        eq = self.cash + self.total_positions_value(current_prices) + self.dividend_receivables
        return max(eq, 1e-9)

    def check_accounting_invariants(self, current_prices: dict[str, float], tolerance: float = 1e-7) -> tuple[bool, str]:
        """Verify the fundamental double-entry balance sheet identity:

        Equity == Start Cash + Realized PnL + Unrealized PnL + Dividends - Commissions
        """
        eq = self.total_equity(current_prices)
        unrealized = self.unrealized_pnl(current_prices)
        reconstructed = (
            self.start_cash
            + self.realized_pnl
            + unrealized
            + self.total_dividends_credited
            + self.dividend_receivables
            - self.total_commissions
        )
        diff = abs(eq - reconstructed)
        if diff > tolerance:
            return False, f"Balance sheet discrepancy: Equity={eq:.6f} vs Reconstructed={reconstructed:.6f} (diff={diff:.2e})"
        return True, "Balance sheet identity verified"

    def get_portfolio_state_dict(self, current_prices: dict[str, float]) -> dict[str, Any]:
        """Format portfolio state matching official competition contract."""
        return {
            "cash": float(self.cash),
            "positions": [
                {"ticker": t, "quantity": q, "avg_cost": self.avg_cost.get(t, 0.0)}
                for t, q in sorted(self.positions.items())
                if q > 0.0
            ],
            "last_prices": {t: float(p) for t, p in sorted(current_prices.items()) if p is not None},
        }

    def reset_daily_trade_counter(self) -> None:
        self.trades_today = 0

    def execute_order(
        self,
        order: dict[str, Any],
        open_price: float | None,
        commission_bps: float = 0.0,
        risk_mode: RiskMode = RiskMode.TELEMETRY_ONLY,
        current_prices: dict[str, float] | None = None,
    ) -> FillResult:
        """Execute a single order with active or telemetry-only risk gates."""
        ticker = str(order.get("ticker", "")).strip().upper()
        side = str(order.get("side", "")).strip().lower()

        try:
            req_qty = float(order.get("quantity", 0.0))
        except (TypeError, ValueError):
            self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": 0.0, "reason": "INVALID_QUANTITY"})
            return None

        if req_qty <= 0.0 or not math.isfinite(req_qty):
            self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": req_qty, "reason": "NONPOSITIVE_QUANTITY"})
            return None

        orig_qty = req_qty

        if open_price is None or open_price <= 0.0 or not math.isfinite(open_price):
            self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "MISSING_EXECUTION_PRICE"})
            return None

        # Active Daily Trade Cap Enforcement
        if risk_mode == RiskMode.ACTIVE_ENFORCEMENT and self.trades_today >= MAX_TRADES_PER_DAY:
            self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "DAILY_TRADE_LIMIT_EXCEEDED"})
            return None

        b = get_beta(ticker)
        slip = SLIP_LEVERAGED if b > 1.0 else SLIP_EQUITY
        prices = current_prices or {}

        if side == "buy":
            fill_px = open_price * (1.0 + slip)
            eq = self.total_equity(prices)

            # Active Pre-Trade Enforcement Gates
            if risk_mode == RiskMode.ACTIVE_ENFORCEMENT:
                # 1. Single Position Concentration Cap (30% of equity)
                cur_held = self.positions.get(ticker, 0.0)
                cur_notional = cur_held * prices.get(ticker, fill_px)
                if eq > 0 and (cur_notional / eq) >= (CONCENTRATION_CAP - 0.002):
                    self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "EXCEEDS_CONCENTRATION_CAP"})
                    return None
                max_pos_notional = (CONCENTRATION_CAP * eq) - cur_notional
                if max_pos_notional <= (0.002 * eq):
                    self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "EXCEEDS_CONCENTRATION_CAP"})
                    return None
                max_qty_conc = max_pos_notional / fill_px
                req_qty = min(req_qty, max_qty_conc)

                # 2. Gross Beta-Adjusted Leverage Cap (1.50x equity)
                cur_gross_beta = sum(
                    self.positions.get(t, 0.0) * prices.get(t, self.avg_cost.get(t, 0.0)) * get_beta(t)
                    for t in self.positions
                )
                if eq > 0 and (cur_gross_beta / eq) >= (LEVERAGE_CAP - 0.005):
                    self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "EXCEEDS_LEVERAGE_CAP"})
                    return None
                avail_beta_room = (LEVERAGE_CAP * eq) - cur_gross_beta
                if avail_beta_room <= (0.005 * eq):
                    self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "EXCEEDS_LEVERAGE_CAP"})
                    return None
                max_qty_lev = avail_beta_room / (fill_px * b)
                req_qty = min(req_qty, max_qty_lev)

            # Cash Affordability Cap
            cost = fill_px * req_qty
            comm = cost * (commission_bps / 10000.0)
            if cost + comm > self.cash:
                avail_cash = max(self.cash - comm, 0.0)
                filled_qty = avail_cash / fill_px if fill_px > 0 else 0.0
                cost = fill_px * filled_qty
                comm = cost * (commission_bps / 10000.0)
            else:
                filled_qty = req_qty

            if filled_qty <= 1e-9:
                self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "INSUFFICIENT_CASH"})
                return None

            held = self.positions.get(ticker, 0.0)
            prev_cost_total = held * self.avg_cost.get(ticker, 0.0)
            new_held = held + filled_qty
            self.positions[ticker] = new_held
            self.avg_cost[ticker] = (prev_cost_total + cost) / new_held
            self.cash -= (cost + comm)
            self.total_commissions += comm
            self.trades_today += 1
            self.trade_count += 1

            res = FillResult(ticker, "buy", orig_qty, filled_qty, fill_px, slip, cost, comm)
            self.fill_log.append(res)
            return res

        elif side == "sell":
            held = self.positions.get(ticker, 0.0)
            if held <= 0.0:
                self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "UNHELD_POSITION"})
                return None

            filled_qty = min(req_qty, held)
            fill_px = open_price * (1.0 - slip)
            proceeds = fill_px * filled_qty
            comm = proceeds * (commission_bps / 10000.0)

            # Gross Realized PnL Calculation (exact identity: Equity == Start + Realized + Unrealized + Div - Comm)
            cost_basis = filled_qty * self.avg_cost.get(ticker, 0.0)
            pnl = proceeds - cost_basis

            self.positions[ticker] = held - filled_qty
            if self.positions[ticker] <= 1e-9:
                self.positions.pop(ticker, None)
                self.avg_cost.pop(ticker, None)

            self.cash += (proceeds - comm)
            self.realized_pnl += pnl
            self.total_commissions += comm
            self.trades_today += 1
            self.trade_count += 1

            res = FillResult(ticker, "sell", orig_qty, filled_qty, fill_px, slip, proceeds, comm, realized_pnl=pnl)
            self.fill_log.append(res)
            return res

        self.rejected_orders.append({"ticker": ticker, "side": side, "quantity": orig_qty, "reason": "UNKNOWN_SIDE"})
        return None

    def mark_to_market(self, close_prices: dict[str, float]) -> float:
        """Mark portfolio to market at session close and update risk telemetry."""
        pos_values = {
            t: q * close_prices.get(t, self.avg_cost.get(t, 0.0))
            for t, q in self.positions.items()
            if q > 0.0
        }
        eq = max(self.cash + sum(pos_values.values()) + self.dividend_receivables, 1e-9)
        self.equity_curve.append(eq)

        # 1. Genuine Gross-Notional Leverage: sum(|V_i|) / equity
        gross_notional = sum(abs(v) for v in pos_values.values()) / eq if eq > 0 else 0.0
        self.peak_gross_notional = max(self.peak_gross_notional, gross_notional)

        # 2. Beta-Adjusted Exposure: sum(|V_i| * beta_i) / equity
        beta_adj = sum(abs(v) * get_beta(t) for t, v in pos_values.items()) / eq if eq > 0 else 0.0
        self.peak_beta_adjusted = max(self.peak_beta_adjusted, beta_adj)
        self.peak_gross = self.peak_beta_adjusted  # Match preview.py evaluator telemetry

        # Single position concentration telemetry
        for t in list(self.positions.keys()):
            frac = abs(pos_values.get(t, 0.0)) / eq
            self.peak_conc = max(self.peak_conc, frac)
            if frac >= CONCENTRATION_CAP:
                self.conc_streak[t] = self.conc_streak.get(t, 0) + 1
                self.max_conc_streak = max(self.max_conc_streak, self.conc_streak[t])
            else:
                self.conc_streak[t] = 0

        return eq


def calculate_metrics(equity_curve: list[float], trades: int = 0, errors: int = 0) -> dict[str, Any]:
    """Compute financial summary metrics matching preview.py."""
    if not equity_curve:
        return {"ret": 0.0, "mdd": 0.0, "sharpe": 0.0, "calmar": 0.0, "trades": trades, "days": 0, "errors": errors}

    ret = equity_curve[-1] / START_CASH - 1.0

    peak, mdd = -1e18, 0.0
    for v in equity_curve:
        peak = max(peak, v)
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)

    if len(equity_curve) < 2:
        sharpe = 0.0
    else:
        rets = [equity_curve[i] / equity_curve[i - 1] - 1.0 for i in range(1, len(equity_curve))]
        n = len(rets)
        mean_ret = sum(rets) / n
        var = sum((r - mean_ret) ** 2 for r in rets) / (n - 1) if n > 1 else 0.0
        stdev = math.sqrt(var) if var > 0 else 0.0
        sharpe = (mean_ret / stdev * math.sqrt(252.0)) if stdev > 1e-9 else 0.0

    ann_ret = ((1.0 + ret) ** (252.0 / len(equity_curve)) - 1.0) if len(equity_curve) > 0 else 0.0
    calmar = (ann_ret / mdd) if mdd > 1e-9 else 0.0

    return {
        "ret": ret,
        "mdd": mdd,
        "sharpe": sharpe,
        "calmar": calmar,
        "trades": trades,
        "days": len(equity_curve),
        "errors": errors,
    }


def validate_and_extract_carryforward_state(
    strat_data: dict[str, Any],
    strat_name: str,
) -> tuple[float, float, dict[str, float], dict[str, float], float]:
    """Fail closed with explicit validation errors when restoring carryforward portfolio state.

    Removes all silent fallback behavior. Validates that:
      1. strat_data is a dictionary.
      2. 'ending_cash' is explicitly present, non-null, numeric, and >= 0.0.
      3. 'dividend_receivables' is explicitly present, non-null, numeric, and >= 0.0.
      4. 'positions' is present as a list of valid position records with non-empty symbol, shares > 0, price > 0.
      5. Double-entry balance sheet conservation matches 'ending_nav' within $0.05.

    Returns:
      (init_cash, receivables, positions_dict, avg_cost_dict, start_capital)
    """
    if not isinstance(strat_data, dict):
        raise FinancialStateValidationError(
            f"Invalid strategy manifest for '{strat_name}': expected dict, got {type(strat_data).__name__}"
        )

    if "ending_cash" not in strat_data:
        raise FinancialStateValidationError(
            f"Missing mandatory 'ending_cash' for strategy '{strat_name}'. Silent fallbacks are prohibited."
        )
    if strat_data["ending_cash"] is None:
        raise FinancialStateValidationError(
            f"Mandatory 'ending_cash' is None for strategy '{strat_name}'"
        )

    try:
        init_cash = float(strat_data["ending_cash"])
    except (ValueError, TypeError) as e:
        raise FinancialStateValidationError(
            f"Malformed 'ending_cash' for strategy '{strat_name}': {e}"
        )

    if not math.isfinite(init_cash) or init_cash < 0.0:
        raise FinancialStateValidationError(
            f"Non-finite or negative 'ending_cash' ({init_cash}) for strategy '{strat_name}'"
        )

    if "dividend_receivables" not in strat_data:
        raise FinancialStateValidationError(
            f"Missing mandatory 'dividend_receivables' for strategy '{strat_name}'. Silent fallbacks are prohibited."
        )
    if strat_data["dividend_receivables"] is None:
        raise FinancialStateValidationError(
            f"Mandatory 'dividend_receivables' is None for strategy '{strat_name}'"
        )

    try:
        receivables = float(strat_data["dividend_receivables"])
    except (ValueError, TypeError) as e:
        raise FinancialStateValidationError(
            f"Malformed 'dividend_receivables' for strategy '{strat_name}': {e}"
        )

    if not math.isfinite(receivables) or receivables < 0.0:
        raise FinancialStateValidationError(
            f"Non-finite or negative 'dividend_receivables' ({receivables}) for strategy '{strat_name}'"
        )

    if "positions" not in strat_data or not isinstance(strat_data["positions"], list):
        raise FinancialStateValidationError(
            f"Missing or invalid 'positions' list for strategy '{strat_name}'"
        )

    init_pos: dict[str, float] = {}
    init_avg_cost: dict[str, float] = {}
    total_positions_val = 0.0

    for p in strat_data["positions"]:
        if not isinstance(p, dict):
            raise FinancialStateValidationError(
                f"Invalid position record in '{strat_name}': expected dict, got {type(p).__name__}"
            )
        sym = p.get("symbol") or p.get("ticker")
        if not sym or not isinstance(sym, str):
            raise FinancialStateValidationError(
                f"Missing symbol in position record for '{strat_name}'"
            )
        if "shares" not in p or p["shares"] is None:
            raise FinancialStateValidationError(
                f"Missing 'shares' for symbol '{sym}' in '{strat_name}'"
            )
        try:
            shares = float(p["shares"])
        except (ValueError, TypeError) as e:
            raise FinancialStateValidationError(
                f"Malformed 'shares' for symbol '{sym}' in '{strat_name}': {e}"
            )
        if not math.isfinite(shares) or shares <= 0.0:
            raise FinancialStateValidationError(
                f"Non-positive shares ({shares}) for symbol '{sym}' in '{strat_name}'"
            )

        px_val = p.get("raw_price")
        if px_val is None:
            px_val = p.get("close_price")
        if px_val is None:
            raise FinancialStateValidationError(
                f"Missing price for symbol '{sym}' in '{strat_name}'"
            )
        try:
            price = float(px_val)
        except (ValueError, TypeError) as e:
            raise FinancialStateValidationError(
                f"Malformed price for symbol '{sym}' in '{strat_name}': {e}"
            )
        if not math.isfinite(price) or price <= 0.0:
            raise FinancialStateValidationError(
                f"Non-positive price ({price}) for symbol '{sym}' in '{strat_name}'"
            )

        init_pos[sym] = shares
        init_avg_cost[sym] = price
        total_positions_val += shares * price

    # Double-entry balance sheet verification on manifest:
    expected_nav = init_cash + receivables + total_positions_val
    if "ending_nav" in strat_data and strat_data["ending_nav"] is not None:
        try:
            manifest_nav = float(strat_data["ending_nav"])
            if abs(expected_nav - manifest_nav) > 0.05:
                raise FinancialStateValidationError(
                    f"Balance sheet conservation violation in '{strat_name}': "
                    f"Cash ({init_cash:.2f}) + Receivables ({receivables:.2f}) + Stock ({total_positions_val:.2f}) = {expected_nav:.2f} "
                    f"does not match manifest ending_nav {manifest_nav:.2f}"
                )
        except (ValueError, TypeError) as e:
            if isinstance(e, FinancialStateValidationError):
                raise
            raise FinancialStateValidationError(
                f"Malformed 'ending_nav' for strategy '{strat_name}': {e}"
            )

    start_capital = init_cash + total_positions_val
    return init_cash, receivables, init_pos, init_avg_cost, start_capital
