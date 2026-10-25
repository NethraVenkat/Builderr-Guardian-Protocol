# V29E-R - Dependency remediation

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

External remediation/evidence directory: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre`. Prior audit: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo`. New evidence index: [evidence_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/evidence_manifest.json). No artifact here is publication approval.

**PASS - demonstrated NumPy declaration/clean-install blocker remediated for CPython 3.11.9, Windows AMD64.** Separate local candidates were created; the repository dependency files and immutable snapshot are unchanged.

## Original evidence and import classification

All eight V29E-family reports and all 130 files indexed by the prior raw evidence manifest were read and verified against recorded sizes/hashes. Prior `minimal_dependencies` exited 2 with 244 partially collected items and V14/V15 import errors because NumPy was undeclared. That failure and all original logs remain unchanged.

A new AST inventory covered every Python file in the exact original 69-path selection: [import_inventory.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/import_inventory.json). Only pytest (27 test modules) and NumPy (V14/V15, line 11) are third-party imports. V14 uses NumPy for statistical array calculations. Production agent.py, public research engine/strategies, CLI diagnostics and optional Tiingo client have no third-party imports in this selection. Optional provider acquisition still requires explicit credentials, licensing and network authorization. Runtime module origins supplement static imports; unselected tooling is outside this claim.

## Pins, compatibility and package sources

Exact supported/tested target: **CPython 3.11.9, Windows AMD64**. Official NumPy 2.4.6 metadata requires Python >=3.11 and provides a cp311-win_amd64 wheel; pytest 9.1.1 requires Python >=3.10. Versions match V29E's observed environment to minimize package-related numerical changes. Other targets are not certified. Primary metadata: [NumPy 2.4.6](https://pypi.org/project/numpy/2.4.6/), [pytest 9.1.1](https://pypi.org/project/pytest/9.1.1/). Raw JSON/hashes are retained locally.

| Package | Pin | Role |
|---|---|---|
| numpy | 2.4.6 | Direct test-only; V14 statistics and V15 import |
| pytest | 9.1.1 | Direct test-only framework |
| colorama | 0.4.6 | Active Windows pytest console dependency |
| pluggy | 1.6.0 | Active pytest plugin infrastructure |
| iniconfig | 2.3.1 | Active pytest configuration parser |
| packaging | 26.3 | Active pytest version/requirement dependency |
| pygments | 2.21.0 | Active pytest highlighting dependency |

All active transitive requirements are satisfied by the seven pins on the actual target: [dependency_closure_check.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/dependency_closure_check.json). Python <3.11-only requirements and development extras are inactive.

Initial sandbox source requests failed with WinError 10013; full recorded errors/timings are preserved in [package_source_requests.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/package_source_requests.json). The subsequent bounded source action succeeded, allowing HTTPS only to pypi.org and files.pythonhosted.org and rejecting other redirects. Compatible non-yanked binary wheels were selected; each size/SHA-256 matched its PyPI metadata. No source build or market-data acquisition occurred. Source/wheel hashes and exact acquisition command: [verified_package_sources.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/verified_package_sources.json), [package_acquisition_record.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/package_acquisition_record.json). These are byte/provenance controls, not independent publisher-attestation or comprehensive vulnerability certification.

## Separate candidates and exact changes

First candidate: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre\revised_payload` (preserved). Corrected candidate: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre\revised_payload_v2`. Both have 71 files. Manifests: [original_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/original_manifest.json), [revised_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/revised_manifest.json), [revised_v2_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/revised_v2_manifest.json).

The first full suite returned **252 passed, 1 failed**, exit 1: the integrity test detected the new README against the stale release checksum. README and dependency checksum entries both needed revision. A second separate candidate updates legitimate non-executable checksum entries and adds the new guide/lock checksums: 19 entries instead of 17. No original manifest, test assertion or financial expectation was changed.

Corrected selection: **3 modified non-executable files + 2 additions**; all Python, strategies, accounting, fixture bytes, tests and JSON financial expectations are unchanged. Exact changes:

