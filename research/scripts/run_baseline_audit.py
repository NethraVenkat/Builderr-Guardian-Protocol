import sys
import os
import subprocess
import time
import json
from datetime import datetime, timezone
from pathlib import Path

py_exe = sys.executable
py_ver = sys.version
print(f"Using Python: {py_exe} ({py_ver})")

test_definitions = [
    {
        "name": "selfcheck",
        "command": [py_exe, "-X", "utf8", "selfcheck.py"],
        "dimension": "Correctness & Secret Compliance",
        "description": "Smoke test on synthetic inputs and credentials scan."
    },
    {
        "name": "preview",
        "command": [py_exe, "-X", "utf8", "preview.py"],
        "dimension": "Financial Behavior & Admission Compliance",
        "description": "Multi-regime replay across 3 public sample windows with leverage/concentration/drawdown checks."
    },
    {
        "name": "strategy_selftest",
        "command": [py_exe, "-X", "utf8", "strategy_selftest.py"],
        "dimension": "Correctness",
        "description": "Strategy unit tests (closes, sma, momentum, vol, weights, rebalance)."
    },
    {
        "name": "endpoint_harness_selftest",
        "command": [py_exe, "-X", "utf8", "endpoint_harness_selftest.py"],
        "dimension": "Correctness & Compliance",
        "description": "Endpoint order generation and harness interface validation."
    },
    {
        "name": "pytest_e0_release",
        "command": [py_exe, "-m", "pytest", "tests/test_e0_release.py", "-v", "-ra", "-p", "no:cacheprovider"],
        "dimension": "Correctness, Reproducibility & Numerical Safety",
        "description": "56 official E0 release verification tests."
    },
    {
        "name": "test_market_open",
        "command": [py_exe, "-X", "utf8", "test_market_open.py"],
        "dimension": "Compliance & Environment Prerequisites",
        "description": "Market open calendar check requiring optional yfinance."
    },
    {
        "name": "live_runner_selftest",
        "command": [py_exe, "-X", "utf8", "live_runner_selftest.py"],
        "dimension": "Correctness & Environment Prerequisites",
        "description": "Live runner scoring harness test requiring optional yfinance."
    },
    {
        "name": "fairness_tests",
        "command": [py_exe, "-X", "utf8", "fairness_tests.py"],
        "dimension": "Inherited Upstream Fixture",
        "description": "Upstream fixture known to have intentional SyntaxError."
    },
    {
        "name": "local_test",
        "command": [py_exe, "-X", "utf8", "local_test.py"],
        "dimension": "External Platform Runner",
        "description": "Requires proprietary unreleased builderr CLI package."
    },
    {
        "name": "full_test",
        "command": [py_exe, "-X", "utf8", "full_test.py"],
        "dimension": "External Platform Runner",
        "description": "Requires proprietary unreleased builderr.backtest package."
    }
]

results = []
evidence_dir = Path("research/evidence")
evidence_dir.mkdir(parents=True, exist_ok=True)

for td in test_definitions:
    cmd = td["command"]
    cmd_str = " ".join(cmd)
    t0 = time.perf_counter()
    start_iso = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(Path(".").resolve()),
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

    log_file = evidence_dir / f"{td['name']}.log"
    log_file.write_text(output, encoding="utf-8")

    res = {
        "name": td["name"],
        "command": cmd_str,
        "dimension": td["dimension"],
        "description": td["description"],
        "interpreter": py_exe,
        "interpreter_version": py_ver,
        "start_utc": start_iso,
        "duration_seconds": round(dur, 4),
        "exit_code": exit_code,
        "log_path": str(log_file),
        "output_preview": output[:500] if len(output) > 500 else output
    }
    results.append(res)
    status_str = "PASS" if exit_code == 0 else f"FAIL (code {exit_code})"
    print(f"{td['name']:28} -> {status_str} ({dur:.2f}s)")

(evidence_dir / "baseline_test_suite_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print("Baseline execution completed and recorded in research/evidence/baseline_test_suite_results.json")
