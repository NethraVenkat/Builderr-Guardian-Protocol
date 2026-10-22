"""
Independent Financial Accounting Verification for Authentic Tier 1 Replay.
Reconciles: Initial NAV + Realized PnL + Unrealized PnL + Dividends - Commissions == Ending NAV.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import agent
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

CACHE_FILE = Path("tiingo_cache") / "tier1_bars.json"
MANIFEST_FILE = Path("research/manifests") / "tier1_accounting_reconciliation.json"


def verify_accounting():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        preloaded_bars = json.load(f)

    symbols = list(preloaded_bars.keys())

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

    provider = TiingoHistoricalProvider(
        symbols=symbols,
        start_date="2015-01-01",
        end_date="2019-12-31",
        warmup_start_date="2014-09-01",
        preloaded_bars=preloaded_bars,
    )

    cand_a = CandidateA_AdaptiveRebalance()
    cand_e = CandidateE_CostAwareRebalancing()
    cand_ae = CandidateAE_Combined()

    strategies = [
        ("Frozen E0", agent.decide),
        ("Candidate A", cand_a.decide),
        ("Candidate E", cand_e.decide),
        ("Candidate A+E", cand_ae.decide),
    ]

    reconciliations = {}

    for name, dec_fn in strategies:
        engine = ReplayEngine(
            agent_path_or_fn=dec_fn,
            provider=provider,
            corporate_actions=corp_registry,
            start_cash=100_000.0,
            commission_bps=0.0,
        )

        out = engine.run_replay("2015-01-01", "2019-12-31")
        p = engine.last_portfolio

        # Get latest market prices
        last_date = provider.get_timeline()[-1]
        last_prices = {
            s: bars[-1]["close"]
            for s, bars in preloaded_bars.items()
            if bars and bars[-1]["ts"] == last_date
        }

        # Double-entry balance sheet reconciliation
        start_cash = p.start_cash
        realized_pnl = p.realized_pnl
        unrealized_pnl = p.unrealized_pnl(last_prices)
        total_divs = p.total_dividends_credited
        div_receivables = p.dividend_receivables
        commissions = p.total_commissions

        reconstructed_nav = start_cash + realized_pnl + unrealized_pnl + total_divs + div_receivables - commissions
        ending_nav = p.total_equity(last_prices)
        discrepancy = abs(ending_nav - reconstructed_nav)

        terminal_positions = {
            sym: {
                "shares": round(qty, 4),
                "avg_cost": round(p.avg_cost.get(sym, 0.0), 4),
                "last_price": round(last_prices.get(sym, 0.0), 4),
                "market_value": round(qty * last_prices.get(sym, 0.0), 4),
                "unrealized_pnl": round(qty * (last_prices.get(sym, 0.0) - p.avg_cost.get(sym, 0.0)), 4),
            }
            for sym, qty in p.positions.items()
            if qty > 0
        }

        reconciliations[name] = {
            "strategy": name,
            "start_cash": round(start_cash, 6),
            "ending_cash": round(p.cash, 6),
            "positions_value": round(p.total_positions_value(last_prices), 6),
            "dividend_receivables": round(div_receivables, 6),
            "ending_nav": round(ending_nav, 6),
            "realized_pnl": round(realized_pnl, 6),
            "unrealized_pnl": round(unrealized_pnl, 6),
            "total_dividends_credited": round(total_divs, 6),
            "total_commissions": round(commissions, 6),
            "reconstructed_nav": round(reconstructed_nav, 6),
            "absolute_discrepancy": round(discrepancy, 10),
            "reconciliation_verdict": "CONSERVED" if discrepancy < 1e-6 else "VIOLATED",
            "terminal_positions_count": len(terminal_positions),
            "terminal_positions": terminal_positions,
        }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(reconciliations, f, indent=2)

    return reconciliations


if __name__ == "__main__":
    rec = verify_accounting()
    print("\n=== FINANCIAL ACCOUNTING RECONCILIATION SUMMARY ===")
    for name, r in rec.items():
        print(f"Strategy: {name:16s} | Ending NAV: ${r['ending_nav']:10.2f} | Reconstructed: ${r['reconstructed_nav']:10.2f} | Diff: ${r['absolute_discrepancy']:.10f} | {r['reconciliation_verdict']}")
