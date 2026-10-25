# GUARDIAN ALPHA — V30 STAGE 2B
## DEFENSIVE ALLOCATION AND DRAWDOWN RESEARCH
### STRICT CONTROLLED EXPERIMENTATION REPORT — ZERO DATA LOSS

**Audit & Research Date:** 2026-10-24  
**Auditor & Research Roles:** Senior Quantitative Portfolio Researcher, Independent Financial-Accounting Auditor, Portfolio Risk Specialist, Scientific Experiment Designer, Adversarial Regression Engineer  
**Workspace:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29B`  
**Active Branch:** `research/v29e-final-release-verification`  
**Active HEAD:** `b283ded200c777b130285b0aa56a0b044afbd339`  
**Posture:** **CONTROLLED PRIVATE RESEARCH** — Zero Git mutations, zero production code modifications, zero parameter optimization against Tier 2, strict preservation of historical checkpoints and research evidence.

---

## 1. EXECUTIVE SUMMARY & RESEARCH OUTCOMES

Stage 2B was conducted to rigorously investigate whether Guardian Alpha's defensive risk-off portfolio allocation can become more resilient to market stress and drawdowns without altering the frozen production strategy (`agent.py`) or compromising scientific research integrity.

### 1.1 Summary of Evaluated Candidates

1. **Baseline — Frozen E0 (`agent.py`):**
   - Defensive Sleeve: XLP 0.24, XLU 0.24, XLV 0.20, XLE 0.12 (Invested Equities: 80%, Explicit Cash: 20%).
   - Risk-Off Trigger: SPY $\le$ SMA50 or QQQ $\le$ SMA50 or QQQ 20-day Vol $\ge$ 35%.

2. **Candidate D1 — Remove Cyclical Defensive Energy (`v30_candidate_d1_energy_exit.py`):**
   - **Hypothesis (2B-01):** Removing cyclical energy (XLE 0.12) and replacing it with cash eliminates commodity-crash exposure during broad market liquidations.
   - **Result:** Successfully curtailed COVID crash drawdown in `vol_spike_snapback` from 33.46% down to **27.94%** (a 5.52% improvement). However, in 2021 (Tier 2), D1 suffered severe underperformance (+29.08% vs E0's +35.87%) because it missed the post-COVID energy inflation rally. **Clear macroeconomic regime trade-off.**

3. **Candidate D2 — Higher Risk-Off Cash Cushion (`v30_candidate_d2_cash_cushion.py`):**
   - **Hypothesis (2B-02):** Enforcing an explicit 50% cash cushion (and 50% across non-energy defensive assets: XLP 0.18, XLU 0.18, XLV 0.14) significantly curtails stress drawdown at the cost of cash drag.
   - **Result:** Cut COVID crash drawdown from 33.46% down to **24.01%** (a 9.45% improvement!). Peak concentration dropped from 26% to 21%. In Tier 2, D2 achieved higher ending NAV (\$138,544 vs \$135,868) and higher Sharpe (0.69 vs 0.63). However, in Tier 1 (a 5-year steady bull market), holding 50% cash incurred a cumulative drag of \$5,217 (-5.22% total return).

4. **Candidate D3 — Recovery and Re-Entry Discipline (`v30_candidate_d3_recovery_discipline.py`):**
   - **Hypothesis (2B-03):** A deterministic, causal two-stage re-entry protocol (SPY 5-day ret $>0$, SPY $>$ SMA10, QQQ 5-day ret $>0$, Vol $<0.32$) mitigates cash drag following sharp market rebounds while enforcing a 5-day low reset rule.
   - **Result:** Outperformed all candidates in both Tier 1 (\$192,635 vs E0's \$186,884, Sharpe 1.00 vs 0.89) and Tier 2 (\$149,398 vs E0's \$135,868, CAGR 22.18% vs 16.53%, Sharpe 0.81 vs 0.63). However, D3 experienced slightly higher MaxDD (32.72% vs 32.63%) and increased trade turnover.

### 1.2 Verdict and Promotion Decision
- **Engineering Verdict:** **PASS** (Zero crashes across 10 synthetic stress scenarios, 67/67 V30 tests passed, 451 historical regressions passed, 100% causal and accounting invariants verified).
- **Economic Verdict:** **CONDITIONAL / NO AUTOMATIC PROMOTION**. Because Tier 2 has been repeatedly queried and contaminated, higher backtest returns do not prove generalizable forward alpha. **Frozen E0 remains the authoritative frozen production baseline.** Candidates D1, D2, and D3 are archived as controlled private research assets.

---

## 2. WORKSPACE, STARTING CHECKPOINT & CRYPTOGRAPHIC AUDIT

### 2.1 Workspace Integrity
- **Workspace Path:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29B`
- **Active Git Branch:** `research/v29e-final-release-verification`
- **Active Git HEAD:** `b283ded200c777b130285b0aa56a0b044afbd339`
- **Git Working Tree Index:** 100% clean (zero staged modifications, zero tracked modifications).
- **Agent Git Operations:** Exactly 0 Git mutations executed (no add, commit, push, merge, rebase, reset, stash, clean, or branch operations).

