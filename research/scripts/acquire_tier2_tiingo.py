"""
Stage B2-N: Authentic Tiingo Tier 2 Historical Ingestion and Qualification.
Fetches 2020-01-01 to 2021-12-31 EOD data for the exact 24 production instruments,
combines with authorized 2019-09-01 to 2019-12-31 warm-up observations from Tier 1 cache,
and validates corporate actions (splits and dividends).
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
import sys
import time
from typing import Any

# Ensure research package is resolvable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from research.engine.tiingo_client import (
    TiingoClient,
    validate_ohlcv_bar,
    RequestLedger,
    RateLimiter,
    HOLDOUT_CUTOFF_DATE,
)

logger = logging.getLogger("acquire_tier2")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SYMBOLS = [
    "SPY", "QQQ", "DIA", "IWM", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY",
    "XLP", "XLU", "XLRE", "XLC", "SMH", "AAPL", "MSFT", "GOOGL", "AMZN",
    "META", "NVDA", "TSLA", "QLD", "SSO"
]

WARMUP_START = "2019-09-01"
TIER2_START = "2020-01-01"
TIER2_END = "2021-12-31"

CACHE_DIR = Path("tiingo_cache")
TIER1_CACHE_FILE = CACHE_DIR / "tier1_bars.json"
CACHE_FILE = CACHE_DIR / "tier2_bars.json"
COVERAGE_FILE = Path("research/manifests") / "tier2_coverage_matrix.json"
CORP_FILE = Path("research/manifests") / "tier2_corporate_actions_inventory.json"


def acquire_and_qualify() -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ledger = RequestLedger()
    rate_limiter = RateLimiter(ledger=ledger)
    client = TiingoClient(rate_limiter=rate_limiter, ledger=ledger)

    if not client.has_token:
        raise RuntimeError("TIINGO_API_KEY is not available in environment or registry.")

    # Load warm-up bars from Tier 1 cache
    warmup_data: dict[str, list[dict[str, Any]]] = {}
    if TIER1_CACHE_FILE.exists():
        with open(TIER1_CACHE_FILE, "r", encoding="utf-8") as f:
            t1_full = json.load(f)
        for sym, bars in t1_full.items():
            warmup_bars = [b for b in bars if WARMUP_START <= b["ts"] < TIER2_START]
            warmup_data[sym] = warmup_bars
        logger.info(f"Loaded warm-up bars for {len(warmup_data)} symbols from {TIER1_CACHE_FILE}.")
    else:
        logger.warning(f"Tier 1 cache not found at {TIER1_CACHE_FILE}. Warm-up bars will not be prepended.")

    logger.info(f"Starting Stage B2-N acquisition for {len(SYMBOLS)} symbols ({TIER2_START} to {TIER2_END})...")
    logger.info(f"RateLimiter status: {rate_limiter.remaining_hourly} hourly requests remaining.")

    dataset: dict[str, list[dict[str, Any]]] = {}
    coverage_matrix: dict[str, dict[str, Any]] = {}
    all_splits: list[dict[str, Any]] = []
    all_dividends: list[dict[str, Any]] = []

    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                dataset = json.load(f)
            logger.info(f"Loaded {len(dataset)} existing symbols from {CACHE_FILE}.")
        except Exception:
            dataset = {}

    for idx, sym in enumerate(SYMBOLS, 1):
        # Check if already cached with tier 2 observations
        has_tier2 = False
        if sym in dataset and len(dataset[sym]) > 0:
            dates = [b["ts"] for b in dataset[sym]]
            if any(d >= TIER2_START for d in dates) and any(d >= "2021-12-01" for d in dates):
                has_tier2 = True

        if has_tier2:
            logger.info(f"[{idx}/{len(SYMBOLS)}] {sym} already cached ({len(dataset[sym])} total bars). Skipping network call.")
            full_bars = dataset[sym]
        else:
            logger.info(f"[{idx}/{len(SYMBOLS)}] Fetching {sym} from Tiingo API ({TIER2_START} to {TIER2_END})...")
            while rate_limiter.remaining_hourly < 1:
                now_t = time.time()
                rate_limiter._purge(now_t)
                if rate_limiter.remaining_hourly >= 1:
                    break
                oldest = rate_limiter.hour_window[0] if rate_limiter.hour_window else now_t
                wait_sec = max(1.0, 3601.0 - (now_t - oldest))
                logger.info(f"Hourly rate limit active. Waiting {wait_sec:.1f}s for sliding window rolloff...")
                time.sleep(min(wait_sec, 15.0))

            t0 = time.perf_counter()
            raw_tier2_bars = client.fetch_historical_prices(sym, TIER2_START, TIER2_END)
            elapsed = time.perf_counter() - t0

            validated_tier2: list[dict[str, Any]] = []
            for b in raw_tier2_bars:
                validate_ohlcv_bar(b)
                # Verify no holdout leakage
                if b["ts"] >= HOLDOUT_CUTOFF_DATE:
                    raise RuntimeError(f"FATAL: Received observation {b['ts']} on or after cutoff {HOLDOUT_CUTOFF_DATE}!")
                validated_tier2.append(b)

            # Combine with warm-up bars
            warmup_bars = warmup_data.get(sym, [])
            full_bars = warmup_bars + validated_tier2
            dataset[sym] = full_bars

            # Save incrementally
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(dataset, f)

            logger.info(f"[{idx}/{len(SYMBOLS)}] {sym}: fetched {len(validated_tier2)} Tier 2 bars in {elapsed:.2f}s.")
            time.sleep(1.0)  # Gentle 1s spacing between requests

        # Extract Tier 2 specific bars for reporting
        tier2_bars = [b for b in full_bars if TIER2_START <= b["ts"] <= TIER2_END]
        t2_dates = [b["ts"] for b in tier2_bars]

        # Inventory corporate actions in Tier 2
        sym_splits = []
        sym_divs = []
        for b in tier2_bars:
            split_factor = float(b.get("split_factor", 1.0))
            if split_factor != 1.0:
                split_entry = {
                    "symbol": sym,
                    "date": b["ts"],
                    "split_factor": split_factor,
                    "raw_close": b["close"],
                    "adj_close": b["adj_close"],
                }
                sym_splits.append(split_entry)
                all_splits.append(split_entry)

            div_cash = float(b.get("div_cash", 0.0))
            if div_cash > 0.0:
                div_entry = {
                    "symbol": sym,
                    "date": b["ts"],
                    "div_cash": div_cash,
                    "raw_close": b["close"],
                    "adj_close": b["adj_close"],
                }
                sym_divs.append(div_entry)
                all_dividends.append(div_entry)

        zero_vol_count = sum(1 for b in tier2_bars if b.get("volume", 0.0) == 0.0)

        coverage_matrix[sym] = {
            "symbol": sym,
            "warmup_bars": len([b for b in full_bars if b["ts"] < TIER2_START]),
            "tier2_bars": len(tier2_bars),
            "total_bars": len(full_bars),
            "tier2_first_date": t2_dates[0] if t2_dates else None,
            "tier2_last_date": t2_dates[-1] if t2_dates else None,
            "splits_count": len(sym_splits),
            "splits": sym_splits,
            "dividends_count": len(sym_divs),
            "total_dividend_cash": round(sum(d["div_cash"] for d in sym_divs), 4),
            "zero_volume_days": zero_vol_count,
            "qualified": len(tier2_bars) >= 500,
        }

    # Verify key known stock splits
    split_summary = {}
    for sp in all_splits:
        split_summary[sp["symbol"]] = sp
    logger.info(f"Tier 2 total stock splits detected across universe: {len(all_splits)}")
    for sym_sp, detail in split_summary.items():
        logger.info(f"  Split: {sym_sp} on {detail['date']} factor {detail['split_factor']}")

    # Write coverage matrix
    COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COVERAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(coverage_matrix, f, indent=2)
    logger.info(f"Wrote Tier 2 coverage matrix to {COVERAGE_FILE}.")

    # Write corporate actions inventory
    corp_inv = {
        "manifest_version": "1.0.0",
        "stage": "Stage B2-N Tier 2 Corporate Actions",
        "observation_window": {"start": TIER2_START, "end": TIER2_END},
        "total_splits": len(all_splits),
        "splits": all_splits,
        "total_dividends": len(all_dividends),
        "dividends": all_dividends,
    }
    with open(CORP_FILE, "w", encoding="utf-8") as f:
        json.dump(corp_inv, f, indent=2)
    logger.info(f"Wrote Tier 2 corporate actions inventory to {CORP_FILE}.")

    return coverage_matrix


if __name__ == "__main__":
    matrix = acquire_and_qualify()
    total_t2 = sum(v["tier2_bars"] for v in matrix.values())
    print(f"COMPLETE: Acquired and qualified {len(matrix)} instruments, {total_t2} total Tier 2 bars.")
