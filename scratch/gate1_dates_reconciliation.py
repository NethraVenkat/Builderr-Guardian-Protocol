"""
Gate 1: Exact Scored-Session and Calendar Date Forensic Reconciliation.
Extracts raw date structures from sample_regimes.json.gz.
"""
import gzip
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath("."))
from preview import _expand

data = json.load(gzip.open("sample_regimes.json.gz"))

print("=" * 90)
print(f"{'Regime':<20} | {'eval_start':<12} | {'eval_end':<12} | {'Warm-up Dates':<15} | {'Scored Dates':<15} | {'Total Dates':<12}")
print("=" * 90)

regime_summaries = {}

for name, payload in data.items():
    eval_start = payload["eval_start"]
    eval_end = payload["eval_end"]
    
    # Collect all unique dates across all tickers
    all_dates = set()
    ticker_date_counts = {}
    for ticker, rows in payload["bars"].items():
        expanded = _expand(rows)
        dates = [b["ts"] for b in expanded]
        all_dates.update(dates)
        ticker_date_counts[ticker] = len(dates)
        
    sorted_all_dates = sorted(list(all_dates))
    warmup_dates = [d for d in sorted_all_dates if d < eval_start]
    scored_dates = [d for d in sorted_all_dates if eval_start <= d <= eval_end]
    post_eval_dates = [d for d in sorted_all_dates if d > eval_end]
    
    regime_summaries[name] = {
        "eval_start": eval_start,
        "eval_end": eval_end,
        "first_bar_date": sorted_all_dates[0],
        "last_bar_date": sorted_all_dates[-1],
        "warmup_count": len(warmup_dates),
        "warmup_range": (warmup_dates[0] if warmup_dates else "None", warmup_dates[-1] if warmup_dates else "None"),
        "scored_count": len(scored_dates),
        "scored_first": scored_dates[0],
        "scored_last": scored_dates[-1],
        "post_eval_count": len(post_eval_dates),
        "total_unique_dates": len(sorted_all_dates),
        "min_ticker_bars": min(ticker_date_counts.values()),
        "max_ticker_bars": max(ticker_date_counts.values()),
    }
    
    print(f"{name:<20} | {eval_start:<12} | {eval_end:<12} | {len(warmup_dates):<15} | {len(scored_dates):<15} | {len(sorted_all_dates):<12}")

print("\n" + "=" * 90)
print("DETAILED DATE BOUNDARIES")
print("=" * 90)
for name, s in regime_summaries.items():
    print(f"Regime: {name}")
    print(f"  Warm-up Period:  {s['warmup_range'][0]} to {s['warmup_range'][1]} ({s['warmup_count']} trading days)")
    print(f"  Scored Period:   {s['scored_first']} to {s['scored_last']} ({s['scored_count']} trading days)")
    print(f"  eval_start match: {s['eval_start'] == s['scored_first']}")
    print(f"  eval_end match:   {s['eval_end'] == s['scored_last']}")
    print(f"  Post-eval bars:  {s['post_eval_count']} days")
    print(f"  Total days:      {s['total_unique_dates']} days")
    print()