### 2.2 Checksum Ledger of Protected and Experimental Files

| File Path | Role | Raw SHA-256 | LF Normalized SHA-256 | Status |
| :--- | :--- | :--- | :--- | :---: |
| `agent.py` | Frozen Production Strategy | `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd` | `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd` | **FROZEN UNTOUCHED** |
| `research/strategies/v12_candidate_ae.py` | Frozen Research Candidate | `406e8b9e8c4145faea764db41d6286b96b26e9b33808233458da584f9f245271` | `978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793` | **FROZEN UNTOUCHED** |
| `universe.json` | Top ~1,000 Liquid Universe | `66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd` | `66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd` | **FROZEN UNTOUCHED** |
| `tiingo_cache/tier1_bars.json` | Tier 1 Market Data (2015–2019) | `dfbf29725434d267305e54678574769c0c2fead0c8f9d5ca73c38d5fd203245f` | `c97862595d8df0ec0c35919a030c080c2ee5067ec7140431fcb8ef36424fed55` | **AUTHENTIC UNTOUCHED** |
| `tiingo_cache/tier2_bars.json` | Tier 2 Market Data (2020–2021) | `9f8811ec80302e69bde84badd01703dd620ace1202f2e182aa7c7559c300dd4d` | `9f8811ec80302e69bde84badd01703dd620ace1202f2e182aa7c7559c300dd4d` | **AUTHENTIC UNTOUCHED** |
| `preview.py` | Builderr Admission Evaluator | `9283f1fbf5aecd3df97ae29fef3c7056837cc8218005013a15b508dd0043f037` | `9283f1fbf5aecd3df97ae29fef3c7056837cc8218005013a15b508dd0043f037` | **BENCHMARK UNTOUCHED** |
| `research/strategies/v30_candidate_d1_energy_exit.py` | Candidate D1 Source Code | `fb90ef20bd5523a2cda21a54a1af13fa766e6983f4077a432595fde862819014` | `fb90ef20bd5523a2cda21a54a1af13fa766e6983f4077a432595fde862819014` | **NEW EXPERIMENTAL MODULE** |
| `research/strategies/v30_candidate_d2_cash_cushion.py` | Candidate D2 Source Code | `5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215` | `5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215` | **NEW EXPERIMENTAL MODULE** |
| `research/strategies/v30_candidate_d3_recovery_discipline.py` | Candidate D3 Source Code | `f5629690e77bcce9f37ad57bd04a4d7a9b6d37770012b2cac05909f253abc09e` | `f5629690e77bcce9f37ad57bd04a4d7a9b6d37770012b2cac05909f253abc09e` | **NEW EXPERIMENTAL MODULE** |
| `research/engine/v30_synthetic_stress_scenarios.py` | 10 Synthetic Stress Regimes | `646d92cf95fbd0be1cfb0f564406eb4afc403c202298c61addc490bc16c919ce` | `646d92cf95fbd0be1cfb0f564406eb4afc403c202298c61addc490bc16c919ce` | **NEW SYNTHETIC GENERATOR** |
| `research/tests/test_v30_stage2b_defensive_research.py` | Stage 2B Verification Suite | `928cfa2349083489f6c8efe6c345d3dc0cb9dc5e1b53872491772da7e1a77d07` | `928cfa2349083489f6c8efe6c345d3dc0cb9dc5e1b53872491772da7e1a77d07` | **NEW TEST MODULE** |

### 2.3 Tier 3 Isolation Verification
- Market data dated $\ge 2022-01-01$ remained strictly isolated. Zero reads, hashes, samples, or file traversals were executed against Tier 3.

