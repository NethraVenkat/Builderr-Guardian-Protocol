"""
Stage B2-I: Authentic Tiingo Tier 1 Historical Ingestion and Qualification.
Fetches 2014-09-01 to 2019-12-31 EOD data for the exact 24 production instruments.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
import sys
import time

# Ensure research package is resolvable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from research.engine.tiingo_client import (
    TiingoClient,
    validate_ohlcv_bar,
    RequestLedger,
    RateLimiter,
)

logger = logging.getLogger("acquire_tier1")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SYMBOLS = [
    "SPY", "QQQ", "DIA", "IWM", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY",
    "XLP", "XLU", "XLRE", "XLC", "SMH", "AAPL", "MSFT", "GOOGL", "AMZN",
    "META", "NVDA", "TSLA", "QLD", "SSO"
]

START_DATE = "2014-09-01"
TIER1_START = "2015-01-01"
END_DATE = "2019-12-31"

CACHE_DIR = Path("tiingo_cache")
CACHE_FILE = CACHE_DIR / "tier1_bars.json"
MANIFEST_FILE = Path("research/manifests") / "tier1_coverage_matrix.json"


def acquire_and_qualify() -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ledger = RequestLedger()
    rate_limiter = RateLimiter(ledger=ledger)
    client = TiingoClient(rate_limiter=rate_limiter, ledger=ledger)

    if not client.has_token:
        raise RuntimeError("TIINGO_API_KEY is not available in environment or registry.")

    logger.info(f"Starting Stage B2-I acquisition for {len(SYMBOLS)} symbols ({START_DATE} to {END_DATE})...")
    logger.info(f"RateLimiter status: {rate_limiter.remaining_hourly} hourly requests remaining.")

    dataset: dict[str, list[dict[str, Any]]] = {}
    coverage_matrix: dict[str, dict[str, Any]] = {}

    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                dataset = json.load(f)
            logger.info(f"Loaded {len(dataset)} existing symbols from cache.")
        except Exception:
            dataset = {}

    for idx, sym in enumerate(SYMBOLS, 1):
        if sym in dataset and len(dataset[sym]) > 0:
            logger.info(f"[{idx}/{len(SYMBOLS)}] {sym} already cached ({len(dataset[sym])} bars). Skipping network call.")
            validated_bars = dataset[sym]
            elapsed = 0.0
        else:
            logger.info(f"[{idx}/{len(SYMBOLS)}] Fetching {sym} from Tiingo API...")
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
            raw_bars = client.fetch_historical_prices(sym, START_DATE, END_DATE)
            elapsed = time.perf_counter() - t0

            validated_bars = []
            for b in raw_bars:
                validate_ohlcv_bar(b)
                validated_bars.append(b)

            dataset[sym] = validated_bars

            # Save incrementally
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(dataset, f)

            time.sleep(1.0)  # Gentle spacing between requests

        # Compute coverage stats
        div_count = sum(1 for b in validated_bars if b.get("div_cash", 0.0) > 0.0)
        split_count = sum(1 for b in validated_bars if b.get("split_factor", 1.0) != 1.0)
        dates = [b["ts"] for b in validated_bars]
        tier1_dates = [d for d in dates if d >= TIER1_START]

        coverage_matrix[sym] = {
            "symbol": sym,
            "provider_ticker": sym,
            "total_bars": len(validated_bars),
            "tier1_bars": len(tier1_dates),
            "first_date": dates[0] if dates else None,
            "last_date": dates[-1] if dates else None,
            "first_tier1_date": tier1_dates[0] if tier1_dates else None,
            "last_tier1_date": tier1_dates[-1] if tier1_dates else None,
            "dividend_events_count": div_count,
            "split_events_count": split_count,
            "fetch_latency_seconds": round(elapsed, 3),
            "coverage_verdict": "QUALIFIED" if len(validated_bars) > 0 else "FAILED",
            "inception_note": (
                "Inception 2015-10-07" if sym == "XLRE"
                else "Inception 2018-06-18" if sym == "XLC"
                else "Standard History"
            ),
        }
        logger.info(
            f"  -> {sym}: {len(validated_bars)} bars ({len(tier1_dates)} in Tier 1). "
            f"First: {coverage_matrix[sym]['first_date']}, Last: {coverage_matrix[sym]['last_date']}, "
            f"Divs: {div_count}, Splits: {split_count}."
        )

    # Save to local gitignored cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    logger.info(f"Saved dataset cache to {CACHE_FILE} ({CACHE_FILE.stat().st_size / 1024:.1f} KB).")

    # Save coverage manifest
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(coverage_matrix, f, indent=2)
    logger.info(f"Saved coverage manifest to {MANIFEST_FILE}.")

    return coverage_matrix


if __name__ == "__main__":
    matrix = acquire_and_qualify()
    print("\n=== COVERAGE MATRIX SUMMARY ===")
    for sym, c in matrix.items():
        print(f"{sym:6s} | Total: {c['total_bars']:4d} | Tier1: {c['tier1_bars']:4d} | Start: {c['first_date']} | End: {c['last_date']} | Divs: {c['dividend_events_count']:2d} | Splits: {c['split_events_count']:1d} | {c['coverage_verdict']}")
