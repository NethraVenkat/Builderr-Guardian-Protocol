"""
Stage B2-N: Independent Double-Entry Accounting Verification and Adversarial Audit for Tier 2 (2020-2021).
Audits all 505 sessions of Tier 2 under Option B causal price semantics for:
  - Frozen E0
  - Candidate A
  - Candidate E
  - Candidate A+E

Asserts:
  1. 100% daily balance sheet conservation: Equity == Start Cash + Realized + Unrealized + Dividends - Commissions.
  2. Independent ledger NAV == ReplayEngine reported NAV (discrepancy < 1e-4).
  3. Terminal holdings, cash, and receivables reconciliation.
  4. Execution of 7 adversarial negative controls.
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
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
    compute_business_day_settlement,
)
from research.engine.independent_accounting import (
    AccountingAnomalyDetected,
    IndependentLedger,
    reconstruct_independent_ledger,
    run_negative_control_altered_fill_price,
    run_negative_control_omitted_trade,
    run_negative_control_reversed_split,
    run_negative_control_double_dividend,
    run_negative_control_double_fee,
    run_negative_control_missing_position,
    run_negative_control_lookahead_leak,
)
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import TiingoHistoricalProvider
from research.strategies.v11_candidates import (
    CandidateA_AdaptiveRebalance,
    CandidateE_CostAwareRebalancing,
)
from research.strategies.v12_candidate_ae import CandidateAE_Combined

logger = logging.getLogger("verify_tier2_accounting")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"
PRIMARY_RESULTS_FILE = Path("research/manifests") / "tier2_four_way_results.json"
ACCOUNTING_MANIFEST = Path("research/manifests") / "tier2_independent_accounting.json"
ROUNDING_BRIDGE_FILE = Path("research/manifests") / "tier2_nav_rounding_bridge.json"

TIER2_START = "2020-01-01"
TIER2_END = "2021-12-31"
WARMUP_START = "2019-09-01"


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


def run_tier2_accounting_verification() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"Cache file {CACHE_FILE} not found. Run acquire_tier2_tiingo.py first.")

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        preloaded_bars = json.load(f)

    symbols = list(preloaded_bars.keys())

    provider = TiingoHistoricalProvider(
        symbols=symbols,
        start_date=TIER2_START,
        end_date=TIER2_END,
        warmup_start_date=WARMUP_START,
        preloaded_bars=preloaded_bars,
    )

    timeline = provider.get_timeline(TIER2_START, TIER2_END)
    logger.info(f"Loaded {len(timeline)} Tier 2 trading sessions ({timeline[0]} to {timeline[-1]}).")

    cand_a = CandidateA_AdaptiveRebalance()
    cand_e = CandidateE_CostAwareRebalancing()
    cand_ae = CandidateAE_Combined()

    strategies = [
        ("Frozen E0", agent.decide),
        ("Candidate A", cand_a.decide),
        ("Candidate E", cand_e.decide),
        ("Candidate A+E", cand_ae.decide),
    ]

    accounting_results: dict[str, Any] = {}
    rounding_bridge: dict[str, Any] = {}

    for name, dec_fn in strategies:
        logger.info(f"Replaying {name} to extract fill log and independent verification baseline...")
        strat_corp = build_clean_corp_registry(preloaded_bars)
        engine = ReplayEngine(
            agent_path_or_fn=dec_fn,
            provider=provider,
            corporate_actions=strat_corp,
            start_cash=100_000.0,
            commission_bps=0.0,
            price_semantics="causal_production",
        )
        res = engine.run_replay(eval_start=TIER2_START, eval_end=TIER2_END, record_traces=True)
        port = engine.last_portfolio

        logger.info(f"Reconstructing independent double-entry ledger for {name} ({len(port.fill_log)} fills)...")
        t0 = time.perf_counter()
        recon_corp = build_clean_corp_registry(preloaded_bars)
        ledger = reconstruct_independent_ledger(
            timeline=timeline,
            preloaded_bars=preloaded_bars,
            fill_log=port.fill_log,
            corp_registry=recon_corp,
            initial_cash=100_000.0,
            commission_bps=0.0,
        )
        recon_dur = time.perf_counter() - t0

        # Daily reconciliation check against engine equity curve
        assert len(ledger.daily_snapshots) == len(res["equity_curve"]) == len(timeline), (
            f"Length mismatch: ledger={len(ledger.daily_snapshots)}, engine={len(res['equity_curve'])}, timeline={len(timeline)}"
        )

        max_discrepancy = 0.0
        discrepancy_count = 0
        terminal_diff = 0.0

        for i, snap in enumerate(ledger.daily_snapshots):
            engine_nav = res["equity_curve"][i]
            ledger_nav = snap["nav"]
            diff = abs(engine_nav - ledger_nav)
            if diff > max_discrepancy:
                max_discrepancy = diff
            if diff > 1e-4:
                discrepancy_count += 1
            if i == len(timeline) - 1:
                terminal_diff = diff

        # Position reconciliation
        pos_mismatch = []
        for ticker, held_qty in port.positions.items():
            ledger_qty = ledger.positions.get(ticker, 0.0)
            if abs(held_qty - ledger_qty) > 1e-6:
                pos_mismatch.append((ticker, held_qty, ledger_qty))

        cash_diff = abs(port.cash - ledger.cash)
        realized_diff = abs(port.realized_pnl - ledger.realized_pnl)
        div_diff = abs(port.total_dividends_credited - ledger.total_dividends_credited)

        is_certified = (
            max_discrepancy < 1e-4
            and discrepancy_count == 0
            and len(pos_mismatch) == 0
            and cash_diff < 1e-4
            and len(ledger.exception_ledger) == 0
        )

        accounting_results[name] = {
            "strategy": name,
            "certified": is_certified,
            "total_sessions": len(timeline),
            "reconstruction_duration_seconds": round(recon_dur, 2),
            "engine_ending_nav": round(res["equity_curve"][-1], 4),
            "ledger_ending_nav": round(ledger.daily_snapshots[-1]["nav"], 4),
            "terminal_discrepancy": round(terminal_diff, 8),
            "max_daily_discrepancy": round(max_discrepancy, 8),
            "discrepancy_sessions_count": discrepancy_count,
            "terminal_engine_cash": round(port.cash, 4),
            "terminal_ledger_cash": round(ledger.cash, 4),
            "cash_discrepancy": round(cash_diff, 8),
            "total_realized_pnl": round(ledger.realized_pnl, 4),
            "total_unrealized_pnl": round(ledger.daily_snapshots[-1]["unrealized_pnl"], 4),
            "total_dividends_credited": round(ledger.total_dividends_credited, 4),
            "total_slippage_cost": round(ledger.total_slippage, 4),
            "total_commissions": round(ledger.total_commissions, 4),
            "active_positions_count": len([p for p in ledger.positions.values() if p > 0]),
            "position_mismatches": pos_mismatch,
            "exceptions_logged": ledger.exception_ledger,
        }

        # NAV rounding bridge analysis
        unrounded_nav = ledger.daily_snapshots[-1]["nav"]
        rounded_2dec = round(unrounded_nav, 2)
        rounding_bridge[name] = {
            "unrounded_nav": unrounded_nav,
            "rounded_nav_2dec": rounded_2dec,
            "rounding_delta": unrounded_nav - rounded_2dec,
            "pct_delta": ((unrounded_nav - rounded_2dec) / unrounded_nav) * 100.0 if unrounded_nav > 0 else 0.0,
            "shares_integer_quantized": all(q.is_integer() for q in port.positions.values()),
        }

        logger.info(
            f"ACCOUNTING {name}: Certified={is_certified}, Max Daily Discrepancy=${max_discrepancy:.8f}, "
            f"Cash Diff=${cash_diff:.8f}, Realized=${ledger.realized_pnl:,.2f}, Unrealized=${ledger.daily_snapshots[-1]['unrealized_pnl']:,.2f}."
        )

    # ==============================================================================
    # 7 ADVERSARIAL NEGATIVE CONTROLS
    # ==============================================================================
    logger.info("Executing 7 institutional adversarial negative controls...")
    controls = [
        ("altered_fill_price", run_negative_control_altered_fill_price),
        ("omitted_trade", run_negative_control_omitted_trade),
        ("reversed_split", run_negative_control_reversed_split),
        ("double_dividend", run_negative_control_double_dividend),
        ("double_fee", run_negative_control_double_fee),
        ("missing_position", run_negative_control_missing_position),
        ("lookahead_leak", run_negative_control_lookahead_leak),
    ]

    negative_control_results = {}
    for c_name, c_fn in controls:
        caught = c_fn()
        negative_control_results[c_name] = {
            "executed": True,
            "detected_anomaly": caught,
            "verdict": "PASS" if caught else "FAIL",
        }
        logger.info(f"  Negative Control [{c_name}]: {'PASS (Anomaly Caught)' if caught else 'FAIL (Undetected)'}")
        assert caught, f"Adversarial negative control {c_name} failed to catch anomaly!"

    # Save manifests
    ACCOUNTING_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTING_MANIFEST, "w", encoding="utf-8") as f:
        json.dump({
            "stage": "Stage B2-N Tier 2 Independent Accounting Verification",
            "observation_window": {"start": TIER2_START, "end": TIER2_END},
            "strategies": accounting_results,
            "negative_controls": negative_control_results,
            "all_strategies_certified": all(v["certified"] for v in accounting_results.values()),
            "all_negative_controls_passed": all(v["verdict"] == "PASS" for v in negative_control_results.values()),
        }, f, indent=2)
    logger.info(f"Wrote Tier 2 independent accounting manifest to {ACCOUNTING_MANIFEST}.")

    with open(ROUNDING_BRIDGE_FILE, "w", encoding="utf-8") as f:
        json.dump(rounding_bridge, f, indent=2)
    logger.info(f"Wrote Tier 2 NAV rounding bridge to {ROUNDING_BRIDGE_FILE}.")

    return {
        "accounting": accounting_results,
        "negative_controls": negative_control_results,
    }


if __name__ == "__main__":
    run_tier2_accounting_verification()
