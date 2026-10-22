"""Stage V11 Registered Research Strategy Candidates (Candidates A through F).

Signature matches official competition contract:
  decide(market_state: dict, portfolio_state: dict, cash: float) -> list[dict]
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


class CandidateA_AdaptiveRebalance:
    """Candidate A: Adaptive Rebalancing (5-day cadence with -3% shock exit)."""

    def __init__(self, shock_threshold: float = -0.03):
        self.shock_threshold = shock_threshold
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0

    def _is_shock(self, market_state: dict[str, list[dict[str, Any]]]) -> bool:
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        return (spy_c[-1] / spy_c[-3] - 1.0) <= self.shock_threshold

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)
        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
            and not self._is_shock(market_state)
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
            sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
            if sc > 0:
                scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        qqq_sma20 = sma(qqq, 20)
        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
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

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        if not market_state:
            return []
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        is_shk = self._is_shock(market_state)
        if not (self.last_rebalance_date is None or self.days_counter >= 5 or is_shk):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts and not is_shk:
            return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateB_EmergencyDeRisking:
    """Candidate B: Emergency De-Risking (Drawdown Budget Multiplier)."""

    def __init__(self, dd_threshold: float = 0.07):
        self.dd_threshold = dd_threshold
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0
        self.peak_val: float = 0.0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]], total_equity: float) -> dict[str, float]:
        self.peak_val = max(self.peak_val, total_equity)
        dd = (self.peak_val - total_equity) / self.peak_val if self.peak_val > 0 else 0.0
        derisk_mult = 1.0
        if dd >= self.dd_threshold:
            derisk_mult = max(0.35, 1.0 - (dd - self.dd_threshold) * 4.0)

        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)
        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
        )
        if not risk_on:
            return _scale_caps({t: w * derisk_mult for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

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
            sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
            if sc > 0:
                scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w * derisk_mult for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        qqq_sma20 = sma(qqq, 20)
        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
            and derisk_mult >= 0.90
        )
        weights: dict[str, float] = {}
        base_budget = (0.76 if overlay_on else 0.92) * derisk_mult
        per_w = min((MAX_WEIGHT - 0.02) * derisk_mult, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
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
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state, tot_eq)
        if not tgts:
            return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateC_SectorRiskBudgeting:
    """Candidate C: Sector Risk Budgeting (20% max single weight, dynamic XLE trend filter)."""

    def __init__(self) -> None:
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)
        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
        )
        if not risk_on:
            weights: dict[str, float] = {}
            for t, w in DEFENSIVE_WEIGHTS:
                c_vals = closes(market_state.get(t))
                if not c_vals:
                    continue
                if t == "XLE":
                    xle_sma50 = sma(c_vals, 50)
                    if xle_sma50 and c_vals[-1] > xle_sma50:
                        weights[t] = w
                else:
                    weights[t] = w
            return _scale_caps(weights)

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
            sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
            if sc > 0:
                scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        qqq_sma20 = sma(qqq, 20)
        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
        )
        weights: dict[str, float] = {}
        base_budget = 0.76 if overlay_on else 0.92
        per_w = min(0.20, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11
            weights["SSO"] = 0.07
        return _scale_caps(weights)

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        if not market_state:
            return []
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts:
            return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateD_RecoveryParticipation:
    """Candidate D: Recovery Participation (Fast Re-Entry via QQQ > SMA20)."""

    def __init__(self) -> None:
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_sma20 = sma(qqq, 20)
        qqq_mom10 = momentum(qqq, 10)
        qqq_vol20 = realized_vol(qqq, 20)

        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
        )
        recovery_on = bool(
            not risk_on
            and qqq_sma20 and qqq_mom10
            and qqq[-1] > qqq_sma20 and qqq_mom10 > 0.02
        )

        if not risk_on and not recovery_on:
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
            sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
            if sc > 0:
                scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        if recovery_on:
            weights = {t: 0.09 for t in winners}
            return _scale_caps(weights)

        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
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

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        if not market_state:
            return []
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts:
            return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateE_CostAwareRebalancing:
    """Candidate E: Cost-Aware Turnover Buffer (suppresses trades under 3% equity delta)."""

    def __init__(self, buffer_pct: float = 0.03):
        self.buffer_pct = buffer_pct
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0

    def decide(
        self,
        market_state: dict[str, list[dict[str, Any]]],
        portfolio_state: dict[str, Any],
        cash: float,
    ) -> list[dict[str, Any]]:
        if not market_state:
            return []
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        if tot_eq <= 0:
            return []

        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)
        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
        )
        if not risk_on:
            targets = _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})
        else:
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
                sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
                if sc > 0:
                    scored.append((sc, ticker))
            scored.sort(reverse=True)
            winners = [t for _, t in scored[:5]]
            if not winners:
                targets = _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})
            else:
                qqq_sma20 = sma(qqq, 20)
                qqq_mom20 = momentum(qqq, 20)
                overlay_on = bool(
                    qqq_sma20 and qqq_sma50 and qqq_mom20
                    and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
                    and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
                )
                weights: dict[str, float] = {}
                base_budget = 0.76 if overlay_on else 0.92
                per_w = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
                for t in winners:
                    weights[t] = per_w
                if overlay_on:
                    weights["QLD"] = 0.11
                    weights["SSO"] = 0.07
                targets = _scale_caps(weights)

        positions = current_positions(portfolio_state)
        prices = _market_prices(market_state)
        filtered_targets: dict[str, float] = {}
        for t, tw in targets.items():
            curr_qty = positions.get(t, {}).get("quantity", 0.0)
            curr_val = curr_qty * prices.get(t, 0.0)
            curr_w = curr_val / tot_eq if tot_eq > 0 else 0.0
            if abs(tw - curr_w) < self.buffer_pct:
                filtered_targets[t] = curr_w
            else:
                filtered_targets[t] = tw

        orders = orders_to_rebalance(filtered_targets, positions, tot_eq, prices, cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateF_IntegratedRiskControl:
    """Candidate F: Integrated Risk Control (Shock Exit + Dynamic XLE + DD Multiplier + Recovery Participation)."""

    def __init__(self, shock_threshold: float = -0.03, dd_threshold: float = 0.07):
        self.shock_threshold = shock_threshold
        self.dd_threshold = dd_threshold
        self.last_rebalance_date: str | None = None
        self.days_counter: int = 0
        self.peak_val: float = 0.0

    def reset(self) -> None:
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def _is_shock(self, market_state: dict[str, list[dict[str, Any]]]) -> bool:
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        return (spy_c[-1] / spy_c[-3] - 1.0) <= self.shock_threshold

    def compute_targets(self, market_state: dict[str, list[dict[str, Any]]], total_equity: float) -> dict[str, float]:
        self.peak_val = max(self.peak_val, total_equity)
        dd = (self.peak_val - total_equity) / self.peak_val if self.peak_val > 0 else 0.0
        derisk_mult = 1.0
        if dd >= self.dd_threshold:
            derisk_mult = max(0.40, 1.0 - (dd - self.dd_threshold) * 3.5)

        is_shk = self._is_shock(market_state)
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_sma20 = sma(qqq, 20)
        qqq_mom10 = momentum(qqq, 10)
        qqq_vol20 = realized_vol(qqq, 20)

        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
            and not is_shk
        )
        recovery_on = bool(
            not risk_on and not is_shk
            and qqq_sma20 and qqq_mom10
            and qqq[-1] > qqq_sma20 and qqq_mom10 > 0.02
        )

        if not risk_on and not recovery_on:
            weights: dict[str, float] = {}
            for t, w in DEFENSIVE_WEIGHTS:
                c_vals = closes(market_state.get(t))
                if not c_vals:
                    continue
                if t == "XLE":
                    xle_sma50 = sma(c_vals, 50)
                    if xle_sma50 and c_vals[-1] > xle_sma50:
                        weights[t] = w * derisk_mult
                else:
                    weights[t] = w * derisk_mult
            return _scale_caps(weights)

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
            sc = 0.55 * m60 + 0.25 * m20 + 0.20 * tg - 0.15 * v20
            if sc > 0:
                scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w * derisk_mult for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        if recovery_on:
            rec_budget = 0.45 * derisk_mult
            per_w = rec_budget / len(winners)
            return _scale_caps({t: per_w for t in winners})

        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
            and derisk_mult >= 0.90
        )
        weights = {}
        base_budget = (0.76 if overlay_on else 0.92) * derisk_mult
        per_w = min((MAX_WEIGHT - 0.02) * derisk_mult, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
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
        ld = _latest_bar_date(market_state)
        if not ld:
            return []
        self.days_counter += 1
        is_shk = self._is_shock(market_state)
        if not (self.last_rebalance_date is None or self.days_counter >= 5 or is_shk):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state, tot_eq)
        if not tgts and not is_shk:
            return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders
