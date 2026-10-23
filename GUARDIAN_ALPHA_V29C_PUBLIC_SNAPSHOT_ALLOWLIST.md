# GUARDIAN ALPHA — V29C: PUBLIC SNAPSHOT ALLOWLIST

**Audit Phase:** Batch V29C: Publication Safety & Release Snapshot Audit  
**Auditor:** Independent Quantitative Research Governance Specialist & Release Engineer  
**Date:** 2026-10-23  
**Target Repository:** Public Release Branch (`release/v29c-clean-publication`)  
**Base Commit Reference:** `origin/main` (`ac733ecddee59f62ffc4a7514767f57c3e716632`)  

---

## 1. Governance Principles for Public Allowlisting

In strict accordance with the V29C safety charter, a file is approved for public release only if it satisfies all seven release criteria:
1. **Zero Proprietary Market Data:** Contains no raw OHLCV market bars or reconstructable vendor price time-series.
2. **Zero Credentials or Secrets:** Contains no live API tokens, passwords, private keys, or unredacted authentication parameters.
3. **Machine Independence:** Contains no hardcoded personal filesystem paths (`C:\Users\...`) or machine-specific environment assumptions.
4. **Clean Licensing & Attribution:** Adheres to open-source licensing without infringing third-party terms of service (specifically Tiingo).
5. **Scientific Reproducibility:** Code and tests execute predictably and deterministically across standard operating systems (Linux, macOS, Windows).
6. **Curated Code Quality:** Contains production or formal research engine code; excludes uncurated scratch experiments and intermediate test artifacts.
7. **Complete Evidence Preservation in Private History:** Excluding a file from the public snapshot does **not** delete it; the complete unredacted research record remains permanently preserved in the internal Git history.

---

## 2. Approved Public Snapshot Allowlist

### 2.1 Core Strategy & Configuration (Root Files)
| File Path | Description | Public Release Role |
| :--- | :--- | :--- |
| `agent.py` | Frozen production strategy (Frozen E0 standard) | Core production agent submitted to competition |
| `universe.json` | 24-asset production universe specification | Defines eligible ETF & equity tickers |
| `requirements.txt` | Core runtime Python dependencies | Ensures reproducible environment installation |
| `requirements-test.txt` | Test suite dependencies (`pytest`, `numpy`, etc.) | Defines testing framework requirements |
| `.gitignore` | Git exclusion rules (`tiingo_cache/`, `*.pyc`, etc.) | Prevents accidental data commits |
| `.gitattributes` | Line-ending and binary tracking rules | Ensures cross-platform LF consistency |
| `LICENSE` | Open-source software license (MIT / Apache 2.0) | Formal legal distribution framework |

