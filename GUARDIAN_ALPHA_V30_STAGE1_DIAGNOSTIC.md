# GUARDIAN ALPHA — V30 STAGE 1
## PRIVATE STRATEGY RESEARCH AND PERFORMANCE DIAGNOSIS

**Audit Date:** 2026-10-24  
**Auditor Roles:** Independent Quantitative Researcher, Portfolio Risk Specialist, Financial-Accounting Auditor, Adversarial Software Verification Engineer  
**Stage:** V30 Stage 1 — Private Strategy Research and Performance Diagnosis  
**Operational Scope:** DIAGNOSIS ONLY. No strategy code modified, no parameters optimized, no trading signals created, no Git mutations executed.  
**Governing Worktree:** `C:\Users\Manish\Downloads\Guardian-Alpha-V29B`  
**Governing Branch:** `research/v29e-final-release-verification`  
**Governing HEAD Commit:** `b283ded200c777b130285b0aa56a0b044afbd339`  

---

## 1. Exact Repository Checkpoint & Workspace State

A comprehensive read-only Git audit was performed prior to analysis. The repository environment is verified as follows:

```
Attribute                     Audited Value / Hash                                                Verification Status
---------------------------------------------------------------------------------------------------------------------
Git Current Branch            research/v29e-final-release-verification                            VERIFIED MATCH
Git HEAD Commit               b283ded200c777b130285b0aa56a0b044afbd339                            VERIFIED MATCH
Tracked Modifications         0 files modified in Git index                                       CLEAN INDEX
Staged Changes                0 files staged for commit                                           CLEAN STAGING
Untracked Governance Reports  20 historical audit reports (V29E/V29F/V29G series preserved)      PRESERVED INTACT
Untracked Evidence Manifest   research/evidence/v29b/test_suite_400_classified_inventory.json     PRESERVED INTACT
Frozen Production Strategy    agent.py (SHA: 46e68dc93fdfb10f1eecfa832673ac4626c1b936...)         VERIFIED IMMUTABLE
Frozen Research Candidate     v12_candidate_ae.py (LF SHA: 978edf7aabc5387af5c8b1fa6a59e15...)    VERIFIED IMMUTABLE
Universe Definition           universe.json (SHA: 66563b613c0bd760759afb23ebb95c59385cfbcf...)   VERIFIED IMMUTABLE
Tiingo Request Ledger         research/manifests/tiingo_request_ledger.jsonl (SHA: a3752805...)  VERIFIED UNTOUCHED
Tier 1 Cache                  tiingo_cache/tier1_bars.json (SHA: dfbf29725434d267305e546785...)   VERIFIED UNTOUCHED
Tier 2 Cache                  tiingo_cache/tier2_bars.json (SHA: 9f8811ec80302e69bde84badd0...)   VERIFIED UNTOUCHED
Tier 3 Holdout Horizon        >= 2022-01-01 unread, unparsed, unhashed, sealed                   VERIFIED SEALED
```

---

## 2. Verified Current Baseline & Historical Performance Ledger

### 2.1 Strategy Architecture
- **Frozen Production Strategy (`agent.py` — Calmar Rotation Hybrid):**
  - **Universe:** 22 risk candidates (15 broad/sector ETFs + 7 mega-cap tech stocks: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA) + 2 leveraged ETFs (QLD, SSO) as overlay only.
  - **Market Regime Filter:** `SPY > SMA50` and `QQQ > SMA50` and `QQQ 20-day realized volatility < 0.35`.
  - **Risk-On Allocation:** Scores risk candidates by composite momentum: $\text{Score} = 0.55 \cdot \text{mom}_{60} + 0.25 \cdot \text{mom}_{20} + 0.20 \cdot (\text{price} / \text{SMA}_{50} - 1) - 0.15 \cdot \text{vol}_{20}$. Selects top 5 positive scores with equal base budget ($0.76$ with overlay, $0.92$ without).
  - **Leveraged ETF Overlay:** Allocates QLD (11%) and SSO (7%) when `QQQ SMA20 > SMA50`, `QQQ mom20 > 0`, and `QQQ vol20 < 0.28`.
  - **Defensive Allocation:** When risk-off, allocates 80% to defensive equities: `XLP` (24%), `XLU` (24%), `XLV` (20%), `XLE` (12%), and 20% in Cash.
  - **Execution Constraints:** 5-day fixed rebalance cadence (`REBALANCE_EVERY_DAYS = 5`); 1.5% rebalance deadband (`MIN_TRADE_PCT = 0.015`); 27% single-position drift trigger; 24% single-position cap; 1.35x gross beta cap.
