# GUARDIAN ALPHA — V29A: REPRODUCIBILITY DEPENDENCY MAP

**Audit Phase:** Batch V29A: Zero-Loss Evidence Integrity & Baseline Protection  
**Auditor:** Principal Quantitative Research Auditor & Verification Engineer  
**Timestamp:** 2026-10-23T18:35:00+05:30  
**Baseline Commit:** `8c77fddf72398b2e016a6f212d067c8aeb2b385e`  
**Total Audited Scratch Inventory:** 123 Files (44 Tracked in Git, 75 Untracked in TrackB, 4 Ignored)  
**Machine-Readable Inventory:** [`research/evidence/v29a/scratch_audit_inventory.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/evidence/v29a/scratch_audit_inventory.json)  

---

## 1. Executive Summary & Classification Taxonomy

In fulfillment of Batch V29A Objective 4D, a comprehensive AST and dependency audit of all 123 files residing in the research scratch directory was performed. None of these files are disposable; all represent critical historical evidence, mathematical derivations, or provenance artifacts.

Per the V29A governance charter, each artifact is classified into one of five rigorous tiers:

| Tier | Category Name | Count | Primary Role in Guardian Alpha Research |
| :---: | :--- | :---: | :--- |
| **1** | **Required for Reproducibility of Published V28 Results** | **13** | Directly generates committed manifests, NAV bridges, or numbers cited in reports. |
| **2** | **Useful Historical Forensic Evidence** | **39** | Investigates anomalies, traces divergences, validates splits, and audits execution. |
| **3** | **Superseded Research Experiment (Preserved)** | **56** | Prior strategy candidates, earlier backtest versions, parameter sweeps. |
| **4** | **Historical Agent Prompt or Working Note** | **9** | Prompts and governance constraints from V17 through V25 research cycles. |
| **5** | **Temporary or Incidental Artifact (Under Review)** | **6** | Environment checks, timing tests, and intermediate scratch JSON outputs. |
| **Total** | **All Audited Scratch Items** | **123** | **100% Accounted For & Classified** |

---

## 2. In-Depth Audit of Priority Focus Scripts

### 2.1 `compute_method_a_and_b_matrices.py`
- **Classification:** **Category 1 (Required for Reproducibility)**
- **File Metrics:** 8,245 bytes | SHA-256: `9B4EF0539DF925484ED488FEAC432F78A33A8679A8A55B25449A5F1DF2C4F1A5` | 240 lines
- **Inputs & Data Dependencies:**
  - Market Data: `tiingo_cache/tier2_bars.json` (24 symbols, 2020-01-01 to 2021-12-31, warmup 2019-09-01)
  - Modules: `agent`, `research.strategies.v12_candidate_ae.CandidateAE_Combined`, `research.engine.replay.ReplayEngine`, `research.engine.accounting`
- **Output Artifacts Generated:**
  - Committed Manifest: [`research/manifests/v27r_two_method_execution_sensitivity.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/manifests/v27r_two_method_execution_sensitivity.json)
