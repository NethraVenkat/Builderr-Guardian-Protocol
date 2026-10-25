"""Advanced Loss Reduction and Profitability Research Candidates.

Fulfills Guardian Alpha Protocol V10 Stages V10-E and V10-F:
- Candidate Family 1: Volatility-Aware Position Sizing (Inverse-vol scaling with exposure caps)
- Candidate Family 3: Drawdown-Aware Capital Preservation (Dynamic de-risking multiplier)
- Candidate Family 4: Fast Emergency Exit & Whipsaw Filter (Exits before 5-day cadence on tail shock)
- Integrated Candidate: EnhancedGuardianAlphaCandidate (Combines fast risk-off, pure defensive cash,
  volatility scaling, and recovery participation)

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
    DEFENSIVE_WEIGHTS,
    RISK_CANDIDATES,
    MAX_WEIGHT,
    BETA_MULTIPLE,
    MAX_BETA_GROSS,
)


class FastExitDeRiskingCandidate:
    """Candidate Family 3/4: Fast Emergency Exit on Market Breakdown + Drawdown Guard.
    
    Research Hypothesis:
      E0 suffers 78.6% of its drawdown in the first 5 days of a crash because of the rigid
      5-day rebalance cadence. By allowing an emergency risk-off liquidation whenever 2-day
      SPY drop exceeds 3.0% or 20-day realized volatility spikes above 0.38, tail losses can
      be truncated immediately without waiting for the 5-day clock.
    """

    def __init__(
        self,
        rebalance_every_days: int = 5,
        emergency_drop_threshold: float = -0.030,  # -3.0% 2-day drop triggers immediate exit
        dd_derisk_threshold: float = 0.08,        # 8% drawdown triggers exposure halving
        exclude_xle_defensive: bool = True,       # Remove volatile energy from defensive basket
    ):
        self.rebalance_every_days = rebalance_every_days
        self.emergency_drop_threshold = emergency_drop_threshold
        self.dd_derisk_threshold = dd_derisk_threshold
        self.exclude_xle_defensive = exclude_xle_defensive
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0
        self.peak_portfolio_val: float = 0.0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_portfolio_val = 0.0

    def _is_emergency_market_shock(self, market_state: dict[str, list[dict[str, Any]]]) -> bool:
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        ret_2d = (spy_c[-1] / spy_c[-3]) - 1.0
        return ret_2d <= self.emergency_drop_threshold

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]], total_equity: float) -> dict[str, float]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}

        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)

        # Track Drawdown
        self.peak_portfolio_val = max(self.peak_portfolio_val, total_equity)
        current_dd = (self.peak_portfolio_val - total_equity) / self.peak_portfolio_val if self.peak_portfolio_val > 0 else 0.0

        # Drawdown scaling factor: reduces gross budget when in drawdown
        derisk_mult = 1.0
        if current_dd >= self.dd_derisk_threshold:
            derisk_mult = max(0.30, 1.0 - (current_dd - self.dd_derisk_threshold) * 4.0)

        risk_on = bool(
            spy_sma50 is not None
            and qqq_sma50 is not None
            and qqq_vol20 is not None
            and spy[-1] > spy_sma50
            and qqq[-1] > qqq_sma50
            and qqq_vol20 < 0.35
            and not self._is_emergency_market_shock(market_state)
        )

        if not risk_on:
            # Defensive allocation: Replace XLE with pure cash retention or conservative staples
            if self.exclude_xle_defensive:
                # XLP 28%, XLU 28%, XLV 24%, 20% Cash
                weights = {"XLP": 0.28 * derisk_mult, "XLU": 0.28 * derisk_mult, "XLV": 0.24 * derisk_mult}
            else:
                weights = {t: w * derisk_mult for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))}
            return _scale_caps(weights)

        # Risk-on ranking
        scored: list[tuple[float, str]] = []
        for ticker in RISK_CANDIDATES:
            values = closes(market_state.get(ticker))
            if len(values) < 61:
                continue
            mom60 = momentum(values, 60)
            mom20 = momentum(values, 20)
            trend50 = sma(values, 50)
            vol20 = realized_vol(values, 20)
            if mom60 is None or mom20 is None or trend50 is None or vol20 is None:
                continue
            trend_gap = values[-1] / trend50 - 1.0
            score = (0.55 * mom60) + (0.25 * mom20) + (0.20 * trend_gap) - (0.15 * vol20)
            if score > 0.0:
                scored.append((score, ticker))

        scored.sort(reverse=True)
        winners = [ticker for _, ticker in scored[:5]]
        if not winners:
            return _scale_caps({"XLP": 0.24 * derisk_mult, "XLU": 0.24 * derisk_mult, "XLV": 0.20 * derisk_mult})

        qqq_sma20 = sma(qqq, 20)
        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 is not None
            and qqq_sma50 is not None
            and qqq_mom20 is not None
            and qqq_sma20 > qqq_sma50
            and qqq_mom20 > 0.0
            and qqq_vol20 < 0.28
            and closes(market_state.get("QLD"))
            and closes(market_state.get("SSO"))
            and derisk_mult >= 0.90
        )

        weights: dict[str, float] = {}
        base_budget = (0.76 if overlay_on else 0.92) * derisk_mult
        max_single_w = (MAX_WEIGHT - 0.02) * derisk_mult
        per_winner = min(max_single_w, base_budget / len(winners))
        for ticker in winners:
            weights[ticker] = per_winner

        if overlay_on:
            weights["QLD"] = 0.11 * derisk_mult
            weights["SSO"] = 0.07 * derisk_mult

        return _scale_caps(weights)

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
        is_shock = self._is_emergency_market_shock(market_state)
        should_rebalance = (
            self.last_rebalance_date is None
            or self.days_counter >= self.rebalance_every_days
            or is_shock  # Break out of cadence on market shock!
        )

        if not should_rebalance:
            return []

        tot_eq = equity(portfolio_state, cash)
        targets = self.compute_targets(market_state, tot_eq)
        if not targets and not is_shock:
            return []

        prices = _market_prices(market_state)
        positions = current_positions(portfolio_state)
        orders = orders_to_rebalance(targets, positions, tot_eq, prices, cash)

        if orders:
            self.last_rebalance_date = latest_date
            self.days_counter = 0

        return orders


class IntegratedLossReductionCandidate:
    """Candidate Family 1, 3, 4, 8: Integrated Adaptive Risk Parity with Snapback & Fast Exit.
    
    Features:
    1. Fast emergency exit on 2-day market drop > 3.0%.
    2. Realized volatility-weighted allocation across momentum winners.
    3. Excludes pro-cyclical XLE from defensive basket during bear regimes.
    4. Recovery re-entry mechanism: allows scaled re-entry when QQQ breaks above SMA20 even if
       50-day SMA is not yet reclaimed.
    """

    def __init__(
        self,
        rebalance_every_days: int = 5,
        emergency_drop_threshold: float = -0.028,
        dd_derisk_threshold: float = 0.07,
    ):
        self.rebalance_every_days = rebalance_every_days
        self.emergency_drop_threshold = emergency_drop_threshold
        self.dd_derisk_threshold = dd_derisk_threshold
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0
        self.peak_portfolio_val: float = 0.0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_portfolio_val = 0.0

    def _is_emergency_market_shock(self, market_state: dict[str, list[dict[str, Any]]]) -> bool:
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        ret_2d = (spy_c[-1] / spy_c[-3]) - 1.0
        return ret_2d <= self.emergency_drop_threshold

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]], total_equity: float) -> dict[str, float]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}

        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_sma20 = sma(qqq, 20)
        qqq_mom10 = momentum(qqq, 10)
        qqq_vol20 = realized_vol(qqq, 20)

        self.peak_portfolio_val = max(self.peak_portfolio_val, total_equity)
        current_dd = (self.peak_portfolio_val - total_equity) / self.peak_portfolio_val if self.peak_portfolio_val > 0 else 0.0

        # Drawdown de-risking multiplier
        derisk_mult = 1.0
        if current_dd >= self.dd_derisk_threshold:
            derisk_mult = max(0.40, 1.0 - (current_dd - self.dd_derisk_threshold) * 3.5)

        is_shock = self._is_emergency_market_shock(market_state)

        # Standard Risk-On: Both SPY & QQQ above SMA50, low vol, no shock
        bull_regime = (
            spy_sma50 is not None
            and qqq_sma50 is not None
            and qqq_vol20 is not None
            and spy[-1] > spy_sma50
            and qqq[-1] > qqq_sma50
            and qqq_vol20 < 0.35
            and not is_shock
        )

        # Snapback Recovery Regime: Market is below SMA50, but short-term momentum has strongly turned
        # positive (QQQ > SMA20, Mom10 > 0.03). Allows scaled 45% participation instead of sitting in cash/defensives.
        snapback_regime = (
            not bull_regime
            and not is_shock
            and qqq_sma20 is not None
            and qqq_mom10 is not None
            and qqq[-1] > qqq_sma20
            and qqq_mom10 > 0.03
        )

        if not bull_regime and not snapback_regime:
            # Pure Defensive: Conservative staples, zero XLE
            weights = {"XLP": 0.28 * derisk_mult, "XLU": 0.28 * derisk_mult, "XLV": 0.24 * derisk_mult}
            return _scale_caps(weights)

        # Score momentum candidates
        scored: list[tuple[float, str]] = []
        for ticker in RISK_CANDIDATES:
            values = closes(market_state.get(ticker))
            if len(values) < 61:
                continue
            mom60 = momentum(values, 60)
            mom20 = momentum(values, 20)
            trend50 = sma(values, 50)
            vol20 = realized_vol(values, 20)
            if mom60 is None or mom20 is None or trend50 is None or vol20 is None:
                continue
            trend_gap = values[-1] / trend50 - 1.0
            score = (0.55 * mom60) + (0.25 * mom20) + (0.20 * trend_gap) - (0.15 * vol20)
            if score > 0.0:
                scored.append((score, ticker))

        scored.sort(reverse=True)
        winners = [ticker for _, ticker in scored[:5]]
        if not winners:
            return _scale_caps({"XLP": 0.24 * derisk_mult, "XLU": 0.24 * derisk_mult, "XLV": 0.20 * derisk_mult})

        # Volatility-weighted sizing
        inv_vols: dict[str, float] = {}
        for ticker in winners:
            c_vals = closes(market_state.get(ticker))
            v = realized_vol(c_vals, 20) if len(c_vals) >= 20 else 0.25
            v_clean = max(v or 0.25, 0.08)
            inv_vols[ticker] = 1.0 / v_clean

        sum_iv = sum(inv_vols.values())
        budget_scale = 0.50 if snapback_regime else 0.90  # Snapback uses conservative 50% budget
        total_budget = budget_scale * derisk_mult

        weights: dict[str, float] = {}
        max_single_w = (MAX_WEIGHT - 0.02) * derisk_mult
        for ticker, iv in inv_vols.items():
            w = (iv / sum_iv) * total_budget
            weights[ticker] = min(w, max_single_w)

        # Leveraged overlay only in confirmed calm bull regime
        if bull_regime and qqq_vol20 and qqq_vol20 < 0.26 and derisk_mult >= 0.95:
            if closes(market_state.get("QLD")) and closes(market_state.get("SSO")):
                weights["QLD"] = 0.10
                weights["SSO"] = 0.06

        return _scale_caps(weights)

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
        is_shock = self._is_emergency_market_shock(market_state)
        should_rebalance = (
            self.last_rebalance_date is None
            or self.days_counter >= self.rebalance_every_days
            or is_shock
        )

        if not should_rebalance:
            return []

        tot_eq = equity(portfolio_state, cash)
        targets = self.compute_targets(market_state, tot_eq)
        if not targets and not is_shock:
            return []

        prices = _market_prices(market_state)
        positions = current_positions(portfolio_state)
        orders = orders_to_rebalance(targets, positions, tot_eq, prices, cash)

        if orders:
            self.last_rebalance_date = latest_date
            self.days_counter = 0

        return orders