- **Frozen Research Candidate (`research/strategies/v12_candidate_ae.py` — Candidate A+E Combined):**
  - Combines Candidate A (5-day cadence + emergency shock liquidation if 2-day SPY return $\le -3.0\%$) with Candidate E (cost-aware rebalance buffer suppressing normal trades with equity delta $< 3.0\%$).

### 2.2 Lawfully Evaluated Observation Windows
1. **Tier 1 (In-Sample Calibration):** 2015-01-02 to 2019-12-31 (1,258 trading sessions, 5.0 calendar years; warm-up 2014-09-01 to 2014-12-31).
2. **Tier 2 (Out-of-Sample Primary Validation):** 2020-01-02 to 2021-12-31 (505 trading sessions, 2.0 calendar years; warm-up 2019-09-01 to 2019-12-31).
3. **Continuous Carry-Forward Horizon:** 2015-01-02 to 2021-12-31 (1,763 trading sessions, 7.0 calendar years).
4. **Sealed Tier 3:** Observations dated on or after 2022-01-01 remain strictly sealed and unaccessed.

### 2.3 Verified Comparative Performance Matrix
The table below compiles verified executed performance metrics across the primary out-of-sample Tier 2 window (505 sessions, fresh-start \$100,000.00 capital, verified from V25, V27, and V28 manifests):

