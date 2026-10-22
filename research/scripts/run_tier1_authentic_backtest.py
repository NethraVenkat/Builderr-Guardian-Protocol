"""
Stage B2-I: Authentic Tiingo Tier 1 (2015-2019) Four-Way Quantitative Backtest.
Evaluates:
  1. Frozen E0 Production Strategy (agent.decide)
  2. Candidate A: Adaptive Rebalancing Shock Exit (CandidateA_AdaptiveRebalance)
  3. Candidate E: Cost-Aware Turnover Buffer (CandidateE_CostAwareRebalancing)
  4. Candidate A+E: Combined Strategy (CandidateAE_Combined)
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import agent
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
    compute_business_day_settlement,
)
from research.engine.provider import MarketDataProvider
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import TiingoHistoricalProvider
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateE_CostAwareRebalancing,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined

logger = logging.getLogger("tier1_backtest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CACHE_FILE = Path("tiingo_cache") / "tier1_bars.json"
RESULTS_FILE = Path("research/manifests") / "tier1_four_way_results.json"


def run_four_way_backtest() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"Cache file {CACHE_FILE} not found. Run acquire_tier1_tiingo.py first.")

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        preloaded_bars = json.load(f)

    symbols = list(preloaded_bars.keys())
    logger.info(f"Loaded {len(symbols)} authentic assets from {CACHE_FILE}.")

    # Build Corporate Actions Registry
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

    # Build provider
    provider = TiingoHistoricalProvider(
        symbols=symbols,
        start_date="2015-01-01",
        end_date="2019-12-31",
        warmup_start_date="2014-09-01",
        preloaded_bars=preloaded_bars,
    )

    timeline = provider.get_timeline("2015-01-01", "2019-12-31")
    logger.info(f"Tier 1 timeline: {len(timeline)} sessions ({timeline[0]} to {timeline[-1]}).")

    cand_a = CandidateA_AdaptiveRebalance()
    cand_e = CandidateE_CostAwareRebalancing()
    cand_ae = CandidateAE_Combined()

    strategies = [
        ("Frozen E0", agent.decide),
        ("Candidate A", cand_a.decide),
        ("Candidate E", cand_e.decide),
        ("Candidate A+E", cand_ae.decide),
    ]

    results = {}

    for name, dec_fn in strategies:
        logger.info(f"Executing replay for {name} across {len(timeline)} sessions...")
        t0 = time.perf_counter()

        # Re-instantiate engine with clean provider & clean registry
        engine = ReplayEngine(
            agent_path_or_fn=dec_fn,
            provider=provider,
            corporate_actions=corp_registry,
            start_cash=100_000.0,
            commission_bps=0.0,
        )

        replay_output = engine.run_replay("2015-01-01", "2019-12-31")
        elapsed = time.perf_counter() - t0

        m = replay_output["metrics"]
        p_state = engine.last_portfolio

        days = m["days"]
        ret_pct = m["ret"] * 100.0
        cagr_pct = ((1.0 + m["ret"]) ** (252.0 / days) - 1.0) * 100.0 if days > 0 else 0.0
        mdd_pct = m["mdd"] * 100.0
        sharpe = m["sharpe"]
        calmar = m["calmar"]
        trades = m["trades"]

        results[name] = {
            "name": name,
            "days_processed": days,
            "starting_nav": 100_000.0,
            "ending_nav": round(replay_output["equity_curve"][-1], 2),
            "net_return_pct": round(ret_pct, 2),
            "cagr_pct": round(cagr_pct, 2),
            "max_drawdown_pct": round(mdd_pct, 2),
            "sharpe_ratio": round(sharpe, 2),
            "calmar_ratio": round(calmar, 2),
            "trades_count": trades,
            "total_dividends_credited": round(p_state.total_dividends_credited, 2),
            "total_slippage_paid": round(replay_output["slippage_cost"], 2),
            "total_commission_paid": round(replay_output["commission_cost"], 2),
            "cash_balance": round(p_state.cash, 2),
            "active_positions_count": len([q for q in p_state.positions.values() if q > 0]),
            "elapsed_seconds": round(elapsed, 2),
        }

        logger.info(
            f"  {name:15s} | Ret: {ret_pct:6.2f}% | CAGR: {cagr_pct:5.2f}% | "
            f"MaxDD: {mdd_pct:5.2f}% | Sharpe: {sharpe:4.2f} | Trades: {trades:4d} | Divs: ${p_state.total_dividends_credited:,.2f}"
        )

    # Save results manifest
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved four-way results to {RESULTS_FILE}.")

    return results


if __name__ == "__main__":
    res = run_four_way_backtest()
    print("\n=========================================================================================")
    print("STAGE B2-I: AUTHENTIC TIINGO TIER 1 (2015-2019) FOUR-WAY PERFORMANCE COMPARISON")
    print("=========================================================================================")
    print(f"{'Strategy':16s} | {'Return':8s} | {'CAGR':7s} | {'MaxDD':7s} | {'Sharpe':7s} | {'Trades':6s} | {'Ending NAV':12s} | {'Dividends':10s}")
    print("-----------------------------------------------------------------------------------------")
    for name, r in res.items():
        print(
            f"{r['name']:16s} | {r['net_return_pct']:6.2f}% | {r['cagr_pct']:5.2f}% | "
            f"{r['max_drawdown_pct']:5.2f}% | {r['sharpe_ratio']:6.2f} | {r['trades_count']:6d} | "
            f"${r['ending_nav']:11,.2f} | ${r['total_dividends_credited']:9,.2f}"
        )
    print("=========================================================================================")
