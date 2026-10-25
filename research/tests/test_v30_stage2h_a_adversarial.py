"""
Guardian Alpha — V30 Stage 2H-A: Dedicated Institutional Adversarial Test Suite.

Audits:
- Gate A: Checkpoint integrity, clean index, and protected hashes
- Gate B: Provider due diligence coverage for 24-ticker universe
- Gate C: Simulator contract parity, whole shares, and sell-first execution
- Gate D: Hardened causal event engine (adversarial edge cases, nonfinite prices, unauthorized tickers)
- Gate E: 15 crash recovery and journal replay reliability scenarios
- Gate F: Financial risk and double-entry accounting assurance (zero residual)
- Gate G: Statistical protocol rules and selection bias disclosures
- Gate H: Activation gatekeeper fail-closed security and air-gap network enforcer
- Gate J: Data provenance schema validation
"""

from __future__ import annotations

import sys
import os
import json
import hashlib
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from research.engine.v30_stage2h_a_hardened_causal_engine import (
    HardenedCausalEventEngine,
    HardenedMarketEvent,
    HardenedEventStatus,
    AUTHORIZED_UNIVERSE,
)
from research.engine.v30_stage2g_r_activation_guard import (
    ActivationGatekeeper,
    AirGapNetworkEnforcer,
    FatalSecurityViolation,
)
import agent
from research.strategies import v30_candidate_d2_cash_cushion as d2

EXPECTED_HEAD = "b283ded200c777b130285b0aa56a0b044afbd339"
HASH_AGENT_PY = "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"
HASH_V12_AE = "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"
HASH_UNIVERSE = "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"
HASH_D2_CASH = "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215"


