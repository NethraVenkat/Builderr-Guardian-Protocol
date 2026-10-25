# Guardian Alpha V29E-N ? Noise reduction proposal

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

Verdict: **CONDITIONAL** for exhaustive workspace scope; **PASS** for additive documentation and preservation checks. Restricted subtrees are opaque, so their descendant counts and storage are unknown. No main V29E validation was started.

## Findings and precise proposed treatment

- Historical reports repeat claims and contain superseded counts. V29D-R explicitly corrects the 147-private-test arithmetic and 17-vs-19 root-file count. This is navigational redundancy, not byte duplication. Preserve originals and consult the reconciliation first.
- `research/scripts/generate_inventory_v3.py` through `generate_inventory_v6.py` and `generate_inventory_v10.py`, plus corresponding evidence JSONs, share purpose but document different audit states. Do not call them obsolete or regenerate over original outputs. Keep as historical reproducibility pairs.
- Python and pytest caches are generated display noise. Hide `**/__pycache__/**`, `**/*.pyc`, `.pytest_cache/**` in a local editor filter if desired; no editor configuration or ignore file was changed. Existing caches are preserved. A future clean run can generate fresh caches, but existing cache deletion still needs approval.
- `scratch/` contains historical tests and forensic scripts. Existing V29A documentation identifies essential order/continuity/PnL reproduction scripts, some absent here. Absence is a provenance availability question, not permission to remove remaining scratch files or claim whole-history reproducibility.
- `tests/e0_expected.json`, `sample_regimes.json.gz`, `universe.json` and `release-manifest.sha256` have direct admission/integrity roles visible in `tests/test_e0_release.py`; no fixture pruning is justified. `preview.py` directly loads the sample regimes.
- `requirements.txt` states production uses the standard library; `requirements-test.txt` pins pytest. No removable declared third-party dependency was established. Imported engine dependencies and optional acquisition use must be assessed by their own environments.
- `research/scripts/soak_harness.py` prints banners and periodic telemetry; validation and audit runners print per-control/per-suite lines. Static counts below identify review targets only. No runtime output-volume or repeated-warning defect was demonstrated.
- Existing request-ledger and telemetry logs carry audit provenance. Do not infer they are redundant from file extension, repetition or exclusion from public publication.

## Proposed console design (not implemented)

For future approval: default audit CLI output can show final verdict, invariant failures, test totals, measured elapsed time and evidence destination. An explicit `--verbose` can retain per-control detail; `--debug` can retain diagnostic traces. Preserve warnings/errors and complete raw file logging in both modes; never suppress financial controls, ledger entries or exception evidence. Keep stdout contracts until subprocess users and tests are reviewed. Validate normal/verbose exit codes, numeric results and full evidence parity with uniquely named output files. No production behavior or current logs were changed.

