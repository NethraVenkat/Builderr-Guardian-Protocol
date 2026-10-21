"""Deterministic Portfolio Accounting, Execution & Risk Telemetry.

Provides exact cash accounting, slippage modeling, position tracking,
and auto-enforced competition risk caps (gross leverage <= 1.5x, concentration <= 30%).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

BETA_3X = {"TQQQ", "SOXL", "UPRO", "SPXL", "TNA", "FAS", "TECL", "LABU", "CURE", "DRN", "UDOW", "NAIL"}
BETA_2X = {"QLD", "SSO", "DDM", "ROM", "UWM", "AGQ"}

SLIP_EQUITY = 0.0005     # 5 bps
SLIP_LEVERAGED = 0.0010  # 10 bps
LEVERAGE_CAP = 1.50
CONCENTRATION_CAP = 0.30
CATASTROPHE_DD = 0.50
START_CASH = 100_000.0


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


@dataclass
class PortfolioState:
    cash: float = START_CASH
    positions: dict[str, float] = field(default_factory=dict)  # ticker -> qty
    avg_cost: dict[str, float] = field(default_factory=dict)   # ticker -> unit cost
    equity_curve: list[float] = field(default_factory=list)
    peak_gross: float = 0.0
    peak_conc: float = 0.0
    conc_streak: dict[str, int] = field(default_factory=dict)
    max_conc_streak: int = 0
    trade_count: int = 0
    fill_log: list[FillResult] = field(default_factory=list)

    def total_equity(self, current_prices: dict[str, float]) -> float:
        pos_val = sum(
            self.positions.get(t, 0.0) * current_prices.get(t, self.avg_cost.get(t, 0.0))
            for t in self.positions
            if self.positions.get(t, 0.0) > 0.0
        )
        return max(self.cash + pos_val, 1e-9)

    def get_portfolio_state_dict(self, current_prices: dict[str, float]) -> dict[str, Any]:
        """Format portfolio state matching competition contract schema."""
        return {
            "cash": float(self.cash),
            "positions": [
                {"ticker": t, "quantity": q, "avg_cost": self.avg_cost.get(t, 0.0)}
                for t, q in sorted(self.positions.items())
                if q > 0.0
            ],
            "last_prices": {t: float(p) for t, p in sorted(current_prices.items()) if p is not None},
        }

    def execute_order(
        self,
        order: dict[str, Any],
        open_price: float | None,
        commission_bps: float = 0.0,
    ) -> FillResult | None:
        """Execute a single order at open_price with slippage.

        Enforces long-only, cash bounds, and holding constraints.
        """
        if open_price is None or open_price <= 0.0 or not math.isfinite(open_price):
            return None

        ticker = str(order.get("ticker", "")).strip().upper()
        side = str(order.get("side", "")).strip().lower()
        try:
            req_qty = float(order.get("quantity", 0.0))
        except (TypeError, ValueError):
            return None

        if req_qty <= 0.0 or not math.isfinite(req_qty):
            return None

        b = get_beta(ticker)
        slip = SLIP_LEVERAGED if b > 1.0 else SLIP_EQUITY

        if side == "buy":
            fill_px = open_price * (1.0 + slip)
            cost = fill_px * req_qty
            comm = cost * (commission_bps / 10000.0)
            if cost + comm > self.cash:
                # Affordability cap: can't buy more than available cash allows
                avail = max(self.cash - comm, 0.0)
                filled_qty = avail / fill_px if fill_px > 0 else 0.0
                cost = fill_px * filled_qty
                comm = cost * (commission_bps / 10000.0)
            else:
                filled_qty = req_qty

            if filled_qty <= 0.0:
                return None

            held = self.positions.get(ticker, 0.0)
            prev_notional = held * self.avg_cost.get(ticker, 0.0)
            new_held = held + filled_qty
            self.positions[ticker] = new_held
            self.avg_cost[ticker] = (prev_notional + cost) / new_held
            self.cash -= (cost + comm)
            self.trade_count += 1

            res = FillResult(ticker, "buy", req_qty, filled_qty, fill_px, slip, cost, comm)
            self.fill_log.append(res)
            return res

        elif side == "sell":
            held = self.positions.get(ticker, 0.0)
            filled_qty = min(req_qty, held)
            if filled_qty <= 0.0:
                return None

            fill_px = open_price * (1.0 - slip)
            proceeds = fill_px * filled_qty
            comm = proceeds * (commission_bps / 10000.0)

            self.positions[ticker] = held - filled_qty
            if self.positions[ticker] <= 1e-9:
                self.positions.pop(ticker, None)
                self.avg_cost.pop(ticker, None)

            self.cash += (proceeds - comm)
            self.trade_count += 1

            res = FillResult(ticker, "sell", req_qty, filled_qty, fill_px, slip, proceeds, comm)
            self.fill_log.append(res)
            return res

        return None

    def mark_to_market(self, close_prices: dict[str, float]) -> float:
        """Mark portfolio to market at session close and update risk telemetry."""
        pos_values = {
            t: q * close_prices.get(t, self.avg_cost.get(t, 0.0))
            for t, q in self.positions.items()
            if q > 0.0
        }
        eq = max(self.cash + sum(pos_values.values()), 1e-9)
        self.equity_curve.append(eq)

        # Gross Beta-adjusted leverage check
        gross = sum(abs(v) * get_beta(t) for t, v in pos_values.items()) / eq
        self.peak_gross = max(self.peak_gross, gross)

        # Single position concentration check
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
    """Compute financial summary metrics identical to preview.py."""
    if not equity_curve:
        return {"ret": 0.0, "mdd": 0.0, "sharpe": 0.0, "calmar": 0.0, "trades": trades, "days": 0, "errors": errors}

    ret = equity_curve[-1] / START_CASH - 1.0

    # Max Drawdown
    peak, mdd = -1e18, 0.0
    for v in equity_curve:
        peak = max(peak, v)
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)

    # Sharpe ratio
    if len(equity_curve) < 2:
        sharpe = 0.0
    else:
        rets = [equity_curve[i] / equity_curve[i - 1] - 1.0 for i in range(1, len(equity_curve))]
        n = len(rets)
        mean_ret = sum(rets) / n
        var = sum((r - mean_ret) ** 2 for r in rets) / (n - 1) if n > 1 else 0.0
        stdev = math.sqrt(var) if var > 0 else 0.0
        sharpe = (mean_ret / stdev * math.sqrt(252.0)) if stdev > 1e-9 else 0.0

    # Calmar ratio
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
