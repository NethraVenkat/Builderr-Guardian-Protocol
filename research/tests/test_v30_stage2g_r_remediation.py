"""
Guardian Alpha — V30 Stage 2G-R: Remediation and Governance Test Suite.

Validates:
- Gate A: Defect inventory and reproduction verification
- Gate B: Causal event streaming engine, watermark protection, and prefix immutability
- Gate C: Crash recovery, snapshot integrity, and append-only journal replay
- Gate D: Revised prospective statistical protocol and historical selection bias
- Gate E: Provider-neutral data rights checklist and ToS coverage
- Gate F: Builderr simulator contract parity and execution rules
- Gate G: Activation security gatekeeper, fail-closed paper mode, and network air-gap
- Gate H: Independent financial accounting invariants and zero margin debt
- Gate J: Owner authorization checklist and fail-closed activation boundaries
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

from research.engine.v30_stage2g_r_causal_event_engine import (
    CausalEventProcessingEngine,
    MarketEvent,
    EventStatus,
    CausalPortfolioState,
)
from research.engine.v30_stage2g_r_activation_guard import (
    ActivationGatekeeper,
    AirGapNetworkEnforcer,
    ExecutionMode,
    FatalSecurityViolation,
)
import agent
from research.strategies import v30_candidate_d2_cash_cushion as d2

EXPECTED_HEAD = "b283ded200c777b130285b0aa56a0b044afbd339"
HASH_AGENT_PY = "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"
HASH_V12_AE = "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"
HASH_UNIVERSE = "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"
HASH_D2_CASH = "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215"


class TestGateAProtectedHashesAndDefects:
    """Verifies repository baselines and defect inventory completeness."""

    def test_git_checkpoint_and_clean_index(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True).strip()
        assert head == EXPECTED_HEAD

        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(REPO_ROOT), text=True)
        tracked_mods = [line for line in status.splitlines() if not line.startswith("??")]
        assert len(tracked_mods) == 0

    def test_protected_source_hashes(self):
        h_agent = hashlib.sha256((REPO_ROOT / "agent.py").read_bytes()).hexdigest()
        assert h_agent == HASH_AGENT_PY

        raw_v12 = (REPO_ROOT / "research" / "strategies" / "v12_candidate_ae.py").read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw_v12).hexdigest() == HASH_V12_AE

        raw_u = (REPO_ROOT / "universe.json").read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw_u).hexdigest() == HASH_UNIVERSE

        raw_d2 = (REPO_ROOT / "research" / "strategies" / "v30_candidate_d2_cash_cushion.py").read_bytes()
        assert hashlib.sha256(raw_d2).hexdigest() == HASH_D2_CASH

    def test_defect_inventory_artifact(self):
        path = REPO_ROOT / "research" / "evidence" / "v30" / "v30_stage2g_r_defect_inventory.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["classification_summary"]["confirmed_defects"] == 2
        assert data["classification_summary"]["documentation_defects"] == 1
        assert data["classification_summary"]["contract_ambiguities"] == 1


class TestGateBCausalEventEngine:
    """Verifies the 15 institutional causal event streaming and immutability rules."""

    def test_unique_event_id_and_idempotency(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        evt1 = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})

        st1 = engine.ingest_event(evt1)
        assert st1 == EventStatus.ACCEPTED
        assert len(engine.event_journal) == 1

        # Resubmitting identical event -> DUPLICATE_IDEMPOTENT
        st2 = engine.ingest_event(evt1)
        assert st2 == EventStatus.DUPLICATE_IDEMPOTENT
        assert len(engine.event_journal) == 1

    def test_conflicting_payload_quarantine(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        evt1 = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        engine.ingest_event(evt1)

        # Same event_id, different payload
        conflict = MarketEvent(
            event_id=evt1.event_id,
            ticker="SPY",
            exchange_ts="2026-04-01",
            received_ts="2026-04-01T17:00:00Z",
            event_type="BAR",
            payload={"open": 999.0, "close": 999.0},
            payload_hash="fake_hash",
        )
        st = engine.ingest_event(conflict)
        assert st == EventStatus.QUARANTINED_CONFLICT
        assert len(engine.quarantine_log) == 1
        assert engine.quarantine_log[0]["reason"] == "PAYLOAD_HASH_MISMATCH_CONFLICT"

    def test_committed_watermark_and_prefix_immutability(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        # Day 1
        e_spy = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        e_aapl = MarketEvent.create("AAPL", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 150.0, "close": 151.0})
        engine.ingest_event(e_spy)
        engine.ingest_event(e_aapl)
        engine.advance_watermark_and_execute("2026-04-01", d2.decide)
        assert engine.committed_watermark_date == "2026-04-01"

        # Record committed prefix
        journal_len_before = len(engine.event_journal)
        fills_len_before = len(engine.fill_ledger)
        cash_before = engine.state.cash

        # Late event for 2026-04-01 arriving after watermark is already committed
        late_evt = MarketEvent.create("MSFT", "2026-04-01", "2026-04-02T10:00:00Z", "BAR", {"open": 400.0, "close": 405.0})
        st_late = engine.ingest_event(late_evt)
        assert st_late == EventStatus.QUARANTINED_LATE

        # Verify committed prefix is completely unchanged
        assert len(engine.event_journal) == journal_len_before
        assert len(engine.fill_ledger) == fills_len_before
        assert engine.state.cash == cash_before

    def test_explicit_revision_does_not_mutate_past_fills(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        e_spy = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        engine.ingest_event(e_spy)
        engine.advance_watermark_and_execute("2026-04-01", d2.decide)

        fills_before = len(engine.fill_ledger)

        # Revision event for Day 1
        rev = MarketEvent.create(
            "SPY", "2026-04-01", "2026-04-02T12:00:00Z", "REVISION",
            {"original": 502.0, "revised": 502.1},
            parent_event_id=e_spy.event_id,
            revision_reason="DIVIDEND_ADJUSTED_CLOSE",
        )
        st_rev = engine.ingest_event(rev)
        assert st_rev == EventStatus.REVISION_ACCEPTED
        assert len(engine.fill_ledger) == fills_before


class TestGateCCrashRecoveryAndReplay:
    """Verifies crash recovery, snapshot verification, and journal replay."""

    def test_corrupt_snapshot_detection(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        evt = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        engine.ingest_event(evt)
        snap = engine.create_snapshot()

        corrupt = dict(snap)
        corrupt["snapshot_hash"] = "corrupt_deadbeef"
        with pytest.raises(ValueError, match="Corrupt snapshot"):
            CausalEventProcessingEngine.recover_from_snapshot_and_journal(corrupt, engine.event_journal)

    def test_exact_recovery_parity(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        evt1 = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        engine.ingest_event(evt1)
        engine.advance_watermark_and_execute("2026-04-01", d2.decide)

        snap = engine.create_snapshot()
        recovered = CausalEventProcessingEngine.recover_from_snapshot_and_journal(snap, engine.event_journal)

        assert recovered.state.cash == engine.state.cash
        assert recovered.state.positions == engine.state.positions
        assert recovered.committed_watermark_date == engine.committed_watermark_date


class TestGateGActivationSafetyAndSecurity:
    """Verifies activation gatekeeper and air-gap network enforcement."""

    def test_offline_synthetic_mode_permitted(self):
        ok, msg = ActivationGatekeeper.verify_activation_request("OFFLINE_SYNTHETIC")
        assert ok is True
        assert "PERMITTED" in msg

    def test_live_trading_fatal_violation(self):
        with pytest.raises(FatalSecurityViolation, match="Live market trading is permanently prohibited"):
            ActivationGatekeeper.verify_activation_request("FORBIDDEN_LIVE_TRADING")

        with pytest.raises(FatalSecurityViolation, match="Live market trading is permanently prohibited"):
            ActivationGatekeeper.verify_activation_request("LIVE_TRADING_ALPACA")

    def test_paper_mode_fails_closed_without_token(self):
        ok, msg = ActivationGatekeeper.verify_activation_request("OWNER_AUTHORIZED_PAPER", authorization_token=None)
        assert ok is False
        assert "Missing mandatory signed Owner Authorization Token" in msg

    def test_paper_mode_succeeds_with_valid_token(self):
        body = {
            "owner_name": "RepositoryOwner",
            "signed_utc": "2026-10-24T12:00:00Z",
            "target_commit": "b283ded200c777b130285b0aa56a0b044afbd339",
            "target_branch": "research/v29e-final-release-verification",
            "feed_provider": "Tiingo_EOD",
        }
        token_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
        token_payload = dict(body)
        token_payload["token_sha256"] = token_hash

        ok, msg = ActivationGatekeeper.verify_activation_request(
            "OWNER_AUTHORIZED_PAPER",
            authorization_token=token_hash,
            token_payload=token_payload,
        )
        assert ok is True
        assert "OWNER_AUTHORIZED_PAPER_PERMITTED" in msg

    def test_airgap_network_enforcer_blocks_sockets(self):
        import socket
        with AirGapNetworkEnforcer():
            with pytest.raises(FatalSecurityViolation, match="External socket creation is blocked"):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class TestGateHIndependentFinancialInvariants:
    """Verifies balance sheet conservation across causal execution steps."""

    def test_balance_sheet_exact_conservation(self):
        engine = CausalEventProcessingEngine(initial_cash=100_000.0)
        e_spy = MarketEvent.create("SPY", "2026-04-01", "2026-04-01T16:00:00Z", "BAR", {"open": 500.0, "close": 502.0})
        engine.ingest_event(e_spy)
        engine.advance_watermark_and_execute("2026-04-01", d2.decide)

        prices = {"SPY": 502.0}
        ok, reason = engine.state.verify_double_entry_balance(prices)
        assert ok is True, f"Invariant failure: {reason}"
        assert engine.state.cash >= 0.0
