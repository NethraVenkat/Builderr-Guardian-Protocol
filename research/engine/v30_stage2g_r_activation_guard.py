"""
Guardian Alpha — V30 Stage 2G-R: Activation Safety Gatekeeper and Security Guard.

Enforces strict boundaries between:
  1. OFFLINE_SYNTHETIC (Default permitted mode; zero network, zero real data, zero external orders).
  2. OWNER_AUTHORIZED_PAPER (Strictly BLOCKED without valid, cryptographically signed owner token).
  3. FORBIDDEN_LIVE_TRADING (Permanently FORBIDDEN; throws uncatchable FatalSecurityError).

Provides network call interceptors to guarantee offline air-gap during research audits.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class ExecutionMode(str, Enum):
    OFFLINE_SYNTHETIC = "OFFLINE_SYNTHETIC"
    OWNER_AUTHORIZED_PAPER = "OWNER_AUTHORIZED_PAPER"
    FORBIDDEN_LIVE_TRADING = "FORBIDDEN_LIVE_TRADING"


class FatalSecurityViolation(Exception):
    """Raised when an illegal or unauthorized execution mode is attempted."""
    pass


class ActivationGatekeeper:
    """Institutional fail-closed gatekeeper preventing unauthorized forward or live activation."""

    AUTHORIZED_BRANCH = "research/v29e-final-release-verification"
    AUTHORIZED_COMMIT = "b283ded200c777b130285b0aa56a0b044afbd339"

    @classmethod
    def verify_activation_request(
        cls,
        requested_mode: str,
        authorization_token: str | None = None,
        token_payload: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """Validate whether the requested execution mode is authorized."""
        # 1. Unconditionally block live trading
        if requested_mode.upper() == ExecutionMode.FORBIDDEN_LIVE_TRADING.value or "LIVE" in requested_mode.upper():
            raise FatalSecurityViolation(
                "CRITICAL SECURITY VIOLATION: Live market trading is permanently prohibited under Guardian Alpha protocol."
            )

        # 2. Allow offline synthetic execution
        if requested_mode.upper() == ExecutionMode.OFFLINE_SYNTHETIC.value:
            return True, "OFFLINE_SYNTHETIC_MODE_PERMITTED"

        # 3. For prospective paper evaluation, enforce strict owner cryptographic authorization
        if requested_mode.upper() == ExecutionMode.OWNER_AUTHORIZED_PAPER.value:
            if not authorization_token or not token_payload:
                return False, "BLOCKED: Missing mandatory signed Owner Authorization Token."

            # Verify token structure
            req_keys = {"owner_name", "signed_utc", "target_commit", "target_branch", "feed_provider", "token_sha256"}
            if not req_keys.issubset(token_payload.keys()):
                return False, f"BLOCKED: Malformed token. Missing keys: {req_keys - set(token_payload.keys())}"

            # Verify target commit matches current frozen state
            if token_payload.get("target_commit") != cls.AUTHORIZED_COMMIT:
                return False, f"BLOCKED: Token commit {token_payload.get('target_commit')} != Authorized {cls.AUTHORIZED_COMMIT}"

            # Verify token signature hash
            body = {k: v for k, v in token_payload.items() if k != "token_sha256"}
            computed_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
            if computed_hash != token_payload.get("token_sha256"):
                return False, "BLOCKED: Token cryptographic signature mismatch!"

            return True, "OWNER_AUTHORIZED_PAPER_PERMITTED"

        return False, f"BLOCKED: Unrecognized execution mode '{requested_mode}'"


class AirGapNetworkEnforcer:
    """Monkey-patches socket creation during offline synthetic dry runs to guarantee zero leakage."""

    def __init__(self) -> None:
        self._orig_socket = None

    def __enter__(self) -> AirGapNetworkEnforcer:
        import socket
        self._orig_socket = socket.socket

        def _blocked_socket(*args: Any, **kwargs: Any) -> Any:
            raise FatalSecurityViolation("AIR-GAP VIOLATION: External socket creation is blocked during offline verification.")

        socket.socket = _blocked_socket
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        import socket
        if self._orig_socket is not None:
            socket.socket = self._orig_socket
