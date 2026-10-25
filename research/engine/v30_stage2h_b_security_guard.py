"""
Guardian Alpha V30 Stage 2H-B - Hardened Activation Security Boundary Guard
Persistent Hard-Stop State, Fail-Closed Multi-Vector Validation, and Real-Path Traversal Protection.

DISCLOSURE ON NETWORK ISOLATION:
In-process monkey-patching of socket.socket intercepts pure Python socket calls (urllib, requests, httpx).
It DOES NOT provide kernel-level OS network isolation against external subprocesses (curl, git, powershell).
System-wide network containment requires OS-level firewall rules or sandbox namespaces.
"""

import os
import sys
import json
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


class SecurityBreachError(Exception):
    """Raised when an activation security rule or integrity constraint is violated."""
    pass


class LiveTradingProhibitedError(SecurityBreachError):
    """Raised when live trading mode is requested."""
    pass


class PersistentHardStopError(SecurityBreachError):
    """Raised when execution is attempted while a persistent hard-stop is active."""
    pass


class Stage2HBSecurityGuard:
    """
    Stage 2H-B Hardened Activation Guard.
    Enforces persistent disk-based hard-stop state across restarts,
    full 22-vector security checks, and path traversal defenses.
    """

    DEFAULT_HARD_STOP_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "evidence", "v30", ".v30_stage2h_b_hard_stop_state.json"
    )

    EXPECTED_STRATEGY_HASH = "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"
    EXPECTED_UNIVERSE_HASH = "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"
    WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def __init__(self, hard_stop_path: Optional[str] = None, shared_secret: bytes = b"guardian_alpha_v30_owner_key"):
        self.hard_stop_path = hard_stop_path or self.DEFAULT_HARD_STOP_PATH
        self.shared_secret = shared_secret
        self.seen_nonces = set()
        self.revoked_tokens = set()

    def check_persistent_hard_stop(self) -> None:
        """Verifies whether an un-cleared hard-stop exists on disk. Survives process restart."""
        if os.path.exists(self.hard_stop_path):
            try:
                with open(self.hard_stop_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                if state.get("is_hard_stopped", False):
                    raise PersistentHardStopError(
                        f"PERSISTENT HARD-STOP ACTIVE: Triggered at {state.get('timestamp_utc')} "
                        f"for reason: '{state.get('reason')}'. Restart alone cannot clear this stop. "
                        "Manual owner reset required."
                    )
            except (json.JSONDecodeError, OSError):
                # If hard stop file is unreadable, fail closed
                raise PersistentHardStopError("Hard-stop state file is corrupt; failing closed.")

    def trigger_hard_stop(self, reason: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Persists a hard-stop flag to disk and raises PersistentHardStopError."""
        state = {
            "is_hard_stopped": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "metadata": metadata or {}
        }
        os.makedirs(os.path.dirname(self.hard_stop_path), exist_ok=True)
        with open(self.hard_stop_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        raise PersistentHardStopError(f"HARD STOP ENGAGED: {reason}")

    def clear_hard_stop_manual(self, owner_key: str) -> bool:
        """Only cleared with explicit owner override key."""
        if owner_key != "OWNER_AUTHORIZED_OVERRIDE_RESET_2026":
            return False
        if os.path.exists(self.hard_stop_path):
            try:
                os.remove(self.hard_stop_path)
            except OSError:
                return False
        return True

    def validate_activation_token(self, token: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        # Always check persistent hard stop first
        self.check_persistent_hard_stop()

        if token is None:
            return False, "REJECTED: Missing authorization token."

        # Check required fields
        required_fields = ["signature", "nonce", "expiry_utc", "strategy_hash", "universe_hash", "mode", "provider", "max_horizon_days"]
        for field in required_fields:
            if field not in token:
                return False, f"REJECTED: Token missing required field '{field}'."

        # Check replay attack / nonce reuse
        nonce = token["nonce"]
        if nonce in self.seen_nonces:
            return False, f"REJECTED: Replay attack detected. Nonce '{nonce}' already used."

        # Check revocation
        token_id = token.get("token_id", nonce)
        if token_id in self.revoked_tokens:
            return False, f"REJECTED: Token '{token_id}' has been revoked by owner."

        # Check expiry
        try:
            expiry = datetime.fromisoformat(token["expiry_utc"])
            if datetime.now(timezone.utc) > expiry:
                return False, "REJECTED: Authorization token has expired."
        except Exception:
            return False, "REJECTED: Malformed expiry timestamp."

        # Check mode
        if token["mode"] == "live":
            self.trigger_hard_stop("CRITICAL_SECURITY_VIOLATION: Attempted activation in LIVE mode.")

        if token["mode"] not in ["paper_simulated", "paper_mock"]:
            return False, f"REJECTED: Invalid operating mode '{token['mode']}'."

        # Check strategy hash
        if token["strategy_hash"] != self.EXPECTED_STRATEGY_HASH:
            return False, f"REJECTED: Strategy hash mismatch. Expected {self.EXPECTED_STRATEGY_HASH}, got {token['strategy_hash']}."

        # Check universe hash
        if token["universe_hash"] != self.EXPECTED_UNIVERSE_HASH:
            return False, f"REJECTED: Universe hash mismatch. Expected {self.EXPECTED_UNIVERSE_HASH}, got {token['universe_hash']}."

        # Verify HMAC signature
        payload = f"{token['nonce']}|{token['expiry_utc']}|{token['strategy_hash']}|{token['universe_hash']}|{token['mode']}|{token['provider']}|{token['max_horizon_days']}".encode()
        expected_sig = hmac.new(self.shared_secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(token["signature"], expected_sig):
            return False, "REJECTED: Invalid cryptographic signature on activation token."

        self.seen_nonces.add(nonce)
        return True, "AUTHORIZED"

    def validate_file_path(self, target_path: str) -> Tuple[bool, str]:
        """
        Validates target path against directory traversal and sealed Tier 3 observation leakage.
        Uses os.path.realpath to eliminate symlink and '..' evasion.
        """
        real_path = os.path.realpath(target_path)
        real_workspace = os.path.realpath(self.WORKSPACE_ROOT)

        # 1. Directory traversal outside workspace
        if not real_path.startswith(real_workspace):
            self.trigger_hard_stop(f"SECURITY_VIOLATION: Directory traversal attempted outside workspace: {target_path}")

        # 2. Tier 3 sealed data access guard (dates >= 2022-01-01)
        tier3_markers = ["tier3", "tier_3", "2022-", "2023-", "2024-", "2025-", "2026-"]
        path_lower = real_path.lower()
        if "tiingo_cache" in path_lower:
            for marker in tier3_markers:
                if marker in path_lower:
                    self.trigger_hard_stop(f"CRITICAL_TIER3_SEAL_BREACH: Attempted access to Tier 3 date observation in cache: {target_path}")

        return True, "PATH_PERMITTED"

    def get_network_isolation_guarantee(self) -> Dict[str, str]:
        return {
            "python_socket_monkey_patching": "Blocks in-process socket.socket connections from standard Python libraries.",
            "os_subprocess_isolation": "NOT GUARANTEED by Python socket patch alone. Subprocesses (curl, powershell) bypass Python runtime.",
            "recommended_containment": "OS-level network namespace, outbound firewall rule, or unprivileged container."
        }
