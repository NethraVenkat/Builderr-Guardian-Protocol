# V29F - Independent synthetic-fixture feasibility

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

**CONDITIONAL feasibility; design only.** No generator, fixture, expectations, candidate, test patch or implementation was created. No regression suite was executed in V29F. The following choices are independent engineering stress parameters, not values estimated from original market prices, moments, correlations, returns or strategy results.

## Design inputs and independence boundary

Use only the program's provider schema, universe metadata, validation/accounting/corporate-action interfaces and mathematical definitions. The current compact input uses top-level scenario entries with `eval_start`, `eval_end` and `bars`; each symbol has ordered `[ts, open, high, low, close, volume]` rows. Agent history/warmup requirements and financial invariants guide coverage, not original fixture lengths/performance.

No old observation is a seed, calibration input, sample, target or validation oracle for generation. Original expected financial numbers are not reproduced in this design or used to choose parameters. Test-source review identifies which assertions depend on historical context; it is not a statistical analysis of that context. Production universe labels may be schema identifiers, not claims about those securities' historical prices. The existing 69/71-file candidates remain immutable.

## Proposed mathematical specification - not implemented

- Version: `synthetic-fixture-v1`; fixed ASCII seed: `GUARDIAN_ALPHA_SYNTHETIC_V1_DESIGN_SEED_0001`.
- Deterministic draws: SHA-256 of a canonical UTF-8 key consisting of version, seed, scenario, sorted-universe symbol, field, decimal session index and decimal draw counter, separated by `|`, with no locale or timestamps. Interpret digest bytes as a big-endian unsigned integer. Use rejection sampling before reduction to each prescribed integer range; increase draw counter on rejection. This avoids a platform PRNG/Gaussian implementation dependency and modulo bias. Different fields/labels use separate keys.
- Timeline: 400 invented weekday sessions beginning 2000-01-03, skipping Saturdays/Sundays only. First 220 sessions are warmup, next 180 are scored. Do not import a real exchange holiday calendar. Every timestamp is explicitly synthetic, before 2022 and not a representation of actual sessions or Tier 3 observations.
- Symbols: fixed sorted labels from the selected program universe metadata, recorded verbatim in synthetic provenance. Do not learn symbol coverage from the original sample. Symbol index i starts with an invented previous close of `1,000,000 + 1,000*i` integer ticks. Tick scale is 10,000 per currency unit.
- Price arithmetic: exact integer/rational operations with specified round-half-even and a floor of one tick. With denominator 100,000, compute open from previous close and an independent gap in [-50,50]; compute close from open and the scenario drift plus independently drawn innovation plus an explicitly imposed shock. No floating Gaussian sampler, observed market parameters or strategy feedback enters generation.
- `synthetic_rising`: drift +100 and innovation [-40,40]. `synthetic_falling`: drift -100 and innovation [-40,40]. `synthetic_shock`: drift 0, innovation [-40,40] normally and [-2000,2000] during scored sessions 88 through 96; impose -12000 at scored session 90 and +3000 at 91. These are arbitrary rational stress knobs, not fitted market dynamics. Their common scenario structure creates imposed co-movement; no original correlation is learned or claimed.
- Let q be max(1, ceil(max(open,close)/10000)). High is max(open,close)+q*(1+draw[0,40]); low is max(1,min(open,close)-q*(1+independent draw[0,40])). Volume is 1,000,000+draw[0,999999]. Require `0 < low <= min(open,close) <= max(open,close) <= high`, positive finite numeric prices, integer positive volume, unique increasing dates and complete declared symbol coverage.
- Serialize prices as exact fixed-point decimal numeric tokens derived from ticks, not locale formatting. Sort keys/symbols; use a specified canonical JSON encoding (UTF-8, no incidental whitespace or build timestamp). Canonical uncompressed JSON is the normative digest. For byte-stable gzip, specify fixed header (mtime 0, no filename/comment, fixed OS byte) and deterministic stored DEFLATE blocks with fixed boundaries, CRC32 and length; do not assume equal compression across zlib versions. Reproduction must verify both logical and compressed bytes.

All ranges/formulas require review before implementation. Never change seeds/parameters to maximize strategy returns, recover an old Sharpe/Calmar or manufacture test PASS. If coverage is insufficient, a separately justified design version may target missing invariants, with previous failed inputs/results preserved.

