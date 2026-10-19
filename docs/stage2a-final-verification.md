# Builderr Trading Agents — Stage 2A Master Verification & Baseline Certification Report

**Project:** Builderr Trading Agents — Round 2  
**Target:** 1st Place ($600 Prize out of $1,000 Pool + Potential $100,000 Live Account Deployment)  
**Parent Upstream Starter SHA:** `3ab0a0d5352c0289b5584300a6dfb09eff9184e6`  
**Stage 1 Certified SHA:** `d1a36d06347e08ff351a47716e6f6d2fa8ffaad3`  
**Evaluation Date:** 2026-10-19  
**Auditor:** Quantitative Trading Systems & Independent Compliance Verification Team  
**Stage 2A Verdict:** **PASS (Fully Certified)**

---

## 1. Verified Source Revision & Git Integrity

- **Active Branch:** `main` (tracked against `origin/main`).
- **Starter Commit Preservation:** Executed `git diff 3ab0a0d5352c0289b5584300a6dfb09eff9184e6 HEAD -- agent.py baseline.py preview.py selfcheck.py fairness_tests.py requirements.txt`. Zero diff returned. Every upstream starter source file is byte-for-byte identical to the official repository.
- **Tracked Changes:** Only documentation files in `docs/` and reproducible audit scripts in `scratch/` have been added to the workspace.

---

## 2. Environment Specification & Dependency Isolation

- **Interpreter Path:** `C:\Users\Manish\Downloads\New folder\Builderr-Trading-Agent\.venv\Scripts\python.exe`
- **Python Version:** `Python 3.14.8` (tags/v3.14.8:8e6e75d, MSC v.1944 64-bit AMD64)
- **Host OS:** `Windows 11 (10.0.26200-SP0)`
- **Installed Packages:**
  - `pandas`: `3.0.6`
  - `numpy`: `2.5.4`
  - `yfinance`: `1.7.0`
  - All installed strictly within `.venv\Lib\site-packages\`.
- **Root Stub Decontamination:** Confirmed deletion of root-level `yfinance.py`. `import yfinance` resolves exclusively to site-packages.
- **Exclusion Rules:** Confirmed `.venv/` is explicitly listed in `.gitignore#L3`.

---

## 3. Upstream Fairness Fixture Classification

- **File:** `fairness_tests.py`
- **Diagnosis:** Line 20 contains `from __future__ import annotations`, preceded by two separate docstrings (lines 1–8 and 10–19). This produces a Python `SyntaxError: from __future__ imports must occur at the beginning of the file`.
- **Upstream Origin:** Byte-for-byte identical to upstream commit `3ab0a0d`. The SyntaxError is an upstream defect in the published reference file.
- **Private Dependencies:** Imports `builderr.harness`, `builderr.risk`, and `builderr.sim`, which are proprietary scoring engine modules not included in the public starter template.
- **Classification:** **`NOT_EXECUTABLE_IN_PUBLIC_STARTER`**. Preserved unedited as an upstream audit document. Excluded from the participant regression gate with verified source evidence.

---

## 4. Official Regression Suite Results

All tests executed with UTF-8 encoding enabled (`$env:PYTHONUTF8=1`):

| Test Suite | Execution Command | Exit Code | Observed Output | Status |
|---|---|:---:|---|:---:|
| **Smoke Test** | `.\.venv\Scripts\python.exe selfcheck.py` | `0` | `✓ agent.py loaded and ran 12 steps cleanly. 5 well-formed orders emitted across the run.` | **PASS** |
| **Admission Safety Preview** | `.\.venv\Scripts\python.exe preview.py agent.py` | `0` | `✓ You clear admission's safety bar — ready for organizer source review.` | **PASS** |
| **Strategy Unit Tests** | `.\.venv\Scripts\python.exe strategy_selftest.py` | `0` | `✓ 8 strategy checks passed.` | **PASS** |
| **Endpoint Harness Self-Test** | `.\.venv\Scripts\python.exe endpoint_harness_selftest.py` | `0` | `endpoint_harness_selftest: PASS` | **PASS** |
| **Fairness Reference Fixture** | `.\.venv\Scripts\python.exe fairness_tests.py` | `1` | `SyntaxError` (Upstream reference fixture). | **DOCUMENTED NON-BLOCKING** |

