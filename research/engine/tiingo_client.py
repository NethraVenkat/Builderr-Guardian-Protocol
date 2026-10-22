"""
Tiingo Historical Market Data Client & Provider Adapter.
Enforces:
  1. Strict secret redaction: tokens are never printed, logged, or serialized.
  2. Rate limiting & request budget: adheres to Tiingo Starter limits (50 req/hr, 1000 req/day).
  3. Hardcoded sealed-holdout protection: rejects any date >= 2022-01-01 before network call.
  4. Ephemeral caching / licensing compliance: complies with StorageComplianceGuard.
  5. Comprehensive point-in-time OHLCV and corporate action (split/dividend) parsing.
"""
from __future__ import annotations

import json
import logging
import math
import os
import sys
import time
from collections import deque
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator
import urllib.error
import urllib.parse
import urllib.request

from research.engine.provider import MarketDataProvider, StorageComplianceGuard

logger = logging.getLogger("tiingo_client")

HOLDOUT_CUTOFF_DATE = "2022-01-01"
TIINGO_BASE_URL = "https://api.tiingo.com/tiingo/daily"
MAX_REQUESTS_PER_HOUR = 50
MAX_REQUESTS_PER_DAY = 1000


class HoldoutProtectionViolation(PermissionError):
    """Raised when an attempt is made to request observations within the sealed holdout (2022-2024)."""


class TiingoTokenMissingError(RuntimeError):
    """Raised when no Tiingo API token is configured in env, registry, or local secret file."""


class TiingoRateLimitExceeded(RuntimeError):
    """Raised when request quota or rate limit is reached."""


class TiingoAPIError(RuntimeError):
    """Raised on HTTP error with secrets strictly redacted."""


class InvalidBarDataError(ValueError):
    """Raised when OHLCV observations violate positivity, finiteness, or bounds."""


def get_tiingo_token() -> str | None:
    """Safely retrieves the Tiingo API token from environment, registry, or uncommitted secret file."""
    # 1. Environment variable
    token = os.environ.get("TIINGO_API_KEY")
    if token and token.strip():
        return token.strip()

    # 2. Windows registry HKCU\Environment (for Windows environments where SetEnvironmentVariable was used)
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                val, _ = winreg.QueryValueEx(key, "TIINGO_API_KEY")
                if val and str(val).strip():
                    return str(val).strip()
        except Exception:
            pass

    # 3. Local uncommitted token file (strictly ignored by .gitignore)
    token_file = Path(".tiingo_token")
    if token_file.exists():
        try:
            content = token_file.read_text(encoding="utf-8").strip()
            if content:
                return content
        except Exception:
            pass

    return None


def redact_secret(text: str, secret: str | None) -> str:
    """Replaces secret with [REDACTED_TIINGO_TOKEN] in any string."""
    if not text or not secret:
        return text
    return text.replace(secret, "[REDACTED_TIINGO_TOKEN]")