### 2.2 Quantitative Engineering & Replay Engine (`research/engine/`)
| File Path | Description | Public Release Role |
| :--- | :--- | :--- |
| `research/engine/__init__.py` | Package initializer | Module namespace export |
| `research/engine/accounting.py` | Double-entry portfolio accounting & cash tracking | Core portfolio state & transaction simulation |
| `research/engine/benchmark.py` | Benchmark comparison metrics (SPY/QQQ) | Relative performance evaluation |
| `research/engine/corporate_actions.py`| Cash dividends and stock split adjustments | Causal corporate action processing |
| `research/engine/event_verifier.py` | Dynamic order event verifier & canonical hasher | Independent verification of order manifests |
| `research/engine/independent_accounting.py`| Secondary independent accounting auditor | Double-entry invariant verification |
| `research/engine/ingestion.py` | Market data parsing and normalization | Input data validation pipeline |
| `research/engine/provider.py` | Abstract market data provider interface | Provider abstraction layer |
| `research/engine/quality.py` | Data hygiene, gap detection, outlier checks | Input quality controls |
| `research/engine/replay.py` | Chronological multi-asset backtest replay engine | Core simulation execution harness |
| `research/engine/report_consistency_checker.py` | Cross-report arithmetic & table validator | Ensures reporting arithmetic integrity |
| `research/engine/stress.py` | Transaction cost stress scenarios (slippage/fee)| Evaluates execution realism |
| `research/engine/tiingo_client.py` | Tiingo API client with rate limiting & ledger | API integration (requires user's own token) |
| `research/engine/validation.py` | Strategy output & constraint validation | Fail-closed execution gate |
| `research/engine/walk_forward.py` | Walk-forward optimization & out-of-sample split| Prevents in-sample overfitting |

### 2.3 Research Strategy Candidates (`research/strategies/`)
| File Path | Description | Public Release Role |
| :--- | :--- | :--- |
| `research/strategies/__init__.py` | Package initializer | Module namespace export |
| `research/strategies/candidate_alpha.py` | Baseline Alpha candidate | Historical candidate implementation |
| `research/strategies/loss_reduction_candidates.py` | Loss mitigation candidate family | Explores hedging and stop-loss logic |
| `research/strategies/v11_candidates.py` | Track B Stage V11 candidate family | Multi-hypothesis exploration |
| `research/strategies/v12_candidate_ae.py` | Frozen Candidate A+E Combined (Research Standard) | Primary research challenger tested vs E0 |

### 2.4 Standalone & Synthetic Public Test Suite (`tests/` & `research/tests/`)
All tests below execute independently using synthetic fixtures or mocked data without requiring proprietary vendor cache files:

| Test File Path | Verified Test Count | Methodological Role |
| :--- | :---: | :--- |
| `tests/test_e0_release.py` (with float approx fix) | 56 | Verifies frozen production agent against admission regimes |
| `tests/e0_expected.json` | Fixture | Expected performance metrics for admission tests |
| `research/tests/test_b2_benchmark.py` | 1 | Benchmark tracking error and beta computation |
| `research/tests/test_b2_causality_integrity.py` | 5 | Strict lookahead bias and causality controls |
| `research/tests/test_b2_financial_accounting.py` | 7 | Realized/unrealized PnL decomposition |
| `research/tests/test_b2_financial_corner_cases.py` | 10 | Zero price, negative cash, and corporate action edge cases |
| `research/tests/test_b2_ingestion_quality.py` | 12 | Data quality anomaly detection |
| `research/tests/test_b2_leveraged_overlay.py` | 5 | SSO/QLD leveraged ETF exposure dynamics |
| `research/tests/test_b2_loss_reduction.py` | 5 | Loss reduction candidate mechanics |
| `research/tests/test_b2_replay_independence.py` | 5 | Determinism and seed independence of replay |
| `research/tests/test_b2_risk_enforcement.py` | 6 | Hard risk enforcement boundary testing |
| `research/tests/test_b2_soak_validation.py` | 6 | Long-duration soak test stability |
| `research/tests/test_b2_storage_compliance.py` | 18 | Storage hygiene and write safety |
| `research/tests/test_b2_trading_stress.py` | 26 | Behavior under severe slippage and fee stress |
| `research/tests/test_b2_walk_forward.py` | 5 | Walk-forward window slicing mechanics |
| `research/tests/test_baseline_parity.py` | 3 | Replay engine parity against baseline implementation |
| `research/tests/test_corporate_actions.py` | 4 | Stock splits, cash dividend reinvestment, and settlement |
| `research/tests/test_provider_compliance.py` | 4 | Data ingestion compliance and schema validation |
| `research/tests/test_replay_accounting.py` | 5 | Double-entry cash/asset conservation during simulation |
| `research/tests/test_risk_limits.py` | 3 | Gross leverage, concentration, and cash overdraft limits |
| `research/tests/test_validation.py` | 8 | Fail-closed input validation and error handling |
| `research/tests/test_v11_candidates.py` | 23 | Track B Stage V11 candidate parameter sweeps |
| `research/tests/test_v12_candidate_ae_conflicts.py` | 10 | Structural candidate invariants |
| `research/tests/test_v13_historical_qualification.py` | 9 | Slippage dollar adjustments & universe validation |
| `research/tests/test_v14_financial_forensics.py` | 5 | Forensic accounting invariants |
| `research/tests/test_v15_evidence_gates.py` | 4 | Research governance gate validation |
| `research/tests/test_v16_procurement_preflight.py` (sanitized) | 4 | Preflight schema and provider horizon checks |
| `research/tests/test_v18_authentic_tier1.py` | 4 | Point-in-time causality and holdout firewall |
| `research/manifests/production_universe_manifest.json` | Manifest | 24-instrument metadata specification (zero prices) |
| **Total Pure Standalone Suite** | **253** | **100% Passable Out-of-the-Box with Zero External Data** |

### 2.5 Advanced Replay & Verification Tests (Requires Optional Fixtures)
The following test modules are included for users who supply their own market data or manifests:
- `research/tests/test_v17_tiingo_qualification.py` (8 tests): Requires non-proprietary request ledger fixture or runs mock requests.
- `research/tests/test_v29b_execution_verification.py` (19 tests): Requires `v29b_method_a_order_event_trace.json` or runs dynamically if regenerated.
- `research/tests/test_v19` through `test_v28` (12 modules, 120 tests): Requires authentic `tiingo_cache/` populated with user's own Tiingo subscription. Fully verified internally (400 passed in 74.98s).

### 2.5 Public Sanitized Documentation
| File Path | Description | Sanitization Requirement |
| :--- | :--- | :--- |
| `README.md` | Public repository overview & quickstart | Strip private developer URLs; verify links |
| `START_HERE.md` | Getting started guide for researchers | Ensure all commands use portable paths |
| `RELEASE.md` | Formal release notes & checksum ledger | Verify strategy SHA-256 hashes |
| `AGENT_BRIEF.md` | Strategy architectural specification | Ensure zero proprietary vendor prices cited |
| `ANATOMY.md` | Internal system anatomy & module layout | Portable relative documentation |
| `SUBMISSION.md` | Competition submission checklist & metadata| Sanitize committer identities |
| `RESEARCH_GOVERNANCE_OVERVIEW.md` | Consolidated sanitized public governance report | Replaces 12 internal reports; summarizes V28/V29 findings |

---

## 3. Explicit Exclusion List (Do Not Publish)

The following categories and specific files are strictly excluded from the public snapshot:

### 3.1 Excluded Manifests & Market Data
1. `research/manifests/tier1_aapl_nvda_position_history.json`: **BLOCKED** (Contains 1,258 daily raw bars from Tiingo).
2. `research/manifests/v29b_method_a_order_event_trace.json`: **BLOCKED** (Contains reconstructable point-in-time execution prices).
3. `research/manifests/tiingo_request_ledger.jsonl`: **BLOCKED** (Internal API request logs and timestamps).
4. `research/manifests/tier1_terminal_holdings_v20.json`: **BLOCKED** (Point-in-time closing prices).
5. `research/manifests/tier1_terminal_holdings_v22.json`: **BLOCKED** (Point-in-time closing prices).
6. `research/manifests/tier2_terminal_holdings.json`: **BLOCKED** (Point-in-time closing prices).
7. `research/manifests/tier1_corporate_actions_inventory.json`: **BLOCKED** (Vendor-derived dividend/split data).
8. `research/manifests/tier2_corporate_actions_inventory.json`: **BLOCKED** (Vendor-derived dividend/split data).
9. `tiingo_cache/` (entire directory): **BLOCKED** (16.6 MB commercial market cache).

### 3.2 Excluded Forensic Artifacts & Evidence Directories
1. `research/evidence/` (entire directory): **BLOCKED** (Contains large internal test inventories, soak logs, and machine-specific audit trails).
2. `scratch/` (entire directory, 44 files): **BLOCKED** (Uncurated intermediate research and debugging scripts).

### 3.3 Excluded Internal Governance Reports (PII & Local Path Hazard)
The following 12 internal audit reports contain machine-specific paths (`C:\Users\Manish\...`) and private developer metadata. They are preserved in the internal research branches but excluded from the public snapshot:
1. `GUARDIAN_ALPHA_V21_PORTFOLIO_FIDELITY_AND_TIER2_READINESS_REPORT.md`
2. `GUARDIAN_ALPHA_V22_CAUSAL_PRICE_ALIGNMENT_AND_TIER1_REQUALIFICATION_REPORT.md`
3. `GUARDIAN_ALPHA_V23_TIER2_OUT_OF_SAMPLE_VALIDATION_REPORT.md`
4. `GUARDIAN_ALPHA_V24_TIER2_CONTINUITY_AND_VALIDATION_FORENSICS_REPORT.md`
5. `GUARDIAN_ALPHA_V25_FINAL_TIER2_FINANCIAL_CERTIFICATION_REPORT.md`
6. `GUARDIAN_ALPHA_V26_ADVERSARIAL_FINANCIAL_CERTIFICATION_REPORT.md`
7. `GUARDIAN_ALPHA_V26R_FINANCIAL_REPORT_RECONCILIATION.md`
8. `GUARDIAN_ALPHA_V27_SCIENTIFIC_VALIDITY_AND_MARKET_REALISM_AUDIT.md`
9. `GUARDIAN_ALPHA_V27R_SCIENTIFIC_AND_EXECUTION_RECONCILIATION_REPORT.md`
10. `GUARDIAN_ALPHA_V28_FINAL_RESEARCH_GOVERNANCE_REPORT.md`
11. `GUARDIAN_ALPHA_V29A_*.md` (4 audit documents)
12. `GUARDIAN_ALPHA_V29B_EXECUTION_VERIFICATION_REPORT.md`
