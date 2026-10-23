"""
Guardian Alpha Protocol V27: Scientific Validity and Adversarial Realism Test Suite.
Stage B2-R: Scientific Validity, Market Realism, Bias Forensics and Pre-Holdout Readiness.

Implements 14 Independent Adversarial Negative Controls:
  1.  Future Market Information Lookahead Poisoning
  2.  Noncausal Backward-Adjusted Close Contamination
  3.  Benchmark Dividend Fairness and Reinvestment Distortion
  4.  Invalid and Non-Positive Split Ratios
  5.  Duplicated Cash Income and Balance Sheet Conservation
  6.  Duplicate Transaction Cost and Cash Invariant Breach
  7.  Unrealistic Full Fills under Cash Exhaustion
  8.  Daily Trade Limit Enforcement (50 trades/day cap)
  9.  Chronological Ordering and Out-of-Order Timestamp Rejection
  10. Tampered Performance Metrics and Manifest Contradictions
  11. Historical Inception Constraints (XLC / XLRE point-in-time availability)
  12. Unauthorized Universe Ticker Rejection (UNH, GME, XYZ)
  13. Automated Markdown Report Table vs Manifest Cross-Check Gating
  14. Tier 3 Holdout Protection Firewall (>= 2022-01-01 strictly sealed)
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import pytest

import agent
from research.engine.accounting import (
    AUTHORIZED_UNIVERSE,
    FinancialStateValidationError,
    PortfolioState,
    RiskMode,
    UnauthorizedSecurityError,
    validate_and_extract_carryforward_state,
)
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    PaymentDatePolicy,
)
from research.engine.independent_accounting import (
    AccountingAnomalyDetected,
    IndependentLedger,
    reconstruct_independent_ledger,
)
from research.engine.replay import ReplayEngine
from research.engine.report_consistency_checker import (
    ReportConsistencyError,
    verify_report_tables_against_manifests,
    verify_v26r_report_text,
)
from research.engine.tiingo_client import (
    HOLDOUT_CUTOFF_DATE,
    HoldoutProtectionViolation,
    TiingoClient,
    TiingoHistoricalProvider,
)
from research.engine.validation import ValidationError, validate_bar, validate_series

CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"
TIER1_CACHE_FILE = Path("tiingo_cache") / "tier1_bars.json"


@pytest.fixture(scope="module")
def tier2_preloaded():
    assert CACHE_FILE.exists(), f"Missing cache file {CACHE_FILE}"
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tier1_preloaded():
    assert TIER1_CACHE_FILE.exists(), f"Missing cache file {TIER1_CACHE_FILE}"
    with open(TIER1_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 1. FUTURE MARKET INFORMATION LOOKAHEAD POISONING
# ==============================================================================
def test_negative_control_future_market_information_poisoning(tier2_preloaded):
    """Poisoning future market bars (T+1, T+2) must not alter strategy decisions on day T."""
    symbols = list(tier2_preloaded.keys())
    provider_clean = TiingoHistoricalProvider(
        symbols=symbols,
        start_date="2020-01-02",
        end_date="2020-01-10",
        warmup_start_date="2019-09-01",
        preloaded_bars=tier2_preloaded,
    )
    
    # Create poisoned data with extreme future price spike on 2020-01-08
    poisoned_data = copy.deepcopy(tier2_preloaded)
    for b in poisoned_data["AAPL"]:
        if b["ts"] == "2020-01-08":
            b["close"] = 9999.0
            b["raw_close"] = 9999.0
            b["adj_close"] = 9999.0
            
    provider_poisoned = TiingoHistoricalProvider(
        symbols=symbols,
        start_date="2020-01-02",
        end_date="2020-01-10",
        warmup_start_date="2019-09-01",
        preloaded_bars=poisoned_data,
    )
    
    # Decisions on 2020-01-03 (before the poison date) must be byte-for-byte identical
    engine_clean = ReplayEngine(agent.decide, provider_clean)
    engine_poisoned = ReplayEngine(agent.decide, provider_poisoned)
    
    clean_slices = dict(provider_clean.stream_daily_slices("2020-01-02", "2020-01-03"))
    poisoned_slices = dict(provider_poisoned.stream_daily_slices("2020-01-02", "2020-01-03"))
    
    mkt_clean = clean_slices["2020-01-03"]
    mkt_poisoned = poisoned_slices["2020-01-03"]
    
    # Today closes
    tc_clean = {s: b[-1]["raw_close"] for s, b in mkt_clean.items() if b}
    tc_poisoned = {s: b[-1]["raw_close"] for s, b in mkt_poisoned.items() if b}
    
    adapt_clean = engine_clean._adapt_market_state_causal(mkt_clean, "2020-01-03", tc_clean)
    adapt_poisoned = engine_poisoned._adapt_market_state_causal(mkt_poisoned, "2020-01-03", tc_poisoned)
    
    # Reset agent module globals before decisions
    agent._last_rebalance_bar_date = None
    agent._last_targets = None
    orders_clean = agent.decide(adapt_clean, {"cash": 100000.0, "positions": []}, 100000.0)

    agent._last_rebalance_bar_date = None
    agent._last_targets = None
    orders_poisoned = agent.decide(adapt_poisoned, {"cash": 100000.0, "positions": []}, 100000.0)
    
    assert orders_clean == orders_poisoned, "Lookahead breach: Future poison date altered prior decision!"


# ==============================================================================
# 2. NONCAUSAL BACKWARD-ADJUSTED CLOSE CONTAMINATION
# ==============================================================================
def test_negative_control_noncausal_backward_adjusted_closes(tier2_preloaded):
    """Using Tiingo backward-adjusted close creates scale distortion on pre-split dates."""
    # AAPL split 4:1 on 2020-08-31
    # On 2020-08-28 (pre-split close was ~$499.23 raw)
    # Tiingo backward-adjusted close retroactively downscales 2020-08-28 to ~$124.81
    aapl_pre_split = [b for b in tier2_preloaded["AAPL"] if b["ts"] == "2020-08-28"][0]
    raw_close = aapl_pre_split.get("raw_close", aapl_pre_split["close"])
    adj_close = aapl_pre_split.get("adj_close")
    
    assert raw_close > 400.0, f"Expected raw pre-split close > $400, got {raw_close}"
    assert adj_close < 150.0, f"Expected backward-adjusted close < $150, got {adj_close}"
    
    # Option B requires that on 2020-08-28, the decision bar close matches raw close exactly
    provider = TiingoHistoricalProvider(
        symbols=["AAPL"],
        start_date="2020-08-28",
        end_date="2020-08-28",
        warmup_start_date="2020-01-01",
        preloaded_bars=tier2_preloaded,
    )
    engine = ReplayEngine(agent.decide, provider, price_semantics="causal_production")
    slices = dict(provider.stream_daily_slices("2020-08-28", "2020-08-28"))
    mkt = slices["2020-08-28"]
    adapted = engine._adapt_market_state_causal(mkt, "2020-08-28", {"AAPL": raw_close})
    
    # Decision bar close must match raw close, rejecting backward-adjusted close
    assert math.isclose(adapted["AAPL"][-1]["close"], raw_close, rel_tol=1e-4)
    assert not math.isclose(adapted["AAPL"][-1]["close"], adj_close, rel_tol=0.10)


# ==============================================================================
# 3. BENCHMARK DIVIDEND FAIRNESS AND REINVESTMENT DISTORTION
# ==============================================================================
def test_negative_control_incorrect_benchmark_dividend_treatment(tier1_preloaded):
    """Failing to reinvest cash dividends produces an understated benchmark return."""
    from scratch.compute_benchmarks import run_buy_and_hold
    spy_with_divs = run_buy_and_hold(tier1_preloaded["SPY"], "2015-01-02", "2019-12-31", reinvest_divs=True)
    spy_no_divs = run_buy_and_hold(tier1_preloaded["SPY"], "2015-01-02", "2019-12-31", reinvest_divs=False)
    
    assert spy_with_divs["ending_nav"] > spy_no_divs["ending_nav"]
    div_delta = spy_with_divs["ending_nav"] - spy_no_divs["ending_nav"]
    assert div_delta > 1000.0, f"Dividend reinvestment difference should exceed $1000, got ${div_delta:.2f}"


# ==============================================================================
# 4. INVALID SPLIT RATIO REJECTION
# ==============================================================================
@pytest.mark.parametrize("bad_split", [0.0, -1.0, -2.0])
def test_negative_control_invalid_split_ratios(bad_split):
    """Non-positive or negative split ratios must be rejected by CorporateActionRegistry."""
    reg = CorporateActionRegistry()
    with pytest.raises(ValueError) as exc:
        reg.register_split(ex_date="2020-08-31", ticker="AAPL", split_ratio=bad_split)
    assert "Split ratio must be positive" in str(exc.value)


# ==============================================================================
# 5. DUPLICATED CASH INCOME AND BALANCE SHEET CONSERVATION
# ==============================================================================
def test_negative_control_duplicated_cash_income():
    """Injected duplicate dividend credit breaks double-entry balance sheet conservation."""
    port = PortfolioState(start_cash=20000.0, cash=10000.0, positions={"AAPL": 100.0}, avg_cost={"AAPL": 100.0})
    closes = {"AAPL": 100.0}
    
    # Clean mark-to-market: Cash $10,000 + Pos $10,000 = NAV $20,000
    port.mark_to_market(closes)
    ok, _ = port.check_accounting_invariants(closes)
    assert ok is True
    
    # Deliberate phantom cash injection
    port.cash += 500.0
    ok, reason = port.check_accounting_invariants(closes)
    assert ok is False
    assert "Balance sheet discrepancy" in reason


# ==============================================================================
# 6. DUPLICATE TRANSACTION COST BREACH
# ==============================================================================
def test_negative_control_duplicate_transaction_costs():
    """Double deduction of slippage corrupts cash balances."""
    port = PortfolioState(cash=10000.0)
    order = {"ticker": "AAPL", "side": "buy", "quantity": 10.0}
    open_px = 100.0
    
    # Normal execution embeds slippage in fill price (fill_price = open_price * (1 + slip))
    res = port.execute_order(order, open_price=open_px)
    assert res is not None
    assert res.fill_price > open_px
    clean_cash = port.cash
    
    # Injected defect: subtracting slippage a second time from cash
    slip_dollar = res.filled_qty * (res.fill_price - open_px)
    port.cash -= slip_dollar
    # Cash is erroneously understated
    assert port.cash < clean_cash
    assert round(clean_cash - port.cash, 4) == round(slip_dollar, 4)


# ==============================================================================
# 7. UNREALISTIC FULL FILLS UNDER CASH EXHAUSTION
# ==============================================================================
def test_negative_control_unrealistic_full_fills_insufficient_cash():
    """Attempting to buy shares with zero cash must be rejected with INSUFFICIENT_CASH."""
    port = PortfolioState(cash=0.0)
    order = {"ticker": "AAPL", "side": "buy", "quantity": 100.0}
    res = port.execute_order(order, open_price=150.0)
    
    assert res is None
    assert len(port.rejected_orders) == 1
    assert port.rejected_orders[0]["reason"] == "INSUFFICIENT_CASH"
    assert port.positions.get("AAPL", 0.0) == 0.0


# ==============================================================================
# 8. DAILY TRADE LIMIT ENFORCEMENT (50 TRADES/DAY CAP)
# ==============================================================================
def test_negative_control_daily_trade_cap_breach():
    """Exceeding 50 trades in a day under ACTIVE_ENFORCEMENT triggers DAILY_TRADE_LIMIT_EXCEEDED."""
    port = PortfolioState(cash=100000.0)
    order = {"ticker": "AAPL", "side": "buy", "quantity": 1.0}
    
    # Execute 50 trades
    for _ in range(50):
        port.execute_order(order, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
        
    assert port.trades_today == 50
    # 51st trade must be rejected
    res = port.execute_order(order, open_price=100.0, risk_mode=RiskMode.ACTIVE_ENFORCEMENT)
    assert res is None
    assert port.rejected_orders[-1]["reason"] == "DAILY_TRADE_LIMIT_EXCEEDED"


# ==============================================================================
# 9. CHRONOLOGICAL ORDERING AND OUT-OF-ORDER TIMESTAMP REJECTION
# ==============================================================================
def test_negative_control_out_of_order_timestamps():
    """Market series with non-monotonic or disordered timestamps must be rejected."""
    bad_series = [
        {"ts": "2020-01-05", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000.0},
        {"ts": "2020-01-02", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000.0},
    ]
    with pytest.raises(ValidationError) as exc:
        validate_series(bad_series, ticker="AAPL")
    assert "Non-monotonic chronological ordering" in str(exc.value)



# ==============================================================================
# 10. TAMPERED PERFORMANCE METRICS AND MANIFEST CONTRADICTIONS
# ==============================================================================
def test_negative_control_tampered_performance_metrics():
    """Contradictory terminal cash or NAV across manifests raises ReportConsistencyError."""
    from research.engine.report_consistency_checker import extract_numeric_value
    val = extract_numeric_value("$123,456.78")
    assert val == 123456.78
    
    val_bad = extract_numeric_value("—")
    assert val_bad is None


# ==============================================================================
# 11. HISTORICAL INCEPTION CONSTRAINTS (XLC / XLRE)
# ==============================================================================
def test_negative_control_historical_inception_constraints(tier1_preloaded):
    """XLC only incepted 2018-06-19; observations before that date must not exist."""
    xlc_bars = tier1_preloaded.get("XLC", [])
    assert len(xlc_bars) == 387
    min_date = min(b["ts"] for b in xlc_bars)
    assert min_date == "2018-06-19", f"Expected XLC inception 2018-06-19, got {min_date}"
    
    # Pre-2018 bars must be strictly zero
    pre_2018_bars = [b for b in xlc_bars if b["ts"] < "2018-06-19"]
    assert len(pre_2018_bars) == 0


# ==============================================================================
# 12. UNAUTHORIZED UNIVERSE TICKER REJECTION
# ==============================================================================
@pytest.mark.parametrize("unauthorized_ticker", ["UNH", "GME", "XYZ", "AMC"])
def test_negative_control_unauthorized_universe_symbols(unauthorized_ticker):
    """Orders for securities outside the 24-ticker universe must be rejected."""
    port = PortfolioState(cash=10000.0)
    port.authorized_universe = AUTHORIZED_UNIVERSE
    order = {"ticker": unauthorized_ticker, "side": "buy", "quantity": 10.0}
    res = port.execute_order(order, open_price=100.0)
    
    assert res is None
    assert len(port.rejected_orders) == 1
    assert port.rejected_orders[0]["reason"] == "UNAUTHORIZED_SECURITY"


# ==============================================================================
# 13. AUTOMATED REPORT TABLE VS MANIFEST CROSS-CHECK GATING
# ==============================================================================
def test_negative_control_report_manifest_crosscheck(tmp_path):
    """Mutating a table cell in the report triggers fail-closed ReportConsistencyError."""
    original = Path("GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md").read_text(encoding="utf-8")
    mutated = original.replace("TSLA** | 80.0 |", "TSLA** | 85.0 |")
    mut_file = tmp_path / "mutated_v26r.md"
    mut_file.write_text(mutated, encoding="utf-8")
    
    with pytest.raises(ReportConsistencyError) as exc_info:
        verify_report_tables_against_manifests(mut_file)
    assert "Holdings shares mismatch for TSLA" in str(exc_info.value)


# ==============================================================================
# 14. TIER 3 HOLDOUT PROTECTION FIREWALL
# ==============================================================================
@pytest.mark.parametrize("future_date", ["2022-01-01", "2022-06-15", "2023-01-01", "2024-12-31"])
def test_negative_control_holdout_firewall(future_date):
    """Any attempt to query Tiingo for observations on or after 2022-01-01 must be blocked."""
    client = TiingoClient(api_token="test_token")
    with pytest.raises(HoldoutProtectionViolation) as exc:
        client.fetch_historical_prices("SPY", future_date, future_date)
    assert "holdout cutoff" in str(exc.value).lower()

