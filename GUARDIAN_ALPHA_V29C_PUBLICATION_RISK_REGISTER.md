# GUARDIAN ALPHA — V29C: PUBLICATION RISK REGISTER

**Audit Phase:** Batch V29C: Publication Safety & Release Snapshot Audit
**Auditor:** Independent Quantitative Research Governance Specialist & Release Engineer
**Date:** 2026-10-23
**Audited History Scope:** `origin/main` (`ac733ecddee59f62ffc4a7514767f57c3e716632`) to `HEAD` (`fd829eff562cebe603b310db2a708b1b3c77999d`)
**Commit Range:** 49 linear research commits (Track B / V12 through V29B)
**Total Objects Audited:** 3,461 Git objects (2,006 blobs, 765 trees, 689 commits)
**Active Worktree:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29B`
**Current Branch:** `research/v29c-publication-safety`

---

## 1. Executive Summary

This Publication Risk Register provides an exhaustive, forensic security and intellectual property audit of all Git objects, commits, and tree states reachable from `HEAD`. The objective of this audit is to identify every artifact whose public exposure on a remote hosting provider (e.g., GitHub) would violate commercial data redistribution licenses, disclose private developer identity / machine configurations, compromise security credentials, or distribute uncurated experimental scratch code.

### Summary of Major Risk Findings
1. **Commercial Data Breach Hazard (Critical):** The Git history contains 979,544 bytes of daily raw OHLCV market bars for Apple and Nvidia across 2015–2019 committed in `research/manifests/tier1_aapl_nvda_position_history.json` (commit `33cfed9`). Pushing this blob to a public repository breaches the commercial Tiingo Terms of Service.
2. **Reconstructable Market Data Hazard (High):** The Git history contains 702,093 bytes of order execution events in `research/manifests/v29b_method_a_order_event_trace.json` (commit `fd829ef`). Inverting the recorded fill prices and effective slippage bps allows deterministic mathematical reconstruction of point-in-time vendor prices for 24 universe assets.
3. **Developer Identity & Private Path Exposure (High):** All 49 outgoing research commits on `origin/main..HEAD` carry personal developer committer metadata (`manishrahul1705 <manishrahul1705@gmail.com>`). Additionally, 22 committed markdown audit reports contain local Windows filesystem paths (`C:\Users\Manish\...`), and `research/tests/test_v16_procurement_preflight.py` hardcodes a local directory path.
4. **Secret Scanning Verification (Clean / Synthetic Mocks Only):** Zero live API tokens, passwords, or production secrets exist in the repository. All flagged token strings in test modules are synthetic dummy strings used for redaction testing. However, high-entropy synthetic strings will trigger automated GitHub secret scanners if pushed without suppression.
5. **Git History Immutability Invariant:** Because Git commit hashes are cryptographically chained, deleting restricted files in a new commit does **not** remove the blobs from repository history. Pushing `research/v29c-publication-safety` directly to GitHub would expose all 49 commits and their restricted blobs.

---

## 2. Granular High-Risk Artifact Register

| Artifact Path | Git Blob Hash | File Size | Intro Commit | Risk Class | Severity | Publication Clearance |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| `research/manifests/tier1_aapl_nvda_position_history.json` | `6c1fdda3de` | 979,544 B | `33cfed9` (v21) | Raw Licensed Market Data | **CRITICAL** | **BLOCKED** |
| `research/manifests/v29b_method_a_order_event_trace.json` | `c19ddb8b50` | 702,093 B | `fd829ef` (v29b) | Reconstructable Vendor Prices | **HIGH** | **REQUIRES REVIEW** |
| `research/manifests/tiingo_request_ledger.jsonl` | `2e5fda61ed` | 30,743 B | `41f1f3d` (B2-I) | Proprietary Request Telemetry | **MEDIUM** | **BLOCKED** |
| `research/manifests/tier1_terminal_holdings_v20.json` | `81701c878f` | 27,796 B | `ef4de09` (v20) | Point-in-Time Close Prices | **MEDIUM** | **REQUIRES REVIEW** |
| `research/manifests/tier1_terminal_holdings_v22.json` | `1e072d2cbd` | 6,473 B | `4ad43d5` (v22) | Point-in-Time Close Prices | **MEDIUM** | **REQUIRES REVIEW** |
| `research/manifests/tier2_terminal_holdings.json` | `a8657aafd9` | 5,290 B | `6d21c4f` (v23) | Point-in-Time Close Prices | **MEDIUM** | **REQUIRES REVIEW** |
| `research/manifests/tier1_corporate_actions_inventory.json` | `e0fe6abf5b` | 844 B | `33cfed9` (v21) | Vendor Corporate Action Data | **LOW** | **REQUIRES REVIEW** |
| `research/manifests/tier2_corporate_actions_inventory.json` | `a90c648839` | 26,664 B | `6d21c4f` (v23) | Vendor Corporate Action Data | **MEDIUM** | **REQUIRES REVIEW** |
| `research/evidence/v29a/test_suite_381_classified_inventory.json` | `914df6deca` | 166,193 B | `4567f4f` (v29a) | Internal Forensic Audit Bloat | **MEDIUM** | **LOCAL ONLY** |
| `research/evidence/v29a/scratch_audit_inventory.json` | `dcf7b3b9a4` | 77,072 B | `4567f4f` (v29a) | Internal Forensic Audit Bloat | **MEDIUM** | **LOCAL ONLY** |
| `research/evidence/v29b/test_suite_400_classified_inventory.json` | `560c718145` | 174,263 B | Untracked (local) | Internal Forensic Audit Bloat | **MEDIUM** | **LOCAL ONLY** |
| `research/evidence/soak/soak_telemetry.jsonl` | `da7c032646` | 7,902 B | `8234336` (G1-G9) | Operational Runtime Telemetry | **LOW** | **LOCAL ONLY** |
| `scratch/` (44 tracked exploration scripts) | Various | ~215,000 B | `700276f` / `cc82d0e` | Uncurated Exploratory Code | **LOW-MED** | **LOCAL ONLY** |
| `GUARDIAN_ALPHA_V21` through `V29B` (12 Master Reports) | Various | ~340,000 B | `16be2a2` to `fd829ef` | Personal Paths (`C:\Users\...`) | **HIGH** | **REQUIRES REVIEW** |
| `research/tests/test_v16_procurement_preflight.py` | `9280dbe459` | 6,561 B | `e18f6bc` (v16) | Machine Path (`C:/Users/Manish`) | **MEDIUM** | **REQUIRES REVIEW** |
| `tiingo_cache/` (`tier1_bars.json`, `tier2_bars.json`) | Disk only | 16,667,737 B | Git-Ignored | Proprietary Commercial Bars | **CRITICAL** | **BLOCKED (GITIGNORE)** |

---

## 3. Forensic Deep Dive into Primary Risk Blobs

### 3.1 `research/manifests/tier1_aapl_nvda_position_history.json`
- **Blob Object:** `6c1fdda3def689b67a358659b91a8b4c990fe907`
- **Introduction Commit:** `33cfed953d7917bd85f3114c13746f10e17c3614` (`feat(v21): portfolio concentration forensics...`)
- **Forensic Content:** Contains 1,258 daily trading entries from `2015-01-02` to `2019-12-31`. Each record contains daily raw close prices for `AAPL` and `NVDA` alongside share counts, cost basis, market value, and orders.
- **Licensing Constraint:** Under the Tiingo Commercial Subscription and Developer Agreement, redistribution of raw, daily end-of-day market price series to third parties or via public internet repositories is strictly forbidden.
- **Remediation:** Must be **excluded** from any public snapshot. The blob must not exist in any commit reachable from a public branch.

### 3.2 `research/manifests/v29b_method_a_order_event_trace.json`
- **Blob Object:** `c19ddb8b506cf9c2f6899e2a327d25a14f07f50d`
- **Introduction Commit:** `fd829eff562cebe603b310db2a708b1b3c77999d` (`feat(v29b): certify evidence-derived execution verification...`)
- **Forensic Content:** 828 detailed order execution events across Scenario 3 and Scenario 4. Each event contains:
  ```json
  {
    "date": "2020-01-02",
    "ticker": "SPY",
    "side": "BUY",
    "requested_qty": 35.0,
    "filled_qty": 35.0,
    "open_price": 323.54,
    "fill_price": 324.34885,
    "effective_slippage_bps": 25.0,
    "commission_paid": 0.0,
    "notional_executed": 11352.20975
  }
  ```
- **Price Reconstructability:** For all 828 orders across 2020 and 2021, an observer can reconstruct unadjusted market prices by inverting the documented execution formula:
  $$\text{open\_price} = \frac{\text{fill\_price}}{1 \pm (\text{effective\_slippage\_bps} \times 10^{-4})}$$
- **Remediation:** While useful for internal research audit, distributing reconstructable market prices poses commercial licensing exposure. Excluded from public snapshot. Public verification is achieved via independent mathematical tests and user-provided market data.

### 3.3 `research/manifests/tiingo_request_ledger.jsonl`
- **Blob Object:** `2e5fda61edfefec48c021f6fcfafa188eee4e6de`
- **Introduction Commit:** `41f1f3d` (`feat(research): implement Stage B2-I authentic Tiingo Tier 1 acquisition...`)
- **Forensic Content:** 101 recorded JSON lines documenting exact API call telemetry, epoch timestamps, symbols, record counts, and byte sizes.
- **Risk Assessment:** While tokens and query authentication parameters are redacted, public release discloses internal API request cadences and infrastructure telemetry. Excluded from public release.

### 3.4 Personal Windows Paths & Developer PII
- **Committer Identity:** All 49 research commits are authored by `manishrahul1705 <manishrahul1705@gmail.com>`.
- **Filesystem Paths:** 22 markdown audit documents contain embedded links to `C:\Users\Manish\Downloads\...` and internal agent task logs in `C:\Users\Manish\.gemini\...`.
- **Unit Test Path:** In `research/tests/test_v16_procurement_preflight.py` (line 39):
  ```python
  clean_clone_path = Path("C:/Users/Manish/Downloads/Guardian-Alpha-Clean-Clone-V15")
  ```
- **Remediation:**
  1. Public release commits must be authored by the sanctioned organizational entity (`Builderr Quantitative Researcher <researcher@builderr.local>`).
  2. Public test suites must use dynamic relative paths (`Path(__file__).resolve().parents[...]`).
  3. Master internal research reports remain in the private research repository; public documentation is replaced by sanitized release documentation.

### 3.5 Secret Scanning Findings & False-Positive Analysis
- **Scanned Files:** 260 tracked files across all 49 outgoing commits.
- **Identified Keyword Matches:** 49 lines across 5 test files contained `"api_token"`, `"tiingo_token"`, or `"secret_key"`.
- **Forensic Verification:** 100% of matches are synthetic mock strings:
  - `"valid_secret_token_abc123"`
  - `"secret_tiingo_token_12345"`
  - `"secret_tiingo_api_token_xyz999"`
  - `"secret_tiingo_token_abcdef123456"`
  - `"mock_token"`
- **Live Secret Exposure:** **ZERO** live API tokens, passwords, private keys, or credentials were committed.
- **Public Risk:** Naive automated scanner tools (e.g., GitHub Secret Scanning, GitGuardian, Trufflehog) may flag high-entropy synthetic mock strings as potential credentials. Tests included in the public snapshot should annotate mock parameters clearly or use explicitly labeled mock tokens (e.g., `MOCK_TIINGO_TOKEN_FOR_TESTING_ONLY`).

### 3.6 Release Engineering Risks: Unsafe Wildcards & Fabricated Authors
- **Unsafe Wildcard & Directory Checkout Risk:** Utilizing bulk directory checkouts (e.g., `git checkout ... -- research/engine/`) or wildcards (e.g., `test_*.py`) risks accidentally importing untracked experimental files, unreviewed scripts, or cache-dependent test modules that reference proprietary data. To achieve airtight safety, every file in the public snapshot must be explicitly and individually enumerated by full path.
- **Author Identity Fabrication Risk:** Using command-line overrides such as `--author="Builderr Quantitative Researcher <researcher@builderr.local>"` fabricates committer identity and generates false git attribution. The public release commit must be authored using the authentic, human-controlled committer identity configured in the environment.

---

## 4. Classification Summary & Mandatory Action Plan

1. **Immediate Public Push Blocked:** Branch `research/v29c-publication-safety` must **never** be pushed to GitHub directly.
2. **Preserve Internal History:** All 49 research commits, manifests, scratch scripts, and evidence remain physically intact in the private research worktree.
3. **Clean Public Branch Architecture:** The public snapshot must be instantiated as an independent branch derived directly from `origin/main` (`ac733ec`), importing only files on the approved Public Snapshot Allowlist.