## Corporate actions and economic correctness

The current compact OHLCV rows cannot alone encode a split/dividend stream. Do not add silently ignored fields or call unchanged StaticRegimeProvider action-aware. Propose a separately versioned synthetic-action sidecar/adapter using the engine's supported event contracts, with explicit pre-open/ex-date/payment ordering.

An independent action micro-scenario may place an invented 2-for-1 split at scored session 60 and an invented fixed cash dividend of 0.05 currency unit at scored session 120. These are not issuer events or market-derived values. Specify share/price reciprocal adjustment and cash/receivable timing, and generate post-action raw prices consistently. Keep the action scenario separate from the base three scenarios until the adapter is independently verified. Preserve frozen agent.py/v12_candidate_ae.py.

Require hand-calculated tiny-account controls, independent accounting, corporate-action conservation and no-phantom-PnL checks. Existing self-contained action tests retain their invariant purpose; additional event/fixture-integration tests are needed. A successful synthetic action replay is not corporate-event coverage on authentic history.

## Provenance and reproducibility requirements

Future authorized work must retain generator source hash, generator/model version, seed/key encoding, rational arithmetic/rounding rules, timeline definition, symbol list, parameters, schema/action versions, canonical/compressed hashes, environment and independently reproduced receipts. Record that no original observations/statistics or expected returns were used. Mark every fixture, derived metric and guide SYNTHETIC, with no historical-performance or data-rights equivalence claim. Identify authorship and intended license for new generator/output rather than adopting a grant for the old sample by implication.

Two clean independent executions must reproduce the bytes; negative controls must reject nonpositive/malformed/duplicate/future or causally inconsistent inputs. No such reproduction/control was executed in V29F.

## Impact on the currently recorded 253 tests

Source: V29E `evidence/final_regression.json` IDs, confirmed identical in V29E-R `evidence/v2_collection.json` and `v2_regression.json`. Static AST/source-structure triage spans 27 files / 146 base test functions and preserves parameterized IDs. No pytest collection or fixture-reading execution occurred here. Numeric historical expectations were not used as generator inputs.

| Category | Recorded cases | Meaning |
|---|---:|---|
| A | 203 | Retains invariant/unit purpose; no original-sample dependency found in reviewed test/helper paths. Candidate for reuse, not a new PASS or proof every line is unchanged for a new package. |
| B | 38 | Fixture, calendar, integration or checksum contract must be rebound and scientifically requalified. Invariant intent can remain; current inputs/assumptions cannot simply be relabeled synthetic. |
| C | 12 | Historical-result/context assertion is not applicable as-is to new synthetic data/root. Preserve original tests/evidence privately; any new control needs its own name, purpose and independently reviewed expected result. |

The sum is 253; this is a design triage, not an execution result. All appropriate unit/integration controls must be rerun in a future candidate. New generator/action/provenance/timeline tests add scope. The final synthetic-suite count is UNKNOWN; maintaining 253 by deleting, renaming away or loosening historical assertions is not an acceptance criterion.

### B: explicit requalification rules

| Base function | Required review |
|---|---|
| `test_benchmark_metrics_validity` | Change input binding and review benchmark/coverage assumptions |
| `test_parity_classification_against_preview` | Reuse parity method on new inputs; requalify provider/preview binding |
| `test_canonical_trace_hash_reproducibility` | Requalify determinism on newly named synthetic input |
| `test_replay_trace_logs_do_not_leak_raw_ohlcv` | Retain hygiene rule; requalify synthetic provider/dates and trace behavior |
| `test_walk_forward_evaluation_on_calm_uptrend` | Requalify synthetic calendar/window sample sizes and statistical interpretation |
| `test_replay_engine_matches_official_preview` | Retain algorithm comparison; requalify preview and engine using same new input |
| `test_static_regime_provider_loading` | Replace original date/symbol/count contract only in separately reviewed synthetic tests |
| `test_candidates_run_cleanly_all_regimes` | Rebind all parameterized scenarios; validate errors/risk/invariants without assuming PASS |
| `test_candidate_determinism` | Requalify repeatability on independently generated inputs |
| `test_regime_calendar_lengths_and_notional` | New synthetic calendar-length contract and notional checks require qualification |
| `test_accounting_invariants_and_slippage_integrity` | Invariant remains valid; requalify event/price adapter and numeric tolerance |
| `test_gate7_pristine_holdout_isolation` | Retain firewall intent; validate new synthetic label/timeline and negative boundaries |
| `test_holdout_boundary_strict_absence` | Rebind scenario names and verify synthetic pre-2022 timeline |
| `test_release_manifest_integrity` | New exact-file/hash contract required; preserve original manifest separately |

