"""
Guardian Alpha V30 Stage 3E - Competition Certification & Governance Verification Suite.
Validates all Stage 3E acceptance gates: checkpoint invariants, contract schemas,
governance crosswalk, requirements traceability, and zero trading activation.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import pytest

sys.path.insert(0, os.path.abspath("."))

EXPECTED_BRANCH = "archive/v30-stage2h-final-evidence-freeze"
EXPECTED_HEAD = "4540ee49dac29e4599fbbeb96bbcffd2dafd6705"
EXPECTED_PARENT = "ce6b4c21b832044d0ffb45dce2ba949ab867d520"

PROTECTED_HASHES = {
    "agent.py": ("raw", "46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd"),
    "universe.json": ("lf", "66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd"),
    "research/strategies/v12_candidate_ae.py": ("lf", "978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793"),
    "research/strategies/v30_candidate_d2_cash_cushion.py": ("raw", "5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215"),
}


def compute_sha256(path: str, normalization: str = "raw") -> str:
    with open(path, "rb") as f:
        data = f.read()
    if normalization == "lf":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def test_01_checkpoint_commit_and_ancestry():
    """Verify repository HEAD, branch, and parent ancestry match Stage 3C freeze."""
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    parent = subprocess.check_output(["git", "rev-parse", "HEAD~1"]).decode().strip()

    assert branch == EXPECTED_BRANCH, f"Branch mismatch: expected {EXPECTED_BRANCH}, got {branch}"
    assert head == EXPECTED_HEAD, f"HEAD mismatch: expected {EXPECTED_HEAD}, got {head}"
    assert parent == EXPECTED_PARENT, f"Parent mismatch: expected {EXPECTED_PARENT}, got {parent}"


def test_02_protected_source_file_hashes():
    """Verify all four protected source files match expected SHA-256 hashes bit-for-bit."""
    for rel_path, (norm, expected_hash) in PROTECTED_HASHES.items():
        assert os.path.exists(rel_path), f"Protected file missing: {rel_path}"
        actual_hash = compute_sha256(rel_path, norm)
        assert actual_hash == expected_hash, (
            f"Hash mismatch on {rel_path} ({norm}): expected {expected_hash}, got {actual_hash}"
        )


def test_03_tier3_holdout_isolation():
    """Verify Tier 3 out-of-sample data in tiingo_cache/ remains untracked and uncommitted."""
    status = subprocess.check_output(["git", "status", "--porcelain", "tiingo_cache/"]).decode().strip()
    assert "??" in status or status == "", "tiingo_cache/ must remain untracked"
    # Ensure no tracked files in tiingo_cache/
    tracked = subprocess.check_output(["git", "ls-files", "tiingo_cache/"]).decode().strip()
    assert tracked == "", f"tiingo_cache/ contains tracked files: {tracked}"


def test_04_zero_tracked_modifications():
    """Verify zero modified tracked files in the Git working tree."""
    diff = subprocess.check_output(["git", "diff", "--name-only"]).decode().strip()
    assert diff == "", f"Tracked files modified in working tree: {diff}"
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"]).decode().strip()
    assert staged == "", f"Staged changes in working tree: {staged}"


def test_05_agent_entrypoint_signature():
    """Verify agent.py exports decide with exact signature."""
    import agent
    import inspect

    assert hasattr(agent, "decide"), "agent.py must export decide()"
    sig = inspect.signature(agent.decide)
    params = list(sig.parameters.keys())
    assert params == ["market_state", "portfolio_state", "cash"], f"Signature mismatch: {params}"


def test_06_agent_standard_library_only():
    """Verify agent.py has zero third-party dependencies using AST inspection."""
    with open("agent.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename="agent.py")

    stdlib_modules = {
        "__future__", "math", "statistics", "typing", "collections", "itertools",
        "datetime", "copy", "json", "sys", "os", "re", "time", "functools"
    }

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split(".")[0])

    unapproved = imported_modules - stdlib_modules
    assert len(unapproved) == 0, f"agent.py imports unapproved modules: {unapproved}"


def test_07_universe_json_specification():
    """Verify universe.json exists, is valid JSON, and contains 1000 tickers."""
    assert os.path.exists("universe.json"), "universe.json missing"
    with open("universe.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    tickers = data.get("tickers", [])
    assert len(tickers) == 1000, f"Expected 1000 tickers, got {len(tickers)}"
    assert "SPY" in tickers and "QQQ" in tickers and "AAPL" in tickers


def test_08_canonical_governance_reconciliation():
    """Verify canonical DEC-01 to DEC-06 definitions are restored and DEC-06 is strictly blocked."""
    canonical_defs = {
        "DEC-01": "Market Data Provider Selection",
        "DEC-02": "Market Data Licensing and Rights",
        "DEC-03": "Statistical Endpoint and Inferential Protocol",
        "DEC-04": "Evaluation Horizon and Stopping Rules",
        "DEC-05": "Monitoring and Incident Governance",
        "DEC-06": "Activation Authority"
    }
    # Check that canonical decision register file exists
    reg_path = "research/evidence/v30/v30_stage3d_canonical_decision_register.json"
    assert os.path.exists(reg_path), "v30_stage3d_canonical_decision_register.json missing"
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)

    decs = {d["decision_id"]: d for d in reg["canonical_decision_register"]["decisions"]}
    for d_id, expected_title in canonical_defs.items():
        assert d_id in decs, f"Missing {d_id} in decision register"
        assert decs[d_id]["title"] == expected_title, (
            f"Title mismatch on {d_id}: expected '{expected_title}', got '{decs[d_id]['title']}'"
        )

    # DEC-06 must be strictly blocked
    assert decs["DEC-06"]["status"] == "STRICTLY_BLOCKED", "DEC-06 must be STRICTLY_BLOCKED"
    assert decs["DEC-06"]["offline_research_permitted"] is False, "DEC-06 offline_research_permitted must be False"


def test_09_preview_safety_bar_metrics():
    """Verify preview.py passes all 6 admission constraints."""
    cmd = [sys.executable, "-X", "utf8", "preview.py"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert res.returncode == 0, f"preview.py failed with code {res.returncode}: {res.stderr}"
    assert "You clear admission's safety bar" in res.stdout, "Safety bar verdict not found in preview.py output"
    assert "[PASS] runs clean, no errors" in res.stdout
    assert "[PASS] no leverage breach" in res.stdout
    assert "[PASS] no concentration breach" in res.stdout
    assert "[PASS] no blow-up" in res.stdout


def test_10_zero_trading_activation_and_no_broker():
    """Verify agent.py does not read credentials or interact with live broker APIs."""
    with open("agent.py", "r", encoding="utf-8") as f:
        src = f.read()

    forbidden_patterns = [
        "os.environ", "getenv", "ALPACA", "TIINGO", "IBKR", "InteractiveBrokers",
        "submit_order", "create_order", "rest.REST", "TradeAPI"
    ]
    for pattern in forbidden_patterns:
        assert pattern not in src, f"Forbidden live broker or credential pattern found in agent.py: {pattern}"
