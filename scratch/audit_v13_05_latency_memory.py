"""
Forensic audit of V13-05: Explicit Latency Hierarchy and Memory Unit Dissection.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import time
import tracemalloc
import ctypes
from ctypes import wintypes
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

def get_process_rss_mb():
    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        return counters.WorkingSetSize / (1024 * 1024)
    return 0.0

prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
cand = CandidateAE_Combined()

rss_before = get_process_rss_mb()

tracemalloc.start()
t0 = time.perf_counter()

cand.reset()
eng = ReplayEngine(cand.decide, prov)
res = eng.run_replay()

t1 = time.perf_counter()
cur_trace, peak_trace = tracemalloc.get_traced_memory()
tracemalloc.stop()

rss_after = get_process_rss_mb()

total_replay_time_ms = (t1 - t0) * 1000.0
total_sessions = len(res["equity_curve"])
total_decisions = total_sessions # decide() called once per scored session
total_trades = res["total_trades"]

ms_per_session = total_replay_time_ms / total_sessions
ms_per_decision = total_replay_time_ms / total_decisions
ms_per_trade = total_replay_time_ms / total_trades if total_trades > 0 else 0.0

print("=== V13-05 LATENCY HIERARCHY & MEMORY UNITS DISSECTION ===")
print("1. LATENCY BREAKDOWN (Candidate A+E on vol_spike_snapback):")
print(f"   - Total Replay Duration:       {total_replay_time_ms:8.2f} ms")
print(f"   - Total Scored Sessions:       {total_sessions:8d}")
print(f"   - Latency per Scored Session:  {ms_per_session:8.4f} ms/session")
print(f"   - Latency per decide() Call:   {ms_per_decision:8.4f} ms/decision")
print(f"   - Latency per Executed Trade:  {ms_per_trade:8.4f} ms/trade")
print(f"   - Throughput:                  {total_sessions / (total_replay_time_ms / 1000.0):8.1f} sessions/second")
print()
print("2. MEMORY DISSECTION:")
print(f"   - Python Traced Peak Memory:   {peak_trace / (1024*1024):8.4f} MB (Tracemalloc heap allocations)")
print(f"   - Python Traced Final Memory:  {cur_trace / (1024*1024):8.4f} MB")
print(f"   - OS Resident Set Size (RSS):  {rss_after:8.2f} MB (Total process working set)")
print(f"   - RSS Growth during Replay:    {rss_after - rss_before:8.4f} MB")
print()
print("AUDIT FINDING FOR V13-05:")
print("In V12, '136.52 ms' was the ENTIRE REPLAY DURATION for 50 sessions, which translates to:")
print(f"-> 2.73 ms per scored session decision (NOT 136 ms per order!)")
print("And '0.22 MB' was TRACEMALLOC HEAP PEAK, whereas OS process RSS is ~40-50 MB.")