| Python source | Static print call sites |
|---|---:|
| `scratch/gate1_v16_reconciliation.py` | 45 |
| `scratch/audit_v14_full_forensics.py` | 37 |
| `scratch/baseline_check.py` | 35 |
| `scratch/reproduce_p0_accounting.py` | 33 |
| `scratch/detailed_loss_attribution.py` | 24 |
| `scratch/deep_baseline_profile.py` | 23 |
| `scratch/run_statistical_validation.py` | 20 |
| `preview.py` | 20 |
| `scratch/audit_v13_05_latency_memory.py` | 19 |
| `scratch/gate4_statistical_review.py` | 18 |
| `research/scripts/verify_remediation_controls.py` | 18 |
| `research/scripts/soak_harness.py` | 18 |
| `scratch/gate2_attribution_bridge.py` | 17 |
| `scratch/backup_and_verify_evidence.py` | 17 |
| `scratch/benchmark_runtime.py` | 16 |
| `scratch/audit_v13_01_costs.py` | 16 |
| `scratch/runtime_check.py` | 15 |
| `scratch/inspect_v11_b_loss_attribution.py` | 15 |
| `scratch/gate1_dates_reconciliation.py` | 15 |
| `research/scripts/test_data_integrity.py` | 15 |
| `scratch/check_turnover_formula.py` | 14 |
| `scratch/v12_statistical_sensitivity.py` | 13 |
| `research/scripts/validate_soak_run.py` | 12 |
| `local_test.py` | 11 |
| `selfcheck.py` | 10 |
| `live_runner.py` | 9 |
| `full_test.py` | 9 |
| `scratch/test_hypotheses.py` | 8 |
| `scratch/reconcile_v10_attribution.py` | 8 |
| `scratch/audit_v13_04_bootstrap.py` | 8 |
| `scratch/audit_v13_02_suppressed_orders.py` | 8 |
| `scratch/analyze_xle_and_sectors.py` | 8 |
| `scratch/test_hypotheses_part2.py` | 7 |
| `scratch/four_way_comparison.py` | 7 |
| `research/scripts/run_tier1_authentic_backtest.py` | 7 |
| `scratch/analyze_vol_spike_attribution.py` | 6 |
| `capture_endpoint_orders.py` | 6 |
| `build_universe.py` | 6 |
| `scratch/test_cadence.py` | 5 |
| `scratch/test_agent_features.py` | 5 |
| `scratch/test_adverse_inputs.py` | 5 |
| `scratch/math_verify.py` | 5 |
| `scratch/inspect_windows.py` | 5 |
| `scratch/build_ledger_and_manifest.py` | 5 |
| `scratch/audit_test.py` | 5 |
| `scratch/audit_all_regimes_turnover.py` | 5 |
| `scratch/test_candidates_a_to_f.py` | 4 |
| `scratch/reproduce_baseline.py` | 4 |
| `scratch/profile_cpu.py` | 4 |
| `scratch/gate3_cost_sensitivity.py` | 4 |
| `scratch/audit_v13_03_liquidation_timeline.py` | 4 |
| `research/scripts/run_b2a_replay_suite.py` | 4 |
| `market_open.py` | 4 |
| `scratch/evaluate_v10_candidates.py` | 3 |
| `scratch/counterfactual_rebalancing.py` | 3 |
| `research/scripts/run_benchmarks.py` | 3 |
| `research/scripts/run_baseline_audit.py` | 3 |
| `scratch/inspect_recovery_timing.py` | 2 |
| `scratch/benchmark_v12.py` | 2 |
| `research/scripts/verify_tier1_accounting.py` | 2 |
| `research/scripts/scan_secrets.py` | 2 |
| `research/scripts/generate_universe_and_provider_matrix.py` | 2 |
| `research/scripts/acquire_tier1_tiingo.py` | 2 |
| `research/engine/report_consistency_checker.py` | 2 |
| `strategy_selftest.py` | 1 |
| `scratch/print_trades.py` | 1 |
| `research/scripts/generate_v29b_order_events.py` | 1 |
| `research/scripts/generate_permissions_matrix.py` | 1 |
| `research/scripts/generate_inventory_v6.py` | 1 |
| `research/scripts/generate_inventory_v5.py` | 1 |
| `research/scripts/generate_inventory_v4.py` | 1 |
| `research/scripts/generate_inventory_v3.py` | 1 |
| `research/scripts/generate_inventory_v10.py` | 1 |
| `research/scripts/generate_acquisition_spec.py` | 1 |
| `research/scripts/acquire_tier2_tiingo.py` | 1 |
| `live_runner_selftest.py` | 1 |
| `endpoint_harness_selftest.py` | 1 |

Warning call sites: `research/engine/tiingo_client.py:106`, `research/engine/tiingo_client.py:281`, `research/engine/tiingo_client.py:323`, `research/scripts/acquire_tier2_tiingo.py:67`. Repetition cannot be measured without an authorized run.

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

## Achieved and deferred reductions