- **Role in V28 Governance:**
  Executes both Model 1/2 (Method A Fixed-Trade Replay) and Model 3 (Method B Reactive Replay) across 8 transaction-cost scenarios (0 to 10 bps commissions, 0 to 100 bps slippage). The generated manifest is directly tested in [`research/tests/test_v28_governance_certification.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/tests/test_v28_governance_certification.py#L72-L100) and cited in V27R/V28 formal reports.

---

### 2.2 `audit_method_a_exact_orders.py`
- **Classification:** **Category 1 (Required for Reproducibility)**
- **File Metrics:** 5,888 bytes | SHA-256: `E98E6E77A73F1C4293E3C8B7CF2E4A9CF64C729D038C7A33CE2FF880CAAA407D` | 165 lines
- **Inputs & Data Dependencies:**
  - Market Data: `tiingo_cache/tier2_bars.json`
  - Modules: `agent`, `research.engine.replay.ReplayEngine`, `research.engine.accounting.PortfolioState`
- **Role in V28 Governance & Test Integrity:**
  Under Method A fixed-trade replay, baseline orders (414 total: 200 buys, 214 sells) are forced into a cash-constrained portfolio. This script derives the exact event-level order counts:
  - **Scenario 3 (Severe Slippage):** 380 full fills (182 buys + 198 sells), 34 partial fills (18 cash-capped buys + 16 inventory-capped sells), 0 rejections = **414 executed orders**.
  - **Scenario 4 (Extreme Slippage):** 319 full fills (150 buys + 169 sells), 89 partial fills (45 cash-capped buys + 44 inventory-capped sells), 6 rejections (5 buys with $0 cash + 1 sell with 0 unheld shares) = **408 executed orders**.
  **CRITICAL FINDING:** These exact figures were hardcoded into [`test_v28_governance_certification.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/tests/test_v28_governance_certification.py#L279-L306). Preserving this script is strictly mandatory because it is the sole computational source deriving those hardcoded numbers from raw bars.

---

### 2.3 `compute_exact_overnight_bridge.py`
- **Classification:** **Category 1 (Required for Reproducibility)**
- **File Metrics:** 3,820 bytes | SHA-256: `9B00F772714571A5A0A7E302FB00995BCFD6EE7A4CD3D2BD15CEB6904E090F16` | 85 lines
- **Inputs & Data Dependencies:**
  - Manifest: [`research/manifests/tier1_terminal_holdings_v22.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/manifests/tier1_terminal_holdings_v22.json)
  - Market Data: `tiingo_cache/tier2_bars.json` (specifically 2020-01-02 opening bars)
- **Output Artifacts Generated:**
  - Committed Manifest: [`research/manifests/tier2_carryforward_continuity_bridge.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/manifests/tier2_carryforward_continuity_bridge.json)
- **Role in V28 Governance:**
  Computes the exact dollar-for-dollar overnight market movement between the Tier 1 closing bell (2019-12-31 close) and Tier 2 opening bell (2020-01-02 open). It proves zero phantom capital injection:
  - Closing Cash: $0.04
  - Overnight Movement: +$5,082.99
  - True Opening Economic NAV: $352,579.24 (+1.46% gap on Frozen E0).
  Tested in `test_v24_continuity_and_forensics.py` and `test_v26r_report_arithmetic_verifier.py`.

---

### 2.4 `reconstruct_pnl_bridge.py`
- **Classification:** **Category 1 (Required for Reproducibility)**
- **File Metrics:** 3,694 bytes | SHA-256: `3B57608ECBFBEF498CE280E1C1F6E20D5FE2DE89E8FE92C55353C47BD7D2531B` | 85 lines
- **Inputs & Data Dependencies:**
  - Market Data: `tiingo_cache/tier2_bars.json`
  - Modules: `agent`, `research.engine.replay.ReplayEngine`, `research.engine.accounting`
- **Role in V28 Governance:**
  Performs complete double-entry PnL conservation decomposition between Baseline friction ($100k starting capital, realized PnL, unrealized PnL, dividends, receivables, slippage drag) and Moderate Slippage, proving zero residual accounting leakage across the two-year evaluation period.

---

### 2.5 Execution Sensitivity and Causal Adapter Tests
- **`test_execution_sensitivity.py` (Category 1):**
  - Generates committed manifest [`research/manifests/v27_execution_realism_stress_results.json`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/research/manifests/v27_execution_realism_stress_results.json) cited throughout V27 and tested in `test_v27_scientific_validity.py`.
- **`test_causal_adapter.py` (Category 2 - Forensic Evidence):**
  - Verifies point-in-time price normalization between split-adjusted prices (V21) and raw prices (V22), proving why AAPL close changed from $70.66 to $293.65 and establishing causal price semantics.

---

### 2.6 Order-Level Trace Scripts
- **`trace_fills.py` (Category 2):** Traces individual order fills comparing Baseline, Moderate Slippage, and Commission scenarios, isolating the exact rebalance date where fills diverge.
- **`trace_execution_divergence.py` (Category 2):** Pinpoints the precise bar where path-dependent cash differences cause order curtailment.
- **`trace_next_divergences.py` (Category 2):** Tracks downstream cascading effects of order sizing differences.
- **`trace_aapl_nvda.py` (Category 2):** Reconstructs trade-by-trade corporate action handling for the top two concentration assets.

---

## 3. Complete 123-File Scratch Inventory

### Category 1: Required for Reproducibility of Published V28 Results (13 Files)
1. [`scratch/audit_method_a_exact_orders.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/audit_method_a_exact_orders.py) — Derives exact order fill partitions (380 full, 34 part, 0 rej in S3; 319 full, 89 part, 6 rej in S4) hardcoded in V28 governance test.
2. [`scratch/compute_bootstrap_ci.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/compute_bootstrap_ci.py) — Computes block-bootstrap paired confidence intervals crossing zero.
3. [`scratch/compute_exact_overnight_bridge.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/compute_exact_overnight_bridge.py) — Generates committed manifest `tier2_carryforward_continuity_bridge.json`.
4. [`scratch/compute_method_a_and_b_matrices.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/compute_method_a_and_b_matrices.py) — Generates committed manifest `v27r_two_method_execution_sensitivity.json`.
5. [`scratch/compute_paired_statistics.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/compute_paired_statistics.py) — Computes paired t-statistic ($p=0.2100$) and Sharpe delta.
6. [`scratch/decimal_nav_bridge.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/decimal_nav_bridge.py) — Derives decimal NAV rounding bridge cited in V21 report.
7. [`scratch/decimal_nav_bridge_v22.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/decimal_nav_bridge_v22.py) — Derives V22 decimal NAV bridge cited in V22 report.
8. [`scratch/reconcile_v25_holdings_discrepancy.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/reconcile_v25_holdings_discrepancy.py) — Reconciles terminal holdings discrepancy between E0 and candidate for V26.
9. [`scratch/reconstruct_pnl_bridge.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/reconstruct_pnl_bridge.py) — Derives PnL conservation decomposition cited in V27R report.
10. [`scratch/run_corrected_carryforward.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/run_corrected_carryforward.py) — Generates corrected carryforward results manifest for V24/V25.
11. [`scratch/table_arithmetic_verifier.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/table_arithmetic_verifier.py) — Verifies table arithmetic consistency across reports.
12. [`scratch/terminal_holdings_reconciliation.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/terminal_holdings_reconciliation.py) — Derives terminal holdings reconciliation cited in V20 report.
13. [`scratch/test_execution_sensitivity.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29A/scratch/test_execution_sensitivity.py) — Generates committed manifest `v27_execution_realism_stress_results.json`.

---

### Category 2: Useful Historical Forensic Evidence (39 Files)
1. `scratch/analyze_method_a_infeasibility.py` — Forensic proof of cash infeasibility under Method A.
2. `scratch/audit_agent_interface.py` — Interface contract and state isolation verification.
3. `scratch/audit_fallbacks.py` — Audit of fallback safety mechanisms.
4. `scratch/audit_pnl_attribution.py` — Forensic daily return factor attribution.
5. `scratch/audit_q4_2019_decisions.py` — Forensic audit of agent rebalance decisions in Q4 2019.
6. `scratch/audit_splits_and_dividends.py` — Corporate actions reconciliation across 24 assets.
7. `scratch/audit_universe_validity.py` — Point-in-time universe membership and survivorship checks.
8. `scratch/benchmark_stability_investigation.py` — Stability analysis of SPY and QQQ benchmarks.
9. `scratch/compare_first_divergence.py` — Compares divergence timestamps across versions.
10. `scratch/compute_slip_audit.py` — Audits effective slippage vs modeled slippage.
11. `scratch/compute_underwater_periods.py` — Computes drawdown durations and underwater profiles.
12. `scratch/diagnose_candidate_accounting.py` — Diagnostic of candidate cash and share accounting.
13. `scratch/diagnose_execution_divergence.py` — Diagnostic of execution divergence mechanics.
14. `scratch/dump_results.py` — Dumps structured replay results.
15. `scratch/explain_delta.py` — Explains performance deltas between revisions.
16. `scratch/find_first_date_trade_diff.py` — Identifies first date with different trade quantities.
17. `scratch/find_first_divergence.py` — Identifies exact bar of first trade divergence.
18. `scratch/inspect_all_manifest_trades.py` — Verifies trade records across committed manifests.
19. `scratch/inspect_four_way.py` — Forensic inspection of 4-way backtest metrics.
20. `scratch/inspect_q4.py` — Inspects Q4 rebalance orders.
21. `scratch/inspect_t2_metrics.py` — Inspects Tier 2 summary metrics.
22. `scratch/inspect_v22_holdings.py` — Inspects V22 terminal holdings against ledger.
23. `scratch/reconstruct_aapl_nvda_history.py` — Reconstructs full trade-by-trade history for top assets.
24. `scratch/show_positions.py` — Displays portfolio positions at rebalance boundaries.
25. `scratch/slippage_forensics.py` — Forensic investigation of leveraged ETF slippage.
26. `scratch/test_carryforward_ledger.py` — Tests carryforward ledger state transitions.
27. `scratch/test_causal_adapter.py` — Forensic test of causal price normalization.
28. `scratch/test_independent_ledger.py` — Tests independent double-entry ledger.
29. `scratch/test_manifest_crosscheck.py` — Cross-checks report markdown tables against manifests.
30. `scratch/test_method_a.py` — Forensic test runner for Method A execution.
31. `scratch/test_order_invariance.py` — Tests invariance to order execution sequence.
32. `scratch/test_recon_table.py` — Tests reconciliation table formulas.
33. `scratch/test_replay_adapter.py` — Tests causal replay adapter interface.
34. `scratch/test_session_flow_ledger.py` — Tests session flow ledger mechanics.
35. `scratch/trace_aapl_nvda.py` — Traces AAPL and NVDA historical position and split adjustments.
36. `scratch/trace_execution_divergence.py` — Traces exact order where execution diverges under friction.
37. `scratch/trace_fills.py` — Order-level fill trace comparing baseline vs moderate slippage.
38. `scratch/trace_next_divergences.py` — Traces subsequent divergence points.
39. `scratch/verify_rebalance_logic.py` — Verifies rebalance order generation logic.
40. `scratch/verify_v22_accounting.py` — Verifies independent accounting against V22 output.

---

### Category 3: Superseded Research Experiments (56 Files)
*(Includes 44 files committed in Git tracking under `scratch/` plus 12 untracked experimental scripts)*

**Committed Tracked Scratch Scripts (44 Files):**
`analyze_vol_spike_attribution.py`, `analyze_xle_and_sectors.py`, `audit_all_regimes_turnover.py`, `audit_test.py`, `audit_v13_01_costs.py`, `audit_v13_02_suppressed_orders.py`, `audit_v13_03_liquidation_timeline.py`, `audit_v13_04_bootstrap.py`, `audit_v13_05_latency_memory.py`, `audit_v14_full_forensics.py`, `backup_and_verify_evidence.py`, `baseline_check.py`, `benchmark_runtime.py`, `benchmark_v12.py`, `build_ledger_and_manifest.py`, `check_turnover_formula.py`, `counterfactual_rebalancing.py`, `deep_baseline_profile.py`, `detailed_loss_attribution.py`, `evaluate_v10_candidates.py`, `four_way_comparison.py`, `gate1_dates_reconciliation.py`, `gate1_v16_reconciliation.py`, `gate2_attribution_bridge.py`, `gate3_cost_sensitivity.py`, `gate4_statistical_review.py`, `inspect_recovery_timing.py`, `inspect_v11_b_loss_attribution.py`, `inspect_windows.py`, `math_verify.py`, `print_trades.py`, `profile_cpu.py`, `reconcile_v10_attribution.py`, `reproduce_baseline.py`, `reproduce_p0_accounting.py`, `runtime_check.py`, `run_statistical_validation.py`, `test_adverse_inputs.py`, `test_agent_features.py`, `test_cadence.py`, `test_candidates_a_to_f.py`, `test_hypotheses.py`, `test_hypotheses_part2.py`, `v12_statistical_sensitivity.py`.

**Untracked Superseded Scripts (12 Files):**
`compute_attribution.py`, `compute_benchmarks.py`, `compute_full_v20_metrics.py`, `compute_v22_statistics.py`, `fix_v22_holdings.py`, `generate_v26_preflight_inventory.py`, `inventory_v22.py`, `investigate_cagr_dd.py`, `run_four_way.py`, `run_four_way_v22.py`, `simulate_v22_vs_v21.py`.

---

### Category 4: Historical Agent Prompts & Working Notes (9 Files)
1. `scratch/v17_prompt.txt` — Stage B2-H qualification specifications and holdout constraints.
2. `scratch/v19_prompt.txt` — Tier 1 forensics and accounting reconciliation prompt.
3. `scratch/v19_prompt_full.txt` — Full uncompressed V19 prompt.
4. `scratch/v20_prompt.txt` — Double-entry accounting verification prompt.
5. `scratch/v21_prompt.txt` — Portfolio fidelity and Tier 2 readiness prompt.
6. `scratch/v23_prompt.txt` — Tier 2 out-of-sample validation mandate.
7. `scratch/v24_prompt_full.txt` — Cross-period continuity and phantom capital prompt.
8. `scratch/v25_prompt.txt` — Final Tier 2 financial certification prompt.
9. `scratch/v25_prompt_full.json` — Structured JSON specification of V25 requirements.

---

### Category 5: Temporary or Incidental Artifacts (6 Files)
1. `scratch/check_env.py` — Quick Python version and virtualenv diagnostic.
2. `scratch/check_tickers.py` — Ticker list sanity check.
3. `scratch/test_speed.py` — Engine replay execution timing diagnostic.
4. `scratch/hypotheses_results.json` — Intermediate scratch output of early hypothesis testing.
5. `scratch/q4_2019_decisions.json` — Intermediate scratch output of Q4 2019 order decisions.
6. `scratch/slippage_forensics.json` — Intermediate scratch output of leveraged slippage calculation.

---

## 4. Directed Upstream & Downstream Dependency Graph

```mermaid
flowchart TD
    subgraph Data Layer
        T1_CACHE["tiingo_cache/tier1_bars.json"]
        T2_CACHE["tiingo_cache/tier2_bars.json"]
    end

    subgraph Engine Core
        ENGINE_ACC["research.engine.accounting"]
        ENGINE_REPLAY["research.engine.replay.ReplayEngine"]
        ENGINE_IND["research.engine.independent_accounting"]
        PROD_STRAT["agent.decide (Frozen E0)"]
        CAND_STRAT["research.strategies.v12_candidate_ae"]
    end

    subgraph Scratch Generation Layer (Category 1)
        SCR_MATRICES["scratch/compute_method_a_and_b_matrices.py"]
        SCR_ORDERS["scratch/audit_method_a_exact_orders.py"]
        SCR_BRIDGE["scratch/compute_exact_overnight_bridge.py"]
        SCR_SENS["scratch/test_execution_sensitivity.py"]
        SCR_PNL["scratch/reconstruct_pnl_bridge.py"]
        SCR_STATS["scratch/compute_paired_statistics.py"]
    end

    subgraph Committed Manifests
        MAN_27R["v27r_two_method_execution_sensitivity.json"]
        MAN_BRIDGE["tier2_carryforward_continuity_bridge.json"]
        MAN_27SENS["v27_execution_realism_stress_results.json"]
        MAN_STATS["tier2_paired_strategy_statistics.json"]
    end

    subgraph Regression Test Suite (381 Tests)
        TEST_V28["test_v28_governance_certification.py"]
        TEST_V27R["test_v27r_scientific_reconciliation.py"]
        TEST_V27["test_v27_scientific_validity.py"]
        TEST_V24["test_v24_continuity_and_forensics.py"]
    end

    subgraph Governance Reports
        REP_V28["GUARDIAN_ALPHA_V28_FINAL_RESEARCH_GOVERNANCE_REPORT.md"]
        REP_V27R["GUARDIAN_ALPHA_V27R_SCIENTIFIC_AND_EXECUTION_RECONCILIATION_REPORT.md"]
    end

    T2_CACHE --> ENGINE_REPLAY
    T2_CACHE --> SCR_MATRICES
    T2_CACHE --> SCR_ORDERS
    T2_CACHE --> SCR_BRIDGE
    T2_CACHE --> SCR_SENS

    ENGINE_ACC --> ENGINE_REPLAY
    PROD_STRAT --> ENGINE_REPLAY
    CAND_STRAT --> ENGINE_REPLAY

    ENGINE_REPLAY --> SCR_MATRICES
    ENGINE_REPLAY --> SCR_ORDERS
    ENGINE_REPLAY --> SCR_SENS
    ENGINE_REPLAY --> SCR_PNL

    SCR_MATRICES --> MAN_27R
    SCR_BRIDGE --> MAN_BRIDGE
    SCR_SENS --> MAN_27SENS
    SCR_STATS --> MAN_STATS

    MAN_27R --> TEST_V28
    MAN_BRIDGE --> TEST_V24
    MAN_27SENS --> TEST_V27

    SCR_ORDERS -.->|Derives Hardcoded Counts| TEST_V28

    MAN_27R --> REP_V28
    MAN_BRIDGE --> REP_V28
    SCR_PNL --> REP_V27R
```

---

## 5. Clean-Checkout Reproducibility Limitations

1. **Missing Data Cache in Fresh Worktrees:**
   `tiingo_cache/` is git-ignored. When a clean worktree is created (such as `Guardian-Alpha-V29A`), `tier1_bars.json` and `tier2_bars.json` are absent. Any script or live regression test attempting to access these caches fails immediately with `FileNotFoundError`.
2. **Untracked Dependency on Category 1 Scripts:**
   The manifests `v27r_two_method_execution_sensitivity.json`, `tier2_carryforward_continuity_bridge.json`, and `v27_execution_realism_stress_results.json` are committed in Git, but the generator scripts that produce them from raw data (`compute_method_a_and_b_matrices.py`, etc.) are untracked in `scratch/`. If `scratch/` were wiped, these manifests could not be regenerated without recovering the scripts.
3. **Hardcoded Test Invariant:**
   `test_v28_governance_certification.py` lines 279–306 assert hardcoded fill counts derived by `scratch/audit_method_a_exact_orders.py`. If that script is lost, the rationale and mathematical derivation of those test numbers becomes opaque.
4. **Preservation Mandate:**
   All 123 scripts must remain immutably preserved in the repository backup archive.