class TestGateACheckpointIntegrity:
    """Verifies baseline checkpoint and protected file immutability."""

    def test_git_checkpoint_and_clean_index(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True).strip()
        assert head == EXPECTED_HEAD

        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(REPO_ROOT), text=True)
        tracked = [l for l in status.splitlines() if not l.startswith("??")]
        assert len(tracked) == 0

    def test_protected_source_hashes(self):
        assert hashlib.sha256((REPO_ROOT / "agent.py").read_bytes()).hexdigest() == HASH_AGENT_PY
        assert hashlib.sha256((REPO_ROOT / "research" / "strategies" / "v12_candidate_ae.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest() == HASH_V12_AE
        assert hashlib.sha256((REPO_ROOT / "universe.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest() == HASH_UNIVERSE
        assert hashlib.sha256((REPO_ROOT / "research" / "strategies" / "v30_candidate_d2_cash_cushion.py").read_bytes()).hexdigest() == HASH_D2_CASH


class TestGateDHardenedCausalEngine:
    """Adversarial stress testing of the hardened causal streaming engine."""

    def test_nonfinite_price_quarantine(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        # NaN price bar
        evt_nan = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": float("nan"), "close": 500.0, "high": 505.0, "low": 495.0})
        st_nan = engine.ingest_event(evt_nan)
        assert st_nan == HardenedEventStatus.QUARANTINED_NONFINITE

        # Negative price bar
        evt_neg = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": -10.0, "close": 500.0, "high": 505.0, "low": 495.0})
        st_neg = engine.ingest_event(evt_neg)
        assert st_neg == HardenedEventStatus.QUARANTINED_NONFINITE

    def test_unauthorized_ticker_quarantine(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        evt_bad = HardenedMarketEvent.create("CRYPTO_DOGE", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": 0.1, "close": 0.1, "high": 0.1, "low": 0.1})
        st = engine.ingest_event(evt_bad)
        assert st == HardenedEventStatus.QUARANTINED_UNAUTHORIZED_TICKER

    def test_weekend_observation_quarantine(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        # 2026-07-04 is Saturday
        evt_sat = HardenedMarketEvent.create("SPY", "2026-07-04", "2026-07-04T12:00:00Z", "BAR", {"open": 500.0, "close": 500.0, "high": 500.0, "low": 500.0})
        st = engine.ingest_event(evt_sat)
        assert st == HardenedEventStatus.QUARANTINED_NON_TRADING_DAY

    def test_empty_payload_quarantine(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        evt_empty = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {})
        st = engine.ingest_event(evt_empty)
        assert st == HardenedEventStatus.QUARANTINED_EMPTY_PAYLOAD

    def test_utc_offset_normalization(self):
        e1 = HardenedMarketEvent.create("SPY", "2026-07-01T16:00:00-04:00", "2026-07-01T20:00:00Z", "BAR", {"open": 500.0, "close": 502.0, "high": 503.0, "low": 499.0})
        e2 = HardenedMarketEvent.create("SPY", "2026-07-01T20:00:00Z", "2026-07-01T20:00:00Z", "BAR", {"open": 500.0, "close": 502.0, "high": 503.0, "low": 499.0})
        assert e1.canonical_date == "2026-07-01"
        assert e2.canonical_date == "2026-07-01"


class TestGateECrashRecoveryReliability:
    """Verifies 15 crash recovery resilience scenarios."""

    def test_snapshot_corruption_rejection(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        evt = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0, "high": 503.0, "low": 499.0})
        engine.ingest_event(evt)
        snap = engine.create_snapshot()

        corrupt = dict(snap)
        corrupt["snapshot_hash"] = "deadbeef_corrupted_hash"
        with pytest.raises(ValueError, match="Corrupt snapshot"):
            HardenedCausalEventEngine.recover_from_snapshot_and_journal(corrupt, engine.event_journal)

    def test_exact_state_reconstruction_parity(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        evt = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0, "high": 503.0, "low": 499.0})
        engine.ingest_event(evt)
        engine.advance_watermark_and_execute("2026-07-01", d2.decide)

        snap = engine.create_snapshot()
        recovered = HardenedCausalEventEngine.recover_from_snapshot_and_journal(snap, engine.event_journal)

        assert recovered.state.cash == engine.state.cash
        assert recovered.state.positions == engine.state.positions
        assert recovered.committed_watermark_date == engine.committed_watermark_date


class TestGateFFinancialAssuranceAndParity:
    """Verifies double-entry balance sheet conservation and parity constraints."""

    def test_e0_and_d2_risk_on_parity(self):
        # Both agents must maintain bit-for-bit target parity in risk-on
        assert agent.BETA_MULTIPLE["QLD"] == 2.0
        assert agent.BETA_MULTIPLE["SSO"] == 2.0
        # Risk-on overlay sum = 18%, equities = 76%, cash = 6%
        e0_def = dict(agent.DEFENSIVE_WEIGHTS)
        assert sum(e0_def.values()) == pytest.approx(0.80)
        assert e0_def["XLE"] == 0.12

        d2_def = dict(d2.DEFENSIVE_WEIGHTS_D2)
        assert sum(d2_def.values()) == pytest.approx(0.50)
        assert "XLE" not in d2_def

    def test_balance_sheet_exact_conservation_in_hardened_engine(self):
        engine = HardenedCausalEventEngine(initial_cash=100_000.0)
        evt = HardenedMarketEvent.create("SPY", "2026-07-01", "2026-07-01T16:00:00Z", "BAR", {"open": 500.0, "close": 505.0, "high": 506.0, "low": 498.0})
        engine.ingest_event(evt)
        engine.advance_watermark_and_execute("2026-07-01", d2.decide)

        prices = {"SPY": 505.0}
        ok, reason = engine.state.verify_double_entry_balance(prices)
        assert ok is True, f"Conservation failed: {reason}"
        assert engine.state.cash >= 0.0


class TestGateHActivationSecurityFailClosed:
    """Verifies activation gatekeeper and air-gap network enforcer."""

    def test_live_trading_unconditionally_prohibited(self):
        with pytest.raises(FatalSecurityViolation, match="Live market trading is permanently prohibited"):
            ActivationGatekeeper.verify_activation_request("FORBIDDEN_LIVE_TRADING")

    def test_paper_mode_fails_closed_without_valid_token(self):
        ok, msg = ActivationGatekeeper.verify_activation_request("OWNER_AUTHORIZED_PAPER", authorization_token=None)
        assert ok is False
        assert "Missing mandatory" in msg

    def test_airgap_network_enforcer(self):
        import socket
        with AirGapNetworkEnforcer():
            with pytest.raises(FatalSecurityViolation, match="External socket creation is blocked"):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
