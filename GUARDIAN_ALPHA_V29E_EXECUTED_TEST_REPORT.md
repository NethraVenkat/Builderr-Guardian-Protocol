# V29E - Executed test report

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

External audit directory: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo`. All raw logs, harnesses, exact commands, identifiers and machine-readable evidence remain there, outside repository staging scope. Evidence index: [evidence_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/evidence_manifest.json).

**Gate 3 PASS for the existing installed environment and bounded offline run. Gate 7 BLOCKED for declared-dependency reproducibility.** Historical V29D results were used only as a comparison target; all outcomes below are newly executed.

## Environment and final regression

Python 3.11.9, Windows AMD64, pytest 9.1.1, installed NumPy 2.4.6. Package metadata: [environment.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/environment.json). This is not a fresh environment and establishes no cross-platform guarantee.

Independent collection: **253 items**, process exit **0**, wall 1.658s. Final regression: **253 passed, zero failed/skipped**, pytest-reported **12.92s**, process wall **13.515s**, process exit **0**. Exact ordered IDs match independent collection and the historical total of 253 (56 admission + 197 research).

Exact command (working directory is the isolated payload):

```text
C:\Users\Manish\AppData\Local\Programs\Python\Python311\python.exe -I -B -X utf8 C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo\launcher_v4.py final_regression pytest -v --tb=long -p no:cacheprovider --confcutdir=C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo\payload --log-file=C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo\evidence\final_regression.pytest.log --junitxml=C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo\evidence\final_regression.junit.xml tests research/tests
```

`launcher_v4.py` calls `pytest.main` with the recorded arguments and audit plugin. This is guarded execution, not a claim that an unguarded shell command was run. The exact separate collection command and all commands/exit codes are stored in each `.process.json` below. Full IDs: [collected_test_ids.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/collected_test_ids.txt). Test-phase outcomes, durations, project import origins and guard events: [final_regression.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/final_regression.json). Machine-readable test report: [final_regression.junit.xml](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/final_regression.junit.xml).

## Offline and isolation controls

The launcher starts with Python `-I -B -X utf8`, explicitly selects the copy as cwd/import root, disables third-party pytest plugin autoload, routes logs/temp files outside the payload, and strips token/password/secret environment entries. Windows registry token lookup is denied in the final launcher. The candidate has no vendor caches or request ledger inputs. Audit hooks deny Python socket connect/bind/DNS/send-to, child processes, system execution, post-bootstrap ctypes calls, opening the original workspace/reference/private credential roots, and writes outside the isolated audit directory. Standard pytest/colorama bootstrap occurs before the hook; no project code is loaded then.

Each launcher proves network connect, DNS, child-process and protected-file guards by deliberate denied controls before project code is loaded. No connection or child process succeeds. Full-run project code has **zero network events and zero project import leaks**; 47 project/test module origins were checked in the pytest session hook. The controls are application-level enforcement, not an OS firewall or a hostile-native-code sandbox certification.

Three additional denied events in final telemetry are Windows `\\.\nul` opens from standard-library `platform._syscmd_ver` fallback. They are not private-file access or network attempts. The final wrapper retains their stack traces and excludes only these null-device events from its failure condition; socket/child/private-path failures still fail the run. No candidate code/assertions were changed for this harness correction.

## Regression coverage and supplemental outcomes

The executed suite covers accounting conservation, arithmetic rounding, independent accounting, determinism, financial edge cases, leverage/concentration, corporate actions, provider/storage rejection, holdout firewall, replay causality, strategy invariants and admission/manifest hashes. The following counts are newly collected, not copied from the historical report. They are test counts, not line/branch-coverage percentages.

| Collected test file | Executed tests passed |
|---|---:|
| `tests/test_e0_release.py` | 56 |
| `research/tests/test_b2_benchmark.py` | 1 |
| `research/tests/test_b2_causality_integrity.py` | 5 |
| `research/tests/test_b2_financial_accounting.py` | 7 |
| `research/tests/test_b2_financial_corner_cases.py` | 10 |
| `research/tests/test_b2_ingestion_quality.py` | 12 |
| `research/tests/test_b2_leveraged_overlay.py` | 5 |
| `research/tests/test_b2_loss_reduction.py` | 5 |
| `research/tests/test_b2_replay_independence.py` | 5 |
| `research/tests/test_b2_risk_enforcement.py` | 6 |
| `research/tests/test_b2_soak_validation.py` | 6 |
| `research/tests/test_b2_storage_compliance.py` | 18 |
| `research/tests/test_b2_trading_stress.py` | 26 |
| `research/tests/test_b2_walk_forward.py` | 5 |
| `research/tests/test_baseline_parity.py` | 3 |
| `research/tests/test_corporate_actions.py` | 4 |
| `research/tests/test_provider_compliance.py` | 4 |
| `research/tests/test_replay_accounting.py` | 5 |
| `research/tests/test_risk_limits.py` | 3 |
| `research/tests/test_v11_candidates.py` | 23 |
| `research/tests/test_v12_candidate_ae_conflicts.py` | 10 |
| `research/tests/test_v13_historical_qualification.py` | 9 |
| `research/tests/test_v14_financial_forensics.py` | 5 |
| `research/tests/test_v15_evidence_gates.py` | 4 |
| `research/tests/test_v16_procurement_preflight.py` | 4 |
| `research/tests/test_v18_authentic_tier1.py` | 4 |
| `research/tests/test_validation.py` | 8 |

New UTF-8 CLI outcomes: selfcheck exit 0 (0.945s wall), strategy selftest exit 0 (0.707s; reports 8 checks), preview exit 0 (1.344s). Preview reports clean execution, no leverage/concentration breach and worst sample drawdown 33.5%; these are local sample results, not organizer admission or future-return evidence. Rendered preview values agree with the rounded RELEASE.md table. Test/preview outputs retain their original stdout/stderr files.

Missing-data probe exit 0 (0.431s): missing static input raises `FileNotFoundError`; the historical provider with no preloaded bars and a no-token client produces an **empty timeline without an explicit missing-data error**. The client is a credential-free stub, not a licensed acquisition. This documents actual behavior; callers must not treat empty results as validated licensed-history performance. No licensed data was accessed.

## Declared-dependency blocker

`requirements-test.txt` declares pytest==9.1.1 only. Public files `research/tests/test_v14_financial_forensics.py:11` and `research/tests/test_v15_evidence_gates.py:11` import NumPy; V14 actually uses it in array/statistical calculations. A separate meta-path negative control made only NumPy unavailable, without changing tests, source or installed packages. Collection then exited **2**: **244 items collected and two module-import errors**. This simulates the missing undeclared package; it is not represented as a clean-environment installation or a passing run.

Offline pip dry-run in the installed interpreter exited 0 because pytest and its dependencies are already installed. A separate `--ignore-installed --no-index` dry-run exited 1 because no pytest wheel was available offline. `pip check` exited 0. No dependency installation or package mutation occurred. A fresh documented installation is therefore **not verified**; the offline wheel-availability result is an environmental limitation, distinct from the confirmed NumPy omission. No unrestricted network access or index download was attempted.

## All attempts, including failures

Initial default-encoding script runs exited 1 on Unicode console output; documentation's UTF-8 form resolves them. Initial pytest bootstrap exited 1 when the native guard blocked colorama's Windows ctypes setup. UTF-8 pytest attempts exited 3 when pytest's default null-device log could not open under the filesystem guard. Explicit external log destinations fixed startup. The next two full suites each passed 253 assertions but wrapper exit was 91 because the three denied Windows null-device probes were initially counted as protected-artifact access. Their logs/telemetry remain preserved. The final wrapper classifies those exact recorded events and exits 0; all actual protection boundaries remain enforced. No failed attempt was removed or overwritten.

| Attempt | Process exit | Wall seconds | Raw output / exact command |
|---|---:|---:|---|
| collection | 1 | 1.692 | [collection.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/collection.stdout.txt) / [collection.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/collection.stderr.txt) / [collection.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/collection.process.json) |
| regression | 1 | 0.875 | [regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/regression.stdout.txt) / [regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/regression.stderr.txt) / [regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/regression.process.json) |
| selfcheck | 1 | 0.334 | [selfcheck.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/selfcheck.stdout.txt) / [selfcheck.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/selfcheck.stderr.txt) / [selfcheck.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/selfcheck.process.json) |
| strategy_selftest | 1 | 0.386 | [strategy_selftest.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/strategy_selftest.stdout.txt) / [strategy_selftest.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/strategy_selftest.stderr.txt) / [strategy_selftest.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/strategy_selftest.process.json) |
| preview | 1 | 0.940 | [preview.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/preview.stdout.txt) / [preview.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/preview.stderr.txt) / [preview.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/preview.process.json) |
| utf8_collection | 3 | 1.586 | [utf8_collection.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_collection.stdout.txt) / [utf8_collection.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_collection.stderr.txt) / [utf8_collection.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_collection.process.json) |
| utf8_regression | 3 | 0.960 | [utf8_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_regression.stdout.txt) / [utf8_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_regression.stderr.txt) / [utf8_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_regression.process.json) |
| utf8_selfcheck | 0 | 0.945 | [utf8_selfcheck.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_selfcheck.stdout.txt) / [utf8_selfcheck.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_selfcheck.stderr.txt) / [utf8_selfcheck.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_selfcheck.process.json) |
| utf8_strategy_selftest | 0 | 0.707 | [utf8_strategy_selftest.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_strategy_selftest.stdout.txt) / [utf8_strategy_selftest.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_strategy_selftest.stderr.txt) / [utf8_strategy_selftest.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_strategy_selftest.process.json) |
| utf8_preview | 0 | 1.344 | [utf8_preview.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_preview.stdout.txt) / [utf8_preview.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_preview.stderr.txt) / [utf8_preview.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/utf8_preview.process.json) |
| guarded_collection | 0 | 4.886 | [guarded_collection.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_collection.stdout.txt) / [guarded_collection.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_collection.stderr.txt) / [guarded_collection.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_collection.process.json) |
| guarded_regression | 91 | 23.498 | [guarded_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_regression.stdout.txt) / [guarded_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_regression.stderr.txt) / [guarded_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/guarded_regression.process.json) |
| audited_collection | 0 | 1.658 | [audited_collection.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_collection.stdout.txt) / [audited_collection.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_collection.stderr.txt) / [audited_collection.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_collection.process.json) |
| audited_regression | 91 | 28.231 | [audited_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_regression.stdout.txt) / [audited_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_regression.stderr.txt) / [audited_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/audited_regression.process.json) |
| final_regression | 0 | 13.515 | [final_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/final_regression.stdout.txt) / [final_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/final_regression.stderr.txt) / [final_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/final_regression.process.json) |
| minimal_dependencies | 2 | 1.727 | [minimal_dependencies.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/minimal_dependencies.stdout.txt) / [minimal_dependencies.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/minimal_dependencies.stderr.txt) / [minimal_dependencies.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/minimal_dependencies.process.json) |
| missing_licensed_data | 0 | 0.431 | [missing_licensed_data.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/missing_licensed_data.stdout.txt) / [missing_licensed_data.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/missing_licensed_data.stderr.txt) / [missing_licensed_data.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/missing_licensed_data.process.json) |
| pip_declared | 0 | 1.359 | [pip_declared.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_declared.stdout.txt) / [pip_declared.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_declared.stderr.txt) / [pip_declared.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_declared.process.json) |
| pip_fresh_offline | 1 | 0.918 | [pip_fresh_offline.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_fresh_offline.stdout.txt) / [pip_fresh_offline.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_fresh_offline.stderr.txt) / [pip_fresh_offline.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_fresh_offline.process.json) |
| pip_check | 0 | 1.616 | [pip_check.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_check.stdout.txt) / [pip_check.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_check.stderr.txt) / [pip_check.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/pip_check.process.json) |

No user test expectations, financial calculations or original evidence were edited. No blanket zero-regression or clean-install claim is made.