class RequestLedger:
    """Persistent, append-only request ledger recording all Tiingo API queries."""

    def __init__(self, ledger_path: Path | None = None):
        self.ledger_path = ledger_path or (Path("research/manifests") / "tiingo_request_ledger.jsonl")

    def record(self, entry: dict[str, Any]) -> None:
        try:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to record to request ledger: {e}")

    def load_recent_timestamps(self, window_seconds: float = 86400.0) -> list[float]:
        if not self.ledger_path.exists():
            return []
        now = time.time()
        timestamps = []
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        ts = data.get("epoch_timestamp", 0.0)
                        if (now - ts) <= window_seconds:
                            timestamps.append(ts)
        except Exception:
            pass
        return sorted(timestamps)

    def get_all_entries(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        entries = []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries


class RateLimiter:
    """Sliding-window request rate limiter with ledger persistence."""

    def __init__(
        self,
        max_per_hour: int = MAX_REQUESTS_PER_HOUR,
        max_per_day: int = MAX_REQUESTS_PER_DAY,
        ledger: RequestLedger | None = None,
    ):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.ledger = ledger
        self.hour_window: deque[float] = deque()
        self.day_window: deque[float] = deque()
        self.total_requests = 0

        # Seed from persistent ledger if available
        if self.ledger:
            recent_ts = self.ledger.load_recent_timestamps(86400.0)
            now = time.time()
            for ts in recent_ts:
                if (now - ts) <= 3600.0:
                    self.hour_window.append(ts)
                self.day_window.append(ts)
            self.total_requests = len(self.day_window)

    def record_request(self) -> None:
        now = time.time()
        self._purge(now)
        if len(self.hour_window) >= self.max_per_hour:
            oldest = self.hour_window[0]
            wait_seconds = max(0.0, 3600.0 - (now - oldest))
            raise TiingoRateLimitExceeded(
                f"Hourly rate limit reached ({self.max_per_hour}/hr). Please wait {wait_seconds:.1f}s."
            )
        if len(self.day_window) >= self.max_per_day:
            raise TiingoRateLimitExceeded(f"Daily request quota reached ({self.max_per_day}/day).")

        self.hour_window.append(now)
        self.day_window.append(now)
        self.total_requests += 1

    def _purge(self, now: float) -> None:
        while self.hour_window and now - self.hour_window[0] > 3600.0:
            self.hour_window.popleft()
        while self.day_window and now - self.day_window[0] > 86400.0:
            self.day_window.popleft()

    @property
    def remaining_hourly(self) -> int:
        self._purge(time.time())
        return max(0, self.max_per_hour - len(self.hour_window))

    @property
    def remaining_daily(self) -> int:
        self._purge(time.time())
        return max(0, self.max_per_day - len(self.day_window))


class TiingoClient:
    """Secure, quota-managed client for Tiingo EOD endpoints."""

    def __init__(
        self,
        api_token: str | None = None,
        rate_limiter: RateLimiter | None = None,
        ledger: RequestLedger | None = None,
    ):
        self._token = api_token or get_tiingo_token()
        self.ledger = ledger or RequestLedger()
        self.rate_limiter = rate_limiter or RateLimiter(ledger=ledger)

    @property
    def has_token(self) -> bool:
        return bool(self._token)

    def _assert_holdout_protection(self, start_date: str | None, end_date: str | None) -> None:
        """Enforces that no request accesses or crosses the 2022-01-01 holdout boundary."""
        if start_date and start_date >= HOLDOUT_CUTOFF_DATE:
            raise HoldoutProtectionViolation(
                f"Blocked: start_date {start_date} is on or after sealed holdout cutoff {HOLDOUT_CUTOFF_DATE}."
            )
        if end_date and end_date >= HOLDOUT_CUTOFF_DATE:
            raise HoldoutProtectionViolation(
                f"Blocked: end_date {end_date} is on or after sealed holdout cutoff {HOLDOUT_CUTOFF_DATE}."
            )
        if end_date is None:
            raise HoldoutProtectionViolation(
                "Blocked: end_date must be explicitly specified to prevent streaming into sealed holdout (2022+)."
            )

    def _execute_request(
        self,
        url: str,
        endpoint_type: str = "generic",
        symbol: str = "",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Any:
        if not self._token:
            raise TiingoTokenMissingError(
                "Tiingo API token not configured. Set TIINGO_API_KEY in environment or registry."
            )

        headers = {
            "Authorization": f"Token {self._token}",
            "Accept": "application/json",
            "User-Agent": "Builderr-Guardian-Alpha-Researcher/1.0",
        }
        req = urllib.request.Request(url, headers=headers)

        max_retries = 3
        last_error = None
        for attempt in range(max_retries + 1):
            self.rate_limiter.record_request()
            try:
                with urllib.request.urlopen(req, timeout=20.0) as resp:
                    status = resp.status
                    payload_bytes = resp.read()
                    data = json.loads(payload_bytes.decode("utf-8"))
                    record_count = len(data) if isinstance(data, list) else 1
                    self.ledger.record({
                        "epoch_timestamp": time.time(),
                        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "endpoint_type": endpoint_type,
                        "http_status": status,
                        "retry_count": attempt,
                        "record_count": record_count,
                        "data_size_bytes": len(payload_bytes),
                        "result_classification": "SUCCESS",
                    })
                    return data
            except urllib.error.HTTPError as e:
                status = e.code
                redacted_msg = redact_secret(str(e), self._token)
                redacted_url = redact_secret(url, self._token)
                last_error = TiingoAPIError(f"HTTP Error {status} for {redacted_url}: {redacted_msg}")
                if status == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after else (2.0 ** attempt) * 5.0
                    logger.warning(f"Rate limited (429). Retrying after {wait_time}s...")
                    self.ledger.record({
                        "epoch_timestamp": time.time(),
                        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "endpoint_type": endpoint_type,
                        "http_status": status,
                        "retry_count": attempt,
                        "record_count": 0,
                        "data_size_bytes": 0,
                        "result_classification": "RATE_LIMITED",
                    })
                    if attempt < max_retries:
                        time.sleep(wait_time)
                        continue
                    raise TiingoRateLimitExceeded(f"HTTP 429 Rate Limited: {redacted_msg}") from None
                elif status in (500, 502, 503, 504) and attempt < max_retries:
                    wait_time = (2.0 ** attempt) * 2.0
                    time.sleep(wait_time)
                    continue
                else:
                    self.ledger.record({
                        "epoch_timestamp": time.time(),
                        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "endpoint_type": endpoint_type,
                        "http_status": status,
                        "retry_count": attempt,
                        "record_count": 0,
                        "data_size_bytes": 0,
                        "result_classification": "HTTP_ERROR",
                    })
                    raise last_error from None
            except Exception as e:
                redacted_msg = redact_secret(str(e), self._token)
                redacted_url = redact_secret(url, self._token)
                if attempt < max_retries:
                    wait_time = (2.0 ** attempt) * 2.0
                    logger.warning(f"Network error on attempt {attempt}: {redacted_msg}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                self.ledger.record({
                    "epoch_timestamp": time.time(),
                    "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "endpoint_type": endpoint_type,
                    "http_status": 0,
                    "retry_count": attempt,
                    "record_count": 0,
                    "data_size_bytes": 0,
                    "result_classification": "NETWORK_ERROR",
                })
                raise TiingoAPIError(f"Network error for {redacted_url}: {redacted_msg}") from None

    def fetch_metadata(self, ticker: str) -> dict[str, Any]:
        """Fetch instrument metadata (ticker, name, exchange, description, startDate, endDate)."""
        clean_ticker = ticker.strip().upper()
        url = f"{TIINGO_BASE_URL}/{urllib.parse.quote(clean_ticker)}"
        return self._execute_request(url, endpoint_type="metadata", symbol=clean_ticker)

    def fetch_historical_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> list[dict[str, Any]]:
        """Fetch historical daily bars for ticker between start_date and end_date."""
        clean_ticker = ticker.strip().upper()
        self._assert_holdout_protection(start_date, end_date)

        query = urllib.parse.urlencode({
            "startDate": start_date,
            "endDate": end_date,
            "format": "json",
        })
        url = f"{TIINGO_BASE_URL}/{urllib.parse.quote(clean_ticker)}/prices?{query}"
        raw_bars = self._execute_request(
            url,
            endpoint_type="prices",
            symbol=clean_ticker,
            start_date=start_date,
            end_date=end_date,
        )

        if not isinstance(raw_bars, list):
            return []

        # Normalize and validate raw bars
        normalized = []
        for b in raw_bars:
            dt_raw = b.get("date", "")[:10]
            norm_bar = {
                "ts": dt_raw,
                "ticker": clean_ticker,
                "open": float(b.get("open", 0.0)),
                "high": float(b.get("high", 0.0)),
                "low": float(b.get("low", 0.0)),
                "close": float(b.get("close", 0.0)),
                "volume": float(b.get("volume", 0.0)),
                "adj_open": float(b.get("adjOpen", b.get("open", 0.0))),
                "adj_high": float(b.get("adjHigh", b.get("high", 0.0))),
                "adj_low": float(b.get("adjLow", b.get("low", 0.0))),
                "adj_close": float(b.get("adjClose", b.get("close", 0.0))),
                "adj_volume": float(b.get("adjVolume", b.get("volume", 0.0))),
                "div_cash": float(b.get("divCash", 0.0)),
                "split_factor": float(b.get("splitFactor", 1.0)),
            }
            validate_ohlcv_bar(norm_bar)
            normalized.append(norm_bar)

        return normalized


def validate_ohlcv_bar(bar: dict[str, Any]) -> None:
    """Validates positivity, finiteness, and canonical OHLCV boundaries."""
    required_floats = ["open", "high", "low", "close", "adj_open", "adj_high", "adj_low", "adj_close"]
    for key in required_floats:
        val = bar.get(key)
        if val is None or not isinstance(val, (int, float)):
            raise InvalidBarDataError(f"Missing or non-numeric value for {key}: {val}")
        if math.isnan(val) or math.isinf(val):
            raise InvalidBarDataError(f"Non-finite numeric value for {key}: {val}")
        if val <= 0.0:
            raise InvalidBarDataError(f"Non-positive price for {key}: {val} (must be > 0)")

    vol = bar.get("volume", 0.0)
    if math.isnan(vol) or math.isinf(vol) or vol < 0.0:
        raise InvalidBarDataError(f"Invalid volume: {vol}")

    # Boundary relationships
    if bar["low"] > bar["high"]:
        raise InvalidBarDataError(f"Invalid bounds: low {bar['low']} > high {bar['high']}")
    if bar["adj_low"] > bar["adj_high"]:
        raise InvalidBarDataError(f"Invalid adjusted bounds: adj_low {bar['adj_low']} > adj_high {bar['adj_high']}")


class TiingoHistoricalProvider(MarketDataProvider):
    """In-memory MarketDataProvider powered by Tiingo API or mock payload."""

    def __init__(
        self,
        symbols: list[str],
        start_date: str = "2015-01-01",
        end_date: str = "2019-12-31",
        warmup_start_date: str = "2014-09-01",
        client: TiingoClient | None = None,
        preloaded_bars: dict[str, list[dict[str, Any]]] | None = None,
        price_semantics: str = "legacy_v20",
    ):
        super().__init__(provider_id="tiingo_starter", prohibit_durable_storage=True)
        self.symbols = [s.strip().upper() for s in symbols]
        self.start_date = start_date
        self.end_date = end_date
        self.warmup_start_date = warmup_start_date
        self.client = client or TiingoClient()
        self._bars: dict[str, list[dict[str, Any]]] = preloaded_bars or {}
        self._timeline: list[str] = []
        self.price_semantics = price_semantics

        if not self._bars and self.client.has_token:
            self._fetch_all()
        elif self._bars:
            self._build_timeline()

    def _fetch_all(self) -> None:
        """Download authorized Tier 1 data in-memory."""
        for sym in self.symbols:
            # Handle historical alias: META traded as FB prior to 2022-06-09
            fetch_ticker = "FB" if sym == "META" and self.end_date < "2022-06-09" else sym
            bars = self.client.fetch_historical_prices(
                fetch_ticker,
                self.warmup_start_date,
                self.end_date,
            )
            # If fetch_ticker returned empty (as live FB does for pre-2022 data on Tiingo), fallback to sym
            if not bars and fetch_ticker != sym:
                bars = self.client.fetch_historical_prices(
                    sym,
                    self.warmup_start_date,
                    self.end_date,
                )
            # Re-label ticker to production symbol
            for b in bars:
                b["ticker"] = sym
            self._bars[sym] = bars

        self._build_timeline()

    def _build_timeline(self) -> None:
        dates = set()
        for bars in self._bars.values():
            dates.update(b["ts"] for b in bars if self.start_date <= b["ts"] <= self.end_date)
        self._timeline = sorted(list(dates))

    def get_available_symbols(self) -> list[str]:
        return list(self._bars.keys())

    def get_timeline(self, start_date: str | None = None, end_date: str | None = None) -> list[str]:
        s = start_date or self.start_date
        e = end_date or self.end_date
        return [d for d in self._timeline if s <= d <= e]

    def stream_daily_slices(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        warmup_bars: int = 220,
    ) -> Iterator[tuple[str, dict[str, list[dict[str, Any]]]]]:
        timeline = self.get_timeline(start_date, end_date)

        # Pre-extract split events by symbol for high-performance causal alignment
        splits_by_sym: dict[str, list[tuple[str, float]]] = {}
        for sym, bars in self._bars.items():
            sps = [(b["ts"], float(b.get("split_factor", 1.0)))
                   for b in bars if float(b.get("split_factor", 1.0)) != 1.0]
            splits_by_sym[sym] = sps

        for cur_dt in timeline:
            market_state: dict[str, list[dict[str, Any]]] = {}
            for sym, all_bars in self._bars.items():
                # Slice point-in-time: bars where ts <= cur_dt
                visible = [b for b in all_bars if b["ts"] <= cur_dt]
                if visible:
                    window = visible[-warmup_bars:]
                    if self.price_semantics == "legacy_v20":
                        # Legacy V20/V21 semantics: Tiingo backward adjusted close in close field
                        market_state[sym] = [
                            {
                                "ts": b["ts"],
                                "open": b["open"],
                                "high": b["high"],
                                "low": b["low"],
                                "close": b.get("adj_close", b["close"]),
                                "raw_close": b.get("raw_close", b.get("close")),
                                "raw_open": b.get("raw_open", b.get("open")),
                                "adj_close": b.get("adj_close", b["close"]),
                                "adj_open": b.get("adj_open", b["open"]),
                                "volume": b.get("volume", 0.0),
                                "div_cash": b.get("div_cash", 0.0),
                                "split_factor": b.get("split_factor", 1.0),
                            }
                            for b in window
                        ]
                    else:
                        # Production-faithful Causal Semantics (Option B):
                        # Latest bar (at cur_dt) has close = raw_close (economically valid market price on cur_dt).
                        # Historical lookback bars are adjusted only for past splits effective on or before cur_dt.
                        # Future splits after cur_dt are strictly excluded.
                        sym_splits = [sp for sp in splits_by_sym.get(sym, []) if sp[0] <= cur_dt]
                        bar_list = []
                        for b in window:
                            b_ts = b["ts"]
                            raw_c = b.get("raw_close", b.get("close"))
                            raw_o = b.get("raw_open", b.get("open"))
                            raw_h = b.get("high", raw_c)
                            raw_l = b.get("low", raw_c)
                            cum_split = 1.0
                            if sym_splits:
                                for sp_date, sp_factor in sym_splits:
                                    if b_ts < sp_date:
                                        cum_split *= sp_factor
                            causal_c = raw_c / cum_split
                            causal_o = raw_o / cum_split
                            causal_h = raw_h / cum_split
                            causal_l = raw_l / cum_split

                            bar_list.append({
                                "ts": b_ts,
                                "open": causal_o,
                                "high": causal_h,
                                "low": causal_l,
                                "close": causal_c,
                                "raw_close": raw_c,
                                "raw_open": raw_o,
                                "causal_adj_close": causal_c,
                                "causal_adj_open": causal_o,
                                "tiingo_backward_adj_close": b.get("adj_close", raw_c),
                                "volume": b.get("volume", 0.0),
                                "div_cash": b.get("div_cash", 0.0),
                                "split_factor": b.get("split_factor", 1.0),
                            })
                        market_state[sym] = bar_list
            yield cur_dt, market_state
