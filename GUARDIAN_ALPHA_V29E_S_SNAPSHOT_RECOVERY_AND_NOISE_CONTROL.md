# Guardian Alpha V29E-S ? Snapshot recovery and noise control

2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

**PASS ? reference recovered and checksums verified. CONDITIONAL ? containing directory includes generated files and must not be published wholesale.** No reconstruction or main V29E validation was performed.

## Recovered evidence

Snapshot root: `C:\Users\Manish\.gemini\antigravity\brain\87f2b861-5bfa-4221-9a63-a54f459a77da\scratch\v29d_simulated_public_snapshot`

Machine-readable inventory: `C:\Users\Manish\.gemini\antigravity\brain\87f2b861-5bfa-4221-9a63-a54f459a77da\scratch\v29d_simulated_public_snapshot\v29d_snapshot_manifest_inventory.json`

Inventory SHA-256: `3a4ae9a30cd91485d5a3d5ce5a0d2e501b25f282e83b2602fea98b2589849d0c`

Comparison authority: `C:\Users\Manish\Downloads\Guardian-Alpha-V29B\GUARDIAN_ALPHA_V29D_R_RECONCILIATION_REPORT.md` (numbered 69-row table). Authority file SHA-256: `70fbeea5daa770c856b2b1bbcf447216fcb894be16c07a2061e77649388b2ad3`.

The workspace-relative `scratch/v29d_simulated_public_snapshot` is absent; the externally recorded original exists. The V29E-N unavailable-artifact limitation is therefore resolved by reading the exact V29D absolute location, without relocating anything.

| Executed comparison | Result |
|---|---:|
| Unique V29D-R paths / JSON paths | 69 / 69 |
| Paths present | 69 |
| SHA-256 matches against V29D-R | 69 |
| Byte-size matches against V29D-R | 69 |
| SHA-256 and size matches against JSON inventory | 69 |
| Missing / changed reference files | 0 / 0 |
| Additional files in containing directory | 54 |

Raw bytes were hashed without line-ending normalization. Only the approved 69 candidate paths and provenance/configuration evidence were hashed; no vendor datasets or request ledgers were read. JSON inventory schema is `file_count`, `files[]` with `rel_path`, `size_bytes`, `sha256`, `sanitized`; it is a final-state inventory, not a pre/post source-hash ledger. Its sanitized flags identify exactly `research/tests/test_v16_procurement_preflight.py` and `tests/test_e0_release.py`. README is not marked sanitized; the earlier V29E-N statement suggesting a recorded README edit is unsupported by this recovered inventory. Original reports remain unchanged.

The 54 extras are the inventory sidecar and 53 Python/pytest cache files, listed below. There are no other observed additions. Cache contents were not executed or used as release inputs. The candidate remains the exact 69 paths, not the entire 123-file directory. This checks byte identity against the recorded reference; it does not rerun tests or independently certify publication safety.

## Noise control proposal

Inspected user settings: `C:\Users\Manish\AppData\Roaming\Code\User\settings.json` (SHA-256 `07da5588d8415b351fa66a81fc132e98b831ebc5097493f5c3133e104d8ae10f`). No workspace `.vscode` directory or root `.code-workspace` file was present. User `files.exclude` currently contains a single key whose text is an entire serialized JSON object, rather than three independent glob keys. It does not express the intended individual filters.

Proposed user-level replacement for that malformed entry, preserving any other existing entries:

```json
"files.exclude": {
  "**/__pycache__": true,
  "**/*.pyc": true,
  "**/.pytest_cache": true
}
```

Apply through VS Code User Settings JSON only if desired. These are Explorer display filters; they neither delete files nor change Git tracking, test behavior or publication selection. No user or repository configuration was changed, so no display reduction is claimed as already applied. Do not hide logs, failures, evidence or research histories. The malformed entry was observed directly in local settings; no UI behavior was tested.

## Actions, preservation and blockers

Actions were read-only Git metadata checks, bounded directory metadata enumeration at the recorded external snapshot, approved-file hashing, static inspection of the historical builder, user-settings inspection, and creation of this one report. No development directory was created. The existing `build_isolated_snapshot.py` contains `shutil.rmtree(DST_ROOT)`; it was read as evidence and **not executed**. Recovery makes reconstruction unnecessary. If future recovery is needed, design a separate explicitly authorized export using pinned source blobs, the exact 69 paths, explicit encoding/newline rules, recorded path/tolerance sanitizations and expected final hashes; never run that destructive builder against this evidence directory.

