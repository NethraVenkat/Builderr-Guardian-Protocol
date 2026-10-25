"""Candidate Research Strategy: Adaptive Volatility-Targeted Alpha with Drawdown De-Risking.

Research Hypothesis:
  Weighting risk-on assets inversely to 20-day realized volatility and scaling down gross
  exposure when portfolio drawdown exceeds 10% dampens tail losses and reduces turnover,
  preventing severe drawdown streaks observed during volatility spikes without sacrificing
  regime-dependent upside.

Signature matches official competition contract:
  decide(market_state: dict, portfolio_state: dict, cash: float) -> list[dict]
"""
from __future__ import annotations

import math
from typing import Any

from agent import (
    closes,
    current_positions,
    equity,
    momentum,
    orders_to_rebalance,
    realized_vol,
    sma,
    _latest_bar_date,
    _market_prices,
    _scale_caps,
)


class AdaptiveRiskParityCandidate:
    """Research strategy candidate for controlled optimization evaluation."""

    def __init__(
        self,
        vol_target: float = 0.15,
        dd_derisk_threshold: float = 0.10,
        rebalance_every_days: int = 5,
        max_position_cap: float = 0.22,
    ):
        self.vol_target = vol_target
        self.dd_derisk_threshold = dd_derisk_threshold
        self.rebalance_every_days = rebalance_every_days
        self.max_position_cap = max_position_cap
        self.peak_portfolio_val: float = 0.0
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0

    def reset(self) -> None:
        self.peak_portfolio_val = 0.0
        self.last_rebalance_date = None
        self.days_counter = 0

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]], total_equity: float) -> dict[str, float]:
        spy_bars = market_state.get("SPY", [])
        qqq_bars = market_state.get("QQQ", [])

        spy_c = closes(spy_bars)
        qqq_c = closes(qqq_bars)

        if len(spy_c) < 50 or len(qqq_c) < 50:
            return {}

        spy_sma50 = sma(spy_c, 50)
        qqq_sma50 = sma(qqq_c, 50)
        qqq_vol20 = realized_vol(qqq_c, 20)

        if spy_sma50 is None or qqq_sma50 is None or qqq_vol20 is None:
            return {}

        self.peak_portfolio_val = max(self.peak_portfolio_val, total_equity)
        current_dd = (self.peak_portfolio_val - total_equity) / self.peak_portfolio_val if self.peak_portfolio_val > 0 else 0.0

        # Drawdown de-risking factor
        derisk_mult = 1.0
        if current_dd >= self.dd_derisk_threshold:
            derisk_mult = max(0.40, 1.0 - (current_dd - self.dd_derisk_threshold) * 3.0)

        bull_regime = (spy_c[-1] > spy_sma50) and (qqq_c[-1] > qqq_sma50)
        low_vol_regime = qqq_vol20 < 0.35

        targets: dict[str, float] = {}

        if bull_regime and low_vol_regime:
            candidates = ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN"]
            inv_vols: dict[str, float] = {}

            for ticker in candidates:
                c_bars = market_state.get(ticker)
                c_vals = closes(c_bars)
                if len(c_vals) >= 20:
                    v = realized_vol(c_vals, 20)
                    if v and v > 0:
                        inv_vols[ticker] = 1.0 / max(v, 0.05)

            sum_inv = sum(inv_vols.values())
            if sum_inv > 0:
                base_budget = 0.85 * derisk_mult
                for ticker, iv in inv_vols.items():
                    raw_w = (iv / sum_inv) * base_budget
                    targets[ticker] = min(raw_w, self.max_position_cap)

            if qqq_vol20 < 0.22 and derisk_mult > 0.85:
                targets["QLD"] = 0.08
        else:
            # Defensive risk-off allocation
            targets = {"SPY": 0.15 * derisk_mult}

        return _scale_caps(targets)

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        if not market_state:
            return []

        latest_date = _latest_bar_date(market_state)
        if latest_date is None:
            return []

        self.days_counter += 1
        should_rebalance = (
            self.last_rebalance_date is None
            or self.days_counter >= self.rebalance_every_days
        )
        if not should_rebalance:
            return []

        tot_eq = equity(portfolio_state, cash)
        targets = self.compute_targets(market_state, tot_eq)
        if not targets:
            return []

        prices = _market_prices(market_state)
        positions = current_positions(portfolio_state)
        orders = orders_to_rebalance(targets, positions, tot_eq, prices, cash)

        if orders:
            self.last_rebalance_date = latest_date
            self.days_counter = 0

        return orders
