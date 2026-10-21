"""Provider-Neutral Market Data Streaming & Storage Compliance Interface.

Provides unified streaming and session iteration while strictly enforcing
licensing compliance (e.g. prohibiting durable caching of Tiingo Free/Starter data).
"""
from __future__ import annotations

import gzip
import json
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from research.engine.validation import validate_market_state, validate_series


class StorageComplianceError(PermissionError):
    """Raised when an attempt is made to persist data under a license prohibiting durable storage."""


class StorageComplianceGuard:
    """Enforces data storage boundaries according to vendor terms."""

    # Providers whose terms forbid local durable storage (Parquet, SQLite, CSV, JSON on disk)
    EPHEMERAL_ONLY_PROVIDERS = {
        "tiingo_free",
        "tiingo_starter",
        "yahoo_finance_unlicensed",
    }

    @classmethod
    def assert_can_persist(cls, provider_id: str, destination_path: Path | str | None = None) -> None:
        norm_id = str(provider_id).strip().lower()
        if norm_id in cls.EPHEMERAL_ONLY_PROVIDERS:
            dest_str = f" to {destination_path}" if destination_path else ""
            raise StorageComplianceError(
                f"License Compliance Gate: Provider {provider_id!r} prohibits durable local caching/storage{dest_str}. "
                "Data must be consumed ephemerally in-memory only."
            )


class MarketDataProvider(ABC):
    """Abstract provider-neutral OHLCV streaming interface."""

    def __init__(self, provider_id: str, prohibit_durable_storage: bool = False):
        self.provider_id = provider_id
        self.prohibit_durable_storage = prohibit_durable_storage

    @abstractmethod
    def get_available_symbols(self) -> list[str]:
        """Return list of uppercase symbols available from this provider."""

    @abstractmethod
    def get_timeline(self, start_date: str | None = None, end_date: str | None = None) -> list[str]:
        """Return sorted list of distinct trading session dates (YYYY-MM-DD)."""

    @abstractmethod
    def stream_daily_slices(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        warmup_bars: int = 220,
    ) -> Iterator[tuple[str, dict[str, list[dict[str, Any]]]]]:
        """Yield (current_date, market_state) for each trading session.

        market_state contains bars strictly through current_date close.
        Enforces zero lookahead and optional ephemeral garbage collection.
        """

    def persist_to_disk(self, destination: Path | str, data: Any) -> None:
        """Attempt to save data to disk, guarded by license compliance."""
        StorageComplianceGuard.assert_can_persist(self.provider_id, destination)
        p = Path(destination)
        p.parent.mkdir(parents=True, exist_ok=True)
        # Concrete providers can override specific serializations if permitted


class StaticRegimeProvider(MarketDataProvider):
    """Loads permitted in-repo gzip JSON sample regimes."""

    def __init__(self, fixture_path: Path | str, regime_name: str = "calm_uptrend"):
        super().__init__(provider_id="in_repo_sample_regime", prohibit_durable_storage=False)
        self.fixture_path = Path(fixture_path)
        self.regime_name = regime_name
        self._raw_data: dict[str, Any] = {}
        self._bars: dict[str, list[dict[str, Any]]] = {}
        self._load()

    def _load(self) -> None:
        raw_regimes = json.loads(gzip.open(self.fixture_path, "rb").read())
        if self.regime_name not in raw_regimes:
            raise KeyError(f"Regime {self.regime_name!r} not found in {self.fixture_path}")
        self._raw_data = raw_regimes[self.regime_name]
        raw_bars = self._raw_data.get("bars", {})
        # Convert compact rows [ts, o, h, l, c, v] to bar dicts
        expanded: dict[str, list[dict[str, Any]]] = {}
        for ticker, rows in raw_bars.items():
            sym = ticker.upper()
            expanded[sym] = [
                {"ts": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]}
                for r in rows
            ]
        self._bars = validate_market_state(expanded, strict_future_rejection=False)

    def get_available_symbols(self) -> list[str]:
        return sorted(self._bars.keys())

    def get_timeline(self, start_date: str | None = None, end_date: str | None = None) -> list[str]:
        all_dates = sorted({b["ts"] for series in self._bars.values() for b in series})
        eval_start = start_date or self._raw_data.get("eval_start")
        eval_end = end_date or self._raw_data.get("eval_end")
        if eval_start:
            all_dates = [d for d in all_dates if d >= eval_start]
        if eval_end:
            all_dates = [d for d in all_dates if d <= eval_end]
        return all_dates

    def stream_daily_slices(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        warmup_bars: int = 220,
    ) -> Iterator[tuple[str, dict[str, list[dict[str, Any]]]]]:
        timeline = self.get_timeline(start_date, end_date)
        for date_str in timeline:
            # Point-in-time slice: only bars with ts <= date_str
            slice_state = {
                t: [b for b in self._bars[t] if b["ts"] <= date_str]
                for t in self._bars
            }
            yield date_str, slice_state


class InMemoryStreamProvider(MarketDataProvider):
    """Ephemeral in-memory provider designed for streaming API responses without disk persistence."""

    def __init__(
        self,
        provider_id: str,
        validated_bars: dict[str, list[dict[str, Any]]],
        prohibit_durable_storage: bool = False,
    ):
        super().__init__(provider_id=provider_id, prohibit_durable_storage=prohibit_durable_storage)
        self._bars = validate_market_state(validated_bars, strict_future_rejection=False)

    def get_available_symbols(self) -> list[str]:
        return sorted(self._bars.keys())

    def get_timeline(self, start_date: str | None = None, end_date: str | None = None) -> list[str]:
        dates = sorted({b["ts"] for series in self._bars.values() for b in series})
        if start_date:
            dates = [d for d in dates if d >= start_date]
        if end_date:
            dates = [d for d in dates if d <= end_date]
        return dates

    def stream_daily_slices(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        warmup_bars: int = 220,
    ) -> Iterator[tuple[str, dict[str, list[dict[str, Any]]]]]:
        timeline = self.get_timeline(start_date, end_date)
        for date_str in timeline:
            slice_state = {
                t: [b for b in self._bars[t] if b["ts"] <= date_str]
                for t in self._bars
            }
            yield date_str, slice_state
