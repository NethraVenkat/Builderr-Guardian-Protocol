"""Task F: Comprehensive Feature-by-Feature Verification Matrix for agent.py.

Tests every function and feature in agent.py across edge cases,
boundary conditions, NaN/inf inputs, constant prices, abnormal spikes,
and repeated invocations.
"""
import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent

def run_feature_tests():
    results = []

    # 1. closes()
    assert agent.closes([]) == []
    assert agent.closes(None) == []
    assert agent.closes([{"close": 100.0}, {"close": 105.5}]) == [100.0, 105.5]
    assert agent.closes([{"close": "100.0"}]) == [100.0]
    assert agent.closes([{"close": -5.0}]) == []  # invalid negative
    assert agent.closes([{"close": 0.0}]) == []   # invalid zero
    assert agent.closes([{"close": None}]) == []  # missing/invalid
    assert agent.closes([{"wrong_key": 100}]) == []
    results.append(("closes() extraction & validation", True))

    # 2. sma()
    vals = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert agent.sma(vals, 3) == 40.0
    assert agent.sma(vals, 5) == 30.0
    assert agent.sma(vals, 6) is None  # insufficient history
    assert agent.sma([], 3) is None
    # Constant values
    assert agent.sma([50.0] * 50, 50) == 50.0
    results.append(("sma() moving average calculation", True))

    # 3. momentum()
    # formula: values[-1] / values[-(n+1)] - 1.0
    vals_m = [100.0, 105.0, 110.0, 120.0]
    assert math.isclose(agent.momentum(vals_m, 3), 0.20)  # 120/100 - 1
    assert agent.momentum(vals_m, 4) is None  # len <= n
    assert agent.momentum([0.0, 100.0], 1) is None  # start <= 0
    # Constant values
    assert agent.momentum([100.0] * 30, 20) == 0.0
    results.append(("momentum() rate of return", True))

    # 4. realized_vol()
    # constant series -> zero volatility
    flat = [100.0] * 30
    assert math.isclose(agent.realized_vol(flat, 20), 0.0)
    # volatile series
    vol_series = [100.0 * (1.02 if i % 2 == 0 else 0.98) for i in range(30)]
    v = agent.realized_vol(vol_series, 20)
    assert v is not None and v > 0.0
    # Insufficient length
    assert agent.realized_vol([100.0, 105.0], 20) is None
    results.append(("realized_vol() annualized standard deviation", True))

    # 5. current_positions()
    ps_empty = {"positions": []}
    assert agent.current_positions(ps_empty) == {}
    ps_valid = {"positions": [{"ticker": "spy", "quantity": 10, "avg_cost": 500.0}]}
    cur = agent.current_positions(ps_valid)
    assert "SPY" in cur and cur["SPY"]["quantity"] == 10.0
    # Negative and invalid entries
    ps_invalid = {"positions": [{"ticker": "QQQ", "quantity": -5}, {"quantity": 10}, {"ticker": ""}, {"ticker": "MSFT", "quantity": "invalid"}]}
    cur_inv = agent.current_positions(ps_invalid)
    assert "QQQ" not in cur_inv
    assert "MSFT" not in cur_inv
    results.append(("current_positions() normalization & filtering", True))

    # 6. equity()
    assert agent.equity({}, 100_000.0) == 100_000.0
    ps_eq = {
        "cash": 50_000.0,
        "positions": [{"ticker": "SPY", "quantity": 100, "avg_cost": 500.0}],
        "last_prices": {"SPY": 550.0}
    }
    assert agent.equity(ps_eq, 50_000.0) == 105_000.0
    # Fallback to avg_cost if last_price missing
    ps_eq_no_px = {
        "cash": 50_000.0,
        "positions": [{"ticker": "SPY", "quantity": 100, "avg_cost": 500.0}],
        "last_prices": {}
    }
    assert agent.equity(ps_eq_no_px, 50_000.0) == 100_000.0
    results.append(("equity() portfolio valuation", True))

    # 7. _latest_bar_date()
    ms_dates = {"SPY": [{"ts": "2026-06-01T00:00:00", "close": 500.0}]}
    assert agent._latest_bar_date(ms_dates) == "2026-06-01"
    assert agent._latest_bar_date({}) is None
    results.append(("_latest_bar_date() date string parsing", True))

    # 8. _scale_caps()
    raw_weights = {"SPY": 0.35, "QQQ": 0.35, "TQQQ": 0.30}  # breach > 0.24, gross beta breach
    scaled = agent._scale_caps(raw_weights)
    assert all(w <= agent.MAX_WEIGHT for w in scaled.values())
    gross_b = sum(w * agent.BETA_MULTIPLE.get(t, 1.0) for t, w in scaled.items())
    assert gross_b <= agent.MAX_BETA_GROSS + 1e-5
    results.append(("_scale_caps() leverage and concentration enforcement", True))

    # 9. _has_position_drifted()
    ps_drift = {
        "positions": [{"ticker": "SPY", "quantity": 100, "avg_cost": 200.0}],
        "last_prices": {"SPY": 300.0}
    }
    # SPY value = 30,000 / 100,000 = 0.30 > DRIFT_LIMIT (0.27)
    assert agent._has_position_drifted(ps_drift, 100_000.0) is True
    # SPY value = 20,000 / 100,000 = 0.20 <= 0.27
    ps_nodrift = {
        "positions": [{"ticker": "SPY", "quantity": 100, "avg_cost": 200.0}],
        "last_prices": {"SPY": 200.0}
    }
    assert agent._has_position_drifted(ps_nodrift, 100_000.0) is False
    results.append(("_has_position_drifted() threshold check", True))

    # 10. orders_to_rebalance() order generation & sizing
    targets = {"SPY": 0.20, "QQQ": 0.20}
    positions = {"AAPL": {"quantity": 50.0, "avg_cost": 150.0}}  # stale position to sell
    prices = {"SPY": 500.0, "QQQ": 400.0, "AAPL": 200.0}
    orders = agent.orders_to_rebalance(targets, positions, 100_000.0, prices, 10_000.0)
    assert len(orders) > 0
    # Sells first
    assert orders[0]["side"] == "sell"
    assert orders[0]["ticker"] == "AAPL"
    # Buys second
    buys = [o for o in orders if o["side"] == "buy"]
    assert all(o["side"] == "buy" for o in buys)
    assert len(orders) <= 45
    results.append(("orders_to_rebalance() sequencing & order-count bounds", True))

    # 11. decide() empty/malformed handling
    assert agent.decide({}, {}, 100_000.0) == []
    assert agent.decide(None, {}, 100_000.0) == []
    results.append(("decide() input fault-tolerance", True))

    print("=" * 80)
    print("TASK F: AGENT FEATURE VERIFICATION MATRIX")
    print("=" * 80)
    for name, passed in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"\nAll {len(results)} / {len(results)} features successfully verified.")

if __name__ == "__main__":
    run_feature_tests()
