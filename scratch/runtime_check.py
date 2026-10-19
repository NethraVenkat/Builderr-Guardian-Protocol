"""Runtime and order-count verification for Stage 2A.

Uses the same data-loading approach as preview.py to feed correct inputs
to agent.decide().
"""
import time
import json
import gzip
import importlib
import importlib.util
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _expand(rows):
    """Compact [ts,o,h,l,c,v] -> the bar dicts the contract specifies."""
    return [
        {"ts": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]}
        for r in rows
    ]


def load_agent():
    """Load agent.py fresh via importlib (same as preview.py does)."""
    spec = importlib.util.spec_from_file_location("agent_test", os.path.join(ROOT, "agent.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.decide


# Load sample regimes
with gzip.open(os.path.join(ROOT, "sample_regimes.json.gz"), "rt") as f:
    regimes = json.load(f)

results = []
global_max_orders = 0
global_max_time = 0.0

for regime_name, regime_data in regimes.items():
    bars = {t: _expand(rows) for t, rows in regime_data["bars"].items()}
    all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
    eval_dates = [d for d in all_dates
                  if regime_data["eval_start"] <= d <= regime_data["eval_end"]]

    # Run 3 trials to verify determinism and measure runtime
    trial_results = []
    for trial in range(3):
        decide = load_agent()  # Fresh agent each trial
        cash = 100000.0
        positions = {}
        avg_cost = {}
        total_orders = 0
        max_orders_single = 0
        times = []

        for i, date in enumerate(eval_dates):
            # Build market_state: bars up to (not including) this date
            market_state = {}
            for ticker, ticker_bars in bars.items():
                prior = [b for b in ticker_bars if b["ts"] < date]
                if prior:
                    market_state[ticker] = prior

            # Build portfolio_state
            last_prices = {}
            for ticker, ticker_bars in bars.items():
                for b in ticker_bars:
                    if b["ts"] < date:
                        last_prices[ticker] = b["close"]

            pos_list = [
                {"ticker": t, "quantity": q, "avg_cost": avg_cost.get(t, 0.0)}
                for t, q in positions.items() if q > 0
            ]
            portfolio_state = {
                "cash": cash,
                "positions": pos_list,
                "last_prices": last_prices,
            }

            t0 = time.perf_counter()
            orders = decide(market_state, portfolio_state, cash)
            elapsed = time.perf_counter() - t0
            times.append(elapsed)

            n_orders = len(orders) if orders else 0
            total_orders += n_orders
            max_orders_single = max(max_orders_single, n_orders)

        trial_results.append({
            "total_orders": total_orders,
            "max_single_call": max_orders_single,
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
        })

    # Check determinism
    deterministic = all(
        t["total_orders"] == trial_results[0]["total_orders"]
        for t in trial_results
    )

    best = trial_results[0]
    max_time_regime = max(t["max_time"] for t in trial_results)
    max_single_call = max(t["max_single_call"] for t in trial_results)

    global_max_orders = max(global_max_orders, max_single_call)
    global_max_time = max(global_max_time, max_time_regime)

    results.append({
        "regime": regime_name,
        "eval_days": len(eval_dates),
        "max_time": max_time_regime,
        "avg_time": best["avg_time"],
        "max_single_call_orders": max_single_call,
        "total_orders": best["total_orders"],
        "deterministic": deterministic,
    })

print("=" * 70)
print("RUNTIME AND ORDER-COUNT VERIFICATION")
print("=" * 70)
for r in results:
    print(f"\nRegime: {r['regime']} ({r['eval_days']} eval days)")
    print(f"  Max runtime per decide(): {r['max_time']:.4f}s")
    print(f"  Avg runtime per decide(): {r['avg_time']:.4f}s")
    print(f"  Max orders in single call: {r['max_single_call_orders']}")
    print(f"  Total orders across regime: {r['total_orders']}")
    print(f"  Deterministic across 3 trials: {r['deterministic']}")

print(f"\n{'=' * 70}")
print(f"GLOBAL MAX ORDERS (single call): {global_max_orders}")
print(f"GLOBAL MAX RUNTIME (single call): {global_max_time:.4f}s")
print(f"5-second limit:    {'PASS' if global_max_time < 5.0 else 'FAIL'}")
print(f"45-order cap:      {'PASS' if global_max_orders <= 45 else 'FAIL'}")
print(f"50-trade/day safe: {'PASS' if global_max_orders <= 50 else 'FAIL'}")

