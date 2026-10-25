# Guardian Alpha V29E-N ? Noise inventory

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

Verdict: **CONDITIONAL** for exhaustive workspace scope; **PASS** for additive documentation and preservation checks. Restricted subtrees are opaque, so their descendant counts and storage are unknown. No main V29E validation was started.

## Scope and methodology

Inventory is the pre-change filesystem snapshot under this workspace, excluding Git internals, protected cache/private roots, sealed/holdout/Tier 3 named directories, and directory links. Git tracked paths come from `git ls-files -z`; enumerated paths are partitioned using `git check-ignore -z --stdin`. No ignored-file Git recursive inventory or vendor-data content scan was used. Sizes are logical `stat` bytes, not allocated disk space; no restricted descendant sizes are included. Zero-byte files count. Git-tracked paths outside safe traversal are listed separately as metadata only. No network, trading, imports of project code or test collection were executed.

Each enumerated file has one primary classification, chosen by ordered path rules: generated cache, logs, evidence, manifests, scratch tests/scripts, active test/fixture paths, research scripts/strategies, engine, documentation, private results, reproducibility inputs, runtime, other Python, supporting configuration, unknown. Research-critical is a conservative preservation classification, not a claim every script is required for current runtime. Historical tests remain valuable and are not declared obsolete. Duplicate bytes and repeated AST function bodies are secondary flags, not mutually exclusive primary categories. No file is reclassified disposable from lack of imports.

Noise baseline is a vector of counts and bytes below, plus duplicate and console-call signals. There is no invented aggregate score. Console call counts measure static output sites, not observed frequency, performance impact or warning repetition. No unreferenced fixture or unnecessary installed dependency is proven by this audit.

## Quantitative baseline

| Measure | Value |
|---|---:|
| Authorized enumerated files | 357 |
| Git tracked paths (all metadata) | 271 |
| Enumerated tracked files | 271 |
| Enumerated untracked files | 1 |
| Enumerated ignored files | 85 |
| Ignored generated files | 84 |
| Research-critical Python scripts | 76 |
| Documentation files | 40 |
| Exact duplicate text/code member paths (review only) | 0 |
| Logical bytes (authorized scope) | 7266347 |
| Protected public candidate paths | 69 |
| Research inventory test IDs (existing JSON) | 400 |
| Static test function definitions (all safe Python) | 377 |

Static definitions do not equal collected parametrized tests. Existing V29D-R reports 456 collected tests: 56 admission + 400 research; 253 public (56 + 197), 203 private (14 research files). These are historical assertions, not tests rerun in V29E-N. No measured line/branch coverage exists in this audit.

| Primary classification | Files | Bytes |
|---|---:|---:|
| Core production files | 7 | 73871 |
| Production dependencies | 21 | 204003 |
| Research-critical files | 77 | 475638 |
| Reproducibility dependencies | 46 | 2495463 |
| Active tests | 50 | 392173 |
| Historical tests | 7 | 74952 |
| Audit evidence | 20 | 669065 |
| Temporary/generated files | 84 | 1985389 |
| Logs | 2 | 38645 |
| Documentation | 40 | 669203 |
| Local/private data | 3 | 187945 |
| Duplicates requiring review | 0 | 0 |
| Unknown or unclassified | 0 | 0 |

Duplicate-review primary count is zero because duplicate membership is an independent flag; see exact groups below.

## Opaque exclusions and completeness limits

- `tiingo_cache/`: pruned before descent; contents, file count, bytes and Tier 3 presence not probed.

Additional protected raw/vendor/sealed locations are excluded by policy even when not encountered. Tier 3 observations dated >= 2022-01-01 were not opened or hashed; date filtering of raw data was deliberately not performed. Licensed Tier 1/Tier 2 caches and request ledgers were not opened or hashed. Ledger paths can have metadata-only size entries.

Git-tracked paths outside enumeration: none.

## Exact path inventory

Public column is membership in the documented protected 69-file reference, not new publication approval. Excluded means retained internally.

### Tracked

