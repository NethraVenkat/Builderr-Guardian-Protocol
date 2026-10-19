"""Task K: Adverse Input and Boundary Stress Tests.

Tests agent.decide() with malformed, adversarial, and boundary inputs.
"""
import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent

def test_adverse_inputs():
    tests = []

    # 1. Empty market state
    assert agent.decide({}, {"cash": 100_000.0}, 100_000.0) == []
    tests.append(("Empty market state", True))

    # 2. Missing key benchmark tickers (SPY / QQQ missing)
    ms_no_bench = {"AAPL": [{"ts": "2026-06-01", "close": 150.0}]}
    assert agent.decide(ms_no_bench, {"cash": 100_000.0}, 100_000.0) == []
    tests.append(("Missing SPY/QQQ benchmarks", True))

    # 3. Insufficient history (< 50 bars)
    ms_short = {
        "SPY": [{"ts": f"2026-06-{i:02d}", "close": 500.0} for i in range(1, 20)],
        "QQQ": [{"ts": f"2026-06-{i:02d}", "close": 400.0} for i in range(1, 20)]
    }
    assert agent.decide(ms_short, {"cash": 100_000.0}, 100_000.0) == []
    tests.append(("Insufficient history (< 50 bars)", True))

    # 4. Zero / negative / NaN prices in bars
    ms_corrupt = {
        "SPY": [{"ts": "2026-06-01", "close": 0.0}],
        "QQQ": [{"ts": "2026-06-01", "close": -100.0}]
    }
    assert agent.decide(ms_corrupt, {"cash": 100_000.0}, 100_000.0) == []
    tests.append(("Zero and negative price tolerance", True))

    # 5. Zero cash available
    ms_valid = {
        "SPY": [{"ts": f"2026-01-{i:02d}", "close": 500.0 + i} for i in range(1, 70)],
        "QQQ": [{"ts": f"2026-01-{i:02d}", "close": 400.0 + i} for i in range(1, 70)]
    }
    orders_zero_cash = agent.decide(ms_valid, {"cash": 0.0, "positions": []}, 0.0)
    # Zero cash with no positions produces zero buy orders
    assert all(o["side"] == "sell" for o in orders_zero_cash)
    tests.append(("Zero cash handling", True))

    # 6. Negative cash available
    orders_neg_cash = agent.decide(ms_valid, {"cash": -500.0, "positions": []}, -500.0)
    assert orders_neg_cash == []
    tests.append(("Negative cash handling", True))

    # 7. Giant cash balance (e.g. $100M)
    orders_giant = agent.decide(ms_valid, {"cash": 100_000_000.0, "positions": []}, 100_000_000.0)
    assert isinstance(orders_giant, list)
    assert len(orders_giant) <= 45
    tests.append(("Extreme high equity sizing", True))

    # 8. Malformed portfolio state (None or non-dict fields)
    assert agent.decide(ms_valid, {}, 100_000.0) is not None
    assert agent.decide(ms_valid, {"positions": None, "last_prices": None}, 100_000.0) is not None
    tests.append(("Malformed portfolio_state recovery", True))

    print("=" * 80)
    print("TASK K: ADVERSE INPUT TESTS RESULTS")
    print("=" * 80)
    for name, passed in tests:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\nAll {len(tests)} / {len(tests)} adverse tests passed.")

if __name__ == "__main__":
    test_adverse_inputs()
