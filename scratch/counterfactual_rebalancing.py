import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from preview import load_decide, _expand, beta, SLIP_LEVERAGED, SLIP_EQUITY, START_CASH, CONCENTRATION_CAP, _max_drawdown, _sharpe, _annualize
from agent import closes, sma, realized_vol, momentum, orders_to_rebalance, DEFENSIVE_WEIGHTS, RISK_CANDIDATES, MAX_WEIGHT, BETA_MULTIPLE, MAX_BETA_GROSS

raw_regimes = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())

class ParameterizedCadenceAgent:
    """Agent that runs E0 logic but with configurable cadence and optional triggers."""
    def __init__(
        self,
        cadence_days: int = 5,
        emergency_drop: float | None = None, # e.g. -0.03
        vol_trigger: float | None = None,   # e.g. 0.35
        exclude_xle: bool = False,
        sector_cap: float | None = None,    # e.g. 0.20
    ):
        self.cadence_days = cadence_days
        self.emergency_drop = emergency_drop
        self.vol_trigger = vol_trigger
        self.exclude_xle = exclude_xle
        self.sector_cap = sector_cap
        self.days_since_rebalance = 0

    def reset(self):
        self.days_since_rebalance = 0

    def decide(self, market_state: dict, portfolio_state: dict, cash: float) -> list[dict]:
        spy = closes(market_state.get("SPY"))
        qqq = closes(market_state.get("QQQ"))
        if len(spy) < 50 or len(qqq) < 50:
            return []

        spy_sma50 = sma(spy, 50)
        qqq_sma50 = sma(qqq, 50)
        qqq_vol20 = realized_vol(qqq, 20)

        # Emergency shock check
        emergency_fired = False
        if self.emergency_drop is not None and len(spy) >= 3:
            ret_2d = (spy[-1] / spy[-3]) - 1.0
            if ret_2d <= self.emergency_drop:
                emergency_fired = True

        vol_spike_fired = False
        if self.vol_trigger is not None and qqq_vol20 is not None:
            if qqq_vol20 >= self.vol_trigger:
                vol_spike_fired = True

        # Check cadence
        time_to_rebalance = (self.days_since_rebalance == 0) or (self.days_since_rebalance >= self.cadence_days) or emergency_fired or vol_spike_fired

        if not time_to_rebalance:
            self.days_since_rebalance += 1
            return []

        # Reset counter
        self.days_since_rebalance = 1

        # Determine regime
        risk_on = bool(
            spy_sma50 is not None
            and qqq_sma50 is not None
            and qqq_vol20 is not None
            and spy[-1] > spy_sma50
            and qqq[-1] > qqq_sma50
            and qqq_vol20 < 0.35
            and not emergency_fired
        )

        from agent import current_positions, equity, _scale_caps, _market_prices
        prices = _market_prices(market_state)
        cur_pos = current_positions(portfolio_state)
        tot_eq = equity(portfolio_state, cash)

        if risk_on:
            scores = {}
            for t in RISK_CANDIDATES:
                c = closes(market_state.get(t))
                if len(c) >= 50:
                    scores[t] = momentum(c, 20)
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
            weights = {t: 0.20 for t, _ in ranked}
        else:
            def_w = dict(DEFENSIVE_WEIGHTS)
            if self.exclude_xle:
                def_w.pop("XLE", None)
                # re-normalize
                tot = sum(def_w.values())
                weights = {t: w / tot for t, w in def_w.items()}
            else:
                weights = def_w

        if self.sector_cap is not None:
            weights = {t: min(w, self.sector_cap) for t, w in weights.items()}

        scaled = _scale_caps(weights)
        return orders_to_rebalance(scaled, cur_pos, tot_eq, prices, cash)