| Exact path | Classification | Bytes | Public | Rationale / proposed action |
|---|---|---:|---|---|
| `.gitattributes` | Production dependencies | 473 | Reference | Repository/license/automation support; preserve; publication per allowlist |
| `.github/workflows/leaderboard.yml` | Production dependencies | 1010 | Excluded | Repository/license/automation support; preserve; publication per allowlist |
| `.gitignore` | Production dependencies | 331 | Reference | Repository/license/automation support; preserve; publication per allowlist |
| `AGENT_BRIEF.md` | Documentation | 6376 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `ANATOMY.md` | Documentation | 4467 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V21_PORTFOLIO_FIDELITY_AND_TIER2_READINESS_REPORT.md` | Documentation | 24926 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V22_CAUSAL_PRICE_ALIGNMENT_AND_TIER1_REQUALIFICATION_REPORT.md` | Documentation | 21798 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V23_TIER2_OUT_OF_SAMPLE_VALIDATION_REPORT.md` | Documentation | 38187 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V24_TIER2_CONTINUITY_AND_VALIDATION_FORENSICS_REPORT.md` | Documentation | 17685 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V25_FINAL_TIER2_FINANCIAL_CERTIFICATION_REPORT.md` | Documentation | 28460 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md` | Documentation | 26470 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V26_ADVERSARIAL_FINANCIAL_CERTIFICATION_REPORT.md` | Documentation | 29083 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V27R_SCIENTIFIC_AND_EXECUTION_RECONCILIATION_REPORT.md` | Documentation | 31273 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V27_SCIENTIFIC_VALIDITY_AND_MARKET_REALISM_AUDIT.md` | Documentation | 25553 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V28_FINAL_RESEARCH_GOVERNANCE_REPORT.md` | Documentation | 31184 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29A_EVIDENCE_INVENTORY.md` | Documentation | 23325 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29A_FINAL_GATE_REPORT.md` | Documentation | 24971 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29A_GIT_PUBLICATION_RISK_REVIEW.md` | Documentation | 22404 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29A_REPRODUCIBILITY_DEPENDENCY_MAP.md` | Documentation | 21665 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29B_EXECUTION_VERIFICATION_REPORT.md` | Documentation | 31528 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29C_FINAL_GATE_REPORT.md` | Documentation | 9986 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29C_PUBLICATION_RISK_REGISTER.md` | Documentation | 11917 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29C_PUBLIC_REPRODUCIBILITY_PLAN.md` | Documentation | 8400 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29C_PUBLIC_SNAPSHOT_ALLOWLIST.md` | Documentation | 12623 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29C_RELEASE_BRANCH_PROCEDURE.md` | Documentation | 12175 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_FINAL_REPORT.md` | Documentation | 8859 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_ISOLATED_TEST_EVIDENCE.md` | Documentation | 14075 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_PUBLIC_BASE_HISTORY_AUDIT.md` | Documentation | 5845 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_RELEASE_SECURITY_GATE.md` | Documentation | 8959 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_R_RECONCILIATION_REPORT.md` | Documentation | 31084 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `GUARDIAN_ALPHA_V29D_SNAPSHOT_CONTENT_AUDIT.md` | Documentation | 10955 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `LICENSE` | Production dependencies | 1065 | Reference | Repository/license/automation support; preserve; publication per allowlist |
| `README.md` | Documentation | 13030 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `RELEASE-AUDIT.md` | Documentation | 10216 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `RELEASE.md` | Documentation | 7479 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `START_HERE.md` | Documentation | 3580 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `SUBMISSION.md` | Documentation | 9148 | Reference | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `agent.py` | Core production files | 12952 | Reference | Runtime/admission/endpoint implementation; preserve; no execution |
| `ai_momentum.py` | Research-critical files | 5429 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `baseline.py` | Research-critical files | 1639 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `build_universe.py` | Research-critical files | 4744 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `capture_endpoint_orders.py` | Core production files | 5600 | Excluded | Runtime/admission/endpoint implementation; preserve; no execution |
| `com.builderr.live-leaderboard.plist` | Production dependencies | 1098 | Excluded | Repository/license/automation support; preserve; publication per allowlist |
| `docs/competition-contract.md` | Documentation | 16607 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/compliance-matrix.md` | Documentation | 8328 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/evidence-ledger.md` | Documentation | 22005 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/evidence-manifest.sha256` | Documentation | 5523 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/stage-status.md` | Documentation | 6308 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/stage2-baseline.md` | Documentation | 8300 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `docs/stage2a-final-verification.md` | Documentation | 14446 | Excluded | Navigation, contract or historical audit; preserve; index rather than consolidate |
| `drawdown_momentum.py` | Research-critical files | 10530 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `endpoint_harness_selftest.py` | Active tests | 3561 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `endpoint_replay.py` | Core production files | 2399 | Excluded | Runtime/admission/endpoint implementation; preserve; no execution |
| `endpoint_security.py` | Core production files | 4464 | Excluded | Runtime/admission/endpoint implementation; preserve; no execution |
| `example_sector_rotation.py` | Research-critical files | 3947 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `example_vol_target.py` | Research-critical files | 3691 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `fairness_tests.py` | Active tests | 5273 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `full_test.py` | Active tests | 2285 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `history.json` | Local/private data | 79950 | Excluded | Results/publication sensitivity; retain; exclude from candidate |
| `house_barbell_realasset.py` | Research-critical files | 8106 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `leaderboard.json` | Local/private data | 19344 | Excluded | Results/publication sensitivity; retain; exclude from candidate |
| `live_runner.py` | Core production files | 35608 | Excluded | Runtime/admission/endpoint implementation; preserve; no execution |
| `live_runner_selftest.py` | Active tests | 5117 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `local_test.py` | Active tests | 2872 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `market_open.py` | Core production files | 1085 | Excluded | Runtime/admission/endpoint implementation; preserve; no execution |
| `momentum_v1.py` | Research-critical files | 1636 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `preview.py` | Core production files | 11763 | Reference | Runtime/admission/endpoint implementation; preserve; no execution |
| `private_results.json` | Local/private data | 88651 | Excluded | Results/publication sensitivity; retain; exclude from candidate |
| `qqq_benchmark.py` | Research-critical files | 1418 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `refresh_live_leaderboard.sh` | Production dependencies | 1295 | Excluded | Repository/license/automation support; preserve; publication per allowlist |
| `release-manifest.sha256` | Reproducibility dependencies | 1390 | Reference | Runtime/admission input or integrity contract; preserve |
| `requirements-test.txt` | Reproducibility dependencies | 86 | Reference | Runtime/admission input or integrity contract; preserve |
| `requirements.txt` | Reproducibility dependencies | 48 | Reference | Runtime/admission input or integrity contract; preserve |
| `research/engine/__init__.py` | Production dependencies | 1193 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/accounting.py` | Production dependencies | 22805 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/benchmark.py` | Production dependencies | 5486 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/corporate_actions.py` | Production dependencies | 12450 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/event_verifier.py` | Production dependencies | 10922 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/independent_accounting.py` | Production dependencies | 18762 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/ingestion.py` | Production dependencies | 7833 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/provider.py` | Production dependencies | 7128 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/quality.py` | Production dependencies | 8605 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/replay.py` | Production dependencies | 13649 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/report_consistency_checker.py` | Production dependencies | 33295 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/stress.py` | Production dependencies | 18576 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/tiingo_client.py` | Production dependencies | 24693 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/validation.py` | Production dependencies | 6862 | Reference | Research engine and financial controls; preserve independent verification |
| `research/engine/walk_forward.py` | Production dependencies | 6472 | Reference | Research engine and financial controls; preserve independent verification |
| `research/evidence/asset_universe_matrix.json` | Audit evidence | 14998 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/b2a_replay_audit_results.json` | Audit evidence | 6041 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory.json` | Audit evidence | 16155 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory_v10.json` | Audit evidence | 29650 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory_v3.json` | Audit evidence | 32559 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory_v4.json` | Audit evidence | 33230 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory_v5.json` | Audit evidence | 39850 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_file_inventory_v6.json` | Audit evidence | 28859 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/baseline_test_suite_results.json` | Audit evidence | 9531 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/data_acquisition_specification.json` | Audit evidence | 6324 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/dataset_acquisition_permissions_matrix.json` | Audit evidence | 12957 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/market_data_integrity_controls.json` | Audit evidence | 1750 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/provider_comparison.json` | Audit evidence | 5878 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/remediation_test_evidence.json` | Audit evidence | 7951 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/soak/soak_summary.json` | Audit evidence | 836 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/soak/soak_telemetry.jsonl` | Logs | 7902 | Excluded | Append-only operational or research record; preserve; publication review |
| `research/evidence/system_efficiency_benchmark.json` | Audit evidence | 2274 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/v29a/scratch_audit_inventory.json` | Audit evidence | 77072 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/v29a/test_suite_381_classified_inventory.json` | Audit evidence | 166193 | Excluded | Historical result or inventory; preserve privately |
| `research/evidence/v29b/v29b_execution_verification_manifest_summary.json` | Audit evidence | 2694 | Excluded | Historical result or inventory; preserve privately |
| `research/manifests/benchmark_stability_profile.json` | Reproducibility dependencies | 3121 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/production_universe_manifest.json` | Reproducibility dependencies | 11492 | Reference | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_aapl_nvda_position_history.json` | Reproducibility dependencies | 979544 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_accounting_reconciliation.json` | Reproducibility dependencies | 10800 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_corporate_actions_inventory.json` | Reproducibility dependencies | 844 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_coverage_matrix.json` | Reproducibility dependencies | 10644 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_four_way_results.json` | Reproducibility dependencies | 2071 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_nav_rounding_bridge.json` | Reproducibility dependencies | 6285 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_paired_strategy_statistics.json` | Reproducibility dependencies | 905 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_terminal_holdings_v20.json` | Reproducibility dependencies | 27796 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_terminal_holdings_v22.json` | Reproducibility dependencies | 6473 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v20_comprehensive_metrics.json` | Reproducibility dependencies | 4388 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v22_comprehensive_metrics.json` | Reproducibility dependencies | 3385 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v22_first_divergence_trace.json` | Reproducibility dependencies | 645 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v22_independent_accounting.json` | Reproducibility dependencies | 472 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v22_nav_rounding_bridge.json` | Reproducibility dependencies | 2474 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier1_v22_paired_strategy_statistics.json` | Reproducibility dependencies | 1220 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_carryforward_continuity_bridge.json` | Reproducibility dependencies | 10447 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_carryforward_corrected_results.json` | Reproducibility dependencies | 58043 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_carryforward_sensitivity_results.json` | Reproducibility dependencies | 58185 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_corporate_actions_inventory.json` | Reproducibility dependencies | 26664 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_coverage_matrix.json` | Reproducibility dependencies | 9358 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_four_way_results.json` | Reproducibility dependencies | 58529 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_independent_accounting.json` | Reproducibility dependencies | 4282 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_leveraged_etf_slippage_audit.json` | Reproducibility dependencies | 1370 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_nav_rounding_bridge.json` | Reproducibility dependencies | 897 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_paired_strategy_statistics.json` | Reproducibility dependencies | 5249 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_preregistration_protocol.json` | Reproducibility dependencies | 7119 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_regime_robustness_profile.json` | Reproducibility dependencies | 8746 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tier2_terminal_holdings.json` | Reproducibility dependencies | 5290 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/tiingo_request_ledger.jsonl` | Logs | 30743 | Excluded | Append-only operational or research record; preserve; publication review |
| `research/manifests/v17_qualification_status.json` | Reproducibility dependencies | 1727 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v22_preflight_inventory.json` | Reproducibility dependencies | 1234 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v23_preflight_inventory.json` | Reproducibility dependencies | 2422 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v24_preflight_inventory.json` | Reproducibility dependencies | 897 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v25_preflight_inventory.json` | Reproducibility dependencies | 4350 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v26_preflight_inventory.json` | Reproducibility dependencies | 5251 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v26_strategy_specific_carryforward_results.json` | Reproducibility dependencies | 1794 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v26_tier1_holdings_forensic_reconciliation.json` | Reproducibility dependencies | 4368 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v27_execution_realism_stress_results.json` | Reproducibility dependencies | 5280 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v27r_two_method_execution_sensitivity.json` | Reproducibility dependencies | 13732 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/manifests/v29b_method_a_order_event_trace.json` | Reproducibility dependencies | 702093 | Excluded | Manifest/provenance input; preserve; public only if allowlisted |
| `research/scripts/acquire_tier1_tiingo.py` | Research-critical files | 6041 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/acquire_tier2_tiingo.py` | Research-critical files | 8974 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/compute_tier2_statistics_and_regimes.py` | Research-critical files | 12209 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_acquisition_spec.py` | Research-critical files | 4607 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_inventory_v10.py` | Research-critical files | 3261 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_inventory_v3.py` | Research-critical files | 3445 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_inventory_v4.py` | Research-critical files | 3484 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_inventory_v5.py` | Research-critical files | 3484 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_inventory_v6.py` | Research-critical files | 3258 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_permissions_matrix.py` | Research-critical files | 5570 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_universe_and_provider_matrix.py` | Research-critical files | 23333 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/generate_v29b_order_events.py` | Research-critical files | 15566 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/run_b2a_replay_suite.py` | Research-critical files | 4893 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/run_baseline_audit.py` | Research-critical files | 4643 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/run_benchmarks.py` | Research-critical files | 2486 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/run_tier1_authentic_backtest.py` | Research-critical files | 6724 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/run_tier2_authentic_backtest.py` | Research-critical files | 15252 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/scan_secrets.py` | Research-critical files | 1351 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/soak_harness.py` | Research-critical files | 12643 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/test_data_integrity.py` | Research-critical files | 7769 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/validate_soak_run.py` | Research-critical files | 11238 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/verify_remediation_controls.py` | Research-critical files | 17482 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/verify_tier1_accounting.py` | Research-critical files | 5545 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/scripts/verify_tier2_accounting.py` | Research-critical files | 11707 | Excluded | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/strategies/__init__.py` | Research-critical files | 238 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/strategies/candidate_alpha.py` | Research-critical files | 4925 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/strategies/loss_reduction_candidates.py` | Research-critical files | 14428 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/strategies/v11_candidates.py` | Research-critical files | 25205 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/strategies/v12_candidate_ae.py` | Research-critical files | 8459 | Reference | Acquisition/generation/strategy research dependency; preserve; do not execute acquisition |
| `research/tests/test_b2_benchmark.py` | Active tests | 1785 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_causality_integrity.py` | Active tests | 6018 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_financial_accounting.py` | Active tests | 11808 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_financial_corner_cases.py` | Active tests | 11879 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_ingestion_quality.py` | Active tests | 7702 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_leveraged_overlay.py` | Active tests | 9069 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_loss_reduction.py` | Active tests | 6712 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_replay_independence.py` | Active tests | 7260 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_risk_enforcement.py` | Active tests | 9198 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_soak_validation.py` | Active tests | 6713 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_storage_compliance.py` | Active tests | 4438 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_trading_stress.py` | Active tests | 2123 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_b2_walk_forward.py` | Active tests | 3936 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_baseline_parity.py` | Active tests | 2197 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_corporate_actions.py` | Active tests | 2488 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_provider_compliance.py` | Active tests | 3131 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_replay_accounting.py` | Active tests | 3671 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_risk_limits.py` | Active tests | 2096 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v11_candidates.py` | Active tests | 3445 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v12_candidate_ae_conflicts.py` | Active tests | 10162 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v13_historical_qualification.py` | Active tests | 7144 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v14_financial_forensics.py` | Active tests | 6743 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v15_evidence_gates.py` | Active tests | 5905 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v16_procurement_preflight.py` | Active tests | 4204 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v17_tiingo_qualification.py` | Active tests | 8925 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v18_authentic_tier1.py` | Active tests | 4754 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v19_tier1_forensics.py` | Active tests | 8752 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v20_financial_integrity.py` | Active tests | 11132 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v21_portfolio_fidelity.py` | Active tests | 13687 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v22_price_semantics.py` | Active tests | 8332 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v23_tier2_validation.py` | Active tests | 12454 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v24_continuity_and_forensics.py` | Active tests | 14227 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v25_financial_certification.py` | Active tests | 14885 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v26_adversarial_challenge.py` | Active tests | 16825 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v26r_report_arithmetic_verifier.py` | Active tests | 15667 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v27_scientific_validity.py` | Active tests | 17666 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v27r_scientific_reconciliation.py` | Active tests | 18314 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v28_governance_certification.py` | Active tests | 22303 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_v29b_execution_verification.py` | Active tests | 17957 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `research/tests/test_validation.py` | Active tests | 6158 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `sample_regimes.json.gz` | Reproducibility dependencies | 412567 | Reference | Runtime/admission input or integrity contract; preserve |
| `scratch/analyze_vol_spike_attribution.py` | Research-critical files | 1218 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/analyze_xle_and_sectors.py` | Research-critical files | 4954 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_all_regimes_turnover.py` | Research-critical files | 1658 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_test.py` | Historical tests | 2950 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v13_01_costs.py` | Research-critical files | 2540 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v13_02_suppressed_orders.py` | Research-critical files | 1461 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v13_03_liquidation_timeline.py` | Research-critical files | 2551 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v13_04_bootstrap.py` | Research-critical files | 3237 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v13_05_latency_memory.py` | Research-critical files | 3533 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/audit_v14_full_forensics.py` | Research-critical files | 7165 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/backup_and_verify_evidence.py` | Research-critical files | 7620 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/baseline_check.py` | Research-critical files | 3893 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/benchmark_runtime.py` | Research-critical files | 3304 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/benchmark_v12.py` | Research-critical files | 1968 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/build_ledger_and_manifest.py` | Research-critical files | 25203 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/check_turnover_formula.py` | Research-critical files | 1753 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/counterfactual_rebalancing.py` | Research-critical files | 9291 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/deep_baseline_profile.py` | Research-critical files | 11148 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/detailed_loss_attribution.py` | Research-critical files | 6495 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/evaluate_v10_candidates.py` | Research-critical files | 1368 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/four_way_comparison.py` | Research-critical files | 3795 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/gate1_dates_reconciliation.py` | Research-critical files | 2790 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/gate1_v16_reconciliation.py` | Research-critical files | 5569 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/gate2_attribution_bridge.py` | Research-critical files | 5424 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/gate3_cost_sensitivity.py` | Research-critical files | 1825 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/gate4_statistical_review.py` | Research-critical files | 3648 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/inspect_recovery_timing.py` | Research-critical files | 2354 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/inspect_v11_b_loss_attribution.py` | Research-critical files | 2481 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/inspect_windows.py` | Research-critical files | 677 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/math_verify.py` | Research-critical files | 7267 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/print_trades.py` | Research-critical files | 360 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/profile_cpu.py` | Research-critical files | 1225 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/reconcile_v10_attribution.py` | Research-critical files | 6235 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/reproduce_baseline.py` | Research-critical files | 1542 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/reproduce_p0_accounting.py` | Research-critical files | 9016 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/run_statistical_validation.py` | Research-critical files | 7209 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/runtime_check.py` | Research-critical files | 4976 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_adverse_inputs.py` | Historical tests | 3011 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_agent_features.py` | Historical tests | 6264 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_cadence.py` | Historical tests | 7205 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_candidates_a_to_f.py` | Historical tests | 25668 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_hypotheses.py` | Historical tests | 14881 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/test_hypotheses_part2.py` | Historical tests | 14973 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `scratch/v12_statistical_sensitivity.py` | Research-critical files | 5704 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `seed_dual_momentum.py` | Research-critical files | 5691 | Excluded | Baseline/example/research utility; preserve pending dependency review |
| `selfcheck.py` | Active tests | 5545 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `strategy_selftest.py` | Active tests | 4710 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `test_market_open.py` | Active tests | 519 | Excluded | Validation source/fixture; preserve coverage; no execution in this batch |
| `tests/e0_expected.json` | Active tests | 1479 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `tests/test_e0_release.py` | Active tests | 8947 | Reference | Validation source/fixture; preserve coverage; no execution in this batch |
| `universe.json` | Reproducibility dependencies | 11486 | Reference | Runtime/admission input or integrity contract; preserve |