Achieved: three additive reports, one full authorized path index, one historical report index and one exact 69-path role map. Files removed: **0**; storage reclaimed: **0 bytes**; public candidate files removed: **0**; runtime/test-output reduction measured: **0**. These are navigation improvements, not a numerical claim of lower repository size. Pre-change file count excludes these three new reports; post-change authorized count is 360.

No destructive reduction is recommended for immediate execution. Any later delete/move/rename/overwrite, including caches, must receive explicit path-specific human approval. No smaller equivalent snapshot is certified. Safe future work is local view filtering, provenance availability review and an independently reviewed console patch with raw before/after evidence.

## Checks and limitations

Documentation-only batch: no pytest execution, runtime benchmarking, code/configuration edits or financial recalculation. Static parsing was used only for inventory signals. Syntax parse exceptions: 0. No zero-regression assertion is made. New report creation uses exclusive file mode. The final preservation check compares safe source bytes, evidence digest, branch/HEAD and tracked Git diff; private datasets are deliberately excluded from hashing. Measured inventory/report-generation time is recorded in the inventory footer. No deployment, API calls, main V29E validation or branch change was performed.

## Historical navigation index

Use V29D-R for reconciled historical claims, V29A dependency map for research provenance, and the V29E-N inventory for current on-disk availability. Earlier counts can refer to other workspaces; the V29A 123-item scratch inventory does not establish that those items exist here.

