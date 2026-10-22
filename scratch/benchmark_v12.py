"""
Stage B2-C: Performance Benchmarking of Candidate A+E vs Baseline E0.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import time
import tracemalloc
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

def benchmark_candidate(name, cand_fn_or_path, regime="vol_spike_snapback", iterations=5):
    prov = StaticRegimeProvider("sample_regimes.json.gz", regime)
    
    times = []
    mem_peaks = []
    
    for _ in range(iterations):
        tracemalloc.start()
        t0 = time.perf_perf_counter() if hasattr(time, "perf_perf_counter") else time.perf_counter()
        
        if hasattr(cand_fn_or_path, "reset"):
            cand_fn_or_path.reset()
            engine = ReplayEngine(cand_fn_or_path.decide, prov)
        else:
            engine = ReplayEngine(cand_fn_or_path, prov)
            
        res = engine.run_replay()
        t1 = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times.append((t1 - t0) * 1000.0) # ms
        mem_peaks.append(peak / (1024 * 1024)) # MB
        
    avg_time = sum(times) / len(times)
    p50_time = sorted(times)[len(times)//2]
    avg_mem = sum(mem_peaks) / len(mem_peaks)
    
    print(f"{name:<30} | Avg Time: {avg_time:6.2f} ms | P50 Time: {p50_time:6.2f} ms | Peak RAM: {avg_mem:5.2f} MB | Sessions: {len(res['equity_curve'])}")
    return {
        "name": name, "avg_time_ms": avg_time, "p50_time_ms": p50_time,
        "peak_ram_mb": avg_mem, "sessions": len(res['equity_curve'])
    }

if __name__ == "__main__":
    print("=== COMPUTATIONAL PERFORMANCE BENCHMARK (5 Iterations per candidate) ===")
    b0 = benchmark_candidate("Baseline E0", "agent.py")
    b_ae = benchmark_candidate("Candidate A+E Combined", CandidateAE_Combined())
