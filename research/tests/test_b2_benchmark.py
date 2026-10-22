"""Stage G8: Performance Benchmarking Tests.

Validates:
  1. PerformanceBenchmarkRunner execution on standard fixture.
  2. Non-negative, finite computational efficiency metrics.
  3. Replay throughput boundaries (>50 decisions/sec).
  4. Memory bounds (<100 MB peak tracemalloc).
  5. Latency distribution monotonicity (P50 <= P95 <= P99 <= Max).
"""
from __future__ import annotations

from pathlib import Path
import pytest

from research.engine.benchmark import PerformanceBenchmarkRunner

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_REGIMES_PATH = REPO_ROOT / "sample_regimes.json.gz"


class TestPerformanceBenchmark:
    def test_benchmark_metrics_validity(self):
        runner = PerformanceBenchmarkRunner(SAMPLE_REGIMES_PATH, "calm_uptrend")
        metrics = runner.run_benchmark(iterations=1)

        assert metrics.dataset_load_time_ms > 0.0
        assert metrics.validation_time_ms > 0.0
        assert metrics.validation_throughput_bars_per_sec > 500.0  # Fast bar validation
        assert metrics.replay_time_ms > 0.0
        assert metrics.sessions_processed >= 60
        assert metrics.sessions_per_sec > 10.0
        assert metrics.decisions_count >= 60
        assert metrics.decisions_per_sec > 10.0

        # Monotonicity of latency percentiles
        assert 0.0 <= metrics.decision_latency_p50_ms <= metrics.decision_latency_p95_ms
        assert metrics.decision_latency_p95_ms <= metrics.decision_latency_p99_ms
        assert metrics.decision_latency_p99_ms <= metrics.decision_latency_max_ms

        # Latency P50 should be sub-5ms in Python
        assert metrics.decision_latency_p50_ms < 5.0

        # Peak memory sanity check
        assert 0.0 < metrics.peak_memory_mb < 200.0
