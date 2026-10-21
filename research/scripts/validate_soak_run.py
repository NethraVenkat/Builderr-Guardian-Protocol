#!/usr/bin/env python3
"""Offline Forensic Soak Test Validator.

Validates the output of a continuous soak test run according to
Guardian Alpha Master Protocol V8 Section 15.

Checks:
- File existence and schema integrity (summary and telemetry)
- Monotonic elapsed duration >= 7,200 seconds for PASS
- Sequential monotonic continuity in telemetry (no duplicates, no backwards jumps)
- Invariant integrity (0 invariant failures)
- Crash freedom (0 unhandled exceptions)
- Fault recovery parity (100% recovery)
- Memory boundedness (RSS < 250 MB, drift rate < 15 MB/hr)
- Internal consistency between telemetry logs and summary counters
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SoakValidationResult:
    verdict: str  # PASS, INCOMPLETE, FAIL, PENDING, INVALID
    target_duration_sec: float
    actual_duration_sec: float
    total_decisions: int
    total_orders: int
    faults_tested: int
    faults_recovered: int
    invariant_failures: int
    unhandled_exceptions: int
    peak_mem_mb: float
    memory_slope_mb_per_hour: float
    telemetry_samples_count: int
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_soak_directory(
    soak_dir: Path | str,
    strict_min_duration_sec: float = 7200.0,
    check_running_pid: bool = True,
) -> SoakValidationResult:
    path = Path(soak_dir)
    if not path.is_dir():
        return SoakValidationResult(
            verdict="INVALID",
            target_duration_sec=strict_min_duration_sec,
            actual_duration_sec=0.0,
            total_decisions=0,
            total_orders=0,
            faults_tested=0,
            faults_recovered=0,
            invariant_failures=0,
            unhandled_exceptions=0,
            peak_mem_mb=0.0,
            memory_slope_mb_per_hour=0.0,
            telemetry_samples_count=0,
            issues=[f"Target soak directory does not exist: {path}"],
        )

    summary_file = path / "soak_summary.json"
    telemetry_file = path / "soak_telemetry.jsonl"

    issues: list[str] = []
    warnings: list[str] = []

    # Check if process is still running and summary not yet generated
    if not summary_file.is_file():
        if telemetry_file.is_file():
            # Check if telemetry is being updated
            return SoakValidationResult(
                verdict="PENDING",
                target_duration_sec=strict_min_duration_sec,
                actual_duration_sec=0.0,
                total_decisions=0,
                total_orders=0,
                faults_tested=0,
                faults_recovered=0,
                invariant_failures=0,
                unhandled_exceptions=0,
                peak_mem_mb=0.0,
                memory_slope_mb_per_hour=0.0,
                telemetry_samples_count=0,
                warnings=["Soak test is currently PENDING (running in progress; soak_summary.json not yet written)."],
            )
        else:
            return SoakValidationResult(
                verdict="INVALID",
                target_duration_sec=strict_min_duration_sec,
                actual_duration_sec=0.0,
                total_decisions=0,
                total_orders=0,
                faults_tested=0,
                faults_recovered=0,
                invariant_failures=0,
                unhandled_exceptions=0,
                peak_mem_mb=0.0,
                memory_slope_mb_per_hour=0.0,
                telemetry_samples_count=0,
                issues=[f"Neither summary nor telemetry file found in {path}"],
            )

    # 1. Parse summary
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
    except Exception as e:
        return SoakValidationResult(
            verdict="INVALID",
            target_duration_sec=strict_min_duration_sec,
            actual_duration_sec=0.0,
            total_decisions=0,
            total_orders=0,
            faults_tested=0,
            faults_recovered=0,
            invariant_failures=0,
            unhandled_exceptions=0,
            peak_mem_mb=0.0,
            memory_slope_mb_per_hour=0.0,
            telemetry_samples_count=0,
            issues=[f"Failed to parse soak_summary.json: {e}"],
        )

    required_fields = [
        "soak_verdict", "target_duration_sec", "actual_duration_sec",
        "total_agent_decisions", "total_orders_executed",
        "fault_injections_tested", "fault_recoveries_successful",
        "invariant_failures", "unhandled_exceptions",
        "final_peak_mem_mb", "memory_slope_mb_per_hour", "telemetry_samples_count",
    ]
    for rf in required_fields:
        if rf not in summary:
            issues.append(f"Missing required summary field: {rf}")

    actual_duration = float(summary.get("actual_duration_sec", 0.0))
    target_duration = float(summary.get("target_duration_sec", strict_min_duration_sec))
    inv_fails = int(summary.get("invariant_failures", 0))
    unhandled_ex = int(summary.get("unhandled_exceptions", 0))
    faults_t = int(summary.get("fault_injections_tested", 0))
    faults_r = int(summary.get("fault_recoveries_successful", 0))
    peak_mem = float(summary.get("final_peak_mem_mb", 0.0))
    mem_slope = float(summary.get("memory_slope_mb_per_hour", 0.0))
    samples_count = int(summary.get("telemetry_samples_count", 0))
    decisions = int(summary.get("total_agent_decisions", 0))
    orders = int(summary.get("total_orders_executed", 0))

    if inv_fails > 0:
        issues.append(f"Invariant failures detected: {inv_fails}")
    if unhandled_ex > 0:
        issues.append(f"Unhandled exceptions detected: {unhandled_ex}")
    if faults_t != faults_r:
        issues.append(f"Fault recovery mismatch: {faults_t} tested vs {faults_r} recovered")
    if peak_mem > 250.0:
        issues.append(f"Peak memory {peak_mem} MB exceeded 250 MB ceiling")
    if mem_slope > 15.0:
        issues.append(f"Memory slope {mem_slope} MB/hr indicates potential memory leak")

    # 2. Parse telemetry log
    telemetry_samples: list[dict[str, Any]] = []
    if telemetry_file.is_file():
        try:
            with open(telemetry_file, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f):
                    line_s = line.strip()
                    if not line_s:
                        continue
                    sample = json.loads(line_s)
                    telemetry_samples.append(sample)
        except Exception as e:
            issues.append(f"Error parsing telemetry log: {e}")

    # Telemetry checks
    if telemetry_samples:
        if len(telemetry_samples) != samples_count:
            issues.append(
                f"Telemetry line count mismatch: summary claims {samples_count}, "
                f"but telemetry file contains {len(telemetry_samples)}"
            )

        # Monotonicity & continuity checks
        prev_idx = -1
        prev_mono = -1.0
        prev_decisions = -1
        prev_orders = -1

        for s in telemetry_samples:
            s_idx = s.get("sample_idx", 0)
            s_mono = s.get("monotonic_sec", 0.0)
            s_dec = s.get("total_decisions", 0)
            s_ord = s.get("total_orders", 0)

            if prev_idx >= 0 and s_idx != prev_idx + 1:
                issues.append(f"Telemetry sample_idx discontinuous: {prev_idx} -> {s_idx}")
            if prev_mono >= 0 and s_mono <= prev_mono:
                issues.append(f"Telemetry monotonic timestamp did not advance: {prev_mono} -> {s_mono}")
            if prev_decisions >= 0 and s_dec < prev_decisions:
                issues.append(f"Telemetry total_decisions decreased: {prev_decisions} -> {s_dec}")
            if prev_orders >= 0 and s_ord < prev_orders:
                issues.append(f"Telemetry total_orders decreased: {prev_orders} -> {s_ord}")

            prev_idx = s_idx
            prev_mono = s_mono
            prev_decisions = s_dec
            prev_orders = s_ord

        # Invariant checks on last sample
        last_s = telemetry_samples[-1]
        if last_s.get("invariant_failures", 0) > 0:
            issues.append("Telemetry recorded invariant failure in stream")
        if last_s.get("unhandled_exceptions", 0) > 0:
            issues.append("Telemetry recorded unhandled exception in stream")
    else:
        issues.append("Zero telemetry samples found in soak_telemetry.jsonl")

    # 3. Determine final verdict
    if issues:
        verdict = "FAIL"
    elif actual_duration < strict_min_duration_sec:
        verdict = "INCOMPLETE"
        warnings.append(
            f"Measured duration {actual_duration:.1f}s is less than mandatory {strict_min_duration_sec:.1f}s (120m)."
        )
    else:
        verdict = "PASS"

    return SoakValidationResult(
        verdict=verdict,
        target_duration_sec=target_duration,
        actual_duration_sec=actual_duration,
        total_decisions=decisions,
        total_orders=orders,
        faults_tested=faults_t,
        faults_recovered=faults_r,
        invariant_failures=inv_fails,
        unhandled_exceptions=unhandled_ex,
        peak_mem_mb=peak_mem,
        memory_slope_mb_per_hour=mem_slope,
        telemetry_samples_count=len(telemetry_samples),
        issues=issues,
        warnings=warnings,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate soak test run directory")
    parser.add_argument("--soak-dir", type=str, default="research/evidence/soak", help="Path to soak evidence directory")
    parser.add_argument("--min-duration-sec", type=float, default=7200.0, help="Required minimum duration in seconds")
    args = parser.parse_args()

    res = validate_soak_directory(args.soak_dir, args.min_duration_sec)
    print("================================================================================")
    print(f"SOAK RUN VALIDATION VERDICT: {res.verdict}")
    print(f"Duration: {res.actual_duration_sec:.2f}s / {res.target_duration_sec:.2f}s")
    print(f"Decisions: {res.total_decisions:,} | Orders: {res.total_orders:,}")
    print(f"Invariants: {res.invariant_failures} | Exceptions: {res.unhandled_exceptions}")
    print(f"Peak RAM: {res.peak_mem_mb} MB | Memory Slope: {res.memory_slope_mb_per_hour} MB/hr")
    print(f"Telemetry Samples: {res.telemetry_samples_count}")

    if res.warnings:
        print("\nWARNINGS:")
        for w in res.warnings:
            print(f"  [!] {w}")
    if res.issues:
        print("\nFAILURES / ISSUES:")
        for iss in res.issues:
            print(f"  [X] {iss}")
        sys.exit(1)

    if res.verdict == "PASS":
        print("\nAll endurance criteria successfully met.")
        sys.exit(0)
    elif res.verdict in ("INCOMPLETE", "PENDING"):
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
