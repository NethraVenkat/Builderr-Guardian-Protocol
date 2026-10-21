"""Guardian Alpha Track B Research Replay Engine Package."""
from research.engine.validation import (
    ValidationError,
    validate_calendar_date,
    validate_bar,
    validate_series,
    validate_market_state,
)
from research.engine.provider import (
    MarketDataProvider,
    StaticRegimeProvider,
    InMemoryStreamProvider,
    StorageComplianceGuard,
    StorageComplianceError,
)
from research.engine.corporate_actions import (
    CorporateActionRegistry,
    StockSplitEvent,
    CashDividendEvent,
)
from research.engine.accounting import (
    PortfolioState,
    FillResult,
    calculate_metrics,
    get_beta,
)
from research.engine.replay import ReplayEngine

__all__ = [
    "ValidationError",
    "validate_calendar_date",
    "validate_bar",
    "validate_series",
    "validate_market_state",
    "MarketDataProvider",
    "StaticRegimeProvider",
    "InMemoryStreamProvider",
    "StorageComplianceGuard",
    "StorageComplianceError",
    "CorporateActionRegistry",
    "StockSplitEvent",
    "CashDividendEvent",
    "PortfolioState",
    "FillResult",
    "calculate_metrics",
    "get_beta",
    "ReplayEngine",
]
