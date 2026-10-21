"""Production E0 numeric boundary: fail closed and recover without state drift."""
import importlib.util
from pathlib import Path
import pytest
import datetime as dt
import copy
import hashlib
import json
import gzip
import sys
import time
import math

ROOT = Path(__file__).resolve().parents[1]

def fresh():
    spec = importlib.util.spec_from_file_location("e0_numeric", ROOT / "agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("field", ["QQQ", "cash", "portfolio_cash", "quantity", "price", "avg_cost"])
def test_invalid_input_abstains_without_advancing_state_and_recovers(field, value):
    agent = fresh()
    m = market(); ps = account(m); cash = 100000
    if field == "QQQ": m["QQQ"][-1]["close"] = value
    elif field == "cash": cash = value
    elif field == "portfolio_cash": ps["cash"] = value
    else:
        ps["positions"] = [{"ticker": "SPY", "quantity": 100, "avg_cost": 100}]
        if field == "price": ps["last_prices"]["SPY"] = value
        else: ps["positions"][0][field] = value
    assert agent.decide(m, ps, cash) == []
    assert agent._last_rebalance_bar_date is None
    assert agent._last_targets == {}
    clean = market(); portfolio = account(clean)
    expected = fresh().decide(clean, portfolio, 100000)
    assert expected
    assert agent.decide(clean, portfolio, 100000) == expected

@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_closes_rejects_nonfinite(value):
    assert fresh().closes([{"close": 100}, {"close": value}]) == []


@pytest.mark.parametrize("case", ["held_zero", "held_negative", "negative_quantity",
                                  "finite_ratio_overflow", "huge_quantity",
                                  "zero_close", "negative_close"])
def test_additional_invalid_boundary_preserves_existing_state(case):
    agent = fresh(); clean = market(); portfolio = account(clean)
    assert agent.decide(clean, portfolio, 100000)
    state = (agent._last_rebalance_bar_date, dict(agent._last_targets))
    # Advance beyond cadence so rejection cannot pass merely by skipping a rebalance.
    m = market(count=106); ps = account(m)
    ps["positions"] = [{"ticker": "SPY", "quantity": 100, "avg_cost": 100}]
    if case == "held_zero": ps["last_prices"]["SPY"] = 0
    elif case == "held_negative": ps["last_prices"]["SPY"] = -100
    elif case == "negative_quantity": ps["positions"][0]["quantity"] = -100
    elif case == "huge_quantity": ps["positions"][0]["quantity"] = 1e308
    elif case == "zero_close": m["QQQ"][-1]["close"] = 0
    elif case == "negative_close": m["QQQ"][-1]["close"] = -1
    else:
        m["QQQ"][-2]["close"] = 1e-308
        m["QQQ"][-1]["close"] = 1e308
    assert agent.decide(m, ps, 100000) == []
    assert (agent._last_rebalance_bar_date, agent._last_targets) == state


def test_zero_quantity_placeholder_is_valid():
    a = fresh(); m = market(); ps = account(m)
    ps["positions"] = [{"ticker": "SPY", "quantity": 0, "avg_cost": 0}]
    ps["last_prices"]["SPY"] = 0
    assert a.decide(m, ps, 100000) == fresh().decide(m, account(m), 100000)


def market(kind="up", count=100):
    result = {}
    for ticker in fresh().RISK_CANDIDATES + ("QLD", "SSO"):
        price = 100.0
        bars = []
        for i in range(count):
            change = {
                "up": .003, "selloff": -.002, "crash": -.08 if i > count-12 else .002,
                "recovery": .025 if i > count-25 else -.002,
                "false_spike": -.15 if i == count-10 else (.18 if i == count-9 else .002),
                "volatile_up": .045 if i % 2 else -.035,
                "lowvol_down": -.001, "whipsaw": .02 if i % 2 else -.02,
                "flat": 0, "gap": -.5 if i == count-1 else .002,
            }[kind]
            price *= 1 + change
            bars.append({"ts": (dt.date(2025, 1, 1)+dt.timedelta(days=i)).isoformat(),
                         "open": price, "close": price, "high": price, "low": price, "volume": 1e6})
        result[ticker] = bars
    return result


def account(m, cash=100000):
    return {"cash": cash, "positions": [], "last_prices": {t: b[-1]["close"] for t, b in m.items()}}




EXPECTED_AGENT_SHA256 = "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"


def test_pinned_source_and_interface():
    import inspect
    assert hashlib.sha256((ROOT / "agent.py").read_bytes()).hexdigest() == EXPECTED_AGENT_SHA256
    assert list(inspect.signature(fresh().decide).parameters) == ["market_state", "portfolio_state", "cash"]


@pytest.mark.parametrize("kind", ["up", "selloff", "crash", "recovery", "false_spike",
                                 "volatile_up", "lowvol_down", "whipsaw", "flat", "gap"])
def test_contract_and_cash_affordability(kind):
    a = fresh(); m = market(kind); ps = account(m)
    orders = a.decide(m, ps, 100000)
    assert orders == fresh().decide(copy.deepcopy(m), copy.deepcopy(ps), 100000)
    universe = set(json.loads((ROOT / "universe.json").read_text())["tickers"])
    assert len(orders) <= 45
    remaining = 100000.0
    gross = 0.0
    for order in orders:
        assert set(order) == {"ticker", "side", "quantity"}
        assert order["ticker"] in universe
        assert order["side"] == "buy"  # no holdings to sell in this fixture
        assert isinstance(order["quantity"], int) and order["quantity"] > 0
        value = order["quantity"] * m[order["ticker"]][-1]["close"]
        remaining -= value
        assert value / 100000 <= a.MAX_WEIGHT + 1e-6
        gross += value * a.BETA_MULTIPLE.get(order["ticker"], 1)
    assert remaining >= -1e-8
    assert gross / 100000 <= a.MAX_BETA_GROSS + 1e-6


@pytest.mark.parametrize("cash", [0, 1, 100, 100000])
def test_sizing_does_not_spend_more_than_available_cash(cash):
    a = fresh()
    orders = a.orders_to_rebalance({"SPY": .24}, {}, 100000, {"SPY": 100}, cash)
    assert sum(o["quantity"] * 100 for o in orders) <= cash


@pytest.mark.parametrize("weight", [.239999, .24, .240001, .30, 1.0])
def test_name_and_beta_target_boundaries(weight):
    a = fresh()
    result = a._scale_caps({"SPY": weight, "QQQ": weight, "TQQQ": weight,
                            "SOXL": weight, "QLD": weight, "SSO": weight})
    assert all(0 < w <= .24 for w in result.values())
    assert sum(w * a.BETA_MULTIPLE.get(t, 1) for t, w in result.items()) <= 1.35 + 6e-6


def test_ordinary_repeated_call_has_no_duplicate_orders():
    a = fresh(); m = market(); ps = account(m)
    assert a.decide(m, ps, 100000)
    assert all(a.decide(m, ps, 100000) == [] for _ in range(12))
    # This fixture does not establish a daily guard for stale overweight accounts.


def test_sell_orders_do_not_exceed_holdings():
    a = fresh()
    orders = a.orders_to_rebalance({}, {"SPY": {"quantity": 123.5, "avg_cost": 100}},
                                   100000, {"SPY": 100}, 87650)
    assert orders == [{"ticker": "SPY", "side": "sell", "quantity": 123}]


def test_heavy_input_runtime():
    a = fresh(); base = market(count=220)
    tickers = json.loads((ROOT / "universe.json").read_text())["tickers"]
    m = {t: base["SPY"] for t in tickers}; m.update(base)
    start = time.perf_counter(); orders = a.decide(m, account(m), 100000)
    elapsed = time.perf_counter() - start
    assert elapsed < 5, f"Observed decision runtime {elapsed}s exceeds published limit"
    assert len(orders) <= 45


@pytest.mark.parametrize("name", ["calm_uptrend", "moderate_selloff", "vol_spike_snapback"])
def test_historical_decision_accounting_and_metrics(name, monkeypatch):
    sys.path.insert(0, str(ROOT))
    import preview
    regimes = json.loads(gzip.open(ROOT / "sample_regimes.json.gz", "rb").read())
    expected = json.loads((ROOT / "tests/e0_expected.json").read_text())[name]
    loader = preview.load_decide
    traces = []
    def traced_loader(path):
        decide = loader(path)
        def traced(m, ps, cash):
            orders = decide(m, ps, cash)
            traces.append(copy.deepcopy({"market_dates": {t: bars[-1]["ts"] if bars else None for t, bars in m.items()},
                                         "portfolio": ps, "cash": cash, "orders": orders}))
            return orders
        return traced
    monkeypatch.setattr(preview, "load_decide", traced_loader)
    result = preview.run_regime(ROOT / "agent.py", name, regimes[name])
    assert set(result.keys()) == set(expected["metrics"].keys())
    for k in ("name", "days", "trades", "errors", "max_conc_streak"):
        assert type(result[k]) is type(expected["metrics"][k])
        assert result[k] == expected["metrics"][k]
    for k in ("ret", "mdd", "sharpe", "calmar", "peak_gross", "peak_conc"):
        assert isinstance(result[k], float)
        assert math.isfinite(result[k])
        assert result[k] == pytest.approx(expected["metrics"][k], rel=1e-12, abs=1e-12)
    digest = hashlib.sha256(json.dumps(traces, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert digest == expected["decision_and_portfolio_sha256"]



def test_release_manifest_integrity():
    for line in (ROOT / "release-manifest.sha256").read_text().splitlines():
        expected, relative = line.split(" *", 1)
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