### C: historical/context limits

| Base function | Why not transferable |
|---|---|
| `test_historical_decision_accounting_and_metrics` | Original market-window metrics/decision hashes; new synthetic expectations require new scientific baseline |
| `test_baseline_vol_spike_attribution_truth` | Historical attribution truth is specific to the original observations |
| `test_four_way_candidate_deterministic_returns` | Original strategy-return reference is not a synthetic performance requirement |
| `test_statistical_uncertainty_negative_control` | Original sample statistical conclusion cannot transfer to an invented return path |
| `test_gate1_raw_fixture_calendar_dates` | Original calendar/warmup counts are historical facts, not generator constraints |
| `test_gate2_attribution_bridge_and_defensive_holdings` | Historical attribution/holding conclusions are not transferable |
| `test_gate3_cost_sensitivity_hierarchy` | Historical strategy/cost ordering is not guaranteed on new data |
| `test_cent_level_rounding_order_reconciliation` | Historical numeric bridge is sample-specific; independently designed rounding controls can supplement it |
| `test_v15_clean_worktree_commit_id` | Historical clean-clone commit pin does not describe a new publication root |
| `test_provider_rolling_10_year_history_insufficiency` | Historical procurement-window assessment may be out of scope for a synthetic-only distribution |

### Exact per-ID disposition

A/B/C meanings and function-specific reasons above apply to every row below. No test is removed by this report.