| Exact path | Action | Original SHA-256 | Revised SHA-256 |
|---|---|---|---|
| `README.md` | modified | `1c61f6777afafe903620096a175f12ddbab0c90a5ce455707cd1befd65017f1a` | `c4fb1eeb204c9fbb516802f7401b26a07dfac62ea2092f4a8136f51e59c101d9` |
| `RELEASE_V29E_R.md` | added | `None` | `57182d7d9e547579eca372b29dbe8427f3792a7af150a3383d96d095f00cfe07` |
| `release-manifest.sha256` | modified | `24170d75441cfdda349fdfd10680ef26923df2f731fa9ad259fba288c8b2b432` | `8089fbd01fbc7cb557a2a38781ab16336aefb93cd5300bf73317bfa15c75cc2d` |
| `requirements-test-win-py311.lock.txt` | added | `None` | `0fc340bf0fd5dd52e379635ac93fcfec28b9b3d87fee77a8255558b187bc56a5` |
| `requirements-test.txt` | modified | `852aa3cfcba51e002694c668696f87d4758aecb46532599a5acefca10a2adc7f` | `52691dd953335a5e1edb8462b6403a2befc805686663cae7f70988b379131832` |

## Clean installation and actual tests

A new venv was created with `system_site_packages=False`. Before install it contained only bundled bootstrap pip 24.0 and setuptools 65.5.0: [pre_install_packages.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/pre_install_packages.stdout.txt). It then installed exactly the seven declared packages from the verified local wheelhouse with no index access, using:

```text
C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre\clean_venv\Scripts\python.exe -I -B -X utf8 -m pip --isolated install --no-index --find-links C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre\wheelhouse --only-binary=:all: --require-hashes -r C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre\revised_payload\requirements-test-win-py311.lock.txt
```

Installation exit **0**, wall **27.440s**; `pip check` exit **0**. Pre/post package lists prove this was not the earlier already-installed dry-run. No global site-packages were inherited; actual third-party origins are under the clean venv.

New independent collection: **253 IDs**, exit 0. Corrected full suite: **253 passed in 13.95s**, exit **0**, wall **14.526s**. Ordered IDs match V29E exactly. Full identifiers, phase outcomes/durations and JUnit: [v2_regression.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_regression.json), [v2_regression.junit.xml](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_regression.junit.xml). Selfcheck, eight strategy checks, preview and absent-data probe exit 0. Missing static input still raises FileNotFoundError; no-bars/no-token historical provider still yields an empty timeline. No production missing-data behavior was modified.

## Financial parity, isolation and security

Three existing public sample regimes x E0/A+E were replayed from a newly copied original baseline and corrected candidate in the same clean environment. **Six scenarios match exactly** for full result hashes, metrics, equity, fills, canonical traces, final states, turnover, slippage and commissions: [financial_parity_comparison.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/financial_parity_comparison.json). This is sample-only parity, not universal equivalence or licensed-history requalification.

The initial portfolio-hash comparison exited 1: its generic serializer used process-dependent `str(frozenset)` for authorized_universe. Every metric and full economic-result digest already matched. Initial failure/snapshots remain preserved. A new harness sorts set/frozenset representations without changing candidate inputs/code/assertions; both replay sets were rerun and canonical snapshots match. Diagnosis: [initial_parity_differences.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/initial_parity_differences.json).

The guarded launcher uses -I/-B/-X utf8, the exact copy root, disabled plugin autoload, denied socket/DNS/child/native calls after trusted bootstrap, protected original/prior-evidence access restrictions, denied registry credential lookup and external log/temp paths. There are zero unexpected network events/project import leaks. Three denied Windows null-device platform probes remain explicitly classified, not discarded. This is application-level enforcement, not an OS hostile-native-code sandbox. Origins/control evidence: [revalidation_summary.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/revalidation_summary.json) and per-run telemetry.

A finite 71-file secret/private-path/identifier scan and 11-object denylist comparison found no matches: [revised_security_scan.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/revised_security_scan.json). The original synthetic redaction-test token is unchanged; the sample gzip was checked opaquely, not decompressed for rights assessment. This does not establish data rights.