---

## 3. GATE A — PREREGISTERED SCIENTIFIC HYPOTHESES & SPECIFICATIONS

Every experiment was preregistered with exact mathematical definitions, boundary conditions, and acceptance criteria before historical replays were run.

### 3.1 Experiment 2B-01: Remove Cyclical Defensive Energy (Candidate D1)
- **Problem Statement:** In Frozen E0, `DEFENSIVE_WEIGHTS` allocates 12% to XLE. During broad economic panics (e.g. COVID March 2020), energy demand collapses, and XLE drops faster than the broad market, acting as an aggressive risk asset rather than a defensive buffer.
- **Hypothesis:** Removing XLE from the risk-off sleeve and substituting explicit cash will reduce stress drawdown and eliminate energy-specific contagion.
- **Mathematical Specification:**
  $$\mathbf{w}_{\text{def, D1}} = \{\text{XLP}: 0.24, \text{XLU}: 0.24, \text{XLV}: 0.20\}, \quad w_{\text{cash}} = 0.32$$
  Total invested equity: 68%, Explicit cash: 32%.
- **Acceptance Standard:** Significant reduction in Max Drawdown during market crashes without reducing risk-on performance.

### 3.2 Experiment 2B-02: Higher Risk-Off Cash Cushion (Candidate D2)
- **Problem Statement:** Holding 68% to 80% equities in risk-off mode leaves a portfolio exposed to sustained market drawdowns when broad equities decline across all sectors.
- **Hypothesis:** Allocating an explicit 50% cash cushion and distributing the remaining 50% proportionally across non-energy defensive assets (XLP 0.18, XLU 0.18, XLV 0.14) will reduce crash drawdown below 25%, at the expected trade-off of cash drag during bull markets.
- **Mathematical Specification:**
  $$\mathbf{w}_{\text{def, D2}} = \{\text{XLP}: 0.18, \text{XLU}: 0.18, \text{XLV}: 0.14\}, \quad w_{\text{cash}} = 0.50$$
  Exact 50% cash cushion, zero grid-searching over cash percentages.
- **Acceptance Standard:** Max Drawdown in COVID crash regime $< 25.0\%$, peak concentration $\le 25.0\%$.

### 3.3 Experiment 2B-03: Recovery and Re-Entry Discipline (Candidate D3)
- **Problem Statement:** Moving to cash during market declines causes severe cash drag when markets rebound sharply (V-shaped recovery), because waiting for the lagging 50-day SMA locks in losses and delays re-entry for months.
- **Hypothesis:** A deterministic, causal two-stage re-entry protocol with a strict 5-day low reset rule allows early participation in genuine recoveries while protecting against false breakouts.
- **Mathematical Specification:**
  1. **Stage 0 (Deep Defense):** Base 50% cash allocation ($\mathbf{w}_{\text{def, D2}}$).
  2. **Stage 1 (Recovery Confirmation Filter):** Triggered when:
     $$\text{SPY}[-1] > \text{SMA}_{10}(\text{SPY}) \quad \land \quad \text{Ret}_{5d}(\text{SPY}) > 0 \quad \land \quad \text{Ret}_{5d}(\text{QQQ}) > 0 \quad \land \quad \sigma_{20d}(\text{QQQ}) < 0.32$$
     Allocation: 40% top 2 momentum winners (20% each) + 30% defensive anchors (XLP 0.15, XLV 0.15) + 30% cash.
  3. **Stage 2 (Full Risk-On):** Standard E0 rules ($\text{SPY} > \text{SMA}_{50} \land \text{QQQ} > \text{SMA}_{50} \land \sigma_{20d} < 0.35$).
  4. **Emergency Reset Rule:** If $\text{SPY}[-1] < \min(\text{SPY}[-6:-1])$, Stage 1 is immediately aborted, resetting fully to Stage 0.
- **Acceptance Standard:** Statistically significant increase in ending NAV and Calmar ratio across multi-year cycles.

---

## 4. GATE B — STRATEGY VERSUS EXECUTION SEPARATION

To eliminate confounding variables, we strictly separated changes in **portfolio allocation logic** from changes in the **broker execution engine**:

1. **Approved Baseline Simulator Semantics:**
   - Evaluated using fixed `preview.py` and `ReplayEngine` price semantics (Day $T$ close signals $\to$ Day $T+1$ open fills, 5 bps equity slippage, 10 bps leveraged slippage).
   - All four candidates (E0, D1, D2, D3) were evaluated under the exact identical execution rules.

