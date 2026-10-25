# Guardian Alpha V29E-N ? Public snapshot minimization

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

Verdict: **CONDITIONAL** for any smaller snapshot; **PASS** for retaining the documented protected 69-file reference unchanged.

## Reference and limits

Exact 69 paths below were parsed from the numbered table in `GUARDIAN_ALPHA_V29D_R_RECONCILIATION_REPORT.md`, avoiding earlier report enumeration errors. All 69 paths are present in the authorized workspace. This is a source-workspace role review, not a newly built or validated public artifact. The historical sanitized `scratch/v29d_simulated_public_snapshot` is absent here. The source checkout is not substituted for those sanitized bytes: V29D-R records edits to README, release tests and procurement tests. Earlier test outcomes and security claims are not independently rerun or recertified.

## Decision

Keep **69 -> 69**, with **zero removals**. A smaller allowlist preserving all runtime, admission, offline reproducibility, financial controls, licensing and documented use is not demonstrated. A tiny runtime-only `agent.py` package would lose the protected candidate's test and reproducibility contract, so it is not an equivalent reduction proposal. Separate user and research distributions could be explored later, but must carry explicit dependency closure, documentation/link integrity and isolated before/after test evidence; no such packaging change is authorized or applied here.

Declared dependencies contain no established redundant package. The independent accounting implementation and report checker must not be collapsed just because related functions have similar purposes. The Tiingo client has optional online acquisition purpose; absence of live API use in an offline test run would not establish dispensability of its provider contract. No network validation was performed.

## Exact role and retention map

| Reference path | Purpose / retention rationale | Proposed action |
|---|---|---|
| `.gitattributes` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `.gitignore` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `AGENT_BRIEF.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `ANATOMY.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `LICENSE` | Licensing; retain | Keep protected reference |
| `README.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `RELEASE-AUDIT.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `RELEASE.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `START_HERE.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `SUBMISSION.md` | User/contract/release documentation; similar purpose is insufficient to remove independently scoped guidance | Keep protected reference |
| `agent.py` | Frozen public runtime; retain unchanged | Keep protected reference |
| `preview.py` | Admission preview and sample-regime consumer | Keep protected reference |
| `release-manifest.sha256` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `requirements-test.txt` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `requirements.txt` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `research/engine/__init__.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/accounting.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/benchmark.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/corporate_actions.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/event_verifier.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/independent_accounting.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/ingestion.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/provider.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/quality.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/replay.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/report_consistency_checker.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/stress.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/tiingo_client.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/validation.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/engine/walk_forward.py` | Offline research/financial correctness or provider boundary; preserve transitive imports and independent controls | Keep protected reference |
| `research/manifests/production_universe_manifest.json` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `research/scripts/validate_soak_run.py` | Offline soak validation; regression dependency | Keep protected reference |
| `research/strategies/__init__.py` | Historical challenger/offline reproducibility and associated tests | Keep protected reference |
| `research/strategies/candidate_alpha.py` | Historical challenger/offline reproducibility and associated tests | Keep protected reference |
| `research/strategies/loss_reduction_candidates.py` | Historical challenger/offline reproducibility and associated tests | Keep protected reference |
| `research/strategies/v11_candidates.py` | Historical challenger/offline reproducibility and associated tests | Keep protected reference |
| `research/strategies/v12_candidate_ae.py` | Historical challenger/offline reproducibility and associated tests | Keep protected reference |
| `research/tests/test_b2_benchmark.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_causality_integrity.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_financial_accounting.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_financial_corner_cases.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_ingestion_quality.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_leveraged_overlay.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_loss_reduction.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_replay_independence.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_risk_enforcement.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_soak_validation.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_storage_compliance.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_trading_stress.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_b2_walk_forward.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_baseline_parity.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_corporate_actions.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_provider_compliance.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_replay_accounting.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_risk_limits.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v11_candidates.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v12_candidate_ae_conflicts.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v13_historical_qualification.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v14_financial_forensics.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v15_evidence_gates.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v16_procurement_preflight.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_v18_authentic_tier1.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `research/tests/test_validation.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `sample_regimes.json.gz` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `selfcheck.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `strategy_selftest.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `tests/e0_expected.json` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |
| `tests/test_e0_release.py` | Admission or financial/research regression coverage; keep test interfaces and independence | Keep protected reference |
| `universe.json` | Environment, fixture, universe or integrity/publication control; retain contract | Keep protected reference |

## Publication exclusions

Every non-reference enumerated file is marked Excluded in the inventory. This is a private retention decision, not deletion authorization or a certification that all reference bytes are publication-safe. Exclude vendor caches, raw market data, request ledgers, holdings/order traces, private results, scratch histories and unapproved audit artifacts from new public artifacts. Preserve them in the development workspace and existing Git history. Root historical audit reports are internal governance evidence, not candidates for automatic public publication. The three new reports likewise contain internal paths/provenance and are excluded from the protected allowlist.

## Next action

Stop after V29E-N. If separately authorized, recover/identify the exact sanitized reference artifact and perform main V29E verification there. Any later reduced candidate needs exact file selection and measured 253-test coverage parity plus runtime/admission and offline financial behavior checks. No deletion, Git staging, branch operation or publication was performed.
