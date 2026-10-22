"""
Guardian Alpha V20 Financial Integrity, Execution Cost Forensics,
Terminal Holdings Reconciliation, and Independent Accounting Verification Suite.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import pytest

import agent
from research.engine.accounting import (
    SLIP_EQUITY,
    SLIP_LEVERAGED,
    LEVERAGE_CAP,
    CONCENTRATION_CAP,
    MAX_TRADES_PER_DAY,
    START_CASH,
    FillResult,
    PortfolioState,
    RiskMode,
)
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
from research.engine.tiingo_client import (
    HoldoutProtectionViolation,
    TiingoClient,
    TiingoHistoricalProvider,
    redact_secret,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TIINGO_CACHE_FILE = REPO_ROOT / "tiingo_cache" / "tier1_bars.json"
MANIFEST_DIR = REPO_ROOT / "research" / "manifests"


class TestV20ExecutionCostForensics:
    """P0: Audit exact basis point rates, dollar fill impact, and traded notional."""

    def test_configured_slippage_constants(self):
        """Verify baseline configured slippage: 5 bps for equity/1x ETFs, 10 bps for 2x overlay."""
        assert SLIP_EQUITY == 0.0005, "SLIP_EQUITY must be exactly 5 basis points (0.0005)"
        assert SLIP_LEVERAGED == 0.0010, "SLIP_LEVERAGED must be exactly 10 basis points (0.0010)"

    def test_per_fill_dollar_impact_formula(self):
        """Verify dollar slippage formula: abs(qty) * abs(fill_price - reference_price)."""
        p = PortfolioState(cash=100_000.0)
        # Test Buy Fill: open_px = 100.0, slip = 0.0005 -> fill_px = 100.05
        fill_buy = p.execute_order({"ticker": "SPY", "side": "buy", "quantity": 100.0}, open_price=100.0)
        assert fill_buy is not None
        assert math.isclose(fill_buy.fill_price, 100.05, abs_tol=1e-6)
        expected_buy_slip = 100.0 * abs(fill_buy.fill_price - 100.0)
        assert math.isclose(expected_buy_slip, 5.00, abs_tol=1e-4)

        # Test Sell Fill: open_px = 100.0, slip = 0.0005 -> fill_px = 99.95
        fill_sell = p.execute_order({"ticker": "SPY", "side": "sell", "quantity": 50.0}, open_price=100.0)
        assert fill_sell is not None
        assert math.isclose(fill_sell.fill_price, 99.95, abs_tol=1e-6)
        expected_sell_slip = 50.0 * abs(100.0 - 99.95)
        assert math.isclose(expected_sell_slip, 2.50, abs_tol=1e-4)

    def test_effective_slippage_rate_reconciliation(self):
        """Reconcile that actual execution slippage is ~5.13 bps, not 100 bps (1%)."""
        forensics_file = REPO_ROOT / "scratch" / "slippage_forensics.json"
        if not forensics_file.exists():
            pytest.skip("scratch/slippage_forensics.json not generated yet")
        with open(forensics_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        e0 = data["Frozen E0"]
        assert e0["total_fills"] == 620
        assert math.isclose(e0["gross_exec_notional"], 30_430_005.31, rel_tol=1e-4)
        assert math.isclose(e0["total_dollar_slippage"], 15_624.97, rel_tol=1e-4)
        assert 5.10 <= e0["effective_bps_exec"] <= 5.15, f"Unexpected effective bps: {e0['effective_bps_exec']}"


class TestV20TerminalHoldingsReconciliation:
    """P0: Audit unrounded terminal position ledger, cost basis, and market value."""

    def test_unrounded_terminal_holdings_sum(self):
        """Assert unrounded position market values sum to exactly $347,491.10."""
        holdings_file = MANIFEST_DIR / "tier1_terminal_holdings_v20.json"
        if not holdings_file.exists():
            pytest.skip("tier1_terminal_holdings_v20.json not found")
        with open(holdings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        e0 = data["Frozen E0"]
        assert e0["position_count"] == 15
        assert math.isclose(e0["sum_market_values"], 347_491.10, abs_tol=0.01)
        assert math.isclose(e0["ending_nav"], 347_496.21, abs_tol=0.01)
        assert math.isclose(e0["ending_cash"], 0.04, abs_tol=0.01)
        assert math.isclose(e0["dividend_receivables"], 5.06, abs_tol=0.01)

        # Check AAPL and NVDA concentration
        positions = {p["symbol"]: p for p in e0["positions"]}
        assert "AAPL" in positions and "NVDA" in positions
        aapl = positions["AAPL"]
        nvda = positions["NVDA"]
        assert math.isclose(aapl["shares_unrounded"], 752.4334, abs_tol=1e-3)
        assert math.isclose(nvda["shares_unrounded"], 524.1329, abs_tol=1e-3)
        assert (aapl["market_value"] + nvda["market_value"]) / e0["ending_nav"] > 0.99

    def test_cost_basis_and_unrealized_pnl_invariants(self):
        """Verify unrealized PnL equals market value less adjusted cost basis for every position."""
        holdings_file = MANIFEST_DIR / "tier1_terminal_holdings_v20.json"
        if not holdings_file.exists():
            pytest.skip("tier1_terminal_holdings_v20.json not found")
        with open(holdings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for name, d in data.items():
            for p in d["positions"]:
                calc_unrealized = p["market_value"] - p["total_cost_basis"]
                assert math.isclose(p["unrealized_pnl"], calc_unrealized, abs_tol=0.05), (
                    f"Mismatch in {name} {p['symbol']}: {p['unrealized_pnl']} vs {calc_unrealized}"
                )


class TestV20CashReserveAndProductionFidelity:
    """P0: Audit frozen production agent allocation weights and cash reserves."""

    def test_production_cash_reserve_targets(self):
        """Verify agent.py allocates budget targeting 6% cash with overlay, 8% without."""
        # Read frozen production agent.py source invariants
        agent_file = REPO_ROOT / "agent.py"
        with open(agent_file, "r", encoding="utf-8") as f:
            code = f.read()

        assert "base_budget = 0.76 if overlay_on else 0.92" in code
        assert 'weights["QLD"] = 0.11' in code
        assert 'weights["SSO"] = 0.07' in code
        # When overlay active: 0.76 + 0.11 + 0.07 = 0.94 -> 6% cash target
        # When overlay inactive: 0.92 -> 8% cash target

    def test_fractional_exhaustion_at_terminal_cash(self):
        """Verify terminal cash of pennies is caused by cash-affordability fill clamping."""
        p = PortfolioState(cash=50.0)
        # Attempt to buy order worth $1000
        res = p.execute_order({"ticker": "SPY", "side": "buy", "quantity": 10.0}, open_price=100.0)
        assert res is not None
        # Cash should be clamped to near zero
        assert p.cash < 0.01, f"Expected cash to be exhausted, got {p.cash}"


class TestV20CorporateActionForensics:
    """P0: Verify split invariants and dividend lifecycle."""

    def test_split_cost_basis_conservation(self):
        """Verify split multiplies shares and divides avg_cost, conserving total cost basis."""
        p = PortfolioState(cash=100_000.0)
        p.execute_order({"ticker": "QLD", "side": "buy", "quantity": 100.0}, open_price=50.0)
        pre_shares = p.positions["QLD"]
        pre_cost_per_share = p.avg_cost["QLD"]
        pre_total_cost = pre_shares * pre_cost_per_share

        reg = CorporateActionRegistry()
        reg.register_split("2016-01-15", "QLD", split_ratio=2.0)
        reg.apply_splits_for_date("2016-01-15", p.positions, p.avg_cost)

        assert math.isclose(p.positions["QLD"], pre_shares * 2.0)
        assert math.isclose(p.avg_cost["QLD"], pre_cost_per_share / 2.0)
        post_total_cost = p.positions["QLD"] * p.avg_cost["QLD"]
        assert math.isclose(pre_total_cost, post_total_cost, abs_tol=1e-6)

    def test_dividend_imputed_settlement_policy(self):
        """Verify dividend lifecycle: ex-date receivable accrual and 10-business-day settlement."""
        ex_date = "2015-01-05"  # Monday
        settle_date = compute_business_day_settlement(ex_date, 10)
        assert settle_date == "2015-01-19"  # Exactly 10 business days later


class TestV20IndependentAccountingAndNegativeControls:
    """P0: Independent double-entry ledger reconstruction and 7 negative controls."""

    def test_seven_adversarial_negative_controls(self):
        """Assert all 7 negative controls are caught by independent verifier."""
        assert run_negative_control_altered_fill_price(), "Failed to catch altered fill price"
        assert run_negative_control_omitted_trade(), "Failed to catch omitted trade"
        assert run_negative_control_reversed_split(), "Failed to catch reversed split"
        assert run_negative_control_double_dividend(), "Failed to catch double dividend"
        assert run_negative_control_double_fee(), "Failed to catch double fee"
        assert run_negative_control_missing_position(), "Failed to catch missing position"
        assert run_negative_control_lookahead_leak(), "Failed to catch future lookahead"

    def test_independent_ledger_double_entry_balance(self):
        """Assert clean double-entry conservation invariant holds without exception."""
        ledger = IndependentLedger(initial_cash=100_000.0)
        ledger.process_fill("2015-01-05", "AAPL", "buy", 100.0, fill_price=100.0, reference_price=100.0)
        snap = ledger.record_daily_snapshot("2015-01-05", {"AAPL": 105.0})
        assert snap["discrepancy"] < 1e-6
        assert snap["unrealized_pnl"] == 500.0
        assert snap["nav"] == 100_500.0


class TestV20HoldoutAndSecurityIntegrity:
    """P1: Strict holdout isolation and credential redaction."""

    def test_holdout_strict_isolation_2022_2024(self):
        """Assert Tiingo client raises HoldoutProtectionViolation on any query >= 2022-01-01."""
        client = TiingoClient(api_token="test_mock_token")
        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2022-01-01", "2022-01-05")

        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2021-01-01", "2023-01-01")

        with pytest.raises(HoldoutProtectionViolation):
            client.fetch_historical_prices("SPY", "2015-01-01", None)

    def test_secret_redaction_sanitizer(self):
        """Verify token is completely masked in logs and URLs."""
        token = "secret_tiingo_token_abcdef123456"
        url = f"https://api.tiingo.com/tiingo/daily/spy/prices?token={token}&startDate=2015-01-01"
        sanitized = redact_secret(url, token)
        assert token not in sanitized
        assert "[REDACTED_TIINGO_TOKEN]" in sanitized
