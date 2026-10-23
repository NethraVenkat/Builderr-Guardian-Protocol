"""
Evidence Generator: Method A Order-Event Trace (Batch V29B).

Replays authentic Tier 2 history (2020-01-01 to 2021-12-31) to derive
complete order-level event traces under Severe and Extreme slippage models.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import agent
from research.engine.accounting import (
    CONCENTRATION_CAP,
    LEVERAGE_CAP,
    MAX_TRADES_PER_DAY,
    PortfolioState,
    get_beta,
)
import research.engine.accounting as accounting
from research.engine.event_verifier import verify_order_events
from research.engine.replay import ReplayEngine
from research.engine.tiingo_client import TiingoHistoricalProvider
from research.scripts.run_tier2_authentic_backtest import build_clean_corp_registry


def generate_method_a_order_event_trace(
    cache_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    cache_file = cache_path or (REPO_ROOT / "tiingo_cache" / "tier2_bars.json")
    if not cache_file.exists():
        raise FileNotFoundError(f"Tier 2 cache file missing: {cache_file}")

    cache_bytes = cache_file.read_bytes()
    cache_hash = hashlib.sha256(cache_bytes).hexdigest()
    preloaded_bars: dict[str, list[dict[str, Any]]] = json.loads(cache_bytes.decode("utf-8"))

    symbols = sorted(list(preloaded_bars.keys()))
    eval_start = "2020-01-01"
    eval_end = "2021-12-31"
    warmup_start = "2019-09-01"

    provider = TiingoHistoricalProvider(
        symbols=symbols,
        start_date=eval_start,
        end_date=eval_end,
        warmup_start_date=warmup_start,
        preloaded_bars=preloaded_bars,
    )

    # 1. Run Baseline Frozen E0 replay to derive authentic 414 orders
    orig_s_eq, orig_s_lev = accounting.SLIP_EQUITY, accounting.SLIP_LEVERAGED
    try:
        accounting.SLIP_EQUITY = 0.0005
        accounting.SLIP_LEVERAGED = 0.0010
        agent._last_rebalance_bar_date = None
        agent._last_targets = {}
        reg = build_clean_corp_registry(preloaded_bars)
        baseline_engine = ReplayEngine(
            agent_path_or_fn=agent.decide,
            provider=provider,
            corporate_actions=reg,
            commission_bps=0.0,
            start_cash=100_000.0,
            price_semantics="causal_production",
        )
        baseline_engine.run_replay(eval_start=eval_start, eval_end=eval_end, record_traces=True)
        base_fills = baseline_engine.last_portfolio.fill_log
    finally:
        accounting.SLIP_EQUITY = orig_s_eq
        accounting.SLIP_LEVERAGED = orig_s_lev

    baseline_orders_by_date: dict[str, list[dict[str, Any]]] = {}
    order_seq = 0
    for f in base_fills:
        item = {
            "order_index": order_seq,
            "date": f.date,
            "ticker": f.ticker,
            "side": f.side,
            "quantity": float(f.filled_qty),
        }
        baseline_orders_by_date.setdefault(f.date, []).append(item)
        order_seq += 1

    total_baseline_orders = order_seq
    assert total_baseline_orders == 414, f"Expected 414 baseline orders, observed {total_baseline_orders}"

    # Scenarios to simulate
    scenario_configs = [
        {
            "id": "scenario_3_severe_slippage",
            "name": "Scenario 3: Severe Slippage (25 bps equity / 50 bps leveraged)",
            "slip_equity": 0.0025,
            "slip_leveraged": 0.0050,
            "commission_bps": 0.0,
            "expected_trades": 414,
        },
        {
            "id": "scenario_4_extreme_slippage",
            "name": "Scenario 4: Extreme Slippage (50 bps equity / 100 bps leveraged)",
            "slip_equity": 0.0050,
            "slip_leveraged": 0.0100,
            "commission_bps": 0.0,
            "expected_trades": 408,
        },
    ]

    scenario_results: dict[str, Any] = {}

    for cfg in scenario_configs:
        s_id = cfg["id"]
        s_eq = cfg["slip_equity"]
        s_lev = cfg["slip_leveraged"]
        c_bps = cfg["commission_bps"]

        corp_registry = build_clean_corp_registry(preloaded_bars)
        portfolio = PortfolioState(cash=100_000.0)

        events: list[dict[str, Any]] = []
        curtailed_buys_history: dict[str, list[dict[str, Any]]] = {}

        for current_date, market_state in provider.stream_daily_slices(eval_start, eval_end):
            portfolio.reset_daily_trade_counter()
            corp_registry.apply_splits_for_date(current_date, portfolio.positions, portfolio.avg_cost)
            div_cash, _, _ = corp_registry.process_dividends_for_date(current_date, portfolio.positions)
            portfolio.cash += div_cash
            portfolio.total_dividends_credited += div_cash
            portfolio.dividend_receivables = corp_registry.total_outstanding_receivables()

            today_opens: dict[str, float] = {}
            today_closes: dict[str, float] = {}
            for sym, bars in market_state.items():
                if bars and bars[-1]["ts"] == current_date:
                    today_opens[sym] = bars[-1].get("raw_open", bars[-1]["open"])
                    today_closes[sym] = bars[-1].get("raw_close", bars[-1]["close"])

            orders_today = baseline_orders_by_date.get(current_date, [])
            sells = [o for o in orders_today if o["side"] == "sell"]
            buys = [o for o in orders_today if o["side"] == "buy"]

            orig_s_eq_sub, orig_s_lev_sub = accounting.SLIP_EQUITY, accounting.SLIP_LEVERAGED
            accounting.SLIP_EQUITY = s_eq
            accounting.SLIP_LEVERAGED = s_lev
            try:
                # 1. Process Sells
                for o in sells:
                    order_idx = o["order_index"]
                    ticker = o["ticker"]
                    req_qty = o["quantity"]
                    px = today_opens.get(ticker, 0.0)
                    held_before = float(portfolio.positions.get(ticker, 0.0))
                    cash_before = float(portfolio.cash)
                    b = get_beta(ticker)
                    slip_rate = s_lev if b > 1.0 else s_eq

                    res = portfolio.execute_order(o, px, commission_bps=c_bps, current_prices=today_opens)

                    held_after = float(portfolio.positions.get(ticker, 0.0))
                    cash_after = float(portfolio.cash)

                    if res is None:
                        filled_qty = 0.0
                        classification = "REJECTED"
                        reason = "UNHELD_POSITION"
                        notional = 0.0
                        fill_px = px * (1.0 - slip_rate)
                        comm = 0.0
                    elif abs(res.filled_qty - req_qty) < 1e-9:
                        filled_qty = float(res.filled_qty)
                        classification = "FULL_FILL"
                        reason = "NORMAL_FILL"
                        notional = float(res.notional)
                        fill_px = float(res.fill_price)
                        comm = float(res.commission)
                    else:
                        filled_qty = float(res.filled_qty)
                        classification = "PARTIAL_FILL"
                        reason = "INVENTORY_CONSTRAINED"
                        notional = float(res.notional)
                        fill_px = float(res.fill_price)
                        comm = float(res.commission)

                    causal_trace = None
                    if classification in ("PARTIAL_FILL", "REJECTED"):
                        prior = curtailed_buys_history.get(ticker, [])
                        if prior:
                            prior_str = "; ".join(
                                f"Order {p['order_index']} ({p['date']}): requested {p['requested_qty']}, filled {p['filled_qty']}"
                                for p in prior
                            )
                            causal_trace = (
                                f"Downstream {reason} sell on {current_date}: requested {req_qty} shares, held {held_before} shares. "
                                f"Causally caused by prior curtailed buy(s): [{prior_str}]."
                            )
                        else:
                            causal_trace = f"Unlinked inventory curtailment: requested {req_qty}, held {held_before}."

                    event_id = f"V29B_{s_id.upper()[:10]}_ORD_{order_idx:03d}_{current_date.replace('-', '')}_{ticker}_SELL"
                    events.append({
                        "event_id": event_id,
                        "scenario_id": s_id,
                        "order_index": order_idx,
                        "date": current_date,
                        "ticker": ticker,
                        "side": "sell",
                        "requested_qty": round(req_qty, 6),
                        "filled_qty": round(filled_qty, 6),
                        "open_price": round(px, 6),
                        "fill_price": round(fill_px, 6),
                        "effective_slippage_bps": round(slip_rate * 10000.0, 1),
                        "commission_paid": round(comm, 4),
                        "notional_executed": round(notional, 4),
                        "classification": classification,
                        "classification_reason": reason,
                        "pre_trade_cash": round(cash_before, 4),
                        "post_trade_cash": round(cash_after, 4),
                        "pre_trade_held_qty": round(held_before, 6),
                        "post_trade_held_qty": round(held_after, 6),
                        "causal_trace": causal_trace,
                    })

                # 2. Process Buys
                for o in buys:
                    order_idx = o["order_index"]
                    ticker = o["ticker"]
                    req_qty = o["quantity"]
                    px = today_opens.get(ticker, 0.0)
                    held_before = float(portfolio.positions.get(ticker, 0.0))
                    cash_before = float(portfolio.cash)
                    b = get_beta(ticker)
                    slip_rate = s_lev if b > 1.0 else s_eq

                    res = portfolio.execute_order(o, px, commission_bps=c_bps, current_prices=today_opens)

                    held_after = float(portfolio.positions.get(ticker, 0.0))
                    cash_after = float(portfolio.cash)

                    if res is None:
                        filled_qty = 0.0
                        classification = "REJECTED"
                        reason = "INSUFFICIENT_CASH"
                        notional = 0.0
                        fill_px = px * (1.0 + slip_rate)
                        comm = 0.0
                    elif abs(res.filled_qty - req_qty) < 1e-9:
                        filled_qty = float(res.filled_qty)
                        classification = "FULL_FILL"
                        reason = "NORMAL_FILL"
                        notional = float(res.notional)
                        fill_px = float(res.fill_price)
                        comm = float(res.commission)
                    else:
                        filled_qty = float(res.filled_qty)
                        classification = "PARTIAL_FILL"
                        reason = "CASH_CONSTRAINED"
                        notional = float(res.notional)
                        fill_px = float(res.fill_price)
                        comm = float(res.commission)

                    causal_trace = None
                    if classification in ("PARTIAL_FILL", "REJECTED"):
                        causal_trace = (
                            f"Cash curtailment on {current_date}: pre-trade cash was ${cash_before:,.2f}. "
                            f"Full requested {req_qty} shares at fill price ${fill_px:.2f} required "
                            f"${req_qty * fill_px:,.2f}. Filled {filled_qty} shares."
                        )
                        curtailed_buys_history.setdefault(ticker, []).append({
                            "order_index": order_idx,
                            "date": current_date,
                            "requested_qty": req_qty,
                            "filled_qty": filled_qty,
                            "cash_before": cash_before,
                        })

                    event_id = f"V29B_{s_id.upper()[:10]}_ORD_{order_idx:03d}_{current_date.replace('-', '')}_{ticker}_BUY"
                    events.append({
                        "event_id": event_id,
                        "scenario_id": s_id,
                        "order_index": order_idx,
                        "date": current_date,
                        "ticker": ticker,
                        "side": "buy",
                        "requested_qty": round(req_qty, 6),
                        "filled_qty": round(filled_qty, 6),
                        "open_price": round(px, 6),
                        "fill_price": round(fill_px, 6),
                        "effective_slippage_bps": round(slip_rate * 10000.0, 1),
                        "commission_paid": round(comm, 4),
                        "notional_executed": round(notional, 4),
                        "classification": classification,
                        "classification_reason": reason,
                        "pre_trade_cash": round(cash_before, 4),
                        "post_trade_cash": round(cash_after, 4),
                        "pre_trade_held_qty": round(held_before, 6),
                        "post_trade_held_qty": round(held_after, 6),
                        "causal_trace": causal_trace,
                    })

            finally:
                accounting.SLIP_EQUITY = orig_s_eq_sub
                accounting.SLIP_LEVERAGED = orig_s_lev_sub

            portfolio.mark_to_market(today_closes)

        # Verify through verifier engine
        verification_summary = verify_order_events(
            events,
            expected_requested_count=414,
            expected_executed_count=cfg["expected_trades"],
            verify_causal_chain=True,
        )

        scenario_results[s_id] = {
            "config": cfg,
            "verification_summary": verification_summary,
            "events": events,
        }

    manifest = {
        "manifest_version": "V29B_ORDER_EVENT_TRACE",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_cache_hash_tier2": cache_hash,
        "total_baseline_orders": total_baseline_orders,
        "scenarios": {
            s_id: {
                "config": data["config"],
                "verification_summary": data["verification_summary"],
                "events_count": len(data["events"]),
                "events": data["events"],
            }
            for s_id, data in scenario_results.items()
        },
    }

    out_file = output_path or (REPO_ROOT / "research" / "manifests" / "v29b_method_a_order_event_trace.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    manifest = generate_method_a_order_event_trace()
    for s_id, data in manifest["scenarios"].items():
        summary = data["verification_summary"]
        print(f"Scenario {s_id}: Verified {summary['total_requested']} orders. "
              f"Full: {summary['full_fills']}, Part: {summary['partial_fills']}, Rej: {summary['rejections']}")