def evaluate_policy(agent_inst, regime_name: str) -> dict:
    regime = raw_regimes[regime_name]
    agent_inst.reset()
    bars = {t: _expand(rows) for t, rows in regime["bars"].items()}
    all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
    eval_dates = [d for d in all_dates if regime["eval_start"] <= d <= regime["eval_end"]]

    cash = START_CASH
    positions: dict[str, float] = {}
    avg_cost: dict[str, float] = {}
    equity_curve: list[float] = []
    trades = 0
    pending: list[dict] = []
    total_turnover = 0.0
    total_slippage_cost = 0.0

    def close_on(ticker: str, date: str):
        for b in bars.get(ticker, []):
            if b["ts"] == date:
                return b["close"]
        return None

    def open_on(ticker: str, date: str):
        for b in bars.get(ticker, []):
            if b["ts"] == date:
                return b["open"]
        return None

    for date in eval_dates:
        for o in pending:
            px = open_on(o["ticker"], date)
            if px is None:
                continue
            slip = SLIP_LEVERAGED if beta(o["ticker"]) > 1 else SLIP_EQUITY
            if o["side"] == "buy":
                fill = px * (1 + slip)
                qty = o["quantity"]
                cost = fill * qty
                if cost > cash:
                    qty = cash / fill if fill > 0 else 0
                    cost = fill * qty
                if qty <= 0:
                    continue
                held = positions.get(o["ticker"], 0.0)
                prev_cost = avg_cost.get(o["ticker"], 0.0) * held
                positions[o["ticker"]] = held + qty
                avg_cost[o["ticker"]] = (prev_cost + cost) / (held + qty)
                cash -= cost
                trades += 1
                total_turnover += cost
                total_slippage_cost += (px * slip) * qty
            else:
                held = positions.get(o["ticker"], 0.0)
                qty = min(o["quantity"], held)
                if qty <= 0:
                    continue
                fill = px * (1 - slip)
                cash += fill * qty
                positions[o["ticker"]] = held - qty
                trades += 1
                total_turnover += fill * qty
                total_slippage_cost += (px * slip) * qty

        pending = []
        positions = {t: q for t, q in positions.items() if q > 1e-9}
        prices = {t: close_on(t, date) for t in bars if close_on(t, date) is not None}
        pos_value = {t: positions.get(t, 0.0) * prices.get(t, 0.0) for t in positions}
        equity = max(cash + sum(pos_value.values()), 1e-9)
        equity_curve.append(equity)

        market_state = {t: [b for b in bars[t] if b["ts"] <= date] for t in bars}
        portfolio_state = {
            "cash": cash,
            "positions": [
                {"ticker": t, "quantity": q, "avg_cost": avg_cost.get(t, 0.0)}
                for t, q in positions.items() if q > 0
            ],
            "last_prices": prices,
        }
        orders = agent_inst.decide(market_state, portfolio_state, cash)
        for o in orders or []:
            if o["side"] in ("buy", "sell") and float(o["quantity"]) > 0 and o["ticker"] in bars:
                pending.append({"ticker": o["ticker"], "side": o["side"], "quantity": float(o["quantity"])})

    ret = equity_curve[-1] / START_CASH - 1.0 if equity_curve else 0.0
    mdd = _max_drawdown(equity_curve)
    sharpe = _sharpe(equity_curve)
    calmar = (_annualize(ret, len(equity_curve)) / mdd) if mdd > 1e-9 else 0.0

    return {
        "regime": regime_name,
        "ret": ret,
        "mdd": mdd,
        "sharpe": sharpe,
        "calmar": calmar,
        "trades": trades,
        "turnover": total_turnover,
        "slippage_cost": total_slippage_cost,
        "end_equity": equity_curve[-1],
    }

POLICIES = {
    "Baseline_Cadence_5": ParameterizedCadenceAgent(cadence_days=5),
    "Cadence_3": ParameterizedCadenceAgent(cadence_days=3),
    "Cadence_2": ParameterizedCadenceAgent(cadence_days=2),
    "Cadence_1_Daily": ParameterizedCadenceAgent(cadence_days=1),
    "FastExit_Drop_3pct": ParameterizedCadenceAgent(cadence_days=5, emergency_drop=-0.03),
    "FastExit_Drop_2pct": ParameterizedCadenceAgent(cadence_days=5, emergency_drop=-0.02),
    "VolTrigger_35": ParameterizedCadenceAgent(cadence_days=5, vol_trigger=0.35),
    "No_XLE_Cadence_5": ParameterizedCadenceAgent(cadence_days=5, exclude_xle=True),
    "SectorCap_20pct": ParameterizedCadenceAgent(cadence_days=5, sector_cap=0.20),
    "Integrated_FastExit_NoXLE": ParameterizedCadenceAgent(cadence_days=5, emergency_drop=-0.03, exclude_xle=True),
}

REGIMES = ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"]

print(f"{'Policy':<28} | {'Regime':<18} | {'Return (%)':>10} | {'MDD (%)':>8} | {'Sharpe':>7} | {'Trades':>6} | {'Turnover ($)':>12} | {'Slippage ($)':>12}")
print("-" * 115)

all_results = {}
for p_name, p_agent in POLICIES.items():
    all_results[p_name] = {}
    for r in REGIMES:
        res = evaluate_policy(p_agent, r)
        all_results[p_name][r] = res
        print(f"{p_name:<28} | {r:<18} | {res['ret']*100:9.2f}% | {res['mdd']*100:7.2f}% | {res['sharpe']:7.2f} | {res['trades']:6d} | ${res['turnover']:11.2f} | ${res['slippage_cost']:11.2f}")