| Strategy / Benchmark | Starting NAV ($) | Ending NAV ($) | Net Return (%) | CAGR (%) | Max Drawdown (%) | Sharpe Ratio | Annual Vol (%) | Trade Count | Commission/Fees ($) | Calmar Ratio (CAGR/MaxDD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SPY (Buy & Hold)** | \$100,000.00 | \$151,594.82 | +51.59% | 23.07% | 33.69% | 0.94 | 25.34% | 1 | \$0.00 | 0.685 |
| **QQQ (Buy & Hold)** | \$100,000.00 | \$187,710.85 | +87.71% | 36.92% | 28.54% | 1.24 | 28.28% | 1 | \$0.00 | 1.294 |
| **Frozen E0 (Production)** | \$100,000.00 | **\$233,249.64** | **+133.25%** | **52.60%** | **31.75%** | **1.63** | **28.53%** | **414** | **\$3,239.29** | **1.657** |
| **Candidate A (Emergency Exit)** | \$100,000.00 | \$192,272.44 | +92.27% | 38.57% | 32.38% | 1.31 | 27.20% | 487 | \$3,512.40 | 1.191 |
| **Candidate E (Buffer)** | \$100,000.00 | \$225,907.32 | +125.91% | 50.18% | 33.38% | 1.56 | 28.31% | 362 | \$2,840.11 | 1.503 |
| **Candidate A+E Combined** | \$100,000.00 | \$207,620.42 | +107.62% | 43.99% | 31.72% | 1.44 | 27.53% | 432 | \$3,190.85 | 1.387 |

*Note on Carry-Forward Horizon (2015–2021, 7 years):* Starting \$100,000.00 grew to \$218,989.40 at Tier 1 close, then bridged overnight (+1.14%) to \$221,482.93 on 2020-01-02, finishing at **\$535,191.10** (+435.19%, CAGR 27.10%, Max DD 31.76%, Sharpe 1.69).

---

## 3. Performance Weaknesses, Ranked by Evidence Strength

### Rank 1: High Drawdown & Prolonged Underwater Stretches (Evidence: Empirical Equity Curve Audit)
- **Empirical Severity:** During Tier 2, Frozen E0 suffered a peak-to-trough drawdown of **-31.75%** (2020-02-19 to 2020-03-23).
- **Underwater Duration:** Over **50% of all Tier 2 trading days** were spent below prior high-water marks.
  - The longest underwater period lasted **92 trading sessions (~4.5 months)** from 2021-02-16 to 2021-06-28.
  - The second longest lasted **86 trading sessions (~4 months)** from 2020-09-02 to 2021-01-06.
  - The COVID-19 crash recovery lasted **78 trading sessions (~3.7 months)** from 2020-02-19 to 2020-06-10.
- **Root Cause:** A 50-day moving average filter requires 10–15 trading days of catastrophic index collapse before falling below the trend line. Consequently, the strategy remained 94% long with 18% in 2x leveraged ETFs through the initial 15% drop of the March 2020 crash.

### Rank 2: Fragility to High Slippage & Execution Frictions (Evidence: V27 Phase D 8-Scenario Matrix)
- **Empirical Severity:** Under severe execution stress (Scenario 3: 25 bps equity / 50 bps leveraged), Frozen E0 ending NAV fell by \$26,460.30 (CAGR collapsed from 52.60% to 43.70%). Under extreme stress (Scenario 4: 50 bps equity / 100 bps leveraged), ending NAV collapsed to **\$162,236.74** (CAGR 27.31%, a \$71,012.90 drag). Candidate A+E under extreme stress delivered only 20.71% CAGR, underperforming passive `SPY` (23.07%).
- **Root Cause:** Rebalancing every 5 calendar days generated \$5,500,129.77 in two-way trading turnover on a portfolio averaging ~\$160k, creating ~34x turnover over 2 years. High turnover multiplies slippage penalties rapidly.

### Rank 3: Brittle Deadband Non-Linearity & Microstructural Sensitivity (Evidence: V27R/V28 P&L Bridge)
- **Empirical Severity:** In V27 Phase D, Moderate Slippage (Scenario 2) paradoxically achieved a *higher* ending NAV (\$235,374.49) than Baseline Scenario 1 (\$233,249.64), producing a negative cost drag of -\$2,124.85.
- **Root Cause:** In V28 Section 3.2, forensic order matching proved that small price perturbations during the Feb–Mar 2021 tech correction shifted portfolio drift slightly below the 1.5% deadband (`MIN_TRADE_PCT = 0.015`), suppressing exactly 13 whipsaw rebalance trades. Avoiding those 13 trades saved transaction fees and held larger equity positions into the year-end recovery. This proves the strategy's return is hypersensitive to discrete deadband boundary crossings.

### Rank 4: Extreme Universe Hindsight & Selection Bias (Evidence: V27 Phase B Bar Audit)
- **Empirical Severity:** The 24-instrument universe includes mega-cap winners (NVDA, TSLA, AAPL, MSFT, AMZN, GOOGL, META) selected based on modern 2024–2026 market capitalization. In Tier 1 (2015–2019), AAPL and NVDA alone accounted for **99.07% of the terminal equity portfolio**.
- **Survivorship Contamination:** `XLC` (Communication Services) was incepted in June 2018 (missing 3.5 years of Tier 1), and `XLRE` (Real Estate) was incepted in October 2015. Historical simulations implicitly conditioned on the survival and dominance of these assets.

### Rank 5: Statistical Uncertainty & Wide Confidence Intervals (Evidence: V27 Phase F 2,000-Iteration Bootstrap)
- **Empirical Severity:** A stationary block bootstrap (N=2,000, block length=5 days) on Tier 2 returns revealed wide 95% confidence intervals:
  - Frozen E0 CAGR: **[5.00%, 120.65%]** | Sharpe: **[0.31, 3.12]** | Max DD: **[12.85%, 41.31%]**
  - Candidate A CAGR: **[-5.39%, 102.79%]** (spans negative returns)
  - Candidate A+E CAGR: **[-3.63%, 111.23%]** (spans negative returns)
- **Root Cause:** A 505-session validation sample represents only ~2 economic cycles and is insufficient to reject the null hypothesis of market-beta tracking with random drift.

---

## 4. Financial-Correctness & Implementation Risks

### 4.1 Order Sizing Cash Buffer Deficit & Simultaneous Order Vulnerability
- **Code Flaw:** In `agent.py::orders_to_rebalance`:
  ```python
  spendable = max(float(cash_available), 0.0) + (sell_proceeds * 0.98)
  ```
- **Financial Risk:** In real-world market execution, buy and sell orders are submitted simultaneously at session open. If a broker does not grant instant intraday credit for pending market sell orders, buy orders bounce due to insufficient cash.
- **Empirical Verification:** In V28/V29B Scenario 4 (Extreme Slippage), sell execution prices slipped down while buy execution prices slipped up, causing available cash to fall short of `spendable` and triggering **6 order rejections** for cash affordability.

### 4.2 Flawed Defensive Asset Allocation (`XLE` in Defensive Sleeve)
- **Code Flaw:** In `agent.py`:
  ```python
  DEFENSIVE_WEIGHTS = (("XLP", 0.24), ("XLU", 0.24), ("XLV", 0.20), ("XLE", 0.12))
  ```
- **Financial Risk:** `XLE` (Energy Sector SPDR) is an asset with high commodity beta and cyclical risk. In Q1 2020 (COVID crash), `XLE` collapsed by over **-55%**, declining significantly worse than `SPY`.
- **Structural Exposure:** During risk-off, the strategy maintains **80% equity exposure** across four sectors with 0% Treasury exposure (no TLT/IEF/SHY) and only 20% cash, failing to insulate capital during broad equity market crashes.

### 4.3 Equal Weighting of Highly Asymmetric Volatility Assets
- **Code Flaw:** In `agent.py::target_weights`:
  ```python
  per_winner = min(MAX_WEIGHT - 0.02, base_budget / len(winners))
  ```
- **Financial Risk:** Allocating identical capital weights (15.2% or 18.4%) to assets with vastly different volatility profiles (e.g., `TSLA` with $\sigma \approx 60\%$ vs `XLK` with $\sigma \approx 22\%$) causes single high-beta stocks to contribute over 70% of total portfolio variance, exposing the portfolio to severe idiosyncratic gap risk.

### 4.4 20-Day Realized Volatility Risk-Off Threshold is Too Permissive
- **Code Flaw:** `qqq_vol20 < 0.35`
- **Financial Risk:** An annualized volatility of 35% corresponds to extreme market distress (equivalent to a VIX of 35–40). By the time 20-day realized volatility reaches 35%, significant capital has already been lost. Gating leveraged ETFs with `qqq_vol20 < 0.28` similarly allows 2x leverage to be held during initial crash expansions.

---

## 5. Regime-Specific Diagnosis

| Market Regime | Historic Window Examined | Observed Strategy Behavior | Structural Limitation & Root Cause |
| :--- | :--- | :--- | :--- |
| **Sharp Market Crash** | Feb 19, 2020 – Mar 23, 2020 (COVID Crash) | Remained 94% invested (including 18% in QLD/SSO) for the first 6 trading sessions. Max DD reached -31.75%. | 50-day SMA lag prevented timely exit. QLD/SSO amplified downside. When risk-off finally triggered, defensive allocation held 12% in XLE which was down >50%. |
| **V-Shaped Tech Rebound** | Mar 24, 2020 – Aug 31, 2020 | Rapid recovery; rotated into SMH, AAPL, NVDA, QLD. Captured sharp upside, recovering peak NAV by June 2020. | Candidate A failed here: its 2-day emergency exit triggered on transient pullbacks (e.g., June 11, 2020 drop), liquidating equities at the bottom and missing the subsequent bounce. |
| **Tech Momentum Pullback & Rotation** | Sep 02, 2020 – Jan 06, 2021 | Experienced an 86-day underwater period. Suffered -8.00% single-day drop on 2020-09-08. | Heavy concentration in high-beta tech (NVDA, TSLA, SMH) caused sharp drawdown when mega-cap tech momentum stalled relative to value/cyclicals. |
| **Choppy Range / Deadband Whipsaw** | Feb 16, 2021 – Jun 28, 2021 | Experienced 92-day underwater stretch (longest in Tier 2). Baseline traded 13 times near troughs. | Rebalancing every 5 days generated unnecessary turnover near local inflection points. 1.5% deadband was too narrow to filter price noise. |
| **Steady Bull Grind** | Jul 01, 2021 – Dec 31, 2021 | Consistent compounding; leveraged overlay (QLD/SSO) active; low volatility enabled steady drift upward. | Ideal operating regime for the strategy; positive momentum and low volatility allow trend-following to generate substantial alpha. |

---

## 6. Existing Failed Experiments (Do Not Repeat Without a New Hypothesis)

1. **Candidate A (Naïve 2-Day SPY Shock Exit — `SPY 2-day return <= -3.0%`):**
   - *Result:* Ending NAV dropped from \$233,249.64 to \$192,272.44; CAGR collapsed from 52.60% to 38.57%; Max Drawdown slightly worsened (32.38% vs 31.75%).
   - *Reason for Failure:* Triggered during mid-trend intraday shocks and transient pullbacks (e.g., June 2020), liquidating positions at local troughs and requiring a 5-day wait to re-enter, incurring double transaction costs and missing sharp v-shaped recoveries.
   - *Directive:* **DO NOT REPEAT** simple index price shock exits without an asymmetric re-entry mechanism or volatility regime context.
2. **Candidate E (Uniform 3.0% Equity Rebalance Buffer Alone):**
   - *Result:* Reduced trade count from 414 to 362, but CAGR dropped from 52.60% to 50.18%, and Max Drawdown worsened from 31.75% to 33.38%.
   - *Reason for Failure:* While suppressing noise trades, a uniform 3% buffer delayed necessary risk trimming on drifting high-beta winners, allowing drawdowns to accumulate before rebalancing executed.
   - *Directive:* **DO NOT REPEAT** symmetric turnover buffers that treat risk-reducing trims the same as risk-increasing adds.
3. **Candidate A+E Combined:**
   - *Result:* Ending NAV \$207,620.42 (CAGR 43.99%, Sharpe 1.44), trailing Frozen E0 by 861 bps in CAGR. Under extreme slippage, underperformed passive SPY.
   - *Reason for Failure:* Inherited the whipsaw flaws of Candidate A with the delayed trimming flaws of Candidate E.
   - *Directive:* **DO NOT REPEAT** simple composition of flawed orthogonal heuristics.
4. **Synthetic Fixture Calibration as Historical Evidence:**
   - *Finding in V29F:* Calibrating strategy parameters on synthetic multi-regime fixtures (`sample_regimes.json.gz`) cannot serve as evidence of authentic forward market alpha.
   - *Directive:* **DO NOT SUBSTITUTE** synthetic fixture performance for authentic market evidence.

---

## 7. Recommended Experiments Ranked by Scientific Merit and Expected Risk

### EXP-01: Defensive Sleeve Rationalization & Cash Cushion Expansion
- **Rank:** **1 (Highest Scientific Merit, Lowest Risk)**
- **Scientific Hypothesis:** Eliminating cyclical Energy (`XLE`) from `DEFENSIVE_WEIGHTS` and increasing the defensive cash allocation from 20% to 50% (allocating 50% across `XLP`, `XLU`, `XLV`) will significantly reduce Max Drawdown during market crashes (e.g., March 2020) without degrading risk-on bull market performance.
- **Mechanism:** In risk-off regimes, capital is insulated in cash rather than taking beta losses in distressed equities.
- **Data Requirements:** Tier 1 (2015–2019) calibration; Tier 2 (2020–2021) validation. Tier 3 remains sealed.
- **Baseline Comparison:** Frozen E0 (current 80% equity defensive sleeve with 12% XLE).
- **Out-of-Sample Method:** Two-fold non-overlapping walk-forward on Tier 1; freeze parameters before single Tier 2 validation.
- **Leakage Protection:** Fixed rule specification; zero parameter tuning on Tier 2.
- **Accounting Invariants:** Double-entry balance sheet matches to \$0.000000; cash balance strictly positive.
- **Failure / Rollback Criteria:** If Tier 2 Calmar ratio drops below 1.657, or if Max Drawdown does not improve by at least 200 bps.
- **Test Requirements:** Full 456-test regression suite must pass without regressions.

### EXP-02: Volatility-Informed Inverse-Volatility Position Sizing
- **Rank:** **2 (High Scientific Merit, Medium Risk)**
- **Scientific Hypothesis:** Replacing equal-weight allocation ($w_i = \text{base\_budget} / 5$) with inverse-volatility weighting ($w_i \propto 1 / \sigma_{i, 20}$) will balance marginal risk contributions across winners, reducing portfolio downside deviation and shortening underwater duration.
- **Mechanism:** High-volatility single stocks (e.g., TSLA $\sigma \approx 60\%$, NVDA $\sigma \approx 50\%$) receive smaller dollar allocations (~8–12%), while lower-volatility sector ETFs receive larger allocations (~18–24%), dampening idiosyncratic gap risk.
- **Data Requirements:** Strictly causal daily closing prices up to session $T$ from Tier 1 and Tier 2.
- **Baseline Comparison:** Frozen E0 (equal weighting).
- **Out-of-Sample Method:** Rolling 252-day walk-forward window on Tier 1; single freeze verification on Tier 2.
- **Leakage Protection:** Volatility calculated strictly on past 20 sessions; zero lookahead.
- **Accounting Invariants:** Sum of target weights scaled below 1.00; beta-gross leverage $\le 1.35\times$; single position $\le 0.24$.
- **Failure / Rollback Criteria:** If annualized portfolio volatility does not decrease, or if Tier 2 Sharpe ratio drops below 1.63.

### EXP-03: Asymmetric Fast-Vol Acceleration Gate for Leveraged Overlay
- **Rank:** **3 (Medium Scientific Merit, Medium-High Risk)**
- **Scientific Hypothesis:** Tightening the leveraged overlay gate from `qqq_vol20 < 0.28` to `qqq_vol20 < 0.22` and adding a fast-volatility acceleration condition ($\sigma_{5} / \sigma_{20} \le 1.25$) will decouple 2x leveraged ETFs (QLD, SSO) before the steepest segment of market crashes.
- **Mechanism:** Leveraged ETFs are rapidly shed when short-term volatility spikes, avoiding amplified losses during crash inception.
- **Data Requirements:** Tier 1 and Tier 2 daily bars.
- **Baseline Comparison:** Frozen E0 (current 0.28 volatility threshold).
- **Accounting Invariants:** Clean order generation with zero negative quantities; daily order count $\le 45$.
- **Failure / Rollback Criteria:** If overlay suppression triggers falsely during healthy bull expansions, reducing CAGR by >300 bps without a corresponding reduction in Max Drawdown.

### EXP-04: Robust Cash-Affordability Sizing Buffer in Order Generator
- **Rank:** **4 (High Engineering & Execution Merit, Lowest Risk)**
- **Scientific Hypothesis:** Amending `orders_to_rebalance` to compute spendable cash with an explicit 5% safety margin (`spendable = max(cash_available, 0.0) + (sell_proceeds * 0.90) - 0.05 * total_equity`) will eliminate buy order rejections in high-slippage environments (Scenarios 3 & 4) without altering strategy return in normal execution.
- **Mechanism:** Buy orders do not overcommit pending sell proceeds, ensuring execution feasibility under extreme execution price dispersion.
- **Data Requirements:** Tier 1 and Tier 2 under the 8 execution stress scenarios from V27 Phase D.
- **Baseline Comparison:** Frozen E0 (current 98% sell-proceeds assumption with 0 rebalance cash buffer).
- **Accounting Invariants:** Zero rejected buy orders in Scenario 3 (25/50 bps) and Scenario 4 (50/100 bps); cash balance strictly positive at all times.
- **Failure / Rollback Criteria:** If cash buffer creates cash drag > 100 bps in baseline execution.

---

## 7. Exact Evidence References and Test Results

### 7.1 Primary Governed Evidence Manifests
1. `research/manifests/tier1_v22_comprehensive_metrics.json`: Certified Tier 1 5-year performance (1,258 sessions, \$218,989.40 ending NAV, CAGR 17.00%, Max DD 19.14%).
2. `research/manifests/tier2_four_way_results.json`: Certified Tier 2 fresh-start 2-year performance (\$233,249.64 ending NAV, CAGR 52.60%, Max DD 31.75%, Sharpe 1.63).
3. `research/manifests/v27_execution_realism_stress_results.json`: Certified 8-scenario slippage stress matrix.
4. `research/manifests/v29b_method_a_order_event_trace.json`: Certified 828-order event trace with zero double-counting.
5. `research/evidence/v29b/test_suite_400_classified_inventory.json`: 400 cataloged internal research tests.

### 7.2 Independent Test Suite Verification (Historical Evidence)
- **Hermetic Public Test Suite:** **253 passed in 10.70s** (verified in V29D).
- **Internal Research Regression Suite:** **400 passed in 68.32s** (verified in V29D-R).
- **Full Combined Repository Suite:** **456 tests** (56 release tests + 400 research tests across 41 test files).

---

## 8. Unresolved Data-Access Limitations & Governance Boundaries

1. **Sealed Tier 3 Observations ($\ge$ 2022-01-01):** Strictly sealed and air-gapped. No experiment may train, tune, or evaluate on post-2022 market data.
2. **Provider Redistribution Prohibitions:** Tiingo Starter license strictly prohibits public redistribution of raw price bars. All research must remain confined to local private worktrees.
3. **Public Release Block:** As resolved in V29F, public publication remains paused until rights clearance or certified synthetic fixture alternatives are realized.
4. **Sample Length Limitation:** Tier 1 (5 years) and Tier 2 (2 years) provide a total of 7 calendar years (1,763 sessions). This limited history mandates conservative significance thresholds to avoid overfitting.

---

## 9. Final Diagnostic Verdict

# **STAGE 1 DIAGNOSTIC VERDICT: PASS (READY FOR CONTROLLED EXPERIMENTATION)**

Guardian Alpha's baseline strategy exhibits formidable historical compounding (+435.19% across 2015–2021), but suffers from documented structural vulnerabilities: prolonged underwater periods (>50% of Tier 2), severe crash drawdown (-31.75%), high turnover slippage drag (\$71,012.90 under extreme stress), and order sizing vulnerabilities under price dislocation.

The diagnostic phase is complete. The 4 recommended experiments (EXP-01 through EXP-04) are prioritized by scientific merit and risk containment, and provide a clear, falsifiable roadmap for Stage 2 private experimentation without compromising frozen baselines or Tier 3 holdout boundaries.

**Stage 1 is complete. Do not optimize strategies, modify code, or start Stage 2 without human authorization.**