| Exact existing test ID | Category |
|---|---|
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[QQQ-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[QQQ-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[QQQ--inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[cash-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[cash-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[cash--inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[portfolio_cash-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[portfolio_cash-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[portfolio_cash--inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[quantity-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[quantity-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[quantity--inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[price-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[price-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[price--inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[avg_cost-nan]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[avg_cost-inf]` | A |
| `tests/test_e0_release.py::test_invalid_input_abstains_without_advancing_state_and_recovers[avg_cost--inf]` | A |
| `tests/test_e0_release.py::test_closes_rejects_nonfinite[nan]` | A |
| `tests/test_e0_release.py::test_closes_rejects_nonfinite[inf]` | A |
| `tests/test_e0_release.py::test_closes_rejects_nonfinite[-inf]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[held_zero]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[held_negative]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[negative_quantity]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[finite_ratio_overflow]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[huge_quantity]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[zero_close]` | A |
| `tests/test_e0_release.py::test_additional_invalid_boundary_preserves_existing_state[negative_close]` | A |
| `tests/test_e0_release.py::test_zero_quantity_placeholder_is_valid` | A |
| `tests/test_e0_release.py::test_pinned_source_and_interface` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[up]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[selloff]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[crash]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[recovery]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[false_spike]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[volatile_up]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[lowvol_down]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[whipsaw]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[flat]` | A |
| `tests/test_e0_release.py::test_contract_and_cash_affordability[gap]` | A |
| `tests/test_e0_release.py::test_sizing_does_not_spend_more_than_available_cash[0]` | A |
| `tests/test_e0_release.py::test_sizing_does_not_spend_more_than_available_cash[1]` | A |
| `tests/test_e0_release.py::test_sizing_does_not_spend_more_than_available_cash[100]` | A |
| `tests/test_e0_release.py::test_sizing_does_not_spend_more_than_available_cash[100000]` | A |
| `tests/test_e0_release.py::test_name_and_beta_target_boundaries[0.239999]` | A |
| `tests/test_e0_release.py::test_name_and_beta_target_boundaries[0.24]` | A |
| `tests/test_e0_release.py::test_name_and_beta_target_boundaries[0.240001]` | A |
| `tests/test_e0_release.py::test_name_and_beta_target_boundaries[0.3]` | A |
| `tests/test_e0_release.py::test_name_and_beta_target_boundaries[1.0]` | A |
| `tests/test_e0_release.py::test_ordinary_repeated_call_has_no_duplicate_orders` | A |
| `tests/test_e0_release.py::test_sell_orders_do_not_exceed_holdings` | A |
| `tests/test_e0_release.py::test_heavy_input_runtime` | A |
| `tests/test_e0_release.py::test_historical_decision_accounting_and_metrics[calm_uptrend]` | C |
| `tests/test_e0_release.py::test_historical_decision_accounting_and_metrics[moderate_selloff]` | C |
| `tests/test_e0_release.py::test_historical_decision_accounting_and_metrics[vol_spike_snapback]` | C |
| `tests/test_e0_release.py::test_release_manifest_integrity` | B |
| `research/tests/test_b2_benchmark.py::TestPerformanceBenchmark::test_benchmark_metrics_validity` | B |
| `research/tests/test_b2_causality_integrity.py::TestCausalityAndTemporalIntegrity::test_nonmonotonic_timestamp_rejections` | A |
| `research/tests/test_b2_causality_integrity.py::TestCausalityAndTemporalIntegrity::test_duplicate_session_timestamp_rejection` | A |
| `research/tests/test_b2_causality_integrity.py::TestCausalityAndTemporalIntegrity::test_calendar_edge_cases` | A |
| `research/tests/test_b2_causality_integrity.py::TestCausalityAndTemporalIntegrity::test_next_session_open_execution_causality` | A |
| `research/tests/test_b2_causality_integrity.py::TestCausalityAndTemporalIntegrity::test_strict_future_bar_exclusion` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_decimal_double_entry_accounting_invariant` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_partial_fill_on_cash_boundary` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_insufficient_funds_rejection` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_halted_asset_missing_price_rejection` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_unheld_short_sale_rejection` | A |
| `research/tests/test_b2_financial_accounting.py::TestIndependentFinancialAccounting::test_repeated_stock_splits_invariant` | A |
| `research/tests/test_b2_financial_accounting.py::TestDividendLifecycleAndTimingEnforcement::test_dividend_receivable_vs_cash_timing_boundary` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_dividend_paid_after_position_liquidated` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_duplicate_corporate_action_registration_deduplication` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_missing_payment_date_rejected_by_policy` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_missing_payment_date_impute_settlement_lag` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_missing_payment_date_impute_business_days_10` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_business_days_vs_calendar_days_distinction` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_missing_payment_date_ex_date_compatibility` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_fees_incurred_only_on_executed_trades` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_equity_conservation_under_zero_movement` | A |
| `research/tests/test_b2_financial_corner_cases.py::TestFinancialCornerCases::test_separation_of_gross_notional_vs_beta_adjusted_leverage` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_clean_bar_passes` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_negative_or_zero_price_rejected` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_geometric_integrity_rejection` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_negative_volume_rejection` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_weekend_date_rejection` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_pre_inception_date_rejection` | A |
| `research/tests/test_b2_ingestion_quality.py::TestDataQualityAuditor::test_series_chronology_and_duplicate_rejection` | A |
| `research/tests/test_b2_ingestion_quality.py::TestIngestionPipelineAndCompliance::test_http_status_classification` | A |
| `research/tests/test_b2_ingestion_quality.py::TestIngestionPipelineAndCompliance::test_ticker_alias_resolution` | A |
| `research/tests/test_b2_ingestion_quality.py::TestIngestionPipelineAndCompliance::test_dataset_hash_reproducibility` | A |
| `research/tests/test_b2_ingestion_quality.py::TestIngestionPipelineAndCompliance::test_ingestion_pipeline_prohibits_durable_storage_on_ephemeral_tier` | A |
| `research/tests/test_b2_ingestion_quality.py::TestIngestionPipelineAndCompliance::test_mock_ingestion_handles_rate_limit_and_auth_failures` | A |
| `research/tests/test_b2_leveraged_overlay.py::test_overlay_inactive_when_qld_sso_missing` | A |
| `research/tests/test_b2_leveraged_overlay.py::test_overlay_activates_in_calm_uptrend_with_qld_sso` | A |
| `research/tests/test_b2_leveraged_overlay.py::test_overlay_deactivates_on_high_volatility` | A |
| `research/tests/test_b2_leveraged_overlay.py::test_overlay_liquidation_on_trend_breakdown` | A |
| `research/tests/test_b2_leveraged_overlay.py::test_replay_engine_executes_leveraged_overlay_with_slippage` | A |
| `research/tests/test_b2_loss_reduction.py::test_candidates_match_competition_contract` | A |
| `research/tests/test_b2_loss_reduction.py::test_emergency_exit_breaks_five_day_cadence` | A |
| `research/tests/test_b2_loss_reduction.py::test_drawdown_multiplier_de_risks_portfolio` | A |
| `research/tests/test_b2_loss_reduction.py::test_defensive_weights_exclude_xle` | A |
| `research/tests/test_b2_loss_reduction.py::test_baseline_vol_spike_attribution_truth` | C |
| `research/tests/test_b2_replay_independence.py::TestReplayIndependenceAndParity::test_parity_classification_against_preview[calm_uptrend]` | B |
| `research/tests/test_b2_replay_independence.py::TestReplayIndependenceAndParity::test_parity_classification_against_preview[moderate_selloff]` | B |
| `research/tests/test_b2_replay_independence.py::TestReplayIndependenceAndParity::test_parity_classification_against_preview[vol_spike_snapback]` | B |
| `research/tests/test_b2_replay_independence.py::TestReplayIndependenceAndParity::test_independent_hand_calculated_replay` | A |
| `research/tests/test_b2_replay_independence.py::TestReplayIndependenceAndParity::test_canonical_trace_hash_reproducibility` | B |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_active_concentration_clamping_and_rejection` | A |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_telemetry_only_concentration_breach_monitoring` | A |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_active_gross_beta_leverage_gating_on_leveraged_etf` | A |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_active_daily_trade_limit_enforcement` | A |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_overnight_market_gap_concentration_drift` | A |
| `research/tests/test_b2_risk_enforcement.py::TestRiskEnforcementVersusTelemetry::test_catastrophic_drawdown_detection` | A |
| `research/tests/test_b2_soak_validation.py::test_missing_soak_directory` | A |
| `research/tests/test_b2_soak_validation.py::test_pending_soak_directory` | A |
| `research/tests/test_b2_soak_validation.py::test_short_run_yields_incomplete_verdict` | A |
| `research/tests/test_b2_soak_validation.py::test_full_7200s_clean_run_passes` | A |
| `research/tests/test_b2_soak_validation.py::test_corrupted_telemetry_sequence_fails` | A |
| `research/tests/test_b2_soak_validation.py::test_invariant_failure_in_summary_fails` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.parquet-tiingo_free]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.parquet-tiingo_starter]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.parquet-yahoo_finance_unlicensed]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.csv-tiingo_free]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.csv-tiingo_starter]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.csv-yahoo_finance_unlicensed]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.json-tiingo_free]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.json-tiingo_starter]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.json-yahoo_finance_unlicensed]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.sqlite-tiingo_free]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.sqlite-tiingo_starter]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.sqlite-yahoo_finance_unlicensed]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.db-tiingo_free]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.db-tiingo_starter]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_forbidden_storage_targets_blocked[.db-yahoo_finance_unlicensed]` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_in_memory_provider_blocks_persist_call` | A |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_replay_trace_logs_do_not_leak_raw_ohlcv` | B |
| `research/tests/test_b2_storage_compliance.py::TestStorageComplianceAudit::test_ephemeral_provider_generates_zero_disk_artifacts` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_all_25_stress_scenarios_pass` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[1]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[2]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[3]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[4]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[5]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[6]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[7]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[8]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[9]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[10]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[11]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[12]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[13]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[14]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[15]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[16]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[17]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[18]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[19]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[20]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[21]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[22]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[23]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[24]` | A |
| `research/tests/test_b2_trading_stress.py::TestTradingStressAndOperationalFailure::test_individual_stress_scenario[25]` | A |
| `research/tests/test_b2_walk_forward.py::TestCandidateStrategyAndOptimization::test_candidate_interface_parity` | A |
| `research/tests/test_b2_walk_forward.py::TestCandidateStrategyAndOptimization::test_candidate_drawdown_derisking` | A |
| `research/tests/test_b2_walk_forward.py::TestWalkForwardBootstrapAndValidator::test_paired_bootstrap_identical_series` | A |
| `research/tests/test_b2_walk_forward.py::TestWalkForwardBootstrapAndValidator::test_paired_bootstrap_strictly_superior_candidate` | A |
| `research/tests/test_b2_walk_forward.py::TestWalkForwardBootstrapAndValidator::test_walk_forward_evaluation_on_calm_uptrend` | B |
| `research/tests/test_baseline_parity.py::TestBaselineParity::test_replay_engine_matches_official_preview[calm_uptrend]` | B |
| `research/tests/test_baseline_parity.py::TestBaselineParity::test_replay_engine_matches_official_preview[moderate_selloff]` | B |
| `research/tests/test_baseline_parity.py::TestBaselineParity::test_replay_engine_matches_official_preview[vol_spike_snapback]` | B |
| `research/tests/test_corporate_actions.py::TestCorporateActions::test_forward_stock_split_accounting_invariant` | A |
| `research/tests/test_corporate_actions.py::TestCorporateActions::test_reverse_stock_split_accounting_invariant` | A |
| `research/tests/test_corporate_actions.py::TestCorporateActions::test_cash_dividend_distribution` | A |
| `research/tests/test_corporate_actions.py::TestCorporateActions::test_unheld_ticker_dividend_yields_zero` | A |
| `research/tests/test_provider_compliance.py::TestProviderCompliance::test_tiingo_storage_prohibition_guard` | A |
| `research/tests/test_provider_compliance.py::TestProviderCompliance::test_permitted_local_provider_storage` | A |
| `research/tests/test_provider_compliance.py::TestProviderCompliance::test_in_memory_stream_provider_ephemeral_usage` | A |
| `research/tests/test_provider_compliance.py::TestProviderCompliance::test_static_regime_provider_loading` | B |
| `research/tests/test_replay_accounting.py::TestReplayAccounting::test_cash_conservation_invariant` | A |
| `research/tests/test_replay_accounting.py::TestReplayAccounting::test_leveraged_etf_slippage` | A |
| `research/tests/test_replay_accounting.py::TestReplayAccounting::test_sell_precedes_buy_cash_replenishment` | A |
| `research/tests/test_replay_accounting.py::TestReplayAccounting::test_missing_execution_price_drops_cleanly` | A |
| `research/tests/test_replay_accounting.py::TestReplayAccounting::test_short_selling_prevention` | A |
| `research/tests/test_risk_limits.py::TestRiskLimits::test_gross_beta_leverage_calculation` | A |
| `research/tests/test_risk_limits.py::TestRiskLimits::test_concentration_streak_tracking` | A |
| `research/tests/test_risk_limits.py::TestRiskLimits::test_catastrophic_drawdown_detection` | A |
| `research/tests/test_v11_candidates.py::test_candidate_contract_parity` | A |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_A]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_B]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_C]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_D]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_E]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_F]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[calm_uptrend-Candidate_AE]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_A]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_B]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_C]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_D]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_E]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_F]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[moderate_selloff-Candidate_AE]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_A]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_B]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_C]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_D]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_E]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_F]` | B |
| `research/tests/test_v11_candidates.py::test_candidates_run_cleanly_all_regimes[vol_spike_snapback-Candidate_AE]` | B |
| `research/tests/test_v11_candidates.py::test_candidate_determinism` | B |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_emergency_sell_smaller_than_buffer_threshold` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_full_liquidation_bypasses_buffer_in_normal_rebalance` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_buffer_suppresses_small_trade_adjustment` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_simultaneous_scheduled_and_emergency_rebalance` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_repeated_emergency_triggers_idempotent` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_missing_or_corrupt_spy_resilience` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_leveraged_etf_exposure_gated_during_distress` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_insufficient_cash_handling` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_stock_split_during_liquidation` | A |
| `research/tests/test_v12_candidate_ae_conflicts.py::test_transaction_cost_shock_balance_sheet_conservation` | A |
| `research/tests/test_v13_historical_qualification.py::test_pre_inception_xlre_rejection` | A |
| `research/tests/test_v13_historical_qualification.py::test_pre_inception_xlc_rejection` | A |
| `research/tests/test_v13_historical_qualification.py::test_production_universe_manifest_exact_24` | A |
| `research/tests/test_v13_historical_qualification.py::test_duplicate_dividend_deduplication` | A |
| `research/tests/test_v13_historical_qualification.py::test_invalid_split_ratio_rejected` | A |
| `research/tests/test_v13_historical_qualification.py::test_future_split_not_applied_prematurely` | A |
| `research/tests/test_v13_historical_qualification.py::test_us_market_holiday_rejection` | A |
| `research/tests/test_v13_historical_qualification.py::test_missing_leveraged_etfs_agent_resilience` | A |
| `research/tests/test_v13_historical_qualification.py::test_storage_compliance_intercepts_unauthorized_persistence` | A |
| `research/tests/test_v14_financial_forensics.py::test_production_universe_exact_equality` | A |
| `research/tests/test_v14_financial_forensics.py::test_regime_calendar_lengths_and_notional` | B |
| `research/tests/test_v14_financial_forensics.py::test_accounting_invariants_and_slippage_integrity` | B |
| `research/tests/test_v14_financial_forensics.py::test_four_way_candidate_deterministic_returns` | C |
| `research/tests/test_v14_financial_forensics.py::test_statistical_uncertainty_negative_control` | C |
| `research/tests/test_v15_evidence_gates.py::test_gate1_raw_fixture_calendar_dates` | C |
| `research/tests/test_v15_evidence_gates.py::test_gate2_attribution_bridge_and_defensive_holdings` | C |
| `research/tests/test_v15_evidence_gates.py::test_gate3_cost_sensitivity_hierarchy` | C |
| `research/tests/test_v15_evidence_gates.py::test_gate7_pristine_holdout_isolation` | B |
| `research/tests/test_v16_procurement_preflight.py::test_cent_level_rounding_order_reconciliation` | C |
| `research/tests/test_v16_procurement_preflight.py::test_v15_clean_worktree_commit_id` | C |
| `research/tests/test_v16_procurement_preflight.py::test_provider_rolling_10_year_history_insufficiency` | C |
| `research/tests/test_v16_procurement_preflight.py::test_holdout_boundary_strict_absence` | B |
| `research/tests/test_v18_authentic_tier1.py::test_holdout_firewall_blocks_boundary_crossings` | A |
| `research/tests/test_v18_authentic_tier1.py::test_negative_controls_bar_validation` | A |
| `research/tests/test_v18_authentic_tier1.py::test_request_ledger_recording_and_redaction` | A |
| `research/tests/test_v18_authentic_tier1.py::test_point_in_time_causality_streaming` | A |
| `research/tests/test_validation.py::TestValidationControls::test_positive_calendar_date` | A |
| `research/tests/test_validation.py::TestValidationControls::test_negative_calendar_date` | A |
| `research/tests/test_validation.py::TestValidationControls::test_weekend_rejection` | A |
| `research/tests/test_validation.py::TestValidationControls::test_positive_bar` | A |
| `research/tests/test_validation.py::TestValidationControls::test_negative_prices_and_nonfinite` | A |
| `research/tests/test_validation.py::TestValidationControls::test_geometric_boundary_integrity` | A |
| `research/tests/test_validation.py::TestValidationControls::test_series_chronology_and_duplicate_rejection` | A |
| `research/tests/test_validation.py::TestValidationControls::test_future_timestamp_strict_rejection_at_boundary` | A |

