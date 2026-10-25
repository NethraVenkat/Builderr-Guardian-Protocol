"""Stage B2-C Integrated Research Candidate: Candidate A + E Combined.

Combines:
  - Candidate A: Adaptive Rebalancing (5-day cadence, -3.0% 2-day SPY shock emergency exit)
  - Candidate E: Cost-Aware Buffer (suppresses normal rebalance trades under 3% equity delta)

CRITICAL INVARIANTS:
  1. A cost-saving buffer must NEVER override emergency risk exits, full liquidations, or risk limits.
  2. Full liquidations (target_weight == 0.0) bypass the buffer completely to avoid dust positions.
  3. Emergency market shock exits bypass the buffer completely.
  4. Normal scheduled rebalances apply the buffer to avoid micro-trade slippage and turnover churn.
  5. Strictly causal: uses only market data up to session T close; orders fill at session T+1 open.
"""
from __future__ import annotations

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


class CandidateAE_Combined:
    """Stage B2-C Candidate: Adaptive Emergency Exit + Cost-Aware Rebalancing Buffer."""

    def __init__(
        self,
        rebalance_every_days: int = 5,
        shock_threshold: float = -0.030,     # -3.0% 2-day SPY drop triggers emergency exit
        buffer_threshold: float = 0.030,    # 3.0% equity delta buffer for normal rebalances
        enable_adaptive_exit: bool = True,
        enable_cost_buffer: bool = True,
    ):
        self.rebalance_every_days = rebalance_every_days
        self.shock_threshold = shock_threshold
        self.buffer_threshold = buffer_threshold
        self.enable_adaptive_exit = enable_adaptive_exit
        self.enable_cost_buffer = enable_cost_buffer

        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0
        self.emergency_exit_count: int = 0
        self.buffer_suppressed_count: int = 0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0
        self.emergency_exit_count = 0
        self.buffer_suppressed_count = 0

    def _is_market_shock(self, market_state: dict[str, list[dict[str, Any]]]) -> bool:
        """Causal detection of severe 2-day market drop."""
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        ret_2d = (spy_c[-1] / spy_c[-3]) - 1.0
        return ret_2d <= self.shock_threshold

    def compute_raw_targets(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        is_shock: bool,
    ) -> dict[str, float]:
        """Compute target weights matching E0 contract rules."""
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}

        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)

        risk_on = bool(
            spy_sma50 is not None
            and qqq_sma50 is not None
            and qqq_vol20 is not None
            and spy[-1] > spy_sma50
            and qqq[-1] > qqq_sma50
            and qqq_vol20 < 0.35
            and not (self.enable_adaptive_exit and is_shock)
        )

        if not risk_on:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        scored: list[tuple[float, str]] = []
        for ticker in RISK_CANDIDATES:
            vals = closes(market_state.get(ticker))
            if len(vals) < 61:
                continue
            m60 = momentum(vals, 60)
            m20 = momentum(vals, 20)
            tr50 = sma(vals, 50)
            v20 = realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None:
                continue
            tg = vals[-1] / tr50 - 1.0
            sc = (0.55 * m60) + (0.25 * m20) + (0.20 * tg) - (0.15 * v20)
            if sc > 0.0:
                scored.append((sc, ticker))

        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

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
        )

        weights: dict[str, float] = {}
        base_budget = 0.76 if overlay_on else 0.92
        per_w = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11
            weights["SSO"] = 0.07

        return _scale_caps(weights)

    def apply_cost_buffer(
        self,
        targets: dict[str, float],
        positions: dict[str, dict[str, float]],
        total_equity: float,
        prices: dict[str, float],
        is_shock: bool,
    ) -> dict[str, float]:
        """Apply cost-aware turnover buffer without overriding safety or liquidations.
        
        Rules:
          1. If is_shock: return raw targets immediately (NO trade suppression on panic).
          2. If target weight is 0.0: return 0.0 (NO dust position retention).
          3. If abs(target - current) < buffer_threshold: maintain current weight.
          4. Otherwise: trade to new target weight.
        """
        if not self.enable_cost_buffer or is_shock or total_equity <= 0:
            return targets

        filtered_targets: dict[str, float] = {}
        all_tickers = set(targets.keys()) | set(positions.keys())

        for t in all_tickers:
            tgt_w = targets.get(t, 0.0)
            curr_qty = positions.get(t, {}).get("quantity", 0.0)
            curr_px = prices.get(t, 0.0)
            curr_w = (curr_qty * curr_px) / total_equity if total_equity > 0 else 0.0

            # Rule 2: Full liquidation must always execute completely
            if tgt_w <= 0.0001:
                if curr_qty > 0:
                    filtered_targets[t] = 0.0
                continue

            # Rule 3: If target is positive and within buffer of current weight, keep current
            delta_w = abs(tgt_w - curr_w)
            if delta_w < self.buffer_threshold and curr_w > 0.0001:
                filtered_targets[t] = curr_w
                self.buffer_suppressed_count += 1
            else:
                filtered_targets[t] = tgt_w

        return _scale_caps(filtered_targets)

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
        is_shock = self._is_market_shock(market_state) if self.enable_adaptive_exit else False

        should_rebalance = (
            self.last_rebalance_date is None
            or self.days_counter >= self.rebalance_every_days
            or (self.enable_adaptive_exit and is_shock)
        )

        if not should_rebalance:
            return []

        tot_eq = equity(portfolio_state, cash)
        raw_targets = self.compute_raw_targets(market_state, is_shock)
        if not raw_targets and not is_shock:
            return []

        positions = current_positions(portfolio_state)
        prices = _market_prices(market_state)

        final_targets = self.apply_cost_buffer(raw_targets, positions, tot_eq, prices, is_shock)
        orders = orders_to_rebalance(final_targets, positions, tot_eq, prices, cash)

        if orders:
            self.last_rebalance_date = latest_date
            self.days_counter = 0
            if is_shock and self.enable_adaptive_exit:
                self.emergency_exit_count += 1

        return orders