All 357 original inventory paths exist and match recorded sizes. Their size/mtime metadata remained unchanged across this task; safe source/document hashes and all three V29E-N reports also remained unchanged. This is bounded preservation evidence, not a retroactive content-hash proof for every file. Protected opaque locations were neither traversed nor hashed. Tier 3 was not accessed. Licensed caches, request ledgers, prior failures and research evidence remain untouched.

The V29B untracked inventory SHA-256 remains `f34db323811b47cb22324b7d5ec882f4a130ba8d15e8cf5adcd5756d9187b1a2`. All 69 recovered hashes and the external inventory/settings hashes were checked again unchanged. Both tracked and staged Git diffs are empty. V28, V29A, V29B, V29C and V29D commit objects all exist and are ancestors of HEAD (five `merge-base --is-ancestor` exit codes 0). No Git mutations, code/configuration changes, deletion, test removal, financial changes, API calls or publication occurred.

Verification/preflight wall time: **7.141 seconds**, covering this report-generation pass; earlier discovery commands are excluded. Tests: **not run**, because executable code and the release candidate were unchanged. Historical 253-test results are not claimed as fresh execution. Files/bytes reclaimed: **0 / 0**.

No blocker remains to locating and identifying the reference. Main V29E execution remains outside this task. Public packaging must select the exact allowlist and omit all extras without deleting original evidence. Applying the proposed user-setting edit is deferred; it is not a recovery blocker.

New file: `GUARDIAN_ALPHA_V29E_S_SNAPSHOT_RECOVERY_AND_NOISE_CONTROL.md`. Existing untracked files remain the three V29E-N reports and `research/evidence/v29b/test_suite_400_classified_inventory.json`. Stop after V29E-S.

## Exact additional paths relative to recovered root

```text
.pytest_cache/.gitignore
.pytest_cache/CACHEDIR.TAG
.pytest_cache/README.md
.pytest_cache/v/cache/lastfailed
.pytest_cache/v/cache/nodeids
__pycache__/agent.cpython-311.pyc
__pycache__/conftest_isolation_guard.cpython-311-pytest-9.1.1.pyc
__pycache__/preview.cpython-311.pyc
research/engine/__pycache__/__init__.cpython-311.pyc
research/engine/__pycache__/accounting.cpython-311.pyc
research/engine/__pycache__/benchmark.cpython-311.pyc
research/engine/__pycache__/corporate_actions.cpython-311.pyc
research/engine/__pycache__/ingestion.cpython-311.pyc
research/engine/__pycache__/provider.cpython-311.pyc
research/engine/__pycache__/quality.cpython-311.pyc
research/engine/__pycache__/replay.cpython-311.pyc
research/engine/__pycache__/stress.cpython-311.pyc
research/engine/__pycache__/tiingo_client.cpython-311.pyc
research/engine/__pycache__/validation.cpython-311.pyc
research/engine/__pycache__/walk_forward.cpython-311.pyc
research/scripts/__pycache__/validate_soak_run.cpython-311.pyc
research/strategies/__pycache__/__init__.cpython-311.pyc
research/strategies/__pycache__/candidate_alpha.cpython-311.pyc
research/strategies/__pycache__/loss_reduction_candidates.cpython-311.pyc
research/strategies/__pycache__/v11_candidates.cpython-311.pyc
research/strategies/__pycache__/v12_candidate_ae.cpython-311.pyc
research/tests/__pycache__/test_b2_benchmark.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_causality_integrity.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_financial_accounting.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_financial_corner_cases.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_ingestion_quality.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_leveraged_overlay.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_loss_reduction.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_replay_independence.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_risk_enforcement.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_soak_validation.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_storage_compliance.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_trading_stress.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_b2_walk_forward.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_baseline_parity.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_corporate_actions.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_provider_compliance.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_replay_accounting.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_risk_limits.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v11_candidates.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v12_candidate_ae_conflicts.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v13_historical_qualification.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v14_financial_forensics.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v15_evidence_gates.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v16_procurement_preflight.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_v18_authentic_tier1.cpython-311-pytest-9.1.1.pyc
research/tests/__pycache__/test_validation.cpython-311-pytest-9.1.1.pyc
tests/__pycache__/test_e0_release.cpython-311-pytest-9.1.1.pyc
v29d_snapshot_manifest_inventory.json
```
