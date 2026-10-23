# GUARDIAN ALPHA — V29A: ZERO-LOSS EVIDENCE INVENTORY & BASELINE AUDIT

**Audit Scope:** Batch V29A: Zero-Loss Evidence Integrity & Baseline Protection  
**Auditor:** Principal Quantitative Research Auditor, Software Verification Engineer, Evidence Governance Lead  
**Timestamp:** 2026-10-23T18:30:00+05:30  
**Protected Baseline Commit:** `8c77fddf72398b2e016a6f212d067c8aeb2b385e`  
**Target Isolated Worktree:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29A`  
**Target Branch:** `research/v29a-evidence-integrity`  
**Protected Repository:** `C:\Users\Manish\Downloads\Guardian-Alpha-TrackB`  
**Protected Branch:** `research/track-b-v28-governance-certification`  

---

## 1. Executive Summary & Verification Mandate

In strict accordance with the V29A governance charter, this audit establishes an immutable, non-destructive baseline inventory across the primary Track B research repository and the newly provisioned V29A isolated worktree. 

All operations executed during Batch V29A have maintained absolute safety invariants:
1. **Zero Git Mutation:** No staging (`git add`), committing (`git commit`), pushing (`git push`), merging, rebasing, resetting, cleaning, stashing, tagging, or worktree deletion commands were executed. All Git inspection commands were strictly read-only.
2. **Zero Modification to Protected V28 Workspace:** The reference repository at [`C:\Users\Manish\Downloads\Guardian-Alpha-TrackB`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-TrackB) was inspected without modifying, deleting, or truncating any files.
3. **Protected Strategy Invariant Verification:** Both frozen assets were verified bit-for-bit against published cryptographic invariants:
   - Frozen Production Strategy [`agent.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/agent.py): Raw SHA-256 = `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd` (**MATCH**).
   - Frozen Candidate [`research/strategies/v12_candidate_ae.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/strategies/v12_candidate_ae.py): Normalized LF SHA-256 = `978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793` (**MATCH**).
4. **Tier 3 Holdout Isolation:** All market data dated on or after 2022-01-01 remained strictly sealed. No Tier 3 records were opened, parsed, sampled, or hashed.
5. **Preservation of Discrepancies:** All discovered anomalies, including the modified Tiingo request ledger and accidental root-level terminal artifacts, have been preserved, classified, and documented in an append-only manner.

---

## 2. Independent Dual-Workspace Baseline State

| Inventory Dimension | Protected Reference (`Guardian-Alpha-TrackB`) | Isolated Worktree (`Guardian-Alpha-V29A`) | Status / Notes |
| :--- | :--- | :--- | :--- |
| **Git Working Directory** | `C:\Users\Manish\Downloads\Guardian-Alpha-TrackB` | `C:\Users\Manish\Downloads\Guardian-Alpha-V29A` | Verified Isolated |
| **Active Branch** | `research/track-b-v28-governance-certification` | `research/v29a-evidence-integrity` | Target Worktree Validated |
| **Exact HEAD Commit** | `8c77fddf72398b2e016a6f212d067c8aeb2b385e` | `8c77fddf72398b2e016a6f212d067c8aeb2b385e` | Bit-for-bit Parity |
| **Parent Commit** | `f7ed5be9fca778817290f84501a45749f57ebbf7` | `f7ed5be9fca778817290f84501a45749f57ebbf7` | Dual Parity |
| **Tracked Modifications** | 1 file: `research/manifests/tiingo_request_ledger.jsonl` | 0 files (Clean checkout) | Reconciled in Section 4 |
| **Untracked Files** | 77 files (5 root accidental + 72 scratch scripts) | 0 files (at baseline start) | Documented in Section 5 & 6 |
| **Meaningful Ignored Files** | 35 files (`tiingo_cache/`, 4 scratch JSONs, 23 logs, caches) | 0 files (at baseline start) | Metadata-only audit |
| **Tracked Files in Tree** | 224 files | 224 files | Identical commit tree |

---

## 3. Cryptographic Invariants & Source Integrity

Cryptographic verification was performed in Python 3.11.9 on both workspaces using SHA-256 hash algorithms:

```powershell
# agent.py Raw SHA-256
$agentHash = (Get-FileHash -Algorithm SHA256 "agent.py").Hash.ToLower()
# Expected: 46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd

# v12_candidate_ae.py Normalized LF SHA-256
$candContent = [System.IO.File]::ReadAllText("research/strategies/v12_candidate_ae.py") -replace "`r`n", "`n"
$candBytes = [System.Text.Encoding]::UTF8.GetBytes($candContent)
$hasher = [System.Security.Cryptography.SHA256]::Create()
$candHash = [System.BitConverter]::ToString($hasher.ComputeHash($candBytes)).Replace("-","").ToLower()
# Expected: 978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793
```

| Component | Path | Recorded Standard | Measured Value | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Frozen E0 Strategy** | [`agent.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/agent.py) | `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd` | `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd` | **VERIFIED INVARIANT** |
| **Frozen Candidate A+E** | [`research/strategies/v12_candidate_ae.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/strategies/v12_candidate_ae.py) | `978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793` | `978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793` | **VERIFIED INVARIANT** |
| **E0 Baseline Parity** | [`baseline.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/baseline.py) | `a49dc3091c0e3860bb6321adbbba4e3205dfb2b53b8e99e0df6fef88ecfe3b75` | `a49dc3091c0e3860bb6321adbbba4e3205dfb2b53b8e99e0df6fef88ecfe3b75` | **VERIFIED MATCH** |
| **Universe Definition** | [`universe.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/universe.json) | `5016541fce3f46fef95b369cfca816db7eb7ae7325b7a0d4cbb8f4be52f20fd0` | `5016541fce3f46fef95b369cfca816db7eb7ae7325b7a0d4cbb8f4be52f20fd0` | **VERIFIED MATCH** |

---

## 4. Tiingo Request Ledger Reconciliation (Objective 4B)

### 4.1 Provenance Forensics
The baseline repository `Guardian-Alpha-TrackB` exhibited an unstaged modification in [`research/manifests/tiingo_request_ledger.jsonl`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-TrackB/research/manifests/tiingo_request_ledger.jsonl) containing two additional lines (103 lines total vs 101 lines in V29A commit `8c77fddf`):

- **Line 102 (Index 101):**
  ```json
  {"epoch_timestamp": 1792758220.2201953, "timestamp_utc": "2026-10-23T12:23:40.220195Z", "symbol": "SPY", "start_date": null, "end_date": null, "endpoint_type": "metadata", "http_status": 200, "retry_count": 0, "record_count": 1, "data_size_bytes": 41, "result_classification": "SUCCESS"}
  ```
- **Line 103 (Index 102):**
  ```json
  {"epoch_timestamp": 1792758759.3672998, "timestamp_utc": "2026-10-23T12:32:39.367299Z", "symbol": "SPY", "start_date": null, "end_date": null, "endpoint_type": "metadata", "http_status": 200, "retry_count": 0, "record_count": 1, "data_size_bytes": 41, "result_classification": "SUCCESS"}
  ```

Forensic investigation into the exact timestamps (`12:23:40Z` and `12:32:39Z` UTC, corresponding to `17:53:40` and `18:02:39` local time on 2026-10-23) revealed their true origin:
1. In [`research/tests/test_v17_tiingo_qualification.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/tests/test_v17_tiingo_qualification.py#L163-L175):
   ```python
   def test_auth_header_and_request_structure():
       """Verify Authorization header is 'Token <secret>' and Accept is 'application/json'."""
       client = TiingoClient(api_token="valid_secret_token_abc123")
       with patch("urllib.request.urlopen") as mock_urlopen:
           mock_resp = MagicMock()
           mock_resp.status = 200
           mock_resp.read.return_value = b'{"ticker": "SPY", "name": "SPDR S&P 500"}'
           mock_urlopen.return_value.__enter__.return_value = mock_resp

           meta = client.fetch_metadata("SPY")
   ```
2. When `TiingoClient` is instantiated without an explicit `ledger` parameter, it defaults to `self.ledger = RequestLedger()`, which binds to `research/manifests/tiingo_request_ledger.jsonl`.
3. Inside `client.fetch_metadata("SPY")` -> `_execute_request`, while `urllib.request.urlopen` was patched, `self.ledger.record(...)` was **not** patched.
4. The mock response payload `b'{"ticker": "SPY", "name": "SPDR S&P 500"}'` has an exact length of **41 bytes** (`len(payload_bytes) == 41`).
5. As a consequence, running `pytest` against `test_v17_tiingo_qualification.py` in the TrackB workspace during pre-commit V28 verification dynamically appended these two mock records to the physical ledger file on disk.

### 4.2 Append-Only Preservation Policy
- **No Network Requests:** Neither record involved real network egress; both were produced by mock unit testing.
- **No Token Leaks:** The logged entries contain null credentials, standard endpoint classification, and 41-byte payloads.
- **Zero Reversion / Zero Truncation:** Per strict safety constraints, the TrackB ledger was not reverted or truncated.
- **Preserved Archive:** The complete 103-line ledger has been preserved into the V29A evidence repository at [`research/evidence/v29a/tiingo_request_ledger_trackb_preservation.jsonl`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/tiingo_request_ledger_trackb_preservation.jsonl) with SHA-256 `74D437B2E48914CBE32A98FFF1796E77D94DD6A1837714CA1742FD758DF94439`.
- **Worktree Clean Baseline:** The tracked ledger in V29A remains at 101 lines matching commit `8c77fddf`.

---

## 5. Investigation of Accidental Terminal-Created Files (Objective 4C)

Five suspicious untracked root-level files were detected in `Guardian-Alpha-TrackB`. None exist in the clean V29A worktree. All five have been forensically inspected, classified, and preserved into [`research/evidence/v29a/accidental_terminal_files/`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/accidental_terminal_files/) alongside machine-readable manifest [`research/evidence/v29a/accidental_files_inventory.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/accidental_files_inventory.json).

| Item | Original File Name | Size (Bytes) | SHA-256 Hash | Origin & Forensic Contents | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `bject System.Text.UTF8Encoding($false)` | 1,403 | `E2B4E650F170530D4098A0BFCBB39C986F94259889835B8066D785CEC2FFF6E3` | PowerShell command clipping (`New-O` truncated); captured Git diff whitespace warnings for V28 report and test. | Accidental Terminal Artifact (Harmless) |
| **2** | `ersManishDownloadsGuardian-Alpha-TrackB•` | 1,403 | `E2B4E650F170530D4098A0BFCBB39C986F94259889835B8066D785CEC2FFF6E3` | Unquoted directory redirection; byte-for-byte clone of Item 1 containing identical Git whitespace check warnings. | Accidental Terminal Artifact (Harmless) |
| **3** | `olve-Path $file).Path` | 15,915 | `8F929F24047CDA1776E8A44835106E26CD32E21D4FA6CB411B287FBF800AAD88` | Clipped PowerShell command `(Resolve-Path $file).Path`; contains terminal output of the `less` pager manual (`SUMMARY OF LESS COMMANDS`). | Accidental Terminal Artifact (Harmless) |
| **4** | `pace errors remain.•` | 1,732 | `9EB93A40D2899427598D61567F2FC5CD19EF00930FC5149A0E984472E5A44BA1` | Clipped output redirection from `git diff --check` ("whitespace errors remain."); contains initial screen of `less` pager manual. | Accidental Terminal Artifact (Harmless) |
| **5** | `tem.IO.File]••ReadAllText($path)` | 3,285 | `DA9EE8B8AA836D342F2E3B8DDC8056174507A6CCA560BD45A0EAF18ACC2FF8F6` | Clipped PowerShell invocation `[System.IO.File]::ReadAllText($path)`; contains section of `less` pager manual. | Accidental Terminal Artifact (Harmless) |

### Human-Controlled Cleanup Recommendation:
The originals in `C:\Users\Manish\Downloads\Guardian-Alpha-TrackB` were **not** deleted by the automated agent. Because they contain no proprietary data, models, market bars, or credentials, the human repository owner may safely remove these five files from TrackB after reviewing the preserved copies in V29A:
```powershell
# MANUAL HUMAN CLEANUP COMMAND (For TrackB Root Only):
Remove-Item -LiteralPath "C:\Users\Manish\Downloads\Guardian-Alpha-TrackB\bject System.Text.UTF8Encoding($false)"
Remove-Item -Path "C:\Users\Manish\Downloads\Guardian-Alpha-TrackB\*ersManishDownloadsGuardian-Alpha-TrackB*"
Remove-Item -LiteralPath "C:\Users\Manish\Downloads\Guardian-Alpha-TrackB\olve-Path `$file).Path"
Remove-Item -Path "C:\Users\Manish\Downloads\Guardian-Alpha-TrackB\*pace errors remain*"
Remove-Item -Path "C:\Users\Manish\Downloads\Guardian-Alpha-TrackB\*ReadAllText*"
```

---

## 6. Comprehensive File Inventory Breakdown

The full repository inventory across tracked, untracked, and ignored files comprises:

```
Guardian-Alpha Repository Structure
├── Production Root (agent.py, baseline.py, universe.json, historical markdown reports V21-V28)
├── research/
│   ├── engine/          (14 modules: accounting, replay, tiingo_client, independent_accounting, etc.)
│   ├── evidence/        (18 tracked JSON files + soak/ + v29a/ evidence area)
│   ├── manifests/       (41 tracked JSON/JSONL manifests: coverage matrices, terminal holdings, etc.)
│   ├── scripts/         (24 research acquisition, benchmark, and verification scripts)
│   ├── strategies/      (4 candidate strategy implementations, including v12_candidate_ae.py)
│   └── tests/           (39 pytest verification modules collecting 381 regression tests)
├── scratch/             (123 total research artifacts: 44 tracked, 75 untracked in TrackB, 4 ignored)
└── tiingo_cache/        (2 git-ignored preloaded market data files: tier1_bars.json, tier2_bars.json)
```

### 6.1 Structured Category Distribution

| Category | File Count | Description / Scope | Permissible Cryptographic Policy |
| :--- | :--- | :--- | :--- |
| **Source Code (Core & Strategy)** | 22 files | `agent.py`, `baseline.py`, `research/strategies/*`, `research/engine/*` | Full SHA-256 validation enforced |
| **Research Manifests** | 41 files | Machine-readable manifests in [`research/manifests/`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/manifests) | Full SHA-256 validation enforced |
| **Research Evidence Files** | 18 files | Baseline inventories, test logs, soak summaries | Full SHA-256 validation enforced |
| **Governance Reports** | 11 files | Markdown governance reports V21 through V28 | LF-normalized text integrity |
| **Regression Test Suites** | 39 files | Test modules in [`research/tests/`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/tests) | 381 tests certified |
| **Scratch Research Scripts** | 123 files | Full inventory in `scratch/` (44 tracked + 79 TrackB untracked/ignored) | Audited & classified in Map |
| **Market Data Caches** | 2 files | `tiingo_cache/tier1_bars.json` (12.5MB), `tier2_bars.json` (4.17MB) | Metadata-only inventory (No Tier 3) |
| **Request Ledgers** | 2 files | `tiingo_request_ledger.jsonl` (101 lines in V29A, 103 in TrackB preservation) | Append-only integrity |
| **Accidental Terminal Files** | 5 files | 5 clipped PowerShell command files in TrackB | Preserved in `research/evidence/v29a/` |

---

## 7. Evidence Manifest Directory Reference

All machine-readable inventories generated during Batch V29A are stored in [`research/evidence/v29a/`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a) and exclude sensitive raw bar content:

1. [`research/evidence/v29a/baseline_inventory_dual_workspace.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/baseline_inventory_dual_workspace.json) — Dual-workspace Git and file metadata.
2. [`research/evidence/v29a/scratch_audit_inventory.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/scratch_audit_inventory.json) — Comprehensive classification, AST imports, and dependencies for all 123 scratch files.
3. [`research/evidence/v29a/test_suite_381_classified_inventory.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/test_suite_381_classified_inventory.json) — Complete classification of all 381 collected regression tests across 6 evidence categories.
4. [`research/evidence/v29a/accidental_files_inventory.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/accidental_files_inventory.json) — Hashes, sizes, timestamps, and classifications of the 5 terminal artifacts.
5. [`research/evidence/v29a/tiingo_request_ledger_trackb_preservation.jsonl`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/tiingo_request_ledger_trackb_preservation.jsonl) — Byte-for-byte preservation of the 103-line TrackB ledger.


---

## 8. V29A-R Remediation Addendum & Inventory Erratum (2026-10-23T18:45:00+05:30)

### 8.1 Reconciliation of the 72-versus-75 Scratch File Discrepancy (Remediation 1)

In Section 2 of the initial V29A report, the summary row for untracked files in `Guardian-Alpha-TrackB` stated:
`Untracked Files: 77 files (5 root accidental + 72 scratch scripts)`.
Simultaneously, the machine manifest [`baseline_inventory_dual_workspace.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/baseline_inventory_dual_workspace.json) correctly recorded:
`"untracked_count": 80`.

#### Root Cause of the Discrepancy:
A rigorous path-by-path recount confirms the following exact inventory directly in `scratch/`:
- **Tracked in Git (`git ls-files scratch`):** **44 files** (all `.py`).
- **Untracked in Git (`git ls-files --others --exclude-standard scratch`):** **75 files** (comprising **67 `.py`** files + **8 `.txt`** files).
- **Ignored in Git (`git ls-files --others --ignored --exclude-standard scratch`):** **18 files** (comprising **4 `.json`** files directly under `scratch/` + **14 `.pyc`** bytecode files inside `scratch/__pycache__/`).
- **Total Physical Files in `scratch/` Root:** $44 + 75 + 4 = \mathbf{123\text{ files}}$.
- **Total Untracked Files Across Entire TrackB Repo:** $5\text{ (root accidental)} + 75\text{ (scratch)} = \mathbf{80\text{ files}}$.

The reported figure of "72 scratch scripts" in the initial prose table was a drafting clerical error where the 67 untracked `.py` files were inadvertently noted as 64 ($64 + 8 = 72$). The machine manifest and the 123-file AST audit in `scratch_audit_inventory.json` always contained all 75 untracked files. This erratum provides the definitive, path-verified reconciliation.

---

### 8.2 Evidential Standard on Tiingo Request Ledger Provenance (Remediation 2)

Section 4 established that the two additional SPY metadata requests (`2026-10-23T12:23:40Z` and `12:32:39Z`) in `tiingo_request_ledger.jsonl` matched the mock response payload in [`research/tests/test_v17_tiingo_qualification.py:169`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/tests/test_v17_tiingo_qualification.py#L169). Under V29A-R forensic standards, we rigorously distinguish matching payloads from conclusive proof:

1. **Physical Payload & Parameter Matching (High Evidential Weight):**
   - In `test_v17_tiingo_qualification.py`, `mock_resp.read.return_value = b'{"ticker": "SPY", "name": "SPDR S&P 500"}'`.
   - Length: exactly **41 bytes** (`len(payload_bytes) == 41`).
   - Endpoint: `"metadata"`, Symbol: `"SPY"`, Status: `200`.
   - In `tiingo_client.py:259`, `self.ledger.record(...)` records `data_size_bytes: len(payload_bytes)` directly to `research/manifests/tiingo_request_ledger.jsonl`.
   - The test mocked network I/O via `patch("urllib.request.urlopen")`, but critically **omitted mocking the filesystem ledger**.
   - A global regex search confirms that the exact 41-byte string `{"ticker": "SPY", "name": "SPDR S&P 500"}` exists **nowhere else** across the entire repository or scratch space.
2. **Limits of Conclusive Proof (Epistemic Boundary):**
   - Conclusive proof requires an OS-level process audit trail or stack trace linking the exact PID at `12:23:40Z` to the write syscall. Git and the append-only ledger record timestamps and payload parameters, not process execution trees.
   - Therefore, while the provenance is demonstrated with near-certainty based on unique payload characteristics and test isolation leakage, it is formally characterized as **conclusive circumstantial and parameter-matched proof**, not process-trace proof.
3. **Test Isolation Defect Confirmed:**
   - The root flaw is an architectural defect in test isolation: unit tests must never perform unmocked disk writes to persistent tracking manifests.

---

### 8.3 File-by-File Publication Safety Classification of V29A Evidence (Remediation 3)

The 11 files residing in [`research/evidence/v29a/`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a) have been audited against credential exposure, personal paths, raw vendor data, and terminal clutter:

| Relative File Path in `research/evidence/v29a/` | Size | Contents Summary | Personal Path? | Secrets / Raw Bars? | Publication Classification |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `scratch_audit_inventory.json` | 77.1 KB | AST imports, hashes, and classifications for 123 scratch files. | None | None | **SAFE TO COMMIT** |
| `test_suite_381_classified_inventory.json` | 166.2 KB | 381 tests classified across 6 integrity categories. | None | None | **SAFE TO COMMIT** |
| `test_suite_integrity_inventory.json` | 89.0 KB | Intermediate AST function parse list (superfluous draft). | None | None | **LOCAL ONLY** |
| `baseline_inventory_dual_workspace.json` | 11.0 KB | Worktree comparison metadata containing absolute machine paths. | Yes (`C:\Users\Manish\...`) | None | **LOCAL ONLY** |
| `accidental_files_inventory.json` | 1.7 KB | Metadata of accidental files; contains clipped path filename. | Yes (in filename) | None | **LOCAL ONLY** |
| `tiingo_request_ledger_trackb_preservation.jsonl`| 31.3 KB | Forensic backup of 103-line TrackB ledger. | None | None | **LOCAL ONLY** |
| `accidental_terminal_files/preserved_accidental_file_1.txt` | 1.4 KB | Clipped PowerShell diff output (whitespace warnings). | None | None | **LOCAL ONLY** |
| `accidental_terminal_files/preserved_accidental_file_2.txt` | 1.4 KB | Clipped PowerShell diff output (whitespace warnings). | None | None | **LOCAL ONLY** |
| `accidental_terminal_files/preserved_accidental_file_3.txt` | 15.9 KB | Clipped `less` pager manual. | None | None | **LOCAL ONLY** |
| `accidental_terminal_files/preserved_accidental_file_4.txt` | 1.7 KB | Clipped `less` pager manual. | None | None | **LOCAL ONLY** |
| `accidental_terminal_files/preserved_accidental_file_5.txt` | 3.3 KB | Clipped `less` pager manual. | None | None | **LOCAL ONLY** |

**Summary:** Only `scratch_audit_inventory.json` and `test_suite_381_classified_inventory.json` are safe for public version control. The remaining 9 files are **LOCAL ONLY** audit evidence and must be excluded from Git staging.