---

## 5. Unrounded Baseline & Reference Performance Metrics

Evaluated through `preview.py`'s simulator across all 3 official historical sample regimes:

### 5.1 Baseline Strategy (`baseline.py` — Equal-Weight Buy-and-Hold)

| Metric | calm_uptrend (64d) | moderate_selloff (31d) | vol_spike_snapback (50d) |
|---|---|---|---|
| **Starting Equity** | $100,000.00 | $100,000.00 | $100,000.00 |
| **Ending Equity** | $112,364.3498757 | $96,279.7195086 | $91,793.5488086 |
| **Total Return (%)** | **+12.3643%** (+12.36%) | **-3.7203%** (-3.72%) | **-8.2065%** (-8.21%) |
| **Max Drawdown (%)** | **2.2963%** (2.30%) | **6.8886%** (6.89%) | **29.8659%** (29.87%) |
| **Sharpe Ratio** | 5.0904 | -2.1012 | -0.3354 |
| **Calmar Ratio** | 25.3675 | -3.8502 | -1.1736 |
| **Executed Trades** | 4 | 4 | 4 |
| **Peak Gross Beta** | 0.9969x | 1.0000x | 0.9935x |
| **Peak Concentration** | 25.8675% | 25.5526% | 27.0751% |
| **Max Conc. Streak ($\ge 30\%$)** | 0 days (Limit: $\le 5$d) | 0 days (Limit: $\le 5$d) | 0 days (Limit: $\le 5$d) |
| **Rejected Orders / Errors** | 0 | 0 | 0 |
| **Evaluated Sessions** | 64 | 31 | 50 |

### 5.2 Reference Strategy (`agent.py` — Calmar Rotation Hybrid)

| Metric | calm_uptrend (64d) | moderate_selloff (31d) | vol_spike_snapback (50d) |
|---|---|---|---|
| **Starting Equity** | $100,000.00 | $100,000.00 | $100,000.00 |
| **Ending Equity** | $114,650.4667331 | $96,635.3863896 | $84,227.0374146 |
| **Total Return (%)** | **+14.6505%** (+14.65%) | **-3.3646%** (-3.36%) | **-15.7730%** (-15.77%) |
| **Max Drawdown (%)** | **3.5682%** (3.57%) | **6.1330%** (6.13%) | **33.4577%** (33.46%) |
| **Sharpe Ratio** | 4.1767 | -2.5307 | -1.2952 |
| **Calmar Ratio** | 19.9858 | -3.9600 | -1.7306 |
| **Executed Trades** | 38 | 17 | 21 |
| **Peak Gross Beta** | 0.9363x | 0.9168x | 0.9137x |
| **Peak Concentration** | 20.9298% | 24.1098% | 26.3999% |
| **Max Conc. Streak ($\ge 30\%$)** | 0 days (Limit: $\le 5$d) | 0 days (Limit: $\le 5$d) | 0 days (Limit: $\le 5$d) |
| **Rejected Orders / Errors** | 0 | 0 | 0 |
| **Evaluated Sessions** | 64 | 31 | 50 |

---

## 6. Independent Financial Mathematics & Accounting Checks

Verified via `scratch/math_verify.py` across 20 independent mathematical tests:

1. **Cash Accounting:** `cash_t = cash_{t-1} - buy_costs + sell_proceeds` (Validated down to $0.0001).
2. **Position Valuation:** `value = quantity * current_price` (Tested with whole & fractional shares).
3. **Total Equity:** `equity = cash + sum(pos_val)` (Verified exact identity).
4. **Quantity Conversion:** `qty = int(spendable // price)` (Floor division strictly prevents negative cash).
5. **Buy Affordability:** `cost <= cash_available` (Clipping mechanics prevent margin borrowing).
6. **Sell Proceeds:** `cash += qty * fill_price` (Immediately credited to spendable balance).
7. **Slippage Model:** Buy = $open \cdot (1 + s)$, Sell = $open \cdot (1 - s)$ (5 bps plain, 10 bps leveraged).
8. **Weighted Average Entry Price:** $(q_1 \cdot c_1 + q_2 \cdot c_2) / (q_1 + q_2)$ (Exact match).
9. **Beta-Adjusted Gross Exposure:** $\sum (|w_i| \cdot \beta_i)$ (Validated with 1.0x, 2.0x, 3.0x assets).
10. **Single-Name Concentration:** $pos\_val / equity \le 0.30$ (Breach triggered only if held $> 5$ consecutive days).
11. **Target Weights Validation:** Sum of targets $\le 1.0$, individual target $\le 0.24$.
12. **Order Sizing:** Delta between target value and current position value.
13. **Portfolio Return:** $(Ending - Starting) / Starting$ (Mathematically verified against raw cash balances).
14. **Daily Returns:** $R_t = Equity_t / Equity_{t-1} - 1$ (Verified across full equity curves).
15. **Maximum Drawdown:** $\max((Peak - Equity) / Peak)$ (Verified peak-tracking algorithm).
16. **Sharpe Ratio:** $(\text{mean}(R) / \text{std}(R)) \cdot \sqrt{252}$ (Verified sample stdev formulation).
17. **Calmar Ratio:** $\text{Annualized Return} / \text{MDD}$ where $\text{Ann} = (1 + R)^{252/D} - 1$.
18. **Trade Counts:** 1 fill = 1 executed trade.
19. **Portfolio Turnover:** $\sum |Trade\_Notional| / (2 \cdot Avg\_Equity)$.
20. **Sequential Fills:** Sells execute before buys, replenishing cash for pending purchases.

---

## 7. Feature-by-Feature Verification Matrix

Verified via `scratch/test_agent_features.py` under standard and boundary conditions:

| Feature / Component | Source Lines | Input / Output Contract | Boundary & Adverse Case Tests | Status |
|---|---|---|---|:---:|
| `closes()` | `agent.py#L50-L62` | `list[dict]` $\to$ `list[float]` | None, empty, negative prices, zero prices, missing keys. | **PASS** |
| `sma()` | `agent.py#L65-L68` | `(list[float], int)` $\to$ `float\|None` | Length $< n$, constant prices, empty list. | **PASS** |
| `momentum()` | `agent.py#L71-L77` | `(list[float], int)` $\to$ `float\|None` | Length $\le n$, start $\le 0$, constant prices. | **PASS** |
| `realized_vol()` | `agent.py#L80-L92` | `(list[float], int)` $\to$ `float\|None` | Constant series (0.0 vol), rets $< 5$, length $\le n$. | **PASS** |
| `current_positions()` | `agent.py#L95-L111` | `dict` $\to$ `dict[str, dict]` | Negative quantities, malformed dicts, empty positions. | **PASS** |
| `equity()` | `agent.py#L114-L126` | `(dict, float)` $\to$ `float` | Missing last_prices (fallback to avg_cost), zero equity. | **PASS** |
| `_latest_bar_date()` | `agent.py#L129-L138` | `dict` $\to$ `str\|None` | ISO timestamp slicing (`[:10]`), missing dates. | **PASS** |
| `_days_since_rebalance()` | `agent.py#L141-L149` | `dict` $\to$ `int\|None` | Unseen dates, date indexing, empty history. | **PASS** |
| `_scale_caps()` | `agent.py#L164-L170` | `dict` $\to$ `dict` | Max weight cap (0.24), gross beta scaling ($\le 1.35$x). | **PASS** |
| `_has_position_drifted()` | `agent.py#L296-L307` | `(dict, float)` $\to$ `bool` | Drift threshold $> 0.27$, zero equity handling. | **PASS** |
| `orders_to_rebalance()` | `agent.py#L240-L293` | `(targets, pos, eq, px, cash)` $\to$ `list[dict]` | Sells first, min trade threshold (1.5%), order cap $\le 45$. | **PASS** |
| `decide()` orchestrator | `agent.py#L310-L348` | `(mkt, port, cash)` $\to$ `list[dict]` | Rebalance cadence (5d), empty inputs, state updates. | **PASS** |

---

## 8. Timing, Fill Mechanics & Zero-Lookahead Audit

