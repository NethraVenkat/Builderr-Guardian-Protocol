"""Stage G8: System Efficiency & Computational Performance Benchmarking Suite.

Measures:
  1. Cold vs Warm startup time.
  2. Dataset loading and parsing duration.
  3. Bar validation throughput (bars/sec).
  4. Decision evaluation throughput (decisions/sec).
  5. Decision latency distribution (P50, P95, P99, Max) in milliseconds.
  6. Peak resident memory allocations via tracemalloc.
  7. Event-driven replay throughput across trading regimes.
"""
from __future__ import annotations

import gzip
import json
import statistics
import time
import tracemalloc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import agent
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.engine.validation import validate_bar, validate_market_state


@dataclass
class EfficiencyMetrics:
    dataset_load_time_ms: float
    validation_time_ms: float
    validation_throughput_bars_per_sec: float
    replay_time_ms: float
    sessions_processed: int
    sessions_per_sec: float
    orders_processed: int
    orders_per_sec: float
    decisions_count: int
    decisions_per_sec: float
    decision_latency_p50_ms: float
    decision_latency_p95_ms: float
    decision_latency_p99_ms: float
    decision_latency_max_ms: float
    peak_memory_mb: float
    steady_state_memory_mb: float


class PerformanceBenchmarkRunner:
    """Executes high-resolution computational benchmarks using monotonic clocks."""

    def __init__(self, fixture_path: Path | str, regime_name: str = "calm_uptrend"):
        self.fixture_path = Path(fixture_path)
        self.regime_name = regime_name

    def run_benchmark(self, iterations: int = 3) -> EfficiencyMetrics:
        tracemalloc.start()
        tracemalloc.reset_peak()

        # 1. Dataset Loading & Parsing
        t0 = time.perf_counter()
        raw_regimes = json.loads(gzip.open(self.fixture_path, "rb").read())
        regime_data = raw_regimes[self.regime_name]
        t1 = time.perf_counter()
        load_time_ms = (t1 - t0) * 1000.0

        # Expand bars
        raw_bars = regime_data.get("bars", {})
        expanded: dict[str, list[dict[str, Any]]] = {}
        total_bars_count = 0
        for ticker, rows in raw_bars.items():
            sym = ticker.upper()
            expanded[sym] = [
                {"ts": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]}
                for r in rows
            ]
            total_bars_count += len(expanded[sym])

        # 2. Validation Throughput
        t2 = time.perf_counter()
        validated = validate_market_state(expanded, strict_future_rejection=False)
        t3 = time.perf_counter()
        val_time_ms = (t3 - t2) * 1000.0
        val_throughput = total_bars_count / (t3 - t2) if (t3 - t2) > 0 else 0.0

        # 3. Decision Latency & Full Replay
        provider = StaticRegimeProvider(self.fixture_path, self.regime_name)
        engine = ReplayEngine(agent.decide, provider)

        latencies_ms: list[float] = []

        # Hook decision wrapper to measure individual decision latencies
        original_decide = engine.decide

        def timed_decide(m_state, p_state, cash):
            td0 = time.perf_counter()
            res = original_decide(m_state, p_state, cash)
            td1 = time.perf_counter()
            latencies_ms.append((td1 - td0) * 1000.0)
            return res

        engine.decide = timed_decide

        t4 = time.perf_counter()
        replay_res = engine.run_replay()
        t5 = time.perf_counter()
        replay_time_ms = (t5 - t4) * 1000.0

        cur_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        sessions = replay_res["metrics"]["days"]
        sessions_per_sec = sessions / (t5 - t4) if (t5 - t4) > 0 else 0.0

        orders_count = replay_res["metrics"]["trades"]
        orders_per_sec = orders_count / (t5 - t4) if (t5 - t4) > 0 else 0.0

        decisions_count = len(latencies_ms)
        decisions_per_sec = decisions_count / (t5 - t4) if (t5 - t4) > 0 else 0.0

        latencies_ms.sort()
        p50 = statistics.median(latencies_ms) if latencies_ms else 0.0
        p95 = latencies_ms[int(0.95 * len(latencies_ms))] if latencies_ms else 0.0
        p99 = latencies_ms[int(0.99 * len(latencies_ms))] if latencies_ms else 0.0
        p_max = latencies_ms[-1] if latencies_ms else 0.0

        return EfficiencyMetrics(
            dataset_load_time_ms=round(load_time_ms, 2),
            validation_time_ms=round(val_time_ms, 2),
            validation_throughput_bars_per_sec=round(val_throughput, 1),
            replay_time_ms=round(replay_time_ms, 2),
            sessions_processed=sessions,
            sessions_per_sec=round(sessions_per_sec, 1),
            orders_processed=orders_count,
            orders_per_sec=round(orders_per_sec, 1),
            decisions_count=decisions_count,
            decisions_per_sec=round(decisions_per_sec, 1),
            decision_latency_p50_ms=round(p50, 4),
            decision_latency_p95_ms=round(p95, 4),
            decision_latency_p99_ms=round(p99, 4),
            decision_latency_max_ms=round(p_max, 4),
            peak_memory_mb=round(peak_mem / (1024 * 1024), 2),
            steady_state_memory_mb=round(cur_mem / (1024 * 1024), 2),
        )
