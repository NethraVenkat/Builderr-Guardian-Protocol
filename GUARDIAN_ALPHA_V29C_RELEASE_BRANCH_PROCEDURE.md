# GUARDIAN ALPHA — V29C: RELEASE BRANCH PROCEDURE

**Audit Phase:** Batch V29C: Publication Safety & Release Snapshot Audit
**Auditor:** Senior Git Release Engineer & Quantitative Systems Auditor
**Date:** 2026-10-23
**Status:** **HUMAN-ONLY EXECUTION RUNBOOK (DO NOT EXECUTE AUTOMATICALLY)**
**Target Public Base:** `origin/main` (`ac733ecddee59f62ffc4a7514767f57c3e716632`)
**Source Research Branch:** `research/v29c-publication-safety` (`fd829eff562cebe603b310db2a708b1b3c77999d`)

---

## 1. Architectural Rationale: Why History Isolation is Mandatory

In Git, a commit object points to a directory tree and one or more parent commits. If a new branch is created from `research/v29c-publication-safety` and pushed to GitHub:
1. Every historical commit in the 49-commit chain (`origin/main..HEAD`) is transmitted to the remote server.
2. Even if a subsequent commit executes `git rm research/manifests/tier1_aapl_nvda_position_history.json`, blob `6c1fdda3def689b67a358659b91a8b4c990fe907` remains permanently accessible in the commit history of `33cfed9`. Anyone cloning the repository can check out commit `33cfed9` and extract the 979 KB of raw commercial price data.
3. Attempting to rewrite history via `git filter-repo`, `git rebase -i`, or BFG destroys the SHA-1/SHA-256 commit hashes of the protected baselines (`8c77fdd`, `4567f4f`, `fd829ef`), violating the core governance invariants.

### The Solution: Non-Destructive Base-Derived Release Branch
The publication branch must be constructed as a **new branch derived directly from `origin/main`**, importing only approved files from the Public Snapshot Allowlist into a clean working tree. This guarantees:
- **Zero History Inheritance:** The public branch contains only `origin/main` commits plus the clean release commit. It does not inherit commit `33cfed9` (V21) or `fd829ef` (V29B).
- **Zero Historical Mutation:** The private research branches (`track-b-v28`, `v29a`, `v29b`, `v29c`) remain 100% untouched, preserving all original forensic evidence, raw manifests, and audit reports.

```
[Clean Upstream Base]
origin/main (ac733ec) ──────────────────────────► release/v29c-clean-publication (New Clean Release Commit)
   │                                                 ▲
   │ (49 Research Commits)                           │ (Selective Import of Allowlisted Files)
   ▼                                                 │
research/v29c-publication-safety (fd829ef) ──────────┘
[Private Research History Preserved Intact]
```

---

## 2. Step-by-Step Human-Only Execution Runbook

> [!IMPORTANT]
> All Git commands below must be executed exclusively by the human repository owner in a clean terminal. The AI agent is strictly forbidden from executing branch creation, checkouts, staging, commits, or pushes.

### Step 1: Verify Starting State & Clean Worktree
Ensure no uncommitted changes exist in the working directory:
```powershell
cd C:\Users\Manish\Downloads\Guardian-Alpha-V29B
git status
# Confirm working tree clean (or only untracked local audit files present)
```

### Step 2: Create Clean Release Branch from `origin/main`
Branch directly from the public base commit:
```powershell
git checkout -b release/v29c-clean-publication origin/main
git rev-parse HEAD
# Output MUST be: ac733ecddee59f62ffc4a7514767f57c3e716632
```

### Step 3: Selectively Import Allowlisted Files (Exact File-by-File Enumeration)
Bring in ONLY explicitly approved files from `research/v29c-publication-safety`.
**CRITICAL MANDATE: Zero directory imports (`research/engine/`) and zero wildcards (`test_*.py`) are permitted.** Every file is enumerated individually:

```powershell
# 1. Quantitative Engine (15 files explicitly checked out)
git checkout research/v29c-publication-safety -- research/engine/__init__.py
git checkout research/v29c-publication-safety -- research/engine/accounting.py
git checkout research/v29c-publication-safety -- research/engine/benchmark.py
git checkout research/v29c-publication-safety -- research/engine/corporate_actions.py
git checkout research/v29c-publication-safety -- research/engine/event_verifier.py
git checkout research/v29c-publication-safety -- research/engine/independent_accounting.py
git checkout research/v29c-publication-safety -- research/engine/ingestion.py
git checkout research/v29c-publication-safety -- research/engine/provider.py
git checkout research/v29c-publication-safety -- research/engine/quality.py
git checkout research/v29c-publication-safety -- research/engine/replay.py
git checkout research/v29c-publication-safety -- research/engine/report_consistency_checker.py
git checkout research/v29c-publication-safety -- research/engine/stress.py
git checkout research/v29c-publication-safety -- research/engine/tiingo_client.py
git checkout research/v29c-publication-safety -- research/engine/validation.py
git checkout research/v29c-publication-safety -- research/engine/walk_forward.py

# 2. Research Strategy Implementations (5 files explicitly checked out)
git checkout research/v29c-publication-safety -- research/strategies/__init__.py
git checkout research/v29c-publication-safety -- research/strategies/candidate_alpha.py
git checkout research/v29c-publication-safety -- research/strategies/loss_reduction_candidates.py
git checkout research/v29c-publication-safety -- research/strategies/v11_candidates.py
git checkout research/v29c-publication-safety -- research/strategies/v12_candidate_ae.py

# 3. Pure Standalone Public Test Suite (24 test modules explicitly checked out)
git checkout research/v29c-publication-safety -- research/tests/test_b2_benchmark.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_causality_integrity.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_financial_accounting.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_financial_corner_cases.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_ingestion_quality.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_leveraged_overlay.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_loss_reduction.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_replay_independence.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_risk_enforcement.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_soak_validation.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_storage_compliance.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_trading_stress.py
git checkout research/v29c-publication-safety -- research/tests/test_b2_walk_forward.py
git checkout research/v29c-publication-safety -- research/tests/test_baseline_parity.py
git checkout research/v29c-publication-safety -- research/tests/test_corporate_actions.py
git checkout research/v29c-publication-safety -- research/tests/test_provider_compliance.py
git checkout research/v29c-publication-safety -- research/tests/test_replay_accounting.py
git checkout research/v29c-publication-safety -- research/tests/test_risk_limits.py
git checkout research/v29c-publication-safety -- research/tests/test_v11_candidates.py
git checkout research/v29c-publication-safety -- research/tests/test_v12_candidate_ae_conflicts.py
git checkout research/v29c-publication-safety -- research/tests/test_v13_historical_qualification.py
git checkout research/v29c-publication-safety -- research/tests/test_v14_financial_forensics.py
git checkout research/v29c-publication-safety -- research/tests/test_v15_evidence_gates.py
git checkout research/v29c-publication-safety -- research/tests/test_v16_procurement_preflight.py
git checkout research/v29c-publication-safety -- research/tests/test_v18_authentic_tier1.py
git checkout research/v29c-publication-safety -- research/tests/test_validation.py

# 4. Safe Universe Manifest (1 file containing instrument metadata, zero market bars)
git checkout research/v29c-publication-safety -- research/manifests/production_universe_manifest.json

# 5. Core Configuration & Environment Declarations (4 files)
git checkout research/v29c-publication-safety -- universe.json
git checkout research/v29c-publication-safety -- requirements.txt
git checkout research/v29c-publication-safety -- requirements-test.txt
git checkout research/v29c-publication-safety -- .gitignore
```

### Step 4: Sanitize Local Machine Paths & Float Comparisons
1. In `research/tests/test_v16_procurement_preflight.py`: Ensure line 39 uses a portable relative path instead of any hardcoded developer directory.
2. In `tests/test_e0_release.py`: Verify `pytest.approx(..., rel=1e-12, abs=1e-12)` is utilized so historical metric assertions pass across Windows, macOS, and Linux without IEEE 754 summation discrepancies.

### Step 5: Verification of Staged Files vs Restricted Blobs
Run an explicit check confirming that zero restricted blobs or unallowlisted directories are staged:
```powershell
# 1. Verify restricted manifests and directories are NOT staged
git status --porcelain | Select-String "tier1_aapl_nvda_position_history"
git status --porcelain | Select-String "v29b_method_a_order_event_trace"
git status --porcelain | Select-String "tiingo_request_ledger"
git status --porcelain | Select-String "scratch"
git status --porcelain | Select-String "research/evidence"
# Expected output: EMPTY (No matches)

# 2. Run standalone public tests on the staged files
python -m pytest tests/test_e0_release.py -v
python -m pytest research/tests -q
# Expected output: 197 research tests + 56 release tests passed cleanly
```

### Step 6: Commit Public Snapshot Using Authentic Human Committer Configuration
Execute the commit using standard Git identity. **Do NOT use fabricated `--author` overrides:**
```powershell
# Ensure your legitimate human/organizational committer identity is configured
# git config user.name "Your Name or Sanctioned Entity"
# git config user.email "your.email@domain.com"

# Commit without fabricated author spoofing
git commit -m "feat(release): publish Guardian Alpha quantitative engine and independent verification suite"
```

### Step 7: Cryptographic Outgoing Object Verification (Mandatory Gate)
Verify the exact objects introduced between `origin/main` and the new release commit. Execute this Python verification script:

```powershell
python -c "
import subprocess, sys

# Prohibited blob hashes (raw bars, reconstructable traces, API ledgers)
BANNED_BLOBS = {
    '6c1fdda3def689b67a358659b91a8b4c990fe907': 'tier1_aapl_nvda_position_history.json',
    'c19ddb8b506cf9c2f6899e2a327d25a14f07f50d': 'v29b_method_a_order_event_trace.json',
    '2e5fda61edfefec48c021f6fcfafa188eee4e6de': 'tiingo_request_ledger.jsonl',
    '81701c878f9fb3532139b6a2b66d61ee01749865': 'tier1_terminal_holdings_v20.json',
    '1e072d2cbd4b935890dc11db474fcf897b1684e9': 'tier1_terminal_holdings_v22.json',
    'a8657aafd9db41359642c756c1cb3e6c752d1838': 'tier2_terminal_holdings.json',
}

objects = subprocess.check_output(['git', 'rev-list', '--objects', 'origin/main..HEAD'], text=True).strip().split('\n')
violations = []
for line in objects:
    if not line:
        continue
    sha = line.split()[0]
    if sha in BANNED_BLOBS:
        violations.append((sha, BANNED_BLOBS[sha], line))

if violations:
    print('SECURITY VIOLATION: Banned blobs detected in outgoing history:')
    for sha, name, l in violations:
        print(f'  {sha} -> {name} ({l})')
    sys.exit(1)
else:
    print(f'AUDIT PASS: Zero banned blobs found across {len(objects)} outgoing objects.')
"
# Expected output: AUDIT PASS: Zero banned blobs found...
```

### Step 8: Safe Remote Publication (Human Discretion Only)
Only after Steps 1 through 7 pass without warnings may the human owner push the new clean release branch to GitHub:
```powershell
# Push ONLY the release branch (NEVER push research branches)
git push origin release/v29c-clean-publication
```
# Push ONLY the release branch (NEVER push research branches)
git push origin release/v29c-clean-publication
```