## Required future file/expectation changes - not applied

Proposed new artifacts include a versioned generator, explicitly named synthetic fixture/provenance/action inputs, synthetic integration tests and independently reviewed synthetic expectations. Exact paths/full allowlist must be frozen in the authorized design before implementation. preview/provider input binding must be explicit and must never silently fall back to the old market fixture.

The new public selection must not depend on `sample_regimes.json.gz`, old `tests/e0_expected.json`, historical-market assertions or old result-bearing documentation whose permission remains UNKNOWN. Excluding those from a future public package is not deletion from the preserved research repository. Split reusable invariant controls from historical-only controls in new test modules; retain original modules and all failed evidence intact. Review affected README/release guide and full checksum manifests for the new contract.

A synthetic replacement necessarily changes financial outputs. New expected metrics must be independently computed/reconciled after a preregistered generator contract, reviewed on scientific grounds, and never tuned to old expected results. Validate full relevant risk/accounting/causality behavior and report every changed metric/failure. Any comparison must distinguish algorithm agreement on the same invented inputs from historical scientific equivalence, which is not established.

Supported alternative: if real fixture rights are documented instead, the original-fixture test contract can be reviewed without a synthetic replacement. V29F makes neither change. Feasibility is CONDITIONAL until implementation authorization, scientific review and executed qualification exist.