## All executed telemetry, including failures

| Step | Exit | Wall seconds | Exact command + complete stdout/stderr |
|---|---:|---:|---|
| pre_install_packages | 0 | 0.821 | [pre_install_packages.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/pre_install_packages.process.json) / [pre_install_packages.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/pre_install_packages.stdout.txt) / [pre_install_packages.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/pre_install_packages.stderr.txt) |
| clean_install | 0 | 27.440 | [clean_install.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/clean_install.process.json) / [clean_install.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/clean_install.stdout.txt) / [clean_install.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/clean_install.stderr.txt) |
| post_install_check | 0 | 0.837 | [post_install_check.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_check.process.json) / [post_install_check.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_check.stdout.txt) / [post_install_check.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_check.stderr.txt) |
| post_install_packages | 0 | 1.103 | [post_install_packages.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_packages.process.json) / [post_install_packages.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_packages.stdout.txt) / [post_install_packages.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/post_install_packages.stderr.txt) |
| v1_regression | 1 | 14.044 | [v1_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v1_regression.process.json) / [v1_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v1_regression.stdout.txt) / [v1_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v1_regression.stderr.txt) |
| initial_parity_comparison | 1 | 0.098 | [initial_parity_comparison.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/initial_parity_comparison.process.json) / [initial_parity_comparison.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/initial_parity_comparison.stdout.txt) / [initial_parity_comparison.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/initial_parity_comparison.stderr.txt) |
| v2_collection | 0 | 1.726 | [v2_collection.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_collection.process.json) / [v2_collection.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_collection.stdout.txt) / [v2_collection.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_collection.stderr.txt) |
| v2_regression | 0 | 14.526 | [v2_regression.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_regression.process.json) / [v2_regression.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_regression.stdout.txt) / [v2_regression.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_regression.stderr.txt) |
| v2_selfcheck | 0 | 0.525 | [v2_selfcheck.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_selfcheck.process.json) / [v2_selfcheck.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_selfcheck.stdout.txt) / [v2_selfcheck.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_selfcheck.stderr.txt) |
| v2_strategy_selftest | 0 | 0.454 | [v2_strategy_selftest.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_strategy_selftest.process.json) / [v2_strategy_selftest.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_strategy_selftest.stdout.txt) / [v2_strategy_selftest.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_strategy_selftest.stderr.txt) |
| v2_preview | 0 | 0.656 | [v2_preview.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_preview.process.json) / [v2_preview.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_preview.stdout.txt) / [v2_preview.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_preview.stderr.txt) |
| v2_missingdata | 0 | 0.362 | [v2_missingdata.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_missingdata.process.json) / [v2_missingdata.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_missingdata.stdout.txt) / [v2_missingdata.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_missingdata.stderr.txt) |
| baseline_financial | 0 | 1.127 | [baseline_financial.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial.process.json) / [baseline_financial.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial.stdout.txt) / [baseline_financial.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial.stderr.txt) |
| v2_financial | 0 | 1.036 | [v2_financial.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial.process.json) / [v2_financial.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial.stdout.txt) / [v2_financial.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial.stderr.txt) |
| baseline_financial_canonical | 0 | 0.990 | [baseline_financial_canonical.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial_canonical.process.json) / [baseline_financial_canonical.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial_canonical.stdout.txt) / [baseline_financial_canonical.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/baseline_financial_canonical.stderr.txt) |
| v2_financial_canonical | 0 | 0.950 | [v2_financial_canonical.process.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial_canonical.process.json) / [v2_financial_canonical.stdout.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial_canonical.stdout.txt) / [v2_financial_canonical.stderr.txt](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/v2_financial_canonical.stderr.txt) |

The report-generation transport also encountered a Windows command-length spawn failure before execution; no file was created/overwritten by that attempt. Its record is [report_generation_transport_failure.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-r-f01airre/evidence/report_generation_transport_failure.json). Shorter independent creation commands resolved it. All failures are retained; no blanket zero-regression or universal equivalence claim is made.
