"""
Stage B2-N: Authentic Tiingo Tier 2 (2020-2021) Four-Way Quantitative Backtest.
Evaluates:
  1. Frozen E0 Production Strategy (agent.decide)
  2. Candidate A: Adaptive Rebalancing Shock Exit (CandidateA_AdaptiveRebalance)
  3. Candidate E: Cost-Aware Turnover Buffer (CandidateE_CostAwareRebalancing)
  4. Candidate A+E: Combined Strategy (CandidateAE_Combined)

Under Option B Causal Price Semantics across both:
  - Primary Preregistered Design: Fresh $100,000 portfolio on 2020-01-02 after warm-up.
  - Secondary Sensitivity Design: Continuous carry-forward from Tier 1 terminal holdings.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
import sys
import time
from typing import Any

# Ensure research package is resolvable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import agent
from research.engine.accounting import (
    PortfolioState,
    calculate_metrics,
)
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
    compute_business_day_settlement,
)
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import TiingoHistoricalProvider
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateE_CostAwareRebalancing,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined

logger = logging.getLogger("tier2_backtest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"
PRIMARY_RESULTS_FILE = Path("research/manifests") / "tier2_four_way_results.json"
SENSITIVITY_RESULTS_FILE = Path("research/manifests") / "tier2_carryforward_sensitivity_results.json"
HOLDINGS_FILE = Path("research/manifests") / "tier2_terminal_holdings.json"

TIER2_START = "2020-01-01"
TIER2_END = "2021-12-31"
WARMUP_START = "2019-09-01"


def compute_extended_metrics(
    equity_curve: list[float],
    timeline: list[str],
    trades: int,
    turnover: float,
    slippage: float,
    dividends: float,
    terminal_portfolio: PortfolioState,
    today_closes: dict[str, float],
    errors: int = 0,
) -> dict[str, Any]:
    """Compute institutional quantitative performance metrics with drawdown dates and Sortino."""
    base = calculate_metrics(equity_curve, trades=trades, errors=errors)
    start_nav = equity_curve[0] if equity_curve else 100_000.0
    end_nav = equity_curve[-1] if equity_curve else 100_000.0
    tot_ret = (end_nav / start_nav) - 1.0

    # Daily returns
    rets = [equity_curve[i] / equity_curve[i - 1] - 1.0 for i in range(1, len(equity_curve))]
    n = len(rets)

    # Sortino ratio
    downside_rets = [r for r in rets if r < 0.0]
    downside_var = sum(r ** 2 for r in downside_rets) / (n - 1) if n > 1 and downside_rets else 0.0
    downside_dev = math.sqrt(downside_var) if downside_var > 0 else 0.0
    mean_ret = sum(rets) / n if n > 0 else 0.0
    sortino = (mean_ret / downside_dev * math.sqrt(252.0)) if downside_dev > 1e-9 else 0.0

    # Annualized volatility
    var = sum((r - mean_ret) ** 2 for r in rets) / (n - 1) if n > 1 else 0.0
    ann_vol = math.sqrt(var * 252.0) if var > 0 else 0.0

    # Drawdown peak and trough dates
    peak = equity_curve[0] if equity_curve else 0.0
    peak_date = timeline[0] if timeline else ""
    max_dd = 0.0
    max_dd_peak_date = peak_date
    max_dd_trough_date = peak_date

    curr_peak_date = peak_date
    for i, val in enumerate(equity_curve):
        dt = timeline[i] if i < len(timeline) else ""
        if val > peak:
            peak = val
            curr_peak_date = dt
        dd = (peak - val) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
            max_dd_peak_date = curr_peak_date
            max_dd_trough_date = dt

    # Worst daily return
    worst_day_ret = min(rets) if rets else 0.0
    worst_day_idx = rets.index(worst_day_ret) + 1 if rets else 0
    worst_day_date = timeline[worst_day_idx] if worst_day_idx < len(timeline) else ""

    # Concentration and terminal HHI
    pos_values = {t: q * today_closes.get(t, 0.0) for t, q in terminal_portfolio.positions.items() if q > 0}
    tot_pos_val = sum(pos_values.values())
    tot_val = tot_pos_val + terminal_portfolio.cash
    weights = {t: v / tot_val for t, v in pos_values.items()} if tot_val > 0 else {}
    hhi = sum((w * 100.0) ** 2 for w in weights.values()) if weights else 0.0

    cagr = ((end_nav / start_nav) ** (252.0 / len(equity_curve)) - 1.0) if len(equity_curve) > 0 else 0.0

    return {
        "starting_nav": round(start_nav, 2),
        "ending_nav": round(end_nav, 2),
        "total_net_return_pct": round(tot_ret * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "sharpe_ratio": round(base["sharpe"], 4),
        "sortino_ratio": round(sortino, 4),
        "annualized_volatility_pct": round(ann_vol * 100.0, 2),
        "max_drawdown_pct": round(max_dd * 100.0, 2),
        "max_drawdown_peak_date": max_dd_peak_date,
        "max_drawdown_trough_date": max_dd_trough_date,
        "worst_day_return_pct": round(worst_day_ret * 100.0, 2),
        "worst_day_date": worst_day_date,
        "trades": trades,
        "annualized_turnover": round(turnover / (len(equity_curve) / 252.0) if len(equity_curve) > 0 else 0.0, 2),
        "total_slippage_cost": round(slippage, 2),
        "total_dividends_credited": round(dividends, 2),
        "terminal_cash": round(terminal_portfolio.cash, 2),
        "terminal_hhi": round(hhi, 2),
        "terminal_positions_count": len(pos_values),
        "days": len(equity_curve),
        "errors": errors,
    }


def build_clean_corp_registry(preloaded_bars: dict[str, list[dict[str, Any]]]) -> CorporateActionRegistry:
    """Build a completely fresh, isolated CorporateActionRegistry for a strategy run."""
    corp_registry = CorporateActionRegistry(payment_date_policy=PaymentDatePolicy.IMPUTE_BUSINESS_DAYS_10)
    for sym, bars in preloaded_bars.items():
        for b in bars:
            div_val = float(b.get("div_cash", 0.0))
            if div_val > 0.0:
                ex = b["ts"]
                pay = compute_business_day_settlement(ex, 10)
                corp_registry.register_dividend(ex_date=ex, ticker=sym, amount_per_share=div_val, payment_date=pay)
            split_val = float(b.get("split_factor", 1.0))
            if split_val != 1.0:
                corp_registry.register_split(ex_date=b["ts"], ticker=sym, split_ratio=split_val)
    return corp_registry


def run_tier2_backtest() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"Cache file {CACHE_FILE} not found. Run acquire_tier2_tiingo.py first.")

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        preloaded_bars = json.load(f)

    symbols = list(preloaded_bars.keys())
    logger.info(f"Loaded {len(symbols)} authentic assets from {CACHE_FILE}.")

    # Build provider
    provider = TiingoHistoricalProvider(
        symbols=symbols,
        start_date=TIER2_START,
        end_date=TIER2_END,
        warmup_start_date=WARMUP_START,
        preloaded_bars=preloaded_bars,
    )

    timeline = provider.get_timeline(TIER2_START, TIER2_END)
    logger.info(f"Tier 2 timeline: {len(timeline)} sessions ({timeline[0]} to {timeline[-1]}).")

    cand_a = CandidateA_AdaptiveRebalance()
    cand_e = CandidateE_CostAwareRebalancing()
    cand_ae = CandidateAE_Combined()

    strategies = [
        ("Frozen E0", agent.decide),
        ("Candidate A", cand_a.decide),
        ("Candidate E", cand_e.decide),
        ("Candidate A+E", cand_ae.decide),
    ]

    # Get final closing prices on 2021-12-31 for terminal valuation
    final_closes = {}
    for sym, bars in preloaded_bars.items():
        if bars:
            t2_bars = [b for b in bars if b["ts"] <= TIER2_END]
            if t2_bars:
                final_closes[sym] = t2_bars[-1]["close"]

    # ==========================================
    # 1. PRIMARY DESIGN: Fresh Portfolio $100k
    # ==========================================
    primary_results = {}
    terminal_holdings_data = {}

    logger.info("Executing PRIMARY DESIGN: Fresh $100k Portfolio Initialization...")
    for name, dec_fn in strategies:
        t0 = time.perf_counter()
        engine = ReplayEngine(
            agent_path_or_fn=dec_fn,
            provider=provider,
            corporate_actions=build_clean_corp_registry(preloaded_bars),
            start_cash=100_000.0,
            commission_bps=0.0,
            price_semantics="causal_production",
        )
        res = engine.run_replay(eval_start=TIER2_START, eval_end=TIER2_END, record_traces=True)
        dur = time.perf_counter() - t0

        port = engine.last_portfolio
        metrics = compute_extended_metrics(
            equity_curve=res["equity_curve"],
            timeline=timeline,
            trades=res["total_trades"],
            turnover=res["turnover"],
            slippage=res["slippage_cost"],
            dividends=port.total_dividends_credited,
            terminal_portfolio=port,
            today_closes=final_closes,
            errors=0 if res["compliance"]["no_errors"] else 1,
        )

        primary_results[name] = {
            "metrics": metrics,
            "equity_curve": res["equity_curve"],
            "execution_duration_seconds": round(dur, 2),
            "trace_sha256": res["trace_sha256"],
            "compliance": res["compliance"],
        }

        # Terminal holdings breakdown
        pos_breakdown = []
        tot_val = metrics["ending_nav"]
        for sym, qty in sorted(port.positions.items()):
            if qty > 0:
                raw_c = final_closes.get(sym, 0.0)
                mkt_val = qty * raw_c
                w = mkt_val / tot_val if tot_val > 0 else 0.0
                pos_breakdown.append({
                    "ticker": sym,
                    "shares": round(qty, 4),
                    "close_price": round(raw_c, 2),
                    "market_value": round(mkt_val, 2),
                    "weight_pct": round(w * 100.0, 2),
                })

        terminal_holdings_data[name] = {
            "terminal_date": timeline[-1],
            "terminal_nav": metrics["ending_nav"],
            "cash": round(port.cash, 2),
            "cash_weight_pct": round(port.cash / tot_val * 100.0, 2) if tot_val > 0 else 0.0,
            "positions": pos_breakdown,
            "active_positions_count": len(pos_breakdown),
            "terminal_hhi": metrics["terminal_hhi"],
        }

        logger.info(
            f"PRIMARY {name}: Ending NAV=${metrics['ending_nav']:,.2f}, "
            f"CAGR={metrics['cagr_pct']}%, MaxDD={metrics['max_drawdown_pct']}%, "
            f"Sharpe={metrics['sharpe_ratio']}, Trades={metrics['trades']} in {dur:.2f}s."
        )

        # Save primary results
        PRIMARY_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PRIMARY_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(primary_results, f, indent=2)
        logger.info(f"Wrote primary four-way results to {PRIMARY_RESULTS_FILE}.")

        with open(HOLDINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(terminal_holdings_data, f, indent=2)
        logger.info(f"Wrote terminal holdings to {HOLDINGS_FILE}.")

    # ====================================================
    # 2. SECONDARY DESIGN: Continuous Carry-Forward
    # ====================================================
    logger.info("Executing SECONDARY DESIGN: Continuous Carry-Forward Sensitivity...")
    # Load Tier 1 terminal portfolios
    tier1_holdings_path = Path("research/manifests") / "tier1_terminal_holdings_v22.json"
    sensitivity_results = {}

    if tier1_holdings_path.exists():
        with open(tier1_holdings_path, "r", encoding="utf-8") as f:
            t1_holdings_manifest = json.load(f)

        for name, dec_fn in strategies:
            t1_strat = t1_holdings_manifest.get(name, {})
            init_cash = float(t1_strat.get("cash", 100_000.0))
            init_pos = {
                (p.get("symbol") or p.get("ticker")): float(p["shares"])
                for p in t1_strat.get("positions", [])
            }
            init_avg_cost = {
                (p.get("symbol") or p.get("ticker")): float(p.get("raw_price") or p.get("close_price", 0.0))
                for p in t1_strat.get("positions", [])
            }
            start_capital = init_cash + sum(q * init_avg_cost.get(t, 0.0) for t, q in init_pos.items())

            init_port = PortfolioState(
                cash=init_cash,
                start_cash=start_capital,
                positions=init_pos,
                avg_cost=init_avg_cost,
            )

            t0 = time.perf_counter()
            engine = ReplayEngine(
                agent_path_or_fn=dec_fn,
                provider=provider,
                corporate_actions=build_clean_corp_registry(preloaded_bars),
                commission_bps=0.0,
                price_semantics="causal_production",
                initial_portfolio=init_port,
            )
            res = engine.run_replay(eval_start=TIER2_START, eval_end=TIER2_END, record_traces=True)
            dur = time.perf_counter() - t0

            port = engine.last_portfolio
            metrics = compute_extended_metrics(
                equity_curve=res["equity_curve"],
                timeline=timeline,
                trades=res["total_trades"],
                turnover=res["turnover"],
                slippage=res["slippage_cost"],
                dividends=port.total_dividends_credited,
                terminal_portfolio=port,
                today_closes=final_closes,
                errors=0 if res["compliance"]["no_errors"] else 1,
            )

            sensitivity_results[name] = {
                "initial_tier1_nav": round(start_capital, 2),
                "metrics": metrics,
                "equity_curve": res["equity_curve"],
                "execution_duration_seconds": round(dur, 2),
                "trace_sha256": res["trace_sha256"],
                "compliance": res["compliance"],
            }
            logger.info(
                f"SENSITIVITY {name}: Ending NAV=${metrics['ending_nav']:,.2f}, "
                f"CAGR={metrics['cagr_pct']}%, MaxDD={metrics['max_drawdown_pct']}%, "
                f"Sharpe={metrics['sharpe_ratio']}, Trades={metrics['trades']} in {dur:.2f}s."
            )

        with open(SENSITIVITY_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(sensitivity_results, f, indent=2)
        logger.info(f"Wrote continuous carry-forward sensitivity results to {SENSITIVITY_RESULTS_FILE}.")

    return {
        "primary": primary_results,
        "sensitivity": sensitivity_results,
    }


if __name__ == "__main__":
    run_tier2_backtest()
