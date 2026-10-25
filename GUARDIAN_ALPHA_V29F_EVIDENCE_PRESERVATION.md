# V29F - Private evidence-durability plan

Date: 2026-10-24 (Asia/Calcutta). Branch: `research/v29e-final-release-verification`. HEAD: `b283ded200c777b130285b0aa56a0b044afbd339`.

**Plan prepared; archival execution NOT PERFORMED. Durability remains CONDITIONAL until an archive is actually copied and verified.** No source was moved, deleted, compressed in place, overwritten or uploaded. No confidential evidence belongs in the public release.

## Exact current source trees and measured scope

The following are authorized audit trees, not vendor-data roots. Metadata traversal encountered no directory links/reparse points or sealed/Tier 3-named subtrees. Observations were not inspected for this plan.

| Exact source | Files | Logical bytes | Existing evidence-index SHA-256 |
|---|---:|---:|---|
| `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-certification-p_3eywdo` | 230 | 3090138 | `9a6e2fc61c52efe06d971bb4f69bf12d4fb3b8e4772d8c2c945978d36df8a8ba` |
| `C:\Users\Manish\AppData\Local\Temp\guardian-v29e-r-f01airre` | 4411 | 113088283 | `85023fd8f7732ff0433e3943ffc6477c74b3845ad76bd3ffdcc2a671ef480d4c` |

Combined: **4,641 files / 116,178,421 logical bytes**. These are metadata measurements, not allocated disk usage or compressed-archive forecasts. One complete private copy needs at least these source bytes plus companion files/manifests/filesystem overhead; an independent second full copy needs the corresponding additional capacity. No arbitrary compression/savings percentage is assumed.

The 130 + 136 = 266 files in the existing evidence indexes were actually read and verified against recorded size/SHA-256. The indexes themselves were hashed as above. Existing indexes intentionally omit parts of their trees; verifying those entries is **not** proof all 4,641 source files already have full archival checksums. A future complete manifest must cover every regular file, including venv/temp artifacts and failures.

## Mandatory retention scope

Archive both whole trees, privately, with their distinct root names. Include:

- All manifests, state JSON, exact process commands/status/timings, failed metadata requests, failed candidate/test logs, stdout/stderr, JUnit, test IDs, harness versions, parity failures/corrections and security/history metadata.
- V29E payload; V29E-R baseline, failed first candidate and validated `revised_payload_v2`; original/revised full manifests and old/new change hashes. The validated candidate has 71 selected files; copying an audit tree is not selecting public payload files.
- The verified wheelhouse and source metadata/locks, existing clean venv, synthetic test temporary artifacts and every original failed experiment in these audit trees. Do not prune them because they can be regenerated.
- Companion private case context outside the two trees: copies of the 13 V29E-family reports, the five V29F reports when finalized, and `research/evidence/v29b/test_suite_400_classified_inventory.json`, each by exact name/path with checksums. Record repository branch/HEAD and five checkpoint IDs as read-only metadata, not a new Git bundle/history export.

The original recovered snapshot under `.gemini/.../scratch/v29d_simulated_public_snapshot` is outside these two trees. Its approved bytes are also preserved in the V29E payload, with original-reference hashes/sidecar custody recorded in evidence. Keep its original 123 files untouched. If the owner wants a separate full private copy of that original directory and sidecar, authorize and enumerate it as an additional source; do not silently claim the two-tree archive includes those separate original caches.

## Destination and access policy - proposed only

The owner should select a persistent local/private archival root outside Windows Temp, Downloads/project publication selection and any public/cloud-sync directory. Example design location: `C:\Users\Manish\Documents\Guardian-Alpha-Private-Archive\V29E-case-<UTC-time>-<random-id>`; it has **not** been created or approved as an actual destination. Use an owner-restricted, encrypted storage location with keys/recovery access retained separately; obtain a private second copy on independently controlled storage if authorized. Do not publish archive contents, private path indexes, licenses/account evidence or raw diagnostic logs.

A package/software license or existing custody does not establish additional third-party archival/retention permissions. Confirm that any private copy/retention is within the owner's authorization before executing the plan; unresolved material is a stop condition for the affected copy, not permission to delete the originals. No vendor caches, ledgers, raw datasets or Tier 3 directories are added as sources by this plan.

## Non-destructive, checksum-verified procedure - not executed

1. Quiesce the two audit trees: no concurrent tests/installers/editors writing them. Inventory source relative path, file type, byte length and mtime; record exact root identities and symlink/reparse/alternate-stream findings. Stop on links, restricted unexpected subtrees, unreadable files, ambiguous paths or unsupported metadata. Do not descend into a newly discovered restricted area.
2. Create a **new collision-safe destination only**. Preserve the two source-root names under separate archive subdirectories. Reject an existing destination, root/path escape, absolute or parent-traversal relative entries and case/Unicode collisions. Copy plain bytes, never hardlink/move or mirror/purge. Do not use cleanup/synchronization flags that delete or overwrite evidence.
3. Build a complete source manifest of every authorized regular file, including existing manifest files: root label, exact relative path, size, SHA-256, mtime and any metadata/stream policy. Preserve existing manifests byte-for-byte; do not rewrite old absolute paths, harness source or receipts for the archive location. Record original-to-archive path mapping in a **new separate** custody receipt.
4. Open each destination file exclusively; copy without overwriting; independently re-read and hash it. Compare size/hash with the source manifest. Check source size/mtime and hash again after copying so a concurrent change cannot be reported as a stable match. A mismatch/unreadable object fails the archive; preserve the failure/partial copy and source for investigation rather than deleting or replacing them.
5. Compare complete source/destination path sets, counts and hashes. Verify the old indexed manifests, 69-file reference payload, 71-file validated candidate, failed-candidate manifest, wheel hashes, test IDs/JUnit and raw failure logs specifically. The new manifest's own digest belongs in a detached receipt, avoiding a self-referential hash claim.
6. Record exact commands/method, source/destination identities, full errors, actual copy/hash start/end times, measured durations and every mismatch. Mark success only after every required file verifies; distinguish metadata/ACL/stream coverage from regular-file byte coverage. The receipt is private evidence, not a public artifact.
7. Independently verify the authorized second copy and perform a read-only restore spot/full verification appropriate to the case. Do not run an archived venv in place or rewrite it: absolute paths in venv configuration may be nonportable. Preserve it as evidence; use verified wheelhouse/lock to rebuild a new environment if future execution is authorized.
8. Leave both Temp originals and all original repository/snapshot evidence untouched even after success. No expiry, source deletion, automatic cleanup, Git staging or upload is authorized by this plan. A subsequent loss of a Temp source must never be retroactively described as protected by an archive that was not executed.

## Current evidence and limitation

V29F verified existing indexed evidence and candidate/reference manifests and checked original metadata; it did not produce a complete archival hash manifest, copy, encrypted container, second replica or restore test. All copy/verification durations are **NOT MEASURED** because those operations were not run. The two Temp locations remain available now but lack a completed persistent backup under this plan. Evidence durability is CONDITIONAL until the owner executes/approves a verified private archive. This is the only archival-plan document; other V29F reports reference it rather than duplicate the procedure.