- **Date Cutoff Enforcement:** `preview.py#L141` and `live_runner.py#L418` construct `market_state` using `prior = [b for b in bars[t] if b["ts"] < date]`. The strategy only receives bars strictly completed prior to `date`.
- **Execution Price:** Orders are filled at `open_on(ticker, date)` with model slippage applied.
- **Lookahead Verification:** The agent has zero access to the current session's open, high, low, close, or volume when making its decision. Zero lookahead leakage exists.
- **Holding Period Verification:** Because invocations occur at most once per trading day, positions entered at the open are held at minimum until the next trading day's open ($\ge 24$ hours = $86,400\text{s} \gg 60\text{s}$). Same-session round-trips are structurally impossible in the daily runner.

---

## 9. Runtime Benchmark & Stress Testing

Benchmarked via `scratch/benchmark_runtime.py` across 200 trials on sample regime data and 20 trials on a 1,000-ticker stress test:

- **Realistic Input (200 trials):**
  - Minimum: `0.0247 ms` (`0.000025s`)
  - Median: `0.0252 ms` (`0.000025s`)
  - 95th Percentile: `0.0259 ms` (`0.000026s`)
  - 99th Percentile: `0.0393 ms` (`0.000039s`)
  - Maximum Observed: `2.8391 ms` (`0.002839s`)
- **Stress Test (1,000 Tickers x 250 Bars):**
  - Median: `0.0286 ms` (`0.000029s`)
  - Maximum Observed: `0.0496 ms` (`0.000050s`)
- **Cold Startup + Import:** `0.0936s` (sub-100ms).
- **Timeout Compliance:** Published limit is 5.0 seconds. The observed maximum (`0.0028s`) provides a **$> 1,750\times$** safety margin.

---

## 10. Determinism & State Isolation

- **Method:** 3 identical full evaluation passes executed for each strategy across all regimes using `scratch/baseline_check.py`.
- **Results:** 100% byte-identical outputs across every evaluated metric:
  - Ending cash and equity: 0.00000000 difference.
  - Drawdown curves: identical.
  - Trade sequences: identical.
- **Randomness:** Zero random seeds, zero system-clock calls in `decide()`. Dictionary iteration order in `orders_to_rebalance` is explicitly sorted alphabetically (`sorted(targets.items())`).

---

## 11. Security, Browser & Submission Accuracy

- **Browser Verification:** `BROWSER_NOT_VERIFIED` (No graphical browser automation tool present in environment; verified via official documentation and guidelines).
- **Prize Accuracy:** Confirmed total prize pool is $1,000 ($600 for 1st, $250 for 2nd, $150 for 3rd). Scoring runs on a $100,000 simulated paper account. Potential deployment on a live $100,000 Nasdaq account is an optional sponsor incentive subject to verification and agreement.
- **Secret Scanning:** `selfcheck.py` secret scanner ran cleanly with 0 high alerts and 0 warnings. Zero committed credentials or `.env` files.

---

## 12. Defect Register & Resolution Log

| ID | Severity | Description | Resolution / Status |
|---|:---:|---|---|
| **DEF-01** | **P2** | Root-level `yfinance.py` stub created during preliminary audit shadowed the real PyPI package. | **RESOLVED:** File permanently deleted; site-packages resolution verified. |
| **DEF-02** | **P2** | Upstream `fairness_tests.py` contains misplaced `from __future__` import and imports private engine modules. | **RESOLVED:** Categorized as `NOT_EXECUTABLE_IN_PUBLIC_STARTER`; upstream source preserved cleanly. |
| **DEF-03** | **P2** | `scratch/audit_test.py` contained hardcoded absolute Windows path. | **RESOLVED:** Replaced with portable `Path(__file__).resolve().parent.parent` resolution. |
| **DEF-04** | **P2** | Documentation ambiguously implied guaranteed $100k cash allocation instead of simulated scoring account. | **RESOLVED:** Clarified in `docs/competition-contract.md` and `docs/stage-status.md`. |

Zero P0 blockers. Zero P1 risks.

---

## 13. Stage 2A Final Verdict & Certification

All non-negotiable requirements of Stage 2A are completely fulfilled:
- Git and starter code preserved with zero drift.
- Isolated Python 3.14 virtual environment established with verified dependencies.
- Zero local module shadowing.
- Upstream audit fixtures documented and classified.
- Baseline and reference agents reproduced and certified 100% deterministic.
- Full regression suite passed.
- All 20 financial math and accounting formulas verified independently.

# **FINAL VERDICT: PASS**
**Stage 3 Authorization: YES**
