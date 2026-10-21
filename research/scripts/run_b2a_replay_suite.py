"""Comprehensive Test Runner and Evidence Generator for Track B2-A."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
evidence_dir = ROOT / "research/evidence"
evidence_dir.mkdir(parents=True, exist_ok=True)

py_exe = sys.executable
py_ver = sys.version

suites = [
    {
        "name": "validation_unit_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_validation.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Input Validation & Boundary Integrity",
        "description": "Tests calendar sanity, positive finite OHLC, geometric bounds, duplicate rejection, and future timestamp strict rejection."
    },
    {
        "name": "provider_compliance_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_provider_compliance.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Storage Compliance & Streaming",
        "description": "Tests storage guard prohibiting Tiingo durable caching and verifies ephemeral in-memory streaming."
    },
    {
        "name": "corporate_actions_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_corporate_actions.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Corporate Action Accounting",
        "description": "Tests stock split ratio invariant and point-in-time cash dividend distribution."
    },
    {
        "name": "replay_accounting_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_replay_accounting.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Execution & Cash Accounting",
        "description": "Tests cash conservation, leveraged slippage, sell-precedes-buy order ordering, and missing price handling."
    },
    {
        "name": "risk_limits_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_risk_limits.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Portfolio Risk Caps",
        "description": "Tests gross beta exposure (1.5x), concentration streaks (30%), and catastrophic drawdown (50%)."
    },
    {
        "name": "baseline_parity_tests",
        "command": [py_exe, "-m", "pytest", "research/tests/test_baseline_parity.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "category": "Baseline Deterministic Reproduction",
        "description": "Proves ReplayEngine reproduces official preview.py metrics across all 3 public regimes."
    }
]

overall_results = []
all_passed = True

print(f"=== Running Track B2-A Test Suite on {py_exe} ===")
suite_t0 = time.perf_counter()

for s in suites:
    cmd = s["command"]
    cmd_str = " ".join(cmd)
    t0 = time.perf_counter()
    start_iso = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        t1 = time.perf_counter()
        dur = t1 - t0
        output = proc.stdout
        exit_code = proc.returncode
    except Exception as e:
        t1 = time.perf_counter()
        dur = t1 - t0
        output = str(e)
        exit_code = -999

    passed = (exit_code == 0)
    if not passed:
        all_passed = False

    log_file = evidence_dir / f"b2a_{s['name']}.log"
    log_file.write_text(output, encoding="utf-8")

    res = {
        "suite": s["name"],
        "category": s["category"],
        "description": s["description"],
        "command": cmd_str,
        "exit_code": exit_code,
        "passed": passed,
        "duration_seconds": round(dur, 4),
        "log_path": str(log_file),
        "output_summary": output[-300:].strip() if len(output) > 300 else output.strip()
    }
    overall_results.append(res)
    status_str = "PASS" if passed else f"FAIL (exit {exit_code})"
    print(f"  {s['name']:32} -> {status_str} ({dur:.2f}s)")

suite_t1 = time.perf_counter()
total_duration = round(suite_t1 - suite_t0, 4)

summary_report = {
    "audit_milestone": "Track B2-A Replay Engine and Data Compliance Gate",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "python_interpreter": py_exe,
    "python_version": py_ver,
    "total_duration_seconds": total_duration,
    "overall_status": "ALL_PASSED" if all_passed else "SOME_FAILED",
    "suite_results": overall_results
}

evidence_file = evidence_dir / "b2a_replay_audit_results.json"
evidence_file.write_text(json.dumps(summary_report, indent=2), encoding="utf-8")
print(f"\nB2-A Audit Suite Complete: {summary_report['overall_status']} in {total_duration}s")
print(f"Recorded evidence in {evidence_file}")
