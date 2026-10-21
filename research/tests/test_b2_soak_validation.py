"""Unit and Forensic Tests for Offline Soak Test Validator.

Verifies:
- Monotonic duration thresholds (duration >= 7200s required for PASS)
- Rejection of prematurely terminated or interrupted soak runs (INCOMPLETE)
- Rejection of runs with invariant failures or unhandled exceptions (FAIL)
- Rejection of discontinuous or duplicate telemetry streams (FAIL)
- Handling of running/pending soak executions (PENDING)
- Rejection of corrupt or missing summary files (INVALID/FAIL)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from research.scripts.validate_soak_run import validate_soak_directory


@pytest.fixture
def temp_soak_dir(tmp_path: Path) -> Path:
    sdir = tmp_path / "soak_test_run"
    sdir.mkdir(parents=True, exist_ok=True)
    return sdir


def test_missing_soak_directory(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist"
    res = validate_soak_directory(non_existent)
    assert res.verdict == "INVALID"
    assert len(res.issues) > 0


def test_pending_soak_directory(temp_soak_dir: Path):
    # Only telemetry written, no summary yet
    telemetry = temp_soak_dir / "soak_telemetry.jsonl"
    telemetry.write_text(json.dumps({"sample_idx": 0, "monotonic_sec": 10.0}) + "\n")
    res = validate_soak_directory(temp_soak_dir)
    assert res.verdict == "PENDING"
    assert "PENDING" in res.warnings[0]


def test_short_run_yields_incomplete_verdict(temp_soak_dir: Path):
    # Clean run but only 180s instead of 7200s
    summary = {
        "soak_verdict": "INCOMPLETE",
        "target_duration_sec": 7200.0,
        "actual_duration_sec": 180.5,
        "total_agent_decisions": 1000,
        "total_orders_executed": 500,
        "fault_injections_tested": 10,
        "fault_recoveries_successful": 10,
        "invariant_failures": 0,
        "unhandled_exceptions": 0,
        "final_peak_mem_mb": 15.0,
        "memory_slope_mb_per_hour": -1.2,
        "telemetry_samples_count": 2,
    }
    (temp_soak_dir / "soak_summary.json").write_text(json.dumps(summary))

    tlines = [
        {"sample_idx": 0, "monotonic_sec": 10.0, "total_decisions": 500, "total_orders": 250, "invariant_failures": 0, "unhandled_exceptions": 0},
        {"sample_idx": 1, "monotonic_sec": 190.5, "total_decisions": 1000, "total_orders": 500, "invariant_failures": 0, "unhandled_exceptions": 0},
    ]
    (temp_soak_dir / "soak_telemetry.jsonl").write_text("\n".join(json.dumps(l) for l in tlines) + "\n")

    res = validate_soak_directory(temp_soak_dir, strict_min_duration_sec=7200.0)
    assert res.verdict == "INCOMPLETE"
    assert res.actual_duration_sec == 180.5
    assert len(res.warnings) > 0


def test_full_7200s_clean_run_passes(temp_soak_dir: Path):
    summary = {
        "soak_verdict": "PASS",
        "target_duration_sec": 7200.0,
        "actual_duration_sec": 7205.2,
        "total_agent_decisions": 500000,
        "total_orders_executed": 250000,
        "fault_injections_tested": 1000,
        "fault_recoveries_successful": 1000,
        "invariant_failures": 0,
        "unhandled_exceptions": 0,
        "final_peak_mem_mb": 22.5,
        "memory_slope_mb_per_hour": 0.5,
        "telemetry_samples_count": 3,
    }
    (temp_soak_dir / "soak_summary.json").write_text(json.dumps(summary))

    tlines = [
        {"sample_idx": 0, "monotonic_sec": 10.0, "total_decisions": 100000, "total_orders": 50000, "invariant_failures": 0, "unhandled_exceptions": 0},
        {"sample_idx": 1, "monotonic_sec": 3610.0, "total_decisions": 300000, "total_orders": 150000, "invariant_failures": 0, "unhandled_exceptions": 0},
        {"sample_idx": 2, "monotonic_sec": 7215.2, "total_decisions": 500000, "total_orders": 250000, "invariant_failures": 0, "unhandled_exceptions": 0},
    ]
    (temp_soak_dir / "soak_telemetry.jsonl").write_text("\n".join(json.dumps(l) for l in tlines) + "\n")

    res = validate_soak_directory(temp_soak_dir, strict_min_duration_sec=7200.0)
    assert res.verdict == "PASS"
    assert res.actual_duration_sec == 7205.2
    assert len(res.issues) == 0


def test_corrupted_telemetry_sequence_fails(temp_soak_dir: Path):
    summary = {
        "soak_verdict": "PASS",
        "target_duration_sec": 7200.0,
        "actual_duration_sec": 7210.0,
        "total_agent_decisions": 1000,
        "total_orders_executed": 500,
        "fault_injections_tested": 10,
        "fault_recoveries_successful": 10,
        "invariant_failures": 0,
        "unhandled_exceptions": 0,
        "final_peak_mem_mb": 15.0,
        "memory_slope_mb_per_hour": 0.1,
        "telemetry_samples_count": 3,
    }
    (temp_soak_dir / "soak_summary.json").write_text(json.dumps(summary))

    # Backward jump in monotonic time
    tlines = [
        {"sample_idx": 0, "monotonic_sec": 100.0, "total_decisions": 100, "total_orders": 50, "invariant_failures": 0, "unhandled_exceptions": 0},
        {"sample_idx": 1, "monotonic_sec": 50.0, "total_decisions": 200, "total_orders": 100, "invariant_failures": 0, "unhandled_exceptions": 0},  # ERROR
        {"sample_idx": 2, "monotonic_sec": 200.0, "total_decisions": 300, "total_orders": 150, "invariant_failures": 0, "unhandled_exceptions": 0},
    ]
    (temp_soak_dir / "soak_telemetry.jsonl").write_text("\n".join(json.dumps(l) for l in tlines) + "\n")

    res = validate_soak_directory(temp_soak_dir, strict_min_duration_sec=7200.0)
    assert res.verdict == "FAIL"
    assert any("monotonic timestamp did not advance" in iss for iss in res.issues)


def test_invariant_failure_in_summary_fails(temp_soak_dir: Path):
    summary = {
        "soak_verdict": "FAIL",
        "target_duration_sec": 7200.0,
        "actual_duration_sec": 7210.0,
        "total_agent_decisions": 1000,
        "total_orders_executed": 500,
        "fault_injections_tested": 10,
        "fault_recoveries_successful": 10,
        "invariant_failures": 1,  # Invariant failure!
        "unhandled_exceptions": 0,
        "final_peak_mem_mb": 15.0,
        "memory_slope_mb_per_hour": 0.1,
        "telemetry_samples_count": 1,
    }
    (temp_soak_dir / "soak_summary.json").write_text(json.dumps(summary))
    (temp_soak_dir / "soak_telemetry.jsonl").write_text(
        json.dumps({"sample_idx": 0, "monotonic_sec": 7210.0, "total_decisions": 1000, "total_orders": 500, "invariant_failures": 1, "unhandled_exceptions": 0}) + "\n"
    )

    res = validate_soak_directory(temp_soak_dir, strict_min_duration_sec=7200.0)
    assert res.verdict == "FAIL"
    assert any("Invariant failures detected: 1" in iss for iss in res.issues)
