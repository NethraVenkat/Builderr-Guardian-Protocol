"""Deterministic Daily Event Simulation Engine.

Enforces:
  1. Strictly causal information filtration: market_state <= session T close.
  2. Next-session execution: orders filled at session T+1 open with model slippage.
  3. Execution sequence: sells precede buys to replenish cash before purchasing.
  4. Point-in-time corporate action handling (splits and cash dividends).
  5. Deterministic trade and portfolio trace hashing for clean-clone reproduction.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

from research.engine.accounting import (
    CATASTROPHE_DD,
    CONCENTRATION_CAP,
    LEVERAGE_CAP,
    PortfolioState,
    RiskMode,
    calculate_metrics,
)
from research.engine.corporate_actions import CorporateActionRegistry
from research.engine.provider import MarketDataProvider
from research.engine.validation import ValidationError, validate_market_state


class ReplayEngine:
    """Deterministic event-driven daily replay simulator."""

    def __init__(
        self,
        agent_path_or_fn: Path | str | Callable,
        provider: MarketDataProvider,
        corporate_actions: CorporateActionRegistry | None = None,
        commission_bps: float = 0.0,
        start_cash: float = 100_000.0,
        risk_mode: RiskMode = RiskMode.TELEMETRY_ONLY,
    ):
        self.provider = provider
        self.corporate_actions = corporate_actions or CorporateActionRegistry()
        self.commission_bps = commission_bps
        self.start_cash = start_cash
        self.risk_mode = risk_mode
        self.decide = self._load_agent(agent_path_or_fn)

    def _load_agent(self, agent_path_or_fn: Path | str | Callable) -> Callable:
        if callable(agent_path_or_fn):
            return agent_path_or_fn
        p = Path(agent_path_or_fn)
        if not p.exists():
            raise FileNotFoundError(f"Agent source file not found: {p}")
        spec = importlib.util.spec_from_file_location("agent_under_test", p)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {p}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "decide"):
            raise AttributeError(f"Module {p} must define decide(market_state, portfolio_state, cash)")
        return mod.decide

    def run_replay(
        self,
        eval_start: str | None = None,
        eval_end: str | None = None,
        record_traces: bool = True,
    ) -> dict[str, Any]:
        """Execute deterministic replay across the provider's trading timeline."""
        timeline = self.provider.get_timeline(eval_start, eval_end)
        portfolio = PortfolioState(cash=self.start_cash)
        pending_orders: list[dict[str, Any]] = []
        errors = 0
        traces: list[dict[str, Any]] = []

        # Stream day-by-day point-in-time slices
        for current_date, market_state in self.provider.stream_daily_slices(eval_start, eval_end):
            portfolio.reset_daily_trade_counter()

            # 1. Point-in-time Corporate Actions before market open
            split_logs = self.corporate_actions.apply_splits_for_date(
                current_date, portfolio.positions, portfolio.avg_cost
            )
            div_cash, div_rec, div_logs = self.corporate_actions.process_dividends_for_date(
                current_date, portfolio.positions
            )
            portfolio.cash += div_cash
            portfolio.total_dividends_credited += div_cash
            portfolio.dividend_receivables = self.corporate_actions.total_outstanding_receivables()

            # Extract today's open and close prices
            today_opens: dict[str, float] = {}
            today_closes: dict[str, float] = {}
            for sym, bars in market_state.items():
                if bars and bars[-1]["ts"] == current_date:
                    today_opens[sym] = bars[-1].get("raw_open", bars[-1]["open"])
                    today_closes[sym] = bars[-1].get("raw_close", bars[-1]["close"])

            # 2. Execution at today's OPEN: Fill yesterday's pending orders
            # Sells first to replenish cash
            sells = [o for o in pending_orders if o.get("side") == "sell"]
            buys = [o for o in pending_orders if o.get("side") == "buy"]

            for order in sells:
                px = today_opens.get(order["ticker"])
                res = portfolio.execute_order(
                    order, px, commission_bps=self.commission_bps,
                    risk_mode=self.risk_mode, current_prices=today_opens
                )
                if res:
                    res.date = current_date
                    res.open_price = px or 0.0

            for order in buys:
                px = today_opens.get(order["ticker"])
                res = portfolio.execute_order(
                    order, px, commission_bps=self.commission_bps,
                    risk_mode=self.risk_mode, current_prices=today_opens
                )
                if res:
                    res.date = current_date
                    res.open_price = px or 0.0

            pending_orders = []

            # 3. Mark to Market at today's CLOSE
            portfolio.mark_to_market(today_closes)

            # 4. Verify double-entry balance sheet invariant
            inv_ok, inv_reason = portfolio.check_accounting_invariants(today_closes)
            if not inv_ok:
                raise RuntimeError(f"Balance sheet invariant violated on {current_date}: {inv_reason}")

            # 4. Invoke agent at today's CLOSE
            # Strict point-in-time contract: bars in market_state must not exceed current_date
            port_dict = portfolio.get_portfolio_state_dict(today_closes)
            try:
                orders = self.decide(market_state, port_dict, portfolio.cash)
            except Exception as e:
                errors += 1
                orders = []

            # Queue well-formed orders for next session open
            for o in orders or []:
                try:
                    sym = str(o.get("ticker", "")).strip().upper()
                    side = str(o.get("side", "")).strip().lower()
                    qty = float(o.get("quantity", 0.0))
                    if side in ("buy", "sell") and qty > 0 and sym in market_state:
                        pending_orders.append({"ticker": sym, "side": side, "quantity": qty})
                except (KeyError, TypeError, ValueError):
                    errors += 1

            if record_traces:
                traces.append({
                    "date": current_date,
                    "cash": round(portfolio.cash, 6),
                    "positions": sorted(
                        [{"ticker": t, "qty": round(q, 4)} for t, q in portfolio.positions.items()],
                        key=lambda x: x["ticker"],
                    ),
                    "orders": pending_orders,
                })

        metrics = calculate_metrics(portfolio.equity_curve, trades=portfolio.trade_count, errors=errors)
        trace_json = json.dumps(traces, sort_keys=True, separators=(",", ":"))
        trace_digest = hashlib.sha256(trace_json.encode("utf-8")).hexdigest()

        tot_turnover = sum(f.notional for f in portfolio.fill_log)
        tot_slippage = sum(f.notional * f.slippage for f in portfolio.fill_log)
        tot_commissions = portfolio.total_commissions

        self.last_portfolio = portfolio

        return {
            "metrics": metrics,
            "equity_curve": list(portfolio.equity_curve),
            "total_trades": portfolio.trade_count,
            "turnover": tot_turnover,
            "slippage_cost": tot_slippage,
            "commission_cost": tot_commissions,
            "fill_log": portfolio.fill_log,
            "peak_gross": portfolio.peak_gross,
            "peak_gross_notional": portfolio.peak_gross_notional,
            "peak_beta_adjusted": portfolio.peak_beta_adjusted,
            "peak_conc": portfolio.peak_conc,
            "max_conc_streak": portfolio.max_conc_streak,
            "trace_sha256": trace_digest,
            "compliance": {
                "no_errors": errors == 0,
                "leverage_compliant": portfolio.peak_gross <= LEVERAGE_CAP,
                "concentration_compliant": portfolio.max_conc_streak <= 5,
                "no_catastrophic_drawdown": metrics["mdd"] < CATASTROPHE_DD,
                "all_safety_bars_cleared": (
                    errors == 0
                    and portfolio.peak_gross <= LEVERAGE_CAP
                    and portfolio.max_conc_streak <= 5
                    and metrics["mdd"] < CATASTROPHE_DD
                ),
            },
        }
