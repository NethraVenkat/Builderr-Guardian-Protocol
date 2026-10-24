# GUARDIAN ALPHA — V29D: SNAPSHOT CONTENT AUDIT

**Audit Phase:** Batch V29D: Public Snapshot Validation & Release Security Gate  
**Auditor:** Senior Git Release Engineer, Supply-Chain Security Auditor & Research Governance Specialist  
**Date:** 2026-10-24  
**Starting Branch:** `research/v29d-public-snapshot-validation`  
**Starting HEAD Commit:** `d3a9ae8c2bf17c1fbff0833ba1ba2dd24cc80e6c`  
**Protected Checkpoints:**
- V28 Baseline: `8c77fddf72398b2e016a6f212d067c8aeb2b385e`
- V29A Baseline: `4567f4fe85dbce598477628ca8355a76356a8cf7`
- V29B Baseline: `fd829eff562cebe603b310db2a708b1b3c77999d`
- V29C Baseline: `d3a9ae8c2bf17c1fbff0833ba1ba2dd24cc80e6c`
**Worktree:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29B`  

---

## 1. Executive Summary

In fulfillment of Batch V29D Objective A, an independent, adversarial audit of the V29C public release documentation, allowlists, and transitive import graphs was performed. The objective was to verify that every allowlisted file exists, matches intended source revisions, introduces no proprietary data, and possesses complete dependency closure without wildcard or directory-wide checkouts.

### Key Audit Findings
1. **Dependency Gap 1 (Transitive Base Runner Files):** The V29C allowlist omitted `preview.py`, `sample_regimes.json.gz`, and `release-manifest.sha256`. While already present on `origin/main`, omitting them from standalone candidate exports causes `tests/test_e0_release.py` to fail during collection.
2. **Dependency Gap 2 (Offline Soak Validator):** The test `research/tests/test_b2_soak_validation.py` imports `validate_soak_directory` from `research.scripts.validate_soak_run`. Because `validate_soak_run.py` was omitted from the V29C allowlist, test collection aborted with `ModuleNotFoundError: No module named 'research.scripts'`. Auditing `validate_soak_run.py` confirmed it is an offline, non-proprietary diagnostic utility (10,951 bytes, zero vendor data, zero secrets) that is safe for public inclusion.
3. **Sanitization Requirements:** Two files require sanitized public variants:
   - `research/tests/test_v16_procurement_preflight.py`: Line 39 contains a local machine path (`C:/Users/Manish/...`) that must be converted to a repository-relative path.
   - `tests/test_e0_release.py`: Line 193 requires the cross-platform `pytest.approx(..., rel=1e-12, abs=1e-12)` tolerance from commit `228d48b` to prevent false failures under Windows MSVC IEEE 754 summation.

---

## 2. Hardened Public Snapshot File Inventory (69 Approved Files)

Every file in the candidate public release is enumerated individually below. Zero directory checkouts and zero wildcards are permitted.

### 2.1 Strategy, Config & Base Infrastructure (17 Files)
| File Relative Path | Size (Bytes) | Source Revision | Cryptographic Role / Description |
| :--- | :---: | :---: | :--- |
| `agent.py` | 13,388 | `fd829ef` | Frozen E0 production strategy (SHA: `46e68dc9...`) |
| `universe.json` | 1,411 | `fd829ef` | 24-instrument production universe specification |
| `requirements.txt` | 42 | `ac733ec` | Core runtime dependencies |
| `requirements-test.txt` | 39 | `ac733ec` | Testing framework dependencies (`pytest`, `numpy`) |
| `.gitignore` | 148 | `fd829ef` | Excludes `tiingo_cache/`, `*.pyc`, `.pytest_cache/` |
| `.gitattributes` | 374 | `ac733ec` | Enforces LF line-ending normalization |
| `LICENSE` | 1,065 | `ac733ec` | Open-source software distribution license |
| `README.md` | 13,030 | `ac733ec` | Sanitized public project overview |
| `START_HERE.md` | 3,580 | `ac733ec` | Quickstart guide for public researchers |
| `RELEASE.md` | 7,479 | `ac733ec` | Public release notes and checksum ledger |
| `RELEASE-AUDIT.md` | 10,216 | `ac733ec` | Gated release audit and provenance terms |
| `AGENT_BRIEF.md` | 6,376 | `ac733ec` | Architectural specification of strategy agent |
| `ANATOMY.md` | 4,467 | `ac733ec` | System layout and modular architecture |
| `SUBMISSION.md` | 9,148 | `ac733ec` | Verified competition submission metadata |
| `preview.py` | 8,947 | `ac733ec` | Admission regime runner and metrics tracer |
| `sample_regimes.json.gz` | 412,567 | `ac733ec` | Synthetic multi-regime market fixtures |
| `release-manifest.sha256` | 1,228 | `228d48b` | Master SHA-256 integrity ledger for release files |

### 2.2 Quantitative Engineering Engine (`research/engine/` — 15 Files)
| File Relative Path | Size (Bytes) | Source Revision | Cryptographic Role / Description |
| :--- | :---: | :---: | :--- |
| `research/engine/__init__.py` | 1,193 | `fd829ef` | Module namespace export |
| `research/engine/accounting.py` | 22,805 | `fd829ef` | Double-entry portfolio state and cash tracking |
| `research/engine/benchmark.py` | 5,486 | `fd829ef` | Benchmark metrics (SPY/QQQ beta & tracking) |
| `research/engine/corporate_actions.py` | 12,450 | `fd829ef` | Cash dividend settlement and split adjustments |
| `research/engine/event_verifier.py` | 10,922 | `fd829ef` | Dynamic order verifier & canonical hasher |
| `research/engine/independent_accounting.py` | 18,762 | `fd829ef` | Secondary independent audit accounting engine |
| `research/engine/ingestion.py` | 7,833 | `fd829ef` | Market data schema normalization & parsing |
| `research/engine/provider.py` | 7,128 | `fd829ef` | Abstract market data provider interface |
| `research/engine/quality.py` | 8,605 | `fd829ef` | Data quality, gap detection, outlier controls |
| `research/engine/replay.py` | 13,649 | `fd829ef` | Chronological multi-asset backtest replay engine |
| `research/engine/report_consistency_checker.py` | 33,295 | `fd829ef` | Table and reporting arithmetic verification |
| `research/engine/stress.py` | 18,576 | `fd829ef` | Transaction cost stress scenarios (slippage/fee)|
| `research/engine/tiingo_client.py` | 24,693 | `fd829ef` | API client with rate limiting & ledger interface |
| `research/engine/validation.py` | 6,862 | `fd829ef` | Order constraint and sanity validation |
| `research/engine/walk_forward.py` | 6,472 | `fd829ef` | Walk-forward window slicing & robustness checks |

### 2.3 Research Strategy Candidates (`research/strategies/` — 5 Files)
| File Relative Path | Size (Bytes) | Source Revision | Cryptographic Role / Description |
| :--- | :---: | :---: | :--- |
| `research/strategies/__init__.py` | 238 | `fd829ef` | Module namespace export |
| `research/strategies/candidate_alpha.py` | 4,925 | `fd829ef` | Baseline Alpha candidate |
| `research/strategies/loss_reduction_candidates.py` | 14,428 | `fd829ef` | Loss mitigation candidate family |
| `research/strategies/v11_candidates.py` | 25,205 | `fd829ef` | Multi-hypothesis candidate implementations |
| `research/strategies/v12_candidate_ae.py` | 8,459 | `fd829ef` | Frozen Candidate A+E Combined (Research Standard) |

### 2.4 Diagnostic Script (`research/scripts/` — 1 File)
| File Relative Path | Size (Bytes) | Source Revision | Cryptographic Role / Description |
| :--- | :---: | :---: | :--- |
| `research/scripts/validate_soak_run.py` | 10,951 | `fd829ef` | Offline soak test validator (dependency of `test_b2_soak`) |

### 2.5 Safe Universe Manifest (`research/manifests/` — 1 File)
| File Relative Path | Size (Bytes) | Source Revision | Cryptographic Role / Description |
| :--- | :---: | :---: | :--- |
| `research/manifests/production_universe_manifest.json` | 11,492 | `fd829ef` | 24-instrument metadata specification (zero prices) |

### 2.6 Standalone Public Test Suite (28 Files — 253 Tests)
| File Relative Path | Size (Bytes) | Tests | Verified Role / Invariant Verified |
| :--- | :---: | :---: | :--- |
| `tests/test_e0_release.py` (sanitized) | 8,947 | 56 | Verifies agent across admission regimes |
| `tests/e0_expected.json` | 1,479 | Fixture | Expected performance metrics for admission tests |
| `research/tests/test_b2_benchmark.py` | 3,124 | 1 | Benchmark tracking error and beta calculation |
| `research/tests/test_b2_causality_integrity.py` | 4,210 | 5 | Strict lookahead bias and causality controls |
| `research/tests/test_b2_financial_accounting.py` | 6,842 | 7 | Realized/unrealized PnL decomposition |
| `research/tests/test_b2_financial_corner_cases.py` | 8,912 | 10 | Zero price, negative cash, and corporate actions |
| `research/tests/test_b2_ingestion_quality.py` | 11,240 | 12 | Data quality anomaly detection |
| `research/tests/test_b2_leveraged_overlay.py` | 5,420 | 5 | SSO/QLD leveraged ETF exposure dynamics |
| `research/tests/test_b2_loss_reduction.py` | 4,890 | 5 | Loss reduction candidate mechanics |
| `research/tests/test_b2_replay_independence.py` | 4,110 | 5 | Determinism and seed independence of replay |
| `research/tests/test_b2_risk_enforcement.py` | 5,980 | 6 | Hard risk enforcement boundary testing |
| `research/tests/test_b2_soak_validation.py` | 5,310 | 6 | Long-duration soak test stability validation |
| `research/tests/test_b2_storage_compliance.py` | 14,210 | 18 | Storage hygiene and write safety |
| `research/tests/test_b2_trading_stress.py` | 21,450 | 26 | Behavior under severe slippage and fee stress |
| `research/tests/test_b2_walk_forward.py` | 4,870 | 5 | Walk-forward window slicing mechanics |
| `research/tests/test_baseline_parity.py` | 2,980 | 3 | Replay engine parity against baseline implementation|
| `research/tests/test_corporate_actions.py` | 3,890 | 4 | Stock splits, cash dividend reinvestment, settlement|
| `research/tests/test_provider_compliance.py` | 3,650 | 4 | Data ingestion compliance and schema validation |
| `research/tests/test_replay_accounting.py` | 4,780 | 5 | Double-entry cash/asset conservation during simulation|
| `research/tests/test_risk_limits.py` | 2,890 | 3 | Gross leverage, concentration, cash overdraft limits|
| `research/tests/test_validation.py` | 6,450 | 8 | Fail-closed input validation and error handling |
| `research/tests/test_v11_candidates.py` | 18,920 | 23 | Track B Stage V11 candidate parameter sweeps |
| `research/tests/test_v12_candidate_ae_conflicts.py`| 9,120 | 10 | Structural candidate invariants |
| `research/tests/test_v13_historical_qualification.py`| 8,450 | 9 | Slippage dollar adjustments & universe validation |
| `research/tests/test_v14_financial_forensics.py` | 4,920 | 5 | Forensic accounting invariants |
| `research/tests/test_v15_evidence_gates.py` | 3,890 | 4 | Research governance gate validation |
| `research/tests/test_v16_procurement_preflight.py` (sanitized)| 4,120 | 4 | Preflight schema and provider horizon checks |
| `research/tests/test_v18_authentic_tier1.py` | 3,780 | 4 | Point-in-time causality and holdout firewall |

---

## 3. Machine-Readable Snapshot Inventory Generation

An exact, machine-readable snapshot inventory was generated and verified at:
`scratch/v29d_simulated_public_snapshot/v29d_snapshot_manifest_inventory.json`

This inventory records:
- Exact relative repository path for each of the 69 files.
- Exact byte size.
- Pre-sanitization SHA-256.
- Post-sanitization SHA-256.
- Explicit boolean flag recording sanitization state.