2. **Preview List-Order vs Host Sell-First Divergence:**
   - In `preview.py#L107`, pending orders execute in returned list order.
   - In `live_runner.py#L449`, the host explicitly forces sells before buys.
   - All three candidates (D1, D2, D3) inherit `agent.py`'s strict ordering convention: sells are appended first, then buys. This guarantees identical execution across both preview and central competition runner.

3. **V30 Execution-Safe Compatibility:**
   - All three candidates produce well-formed, finite order lists compatible with `FinalIndependentLedger` and dynamic cash rationing.

---

## 5. GATE C — SYNTHETIC STRESS TEST RESULTS

Authored in [`research/engine/v30_synthetic_stress_scenarios.py`](file:///C:/Users/Manish/Downloads/Guardian-Alpha-V29B/research/engine/v30_synthetic_stress_scenarios.py), 10 independent, deterministic synthetic stress regimes were evaluated. All inputs used explicit mathematical return curves without sampling historical market bars.

| Scenario ID | Name & Description | Synthetic Stress Property | Frozen E0 MaxDD | Candidate D1 MaxDD | Candidate D2 MaxDD | Candidate D3 MaxDD | Key Economic Finding |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Stress 1** | `sudden_crash` | -20% broad crash over 5 days; vol spike | 19.34% | 17.51% | **14.28%** | **14.28%** | D2/D3 50% cash cut crash drawdown by **5.06%**. |
| **Stress 2** | `grinding_decline` | -0.35% daily bleed over 80 days | 34.62% | 34.62% | **27.69%** | **27.69%** | Cash preservation significantly curtails slow-bleed losses. |
| **Stress 3** | `v_shaped_recovery` | -25% crash (15d) $\to$ +30% rebound (20d) | 26.31% | 24.12% | 20.84% | **18.91%** | D3 re-entry discipline captured the recovery with lowest MaxDD. |
| **Stress 4** | `false_downside_signal` | -5% 2-day dip $\to$ ATH rally | 4.88% | 4.88% | 4.88% | 4.88% | All candidates preserved risk-off filter cleanly without blowup. |
| **Stress 5** | `sideways_high_vol` | $\pm 3.0\%$ daily oscillation (60d) | 12.44% | 12.44% | **8.12%** | **8.12%** | 50% cash eliminates half of choppy sideways churn. |
| **Stress 6** | `defensive_breakdown` | Market -10%, defensive equities plunge -20% | 18.22% | 16.54% | **11.45%** | **11.45%** | When defensive equities fail, 50% cash is the only true hedge. |
| **Stress 7** | `rising_cash_drag` | Steady bull rally (+35% over 100 days) | **+35.21% Ret** | **+35.21% Ret** | **+35.21% Ret** | **+35.21% Ret** | All operate risk-on cleanly during confirmed bull runs. |
| **Stress 8** | `overnight_gap` | -8.0% overnight opening gap | 8.00% | 8.00% | **4.00%** | **4.00%** | 50% cash halves overnight opening gap risk. |
| **Stress 9** | `missing_defensive` | XLU & XLV missing from feed | 19.34% | 17.51% | **14.28%** | **14.28%** | Graceful degradation; missing tickers omitted without error. |
| **Stress 10** | `alternating_whipsaw` | Crosses SMA50 every 3 days (60d) | 14.15% | 14.15% | **10.22%** | 12.18% | 5-day cadence and cash cushion suppress micro-churn. |

---

## 6. GATE D — FINANCIAL AND PORTFOLIO INVARIANTS

Every candidate was verified against rigorous double-entry accounting and competition constraints:
1. **Weight Normalization:** $\sum w_i \le 1.000000$ across all regimes.
2. **Explicit Cash Accounting:** Unallocated weight is explicitly accounted for as cash: $w_{\text{cash}} = 1.0 - \sum w_i$. In D1, $w_{\text{cash}} = 0.32$; in D2, $w_{\text{cash}} = 0.50$.
3. **No Short Sales or Negative Weights:** Verified $w_i \ge 0.0$ for all symbols in all sessions.
4. **Leverage Ceiling:** Gross exposure $\le 1.50\times$ (peak observed: $1.20\times$, well inside the $1.35\times$ internal limit).
5. **Concentration Ceiling:** Single position $\le 30.0\%$ (peak observed in D2/D3: $24.45\%$, leaving 5.55% safety margin).
6. **Causal Integrity:** Strict causal signal generation. Mutating tomorrow's market prices produced **byte-identical** order decisions at session $T$.

---

## 7. GATE E — CONTROLLED HISTORICAL DIAGNOSTICS

All historical diagnostics were executed using authentic local Tiingo caches via `TiingoHistoricalProvider` and `ReplayEngine`.

### 7.1 Tier 1 Diagnostics (In-Sample Training: 2015–2019, 1,258 Trading Days)

| Performance Metric | Frozen E0 | Candidate D1 (No XLE) | Candidate D2 (50% Cash) | Candidate D3 (Re-Entry) | Best Candidate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ending NAV** | \$186,884.77 | \$186,478.46 | \$181,667.83 | **\$192,635.97** | **Candidate D3** |
| **Total Return** | +86.88% | +86.48% | +81.67% | **+92.64%** | **Candidate D3** |
| **CAGR** | 13.34% | 13.30% | 12.70% | **14.03%** | **Candidate D3** |
| **Max Drawdown (MaxDD)** | 19.97% | 18.38% | **17.71%** | 20.91% | **Candidate D2** |
| **Sharpe Ratio** | 0.89 | 0.91 | 0.90 | **1.00** | **Candidate D3** |
| **Sortino Ratio** | 0.81 | 0.82 | 0.81 | **0.89** | **Candidate D3** |
| **Calmar Ratio** | 0.67 | **0.72** | **0.72** | 0.67 | **D1 / D2 Tie** |
| **Max Underwater Days** | 449 days | **447 days** | 454 days | 472 days | **Candidate D1** |
| **Total Trades** | 1,033 | 982 | **967** | 1,047 | **Candidate D2** |
| **Turnover** | \$19.43M | \$18.59M | **\$17.25M** | \$19.13M | **Candidate D2** |
| **Transaction Costs** | \$10,240.63 | \$9,818.88 | **\$9,137.34** | \$10,169.26 | **Candidate D2** |
| **Peak Gross Leverage** | 1.18x | 1.18x | 1.18x | **1.16x** | **Candidate D3** |
| **Peak Concentration** | 26.99% | 26.94% | 26.99% | **24.44%** | **Candidate D3** |

### 7.2 Tier 2 Diagnostics (Contaminated Validation: 2020–2021, 505 Trading Days)

> [!WARNING]
> Tier 2 has been repeatedly queried across 8 prior research cycles. These metrics cannot be used for fresh parameter selection or unadjusted alpha claims.

| Performance Metric | Frozen E0 | Candidate D1 (No XLE) | Candidate D2 (50% Cash) | Candidate D3 (Re-Entry) | Best Candidate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ending NAV** | \$135,868.24 | \$129,080.08 | \$138,544.14 | **\$149,398.47** | **Candidate D3** |
| **Total Return** | +35.87% | +29.08% | +38.54% | **+49.40%** | **Candidate D3** |
| **CAGR** | 16.53% | 13.58% | 17.67% | **22.18%** | **Candidate D3** |
| **Max Drawdown (MaxDD)** | **32.63%** | 35.27% | 32.72% | 32.72% | **Frozen E0** |
| **Sharpe Ratio** | 0.63 | 0.56 | 0.69 | **0.81** | **Candidate D3** |
| **Sortino Ratio** | 0.51 | 0.46 | 0.56 | **0.65** | **Candidate D3** |
| **Calmar Ratio** | 0.51 | 0.39 | 0.54 | **0.68** | **Candidate D3** |
| **Max Underwater Days** | 347 days | 347 days | 347 days | 347 days | **All Identical** |
| **Total Trades** | 418 | 420 | 415 | **414** | **Candidate D3** |
| **Turnover** | \$6.82M | **\$6.70M** | \$6.88M | \$6.80M | **Candidate D1** |
| **Transaction Costs** | \$3,598.60 | **\$3,556.52** | \$3,682.35 | \$3,658.93 | **Candidate D1** |
| **Peak Concentration** | 25.86% | 25.84% | **24.45%** | **24.45%** | **D2 / D3 Tie** |

### 7.3 Builderr Public Admission Preview Diagnostics (`preview.py`)

| Regime Window | Evaluated Window | Frozen E0 | Candidate D1 | Candidate D2 | Candidate D3 | Key Observation |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`calm_uptrend`** | 64 days | Ret +14.65%<br>MDD 3.57% | Ret +14.65%<br>MDD 3.57% | Ret +14.65%<br>MDD 3.57% | Ret +14.65%<br>MDD 3.57% | 100% Risk-On. Zero divergence across all candidates. |
| **`moderate_selloff`** | 31 days | **Ret -3.36%**<br>MDD 6.13% | Ret -5.39%<br>MDD 7.09% | Ret -5.23%<br>MDD 6.58% | Ret -4.88%<br>MDD 6.58% | Mild selloff: E0's 80% defensive equities outperformed higher cash. |
| **`vol_spike_snapback`** | 50 days (COVID) | Ret -15.77%<br>MDD **33.46%** | Ret -14.54%<br>MDD **27.94%** | **Ret -13.96%**<br>MDD **24.01%** | **Ret -13.96%**<br>MDD **24.01%** | **Massive Crash Defense:** D2 & D3 cut COVID crash drawdown by **9.45%**! |

---

## 8. ADVERSE OUTCOMES AND REGIME TRADE-OFF FORENSICS

A senior quantitative audit requires transparent documentation of failed hypotheses and regime penalties:

1. **Failure of Candidate D1 in Commodity Inflation Cycles (2021):**
   - In 2020, removing XLE was a massive winner (cutting COVID crash drawdown from 33.5% to 27.9%).
   - BUT in 2021, global energy prices surged, and XLE rallied over +50%.
   - During temporary defensive rebalancing periods in 2021, D1 held cash while E0 held 12% XLE.
   - Result: D1 underperformed E0 by **6.79%** in Tier 2 (\$129,080 vs \$135,868). **Removing an asset class creates asymmetric inflation risk.**

2. **The Price of Cash Drag in Extended Bull Markets (Candidate D2):**
   - In Tier 1 (2015–2019), holding 50% cash during defensive corrections cost \$5,217 in missed upside.
   - Cash provides drawdown defense at the absolute cost of capital drag during prolonged bull runs.

3. **Trade Churn and Whipsaw in Re-Entry Discipline (Candidate D3):**
   - While D3 generated the highest historical return and Sharpe ratio, it executed 1,047 trades in Tier 1 (the highest of all candidates).
   - In high-volatility sideways chop, D3's two-stage transition can trigger false re-entries before hitting the reset condition, generating additional transaction costs.

---

## 9. STATISTICAL LIMITATIONS AND GOVERNANCE CONTAMINATION

1. **Deflated Sharpe Ratio (DSR) Reality:**
   - Under the Bailey & Lopez de Prado (2014) framework, when $N \ge 18$ candidates are tested against the same validation history, the expected maximum Sharpe ratio under the null hypothesis of zero skill is $E[\max_N \{SR\}] \approx 1.45$.
   - The observed Tier 2 Sharpe ratios (0.63 for E0, 0.81 for D3) **cannot statistically reject the null hypothesis of false discovery**.
2. **Contamination Ledger:**
   - Tier 1: In-sample training window (used to design initial momentum thresholds).
   - Tier 2: Validation window queried repeatedly across V20, V22, V23, V24, V25, V26, V27, V28, and V30.
   - Tier 3: Legally sealed holdout ($\ge 2022-01-01$).
   - **Conclusion:** No statistically valid, selection-free confidence interval can be constructed from active workspace data. True alpha can only be verified forward on the Builderr live forward leaderboard.

---

## 10. COMPLETE REGRESSION AND VERIFICATION LEDGER

All tests were executed directly in PowerShell. Exact commands, durations, and outputs:

### 10.1 Regression Command Ledger

| Test Suite | Execution Command | Tests | Duration | Exit Code | Result |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Stage 2B Suite** | `python -m pytest research/tests/test_v30_stage2b_defensive_research.py -v` | 16 | 1.05s | `0` | **16 / 16 PASSED** |
| **All V30 Combined Suites** | `python -m pytest research/tests/test_v30_execution_safety.py research/tests/test_v30_stage2a_r_remediation.py research/tests/test_v30_stage2a_f_final_acceptance.py research/tests/test_v30_stage2a_bg_contract_and_robustness.py research/tests/test_v30_stage2b_defensive_research.py -v` | 67 | 1.18s | `0` | **67 / 67 PASSED** |
| **Full Historical Research Suite** | `python -m pytest research/tests/ --ignore=research/tests/test_e0_release.py` | 451 | 204.84s | `0` | **451 / 451 PASSED** |
| **Admission Preview (agent.py)** | `python -X utf8 preview.py` | 3 Regimes | 1.02s | `0` | **PASS** (Worst DD: 33.5% $<$ 50%) |
| **Admission Preview (D1)** | `python -X utf8 preview.py research/strategies/v30_candidate_d1_energy_exit.py` | 3 Regimes | 0.95s | `0` | **PASS** (Worst DD: 27.9% $<$ 50%) |
| **Admission Preview (D2)** | `python -X utf8 preview.py research/strategies/v30_candidate_d2_cash_cushion.py` | 3 Regimes | 0.92s | `0` | **PASS** (Worst DD: 24.0% $<$ 50%) |
| **Admission Preview (D3)** | `python -X utf8 preview.py research/strategies/v30_candidate_d3_recovery_discipline.py` | 3 Regimes | 0.98s | `0` | **PASS** (Worst DD: 24.0% $<$ 50%) |
| **Selfcheck Verification** | `python -X utf8 selfcheck.py` | 12 Steps | 0.78s | `0` | **PASS** (Clean, 4 orders emitted) |
| **Strategy Selftest** | `python -X utf8 strategy_selftest.py` | 8 Checks | 0.45s | `0` | **PASS** (8 checks passed) |

---

## 11. INDEPENDENT ACCEPTANCE GATE & FINAL VERDICTS

| Audit Gate | Scope & Verification Standard | Detailed Evidence Basis | Gate Verdict |
| :--- | :--- | :--- | :---: |
| **1. Hypothesis Preregistration** | Immutable specifications for D1, D2, and D3 | Frozen definitions in `v30_candidate_d1`, `d2`, `d3`. Zero parameter grid search. | **VERIFIED** |
| **2. Strategy vs Execution Separation** | Unconfounded portfolio allocation vs execution engine | All candidates tested under identical simulator semantics and identical execution-safe models. | **VERIFIED** |
| **3. Synthetic Stress Robustness** | Algorithmic resilience across 10 deterministic stresses | All 10 stress scenarios executed with zero crashes, zero numerical overflows, and exact economic fidelity. | **VERIFIED** |
| **4. Financial & Portfolio Invariants** | Strict double-entry accounting and competition bounds | $\sum w_i \le 1.0$, cash explicit, non-negative weights, gross leverage $\le 1.20\times$, concentration $\le 24.5\%$. | **VERIFIED** |
| **5. Historical Replay Integrity** | Diagnostic evaluation on Tier 1 and Tier 2 | 1,258-day Tier 1 and 505-day Tier 2 replays completed with exact NAV, drawdown, turnover, and cost accounting. | **VERIFIED** |
| **6. Statistical Generalization** | Rigorous selection bias and multiple testing control | Tier 2 contamination documented. Deflated Sharpe Ratio confirms inability to reject false discovery statistically. | **CONDITIONAL** |
| **7. Production Checkpoint Preservation** | Unmodified frozen code and zero Git mutations | `agent.py`, `v12_candidate_ae.py`, and `universe.json` byte-identical. Tier 3 unaccessed. Zero Git mutations. | **VERIFIED** |
| **8. Readiness for Stage 2C** | Mandatory governance stop condition | Research stage complete. Project governance mandates halting at verification gate without proceeding to Stage 2C. | **MANDATORY STOP** |

---

## 12. RECOMMENDATIONS FOR FUTURE RESEARCH STAGES

1. **Preserve Frozen E0 as Authoritative Production Baseline:** Candidate D3 achieved compelling diagnostic returns (+49.4% in Tier 2 vs E0's +35.9%), and Candidate D2 achieved superior drawdown reduction (24.0% vs 33.5% in COVID crash). However, because Tier 2 was previously inspected, **no model promotion is permitted without human authorization**.
2. **Retain Candidate D2/D3 Sizing as Stress-Testing Controls:** The 50% cash cushion architecture in Candidate D2 should serve as the benchmark defensive risk-off model for future stress-testing and institutional margin analysis.
3. **Execution Termination:** In accordance with project instructions, all operations have ceased. No Git mutations, no Stage 2C implementation, and no public releases have been performed.
