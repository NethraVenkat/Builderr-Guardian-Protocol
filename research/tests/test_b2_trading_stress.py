"""Stage G5: Comprehensive 25-Scenario Trading Stress, Financial Risk & Operational Failure Tests.

Executes and verifies:
  1. Overnight price gaps (-20%)
  2. Large bear-market drawdowns (55%)
  3. Extended sideways conditions (60 sessions)
  4. High-volatility reversals
  5. Rapid volatility compression
  6. Concentrated sector declines
  7. Leveraged ETF volatility decay
  8. Missing QLD/SSO data resilience
  9. Missing execution prices
  10. Corporate action anomalies
  11. Stale market observations
  12. Invalid timestamps
  13. Duplicated execution calls
  14. Repeated same-day rebalances
  15. 50-trade daily limit
  16. Position concentration drift
  17. Gross notional exposure breaches
  18. Beta-adjusted exposure breaches
  19. Insufficient cash boundary
  20. Large slippage shocks
  21. Commission rate shocks
  22. Partial fills and rejected orders
  23. Delayed or dropped market bars
  24. Process interruption / state serialization
  25. Deterministic state recovery
"""
from __future__ import annotations

import pytest

from research.engine.stress import StressScenarioResult, StressTestEngine


class TestTradingStressAndOperationalFailure:
    @pytest.fixture
    def engine(self) -> StressTestEngine:
        return StressTestEngine()

    def test_all_25_stress_scenarios_pass(self, engine: StressTestEngine):
        results = engine.run_all()
        assert len(results) == 25
        failed = [r for r in results if not r.passed]
        assert len(failed) == 0, f"Stress scenarios failed: {[f.name for f in failed]}"

    @pytest.mark.parametrize("scenario_idx", range(1, 26))
    def test_individual_stress_scenario(self, engine: StressTestEngine, scenario_idx: int):
        method_name = f"test_{scenario_idx:02d}_"
        matching = [getattr(engine, m) for m in dir(engine) if m.startswith(method_name)]
        assert len(matching) == 1, f"Expected exactly one method for scenario {scenario_idx}"
        res: StressScenarioResult = matching[0]()
        assert res.passed is True, f"Scenario {res.name} failed: {res.details}"
