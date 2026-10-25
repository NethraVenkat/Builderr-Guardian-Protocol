# V29E - Reference and payload audit

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

External audit directory: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo`. All raw logs, harnesses, exact commands, identifiers and machine-readable evidence remain there, outside repository staging scope. Evidence index: [evidence_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/evidence_manifest.json).

**Gate 1 PASS. Gate 2 PASS.** Recovered bytes match V29E-S and V29D-R. This is a filesystem test candidate, not a committed or published release.

## Immutable reference

- Recovered root: `C:\Users\Manish\.gemini\antigravity\brain\87f2b861-5bfa-4221-9a63-a54f459a77da\scratch\v29d_simulated_public_snapshot`.
- Original sidecar: `C:\Users\Manish\.gemini\antigravity\brain\87f2b861-5bfa-4221-9a63-a54f459a77da\scratch\v29d_simulated_public_snapshot\v29d_snapshot_manifest_inventory.json`.
- Sidecar SHA-256: `3a4ae9a30cd91485d5a3d5ce5a0d2e501b25f282e83b2602fea98b2589849d0c` (matches V29E-S).
- V29D-R authority SHA-256: `70fbeea5daa770c856b2b1bbcf447216fcb894be16c07a2061e77649388b2ad3` (matches V29E-S).
- Verified 69 unique approved paths against both the sidecar and numbered V29D-R table: 69 present, 69 size matches, 69 raw-byte SHA-256 matches; zero missing/changed paths. No newline normalization was used.
- All 54 extra paths are separately recorded with size/mtime in [reference_extras.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/reference_extras.json); they are the sidecar plus 53 Python/pytest caches. No extra was copied or deleted. Their exact prior listing remains in the unchanged V29E-S report.

## Isolated copy

Location: `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo\payload`. Created with `tempfile.mkdtemp` and exclusive destination-file writes; ordinary filesystem operations only. Exactly 69 files were selected from the approved list; directories and wildcards were not copied. Every destination hash was verified before execution and again afterwards. No sidecar, bytecode, pytest cache, private research result or licensed cache is in this payload. Final file set is still exactly the 69 approved paths.

Path-by-path sizes, SHA-256, Git blob IDs and comparison results: [verified_payload_manifest.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/verified_payload_manifest.json). The new JSON is outside the payload. Setup and pre-execution preservation snapshot took 14.610 seconds; discovery commands are excluded from that duration.

No reconstruction, source edit, test assertion change, builder execution, Git worktree or branch operation occurred. The historical builder containing `shutil.rmtree` was not run. Both original frozen strategy implementations and their isolated copies remain byte-identical.

## Zero-loss checks

[preservation_pre_report.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/preservation_pre_report.json) records:

- All 357 pre-V29E-N inventoried paths still exist, with unchanged size/mtime across this batch.
- The four V29E-N/V29E-S reports and V29B untracked inventory retain their task-start SHA-256 values. V29B SHA-256: `f34db323811b47cb22324b7d5ec882f4a130ba8d15e8cf5adcd5756d9187b1a2`.
- All 123 original reference-directory files retain size/mtime; all 69 reference SHA-256 values and the sidecar hash are unchanged.
- V28 through V29D commit objects exist and are ancestors of HEAD. Exact object IDs and exit codes are in that evidence file.
- Tracked and staged diffs are empty. No original file, cache, forensic log, failed experiment or scratch script was deleted, moved, renamed or overwritten.

Restricted market-data roots and Tier 3 were not traversed or hashed. Preservation there follows the no-access/no-write execution boundary; it is not a fabricated byte-for-byte comparison of sealed contents. Only the approved public sample fixture was used by tests, never licensed vendor caches or sealed Tier 3 observations.

The four new reports are the only repository additions from this batch. Final checks are recorded in [completion_verification.json](C:/Users/Manish/AppData/Local/Temp/guardian-v29e-certification-p_3eywdo/evidence/completion_verification.json). Existing untracked evidence remains untracked; no files were staged.