- [.pytest_cache/README.md](.pytest_cache/README.md)
- [AGENT_BRIEF.md](AGENT_BRIEF.md)
- [ANATOMY.md](ANATOMY.md)
- [GUARDIAN_ALPHA_V21_PORTFOLIO_FIDELITY_AND_TIER2_READINESS_REPORT.md](GUARDIAN_ALPHA_V21_PORTFOLIO_FIDELITY_AND_TIER2_READINESS_REPORT.md)
- [GUARDIAN_ALPHA_V22_CAUSAL_PRICE_ALIGNMENT_AND_TIER1_REQUALIFICATION_REPORT.md](GUARDIAN_ALPHA_V22_CAUSAL_PRICE_ALIGNMENT_AND_TIER1_REQUALIFICATION_REPORT.md)
- [GUARDIAN_ALPHA_V23_TIER2_OUT_OF_SAMPLE_VALIDATION_REPORT.md](GUARDIAN_ALPHA_V23_TIER2_OUT_OF_SAMPLE_VALIDATION_REPORT.md)
- [GUARDIAN_ALPHA_V24_TIER2_CONTINUITY_AND_VALIDATION_FORENSICS_REPORT.md](GUARDIAN_ALPHA_V24_TIER2_CONTINUITY_AND_VALIDATION_FORENSICS_REPORT.md)
- [GUARDIAN_ALPHA_V25_FINAL_TIER2_FINANCIAL_CERTIFICATION_REPORT.md](GUARDIAN_ALPHA_V25_FINAL_TIER2_FINANCIAL_CERTIFICATION_REPORT.md)
- [GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md](GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md)
- [GUARDIAN_ALPHA_V26_ADVERSARIAL_FINANCIAL_CERTIFICATION_REPORT.md](GUARDIAN_ALPHA_V26_ADVERSARIAL_FINANCIAL_CERTIFICATION_REPORT.md)
- [GUARDIAN_ALPHA_V27R_SCIENTIFIC_AND_EXECUTION_RECONCILIATION_REPORT.md](GUARDIAN_ALPHA_V27R_SCIENTIFIC_AND_EXECUTION_RECONCILIATION_REPORT.md)
- [GUARDIAN_ALPHA_V27_SCIENTIFIC_VALIDITY_AND_MARKET_REALISM_AUDIT.md](GUARDIAN_ALPHA_V27_SCIENTIFIC_VALIDITY_AND_MARKET_REALISM_AUDIT.md)
- [GUARDIAN_ALPHA_V28_FINAL_RESEARCH_GOVERNANCE_REPORT.md](GUARDIAN_ALPHA_V28_FINAL_RESEARCH_GOVERNANCE_REPORT.md)
- [GUARDIAN_ALPHA_V29A_EVIDENCE_INVENTORY.md](GUARDIAN_ALPHA_V29A_EVIDENCE_INVENTORY.md)
- [GUARDIAN_ALPHA_V29A_FINAL_GATE_REPORT.md](GUARDIAN_ALPHA_V29A_FINAL_GATE_REPORT.md)
- [GUARDIAN_ALPHA_V29A_GIT_PUBLICATION_RISK_REVIEW.md](GUARDIAN_ALPHA_V29A_GIT_PUBLICATION_RISK_REVIEW.md)
- [GUARDIAN_ALPHA_V29A_REPRODUCIBILITY_DEPENDENCY_MAP.md](GUARDIAN_ALPHA_V29A_REPRODUCIBILITY_DEPENDENCY_MAP.md)
- [GUARDIAN_ALPHA_V29B_EXECUTION_VERIFICATION_REPORT.md](GUARDIAN_ALPHA_V29B_EXECUTION_VERIFICATION_REPORT.md)
- [GUARDIAN_ALPHA_V29C_FINAL_GATE_REPORT.md](GUARDIAN_ALPHA_V29C_FINAL_GATE_REPORT.md)
- [GUARDIAN_ALPHA_V29C_PUBLICATION_RISK_REGISTER.md](GUARDIAN_ALPHA_V29C_PUBLICATION_RISK_REGISTER.md)
- [GUARDIAN_ALPHA_V29C_PUBLIC_REPRODUCIBILITY_PLAN.md](GUARDIAN_ALPHA_V29C_PUBLIC_REPRODUCIBILITY_PLAN.md)
- [GUARDIAN_ALPHA_V29C_PUBLIC_SNAPSHOT_ALLOWLIST.md](GUARDIAN_ALPHA_V29C_PUBLIC_SNAPSHOT_ALLOWLIST.md)
- [GUARDIAN_ALPHA_V29C_RELEASE_BRANCH_PROCEDURE.md](GUARDIAN_ALPHA_V29C_RELEASE_BRANCH_PROCEDURE.md)
- [GUARDIAN_ALPHA_V29D_FINAL_REPORT.md](GUARDIAN_ALPHA_V29D_FINAL_REPORT.md)
- [GUARDIAN_ALPHA_V29D_ISOLATED_TEST_EVIDENCE.md](GUARDIAN_ALPHA_V29D_ISOLATED_TEST_EVIDENCE.md)
- [GUARDIAN_ALPHA_V29D_PUBLIC_BASE_HISTORY_AUDIT.md](GUARDIAN_ALPHA_V29D_PUBLIC_BASE_HISTORY_AUDIT.md)
- [GUARDIAN_ALPHA_V29D_RELEASE_SECURITY_GATE.md](GUARDIAN_ALPHA_V29D_RELEASE_SECURITY_GATE.md)
- [GUARDIAN_ALPHA_V29D_R_RECONCILIATION_REPORT.md](GUARDIAN_ALPHA_V29D_R_RECONCILIATION_REPORT.md)
- [GUARDIAN_ALPHA_V29D_SNAPSHOT_CONTENT_AUDIT.md](GUARDIAN_ALPHA_V29D_SNAPSHOT_CONTENT_AUDIT.md)
- [README.md](README.md)
- [RELEASE-AUDIT.md](RELEASE-AUDIT.md)
- [RELEASE.md](RELEASE.md)
- [START_HERE.md](START_HERE.md)
- [SUBMISSION.md](SUBMISSION.md)
- [docs/competition-contract.md](docs/competition-contract.md)
- [docs/compliance-matrix.md](docs/compliance-matrix.md)
- [docs/evidence-ledger.md](docs/evidence-ledger.md)
- [docs/stage-status.md](docs/stage-status.md)
- [docs/stage2-baseline.md](docs/stage2-baseline.md)
- [docs/stage2a-final-verification.md](docs/stage2a-final-verification.md)