### Untracked

| Exact path | Classification | Bytes | Public | Rationale / proposed action |
|---|---|---:|---|---|
| `research/evidence/v29b/test_suite_400_classified_inventory.json` | Audit evidence | 174263 | Excluded | Historical result or inventory; preserve privately |

### Ignored

| Exact path | Classification | Bytes | Public | Rationale / proposed action |
|---|---|---:|---|---|
| `.pytest_cache/.gitignore` | Temporary/generated files | 37 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `.pytest_cache/CACHEDIR.TAG` | Temporary/generated files | 191 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `.pytest_cache/README.md` | Temporary/generated files | 302 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `.pytest_cache/v/cache/lastfailed` | Temporary/generated files | 338 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `.pytest_cache/v/cache/nodeids` | Temporary/generated files | 49730 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/agent.cpython-311.pyc` | Temporary/generated files | 20508 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/full_test.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 4470 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/live_runner.cpython-311.pyc` | Temporary/generated files | 44717 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/local_test.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 4553 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/market_open.cpython-311.pyc` | Temporary/generated files | 2281 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/preview.cpython-311.pyc` | Temporary/generated files | 20079 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `__pycache__/test_market_open.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 1662 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/__init__.cpython-311.pyc` | Temporary/generated files | 1343 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/accounting.cpython-311.pyc` | Temporary/generated files | 28811 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/benchmark.cpython-311.pyc` | Temporary/generated files | 8106 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/corporate_actions.cpython-311.pyc` | Temporary/generated files | 13314 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/event_verifier.cpython-311.pyc` | Temporary/generated files | 14552 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/independent_accounting.cpython-311.pyc` | Temporary/generated files | 20909 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/ingestion.cpython-311.pyc` | Temporary/generated files | 12388 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/provider.cpython-311.pyc` | Temporary/generated files | 13073 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/quality.cpython-311.pyc` | Temporary/generated files | 13639 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/replay.cpython-311.pyc` | Temporary/generated files | 16270 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/report_consistency_checker.cpython-311.pyc` | Temporary/generated files | 39810 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/stress.cpython-311.pyc` | Temporary/generated files | 25934 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/tiingo_client.cpython-311.pyc` | Temporary/generated files | 34634 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/validation.cpython-311.pyc` | Temporary/generated files | 9206 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/engine/__pycache__/walk_forward.cpython-311.pyc` | Temporary/generated files | 9754 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/scripts/__pycache__/generate_v29b_order_events.cpython-311.pyc` | Temporary/generated files | 17010 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/scripts/__pycache__/run_tier2_authentic_backtest.cpython-311.pyc` | Temporary/generated files | 20333 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/scripts/__pycache__/test_data_integrity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 10333 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/scripts/__pycache__/validate_soak_run.cpython-311.pyc` | Temporary/generated files | 12785 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/strategies/__pycache__/__init__.cpython-311.pyc` | Temporary/generated files | 466 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/strategies/__pycache__/candidate_alpha.cpython-311.pyc` | Temporary/generated files | 5996 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/strategies/__pycache__/loss_reduction_candidates.cpython-311.pyc` | Temporary/generated files | 15785 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/strategies/__pycache__/v11_candidates.cpython-311.pyc` | Temporary/generated files | 35672 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/strategies/__pycache__/v12_candidate_ae.cpython-311.pyc` | Temporary/generated files | 10694 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_benchmark.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 12542 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_causality_integrity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 14326 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_financial_accounting.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 49844 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_financial_corner_cases.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 43331 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_ingestion_quality.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 34053 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_leveraged_overlay.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 25790 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_loss_reduction.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 22885 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_replay_independence.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 22646 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_risk_enforcement.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 30285 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_soak_validation.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 17874 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_storage_compliance.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 10947 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_trading_stress.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 8081 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_b2_walk_forward.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 18529 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_baseline_parity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 10930 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_corporate_actions.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 12573 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_provider_compliance.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 13476 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_replay_accounting.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 22414 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_risk_limits.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 9799 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v11_candidates.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 12718 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v12_candidate_ae_conflicts.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 28920 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v13_historical_qualification.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 25525 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v14_financial_forensics.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 25117 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v15_evidence_gates.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 22940 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v16_procurement_preflight.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 13046 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v17_tiingo_qualification.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 36845 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v18_authentic_tier1.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 15419 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v19_tier1_forensics.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 33514 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v20_financial_integrity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 47796 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v21_portfolio_fidelity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 47879 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v22_price_semantics.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 21376 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v23_tier2_validation.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 50672 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v24_continuity_and_forensics.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 45994 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v25_financial_certification.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 45967 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v26_adversarial_challenge.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 46266 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v26r_report_arithmetic_verifier.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 51520 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v27_scientific_validity.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 48316 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v27r_scientific_reconciliation.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 63826 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v28_governance_certification.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 70990 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_v29b_execution_verification.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 79184 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `research/tests/__pycache__/test_validation.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 20297 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/audit_test.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 4601 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_adverse_inputs.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 14771 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_agent_features.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 45148 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_cadence.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 11909 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_candidates_a_to_f.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 38983 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_hypotheses.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 21142 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/__pycache__/test_hypotheses_part2.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 22916 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |
| `scratch/hypotheses_results.json` | Research-critical files | 8130 | Excluded | Historical forensic/experiment script; retain; use V29A dependency map before executing |
| `tests/__pycache__/test_e0_release.cpython-311-pytest-9.1.1.pyc` | Temporary/generated files | 51782 | Excluded | Interpreter/test cache; hide in local views; preserve existing bytes |

## Duplicate and repeated-code review

Exact SHA-256 groups within safe source/documentation/config text only (not a repository-wide binary/data comparison):

No exact byte duplicate groups found.

Repeated nontrivial function bodies (>=9 lines, AST identical ignoring line locations; no alpha renaming):

- `example_sector_rotation.py:72 (decide)`; `example_vol_target.py:71 (decide)`
- `example_vol_target.py:38 (_vol)`; `house_barbell_realasset.py:76 (_vol)`
- `research/engine/provider.py:119 (stream_daily_slices)`; `research/engine/provider.py:158 (stream_daily_slices)`
- `research/scripts/generate_inventory_v3.py:13 (get_git_files)`; `research/scripts/generate_inventory_v4.py:13 (get_git_files)`; `research/scripts/generate_inventory_v5.py:13 (get_git_files)`
- `research/scripts/run_tier2_authentic_backtest.py:149 (build_clean_corp_registry)`; `research/scripts/verify_tier2_accounting.py:67 (build_clean_corp_registry)`
- `research/strategies/loss_reduction_candidates.py:161 (decide)`; `research/strategies/loss_reduction_candidates.py:334 (decide)`
- `research/strategies/v11_candidates.py:99 (decide)`; `scratch/test_candidates_a_to_f.py:103 (decide)`
- `research/strategies/v11_candidates.py:198 (decide)`; `scratch/test_candidates_a_to_f.py:190 (decide)`
- `research/strategies/v11_candidates.py:297 (decide)`; `research/strategies/v11_candidates.py:397 (decide)`; `scratch/test_candidates_a_to_f.py:278 (decide)`; `scratch/test_candidates_a_to_f.py:366 (decide)`
- `research/strategies/v11_candidates.py:628 (decide)`; `scratch/test_candidates_a_to_f.py:570 (decide)`

These matches can be package placeholders or independent test implementations; merging financial verification paths could destroy independence. Preserve all matches.

## Preservation evidence

| Checkpoint | Exact object | Executed result |
|---|---|---|
| V28 | `8c77fddf72398b2e016a6f212d067c8aeb2b385e` | commit; ancestor of HEAD (exit 0) |
| V29A | `4567f4fe85dbce598477628ca8355a76356a8cf7` | commit; ancestor of HEAD (exit 0) |
| V29B | `fd829eff562cebe603b310db2a708b1b3c77999d` | commit; ancestor of HEAD (exit 0) |
| V29C | `d3a9ae8c2bf17c1fbff0833ba1ba2dd24cc80e6c` | commit; ancestor of HEAD (exit 0) |
| V29D | `b283ded200c777b130285b0aa56a0b044afbd339` | commit; ancestor of HEAD (exit 0) |

Untracked `research/evidence/v29b/test_suite_400_classified_inventory.json`: 174263 bytes; SHA-256 `f34db323811b47cb22324b7d5ec882f4a130ba8d15e8cf5adcd5756d9187b1a2`; 400 existing entries. Hash is authorized non-vendor evidence. Frozen strategy files were only read as source text for static analysis, never executed or edited. No Git mutations or cleanup commands were run. Checkpoint verification establishes commit-object existence and ancestry, not a full object-database integrity scan.

Initial `git status --short --untracked-files=normal` raw output:

```text
?? research/evidence/v29b/test_suite_400_classified_inventory.json
```

## Execution record

Inventory/static analysis/preservation preflight elapsed: 3.264 seconds (wall clock). No test runtime measured. Checks passed: 69 unique reference paths present; safe source bytes unchanged; V29B evidence digest unchanged; both tracked diffs empty; branch/HEAD unchanged. Raw checkpoint command exit results appear above.

Expected new untracked files:

- `GUARDIAN_ALPHA_V29E_N_NOISE_INVENTORY.md`
- `GUARDIAN_ALPHA_V29E_N_NOISE_REDUCTION_PROPOSAL.md`
- `GUARDIAN_ALPHA_V29E_N_PUBLIC_SNAPSHOT_MINIMIZATION.md`

The pre-existing V29B JSON remains untracked. No other existing artifacts were modified by this batch.
