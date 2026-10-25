"""
Comprehensive evaluation of Candidates A through F across all 3 regimes.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
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
from typing import Any

# ==============================================================================
# CANDIDATE DEFINITIONS
# ==============================================================================

class CandidateA_AdaptiveRebalance:
    """Candidate A: Adaptive Rebalancing (5-day cadence with -3% shock exit)."""
    def __init__(self, shock_threshold: float = -0.03):
        self.shock_threshold = shock_threshold
        self.last_rebalance_date = None
        self.days_counter = 0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def _is_shock(self, market_state):
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3:
            return False
        return (spy_c[-1] / spy_c[-3] - 1.0) <= self.shock_threshold

    def compute_targets(self, market_state):
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

        scored = []
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
            sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
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
        weights = {}
        base_budget = 0.76 if overlay_on else 0.92
        per_w = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11
            weights["SSO"] = 0.07
        return _scale_caps(weights)

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        is_shk = self._is_shock(market_state)
        if not (self.last_rebalance_date is None or self.days_counter >= 5 or is_shk):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts and not is_shk: return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateB_EmergencyDeRisking:
    """Candidate B: Emergency De-Risking (Drawdown Budget Multiplier)."""
    def __init__(self, dd_threshold: float = 0.07):
        self.dd_threshold = dd_threshold
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def compute_targets(self, market_state, total_equity):
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

        scored = []
        for ticker in RISK_CANDIDATES:
            vals = closes(market_state.get(ticker))
            if len(vals) < 61: continue
            m60 = momentum(vals, 60)
            m20 = momentum(vals, 20)
            tr50 = sma(vals, 50)
            v20 = realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None: continue
            tg = vals[-1] / tr50 - 1.0
            sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
            if sc > 0: scored.append((sc, ticker))
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
        weights = {}
        base_budget = (0.76 if overlay_on else 0.92) * derisk_mult
        per_w = min((MAX_WEIGHT - 0.02) * derisk_mult, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11 * derisk_mult
            weights["SSO"] = 0.07 * derisk_mult
        return _scale_caps(weights)

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state, tot_eq)
        if not tgts: return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateC_SectorRiskBudgeting:
    """Candidate C: Sector Risk Budgeting (20% max single weight, dynamic XLE trend filter)."""
    def __init__(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def compute_targets(self, market_state):
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50: return {}
        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)
        risk_on = bool(
            spy_sma50 and qqq_sma50 and qqq_vol20
            and spy[-1] > spy_sma50 and qqq[-1] > qqq_sma50 and qqq_vol20 < 0.35
        )
        if not risk_on:
            # Dynamic check on defensive basket: only hold XLE if XLE > SMA50
            weights = {}
            for t, w in DEFENSIVE_WEIGHTS:
                c_vals = closes(market_state.get(t))
                if not c_vals: continue
                if t == "XLE":
                    xle_sma50 = sma(c_vals, 50)
                    if xle_sma50 and c_vals[-1] > xle_sma50:
                        weights[t] = w
                    # Else drop XLE and keep cash
                else:
                    weights[t] = w
            return _scale_caps(weights)

        scored = []
        for ticker in RISK_CANDIDATES:
            vals = closes(market_state.get(ticker))
            if len(vals) < 61: continue
            m60 = momentum(vals, 60)
            m20 = momentum(vals, 20)
            tr50 = sma(vals, 50)
            v20 = realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None: continue
            tg = vals[-1] / tr50 - 1.0
            sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
            if sc > 0: scored.append((sc, ticker))
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
        weights = {}
        base_budget = 0.76 if overlay_on else 0.92
        # Capped at 20% strictly (instead of 23%)
        per_w = min(0.20, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11
            weights["SSO"] = 0.07
        return _scale_caps(weights)

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts: return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateD_RecoveryParticipation:
    """Candidate D: Recovery Participation (Fast Re-Entry via QQQ > SMA20)."""
    def __init__(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def compute_targets(self, market_state):
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50: return {}
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

        scored = []
        for ticker in RISK_CANDIDATES:
            vals = closes(market_state.get(ticker))
            if len(vals) < 61: continue
            m60 = momentum(vals, 60)
            m20 = momentum(vals, 20)
            tr50 = sma(vals, 50)
            v20 = realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None: continue
            tg = vals[-1] / tr50 - 1.0
            sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
            if sc > 0: scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        if recovery_on:
            # Scaled 45% budget across top winners, no leveraged overlay
            weights = {t: 0.09 for t in winners}
            return _scale_caps(weights)

        qqq_mom20 = momentum(qqq, 20)
        overlay_on = bool(
            qqq_sma20 and qqq_sma50 and qqq_mom20
            and qqq_sma20 > qqq_sma50 and qqq_mom20 > 0.0 and qqq_vol20 < 0.28
            and closes(market_state.get("QLD")) and closes(market_state.get("SSO"))
        )
        weights = {}
        base_budget = 0.76 if overlay_on else 0.92
        per_w = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
        for t in winners:
            weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11
            weights["SSO"] = 0.07
        return _scale_caps(weights)

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state)
        if not tgts: return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders


class CandidateE_CostAwareRebalancing:
    """Candidate E: Cost-Aware Turnover Buffer (suppresses trades under 3% equity delta)."""
    def __init__(self, buffer_pct: float = 0.03):
        self.buffer_pct = buffer_pct
        self.last_rebalance_date = None
        self.days_counter = 0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        if not (self.last_rebalance_date is None or self.days_counter >= 5):
            return []
        tot_eq = equity(portfolio_state, cash)
        if tot_eq <= 0: return []

        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50: return []
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
            scored = []
            for ticker in RISK_CANDIDATES:
                vals = closes(market_state.get(ticker))
                if len(vals) < 61: continue
                m60 = momentum(vals, 60)
                m20 = momentum(vals, 20)
                tr50 = sma(vals, 50)
                v20 = realized_vol(vals, 20)
                if m60 is None or m20 is None or tr50 is None or v20 is None: continue
                tg = vals[-1] / tr50 - 1.0
                sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
                if sc > 0: scored.append((sc, ticker))
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
                weights = {}
                base_budget = 0.76 if overlay_on else 0.92
                per_w = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
                for t in winners: weights[t] = per_w
                if overlay_on:
                    weights["QLD"] = 0.11
                    weights["SSO"] = 0.07
                targets = _scale_caps(weights)

        # Buffer filter: if abs(target_w - current_w) < buffer_pct and target_w > 0, keep current_w
        positions = current_positions(portfolio_state)
        prices = _market_prices(market_state)
        filtered_targets = {}
        for t, tw in targets.items():
            curr_qty = positions.get(t, {}).get("quantity", 0.0)
            curr_val = curr_qty * prices.get(t, 0.0)
            curr_w = curr_val / tot_eq if tot_eq > 0 else 0.0
            if abs(tw - curr_w) < self.buffer_pct:
                filtered_targets[t] = curr_w  # No trade needed
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
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def reset(self):
        self.last_rebalance_date = None
        self.days_counter = 0
        self.peak_val = 0.0

    def _is_shock(self, market_state):
        spy_c = closes(market_state.get("SPY"))
        if len(spy_c) < 3: return False
        return (spy_c[-1] / spy_c[-3] - 1.0) <= self.shock_threshold

    def compute_targets(self, market_state, total_equity):
        self.peak_val = max(self.peak_val, total_equity)
        dd = (self.peak_val - total_equity) / self.peak_val if self.peak_val > 0 else 0.0
        derisk_mult = 1.0
        if dd >= self.dd_threshold:
            derisk_mult = max(0.40, 1.0 - (dd - self.dd_threshold) * 3.5)

        is_shk = self._is_shock(market_state)
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50: return {}
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
            # Defensive basket with dynamic XLE check
            weights = {}
            for t, w in DEFENSIVE_WEIGHTS:
                c_vals = closes(market_state.get(t))
                if not c_vals: continue
                if t == "XLE":
                    xle_sma50 = sma(c_vals, 50)
                    if xle_sma50 and c_vals[-1] > xle_sma50:
                        weights[t] = w * derisk_mult
                else:
                    weights[t] = w * derisk_mult
            return _scale_caps(weights)

        scored = []
        for ticker in RISK_CANDIDATES:
            vals = closes(market_state.get(ticker))
            if len(vals) < 61: continue
            m60 = momentum(vals, 60)
            m20 = momentum(vals, 20)
            tr50 = sma(vals, 50)
            v20 = realized_vol(vals, 20)
            if m60 is None or m20 is None or tr50 is None or v20 is None: continue
            tg = vals[-1] / tr50 - 1.0
            sc = 0.55*m60 + 0.25*m20 + 0.20*tg - 0.15*v20
            if sc > 0: scored.append((sc, ticker))
        scored.sort(reverse=True)
        winners = [t for _, t in scored[:5]]
        if not winners:
            return _scale_caps({t: w * derisk_mult for t, w in DEFENSIVE_WEIGHTS if closes(market_state.get(t))})

        if recovery_on:
            # Scaled 45% budget in recovery mode
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
        for t in winners: weights[t] = per_w
        if overlay_on:
            weights["QLD"] = 0.11 * derisk_mult
            weights["SSO"] = 0.07 * derisk_mult
        return _scale_caps(weights)

    def decide(self, market_state, portfolio_state, cash):
        if not market_state: return []
        ld = _latest_bar_date(market_state)
        if not ld: return []
        self.days_counter += 1
        is_shk = self._is_shock(market_state)
        if not (self.last_rebalance_date is None or self.days_counter >= 5 or is_shk):
            return []
        tot_eq = equity(portfolio_state, cash)
        tgts = self.compute_targets(market_state, tot_eq)
        if not tgts and not is_shk: return []
        orders = orders_to_rebalance(tgts, current_positions(portfolio_state), tot_eq, _market_prices(market_state), cash)
        if orders:
            self.last_rebalance_date = ld
            self.days_counter = 0
        return orders

# ==============================================================================
# EXECUTION & BENCHMARKING
# ==============================================================================

def compute_sortino(equity_curve: list[float]) -> float:
    if len(equity_curve) < 2:
        return 0.0
    rets = [equity_curve[i] / equity_curve[i - 1] - 1.0 for i in range(1, len(equity_curve))]
    mean_ret = sum(rets) / len(rets)
    downside_rets = [r for r in rets if r < 0.0]
    if not downside_rets:
        return 0.0
    downside_var = sum(r ** 2 for r in downside_rets) / len(rets)
    downside_std = (downside_var ** 0.5)
    return (mean_ret / downside_std * (252.0 ** 0.5)) if downside_std > 1e-9 else 0.0

candidates = {
    "Baseline E0": "agent.py",
    "Candidate A (Adaptive Rebal)": CandidateA_AdaptiveRebalance(),
    "Candidate B (Emergency DeRisk)": CandidateB_EmergencyDeRisking(),
    "Candidate C (Sector Risk Budget)": CandidateC_SectorRiskBudgeting(),
    "Candidate D (Recovery Partic)": CandidateD_RecoveryParticipation(),
    "Candidate E (Cost-Aware Buffer)": CandidateE_CostAwareRebalancing(),
    "Candidate F (Integrated Risk)": CandidateF_IntegratedRiskControl(),
}

regimes = ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]

print(f"{'Candidate':<32} | {'Regime':<18} | {'Return':>8} | {'MDD':>7} | {'Sharpe':>7} | {'Sortino':>7} | {'Calmar':>7} | {'Trades':>6}")
print("=" * 105)

for c_name, cand in candidates.items():
    for r in regimes:
        prov = StaticRegimeProvider("sample_regimes.json.gz", r)
        if isinstance(cand, str):
            engine = ReplayEngine(cand, prov)
        else:
            cand.reset()
            engine = ReplayEngine(cand.decide, prov)
        res = engine.run_replay()
        m = res["metrics"]
        sortino = compute_sortino(res["equity_curve"])
        print(f"{c_name:<32} | {r:<18} | {m['ret']*100:7.2f}% | {m['mdd']*100:6.2f}% | {m['sharpe']:7.2f} | {sortino:7.2f} | {m['calmar']:7.2f} | {m['trades']:6d}")
    print("-" * 105)
