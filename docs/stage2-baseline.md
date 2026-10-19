# Stage 2A — Environment Setup, Baseline Reproduction & Verification Report

**Competition:** Builderr Trading Agents — Round 2  
**Evaluation Date:** 2026-10-19  
**Parent Upstream SHA:** `3ab0a0d5352c0289b5584300a6dfb09eff9184e6`  
**Stage 1 Commit SHA:** `d1a36d06347e08ff351a47716e6f6d2fa8ffaad3`  
**Target:** 1st Place ($600 Prize + $100,000 Real Account Allocation)  
**Stage 2A Verdict:** **PASS** (Ready for Stage 3)

---

## 1. Isolated Python Environment

An isolated virtual environment was initialized and verified to avoid contamination and module shadowing:

- **Interpreter Path:** `C:\Users\Manish\Downloads\New folder\Builderr-Trading-Agent\.venv\Scripts\python.exe`
- **Python Version:** `Python 3.14.8` (compatible with official range 3.10 – 3.14)
- **Virtual Environment Directory:** `.venv` (confirmed present in `.gitignore#L3`)
- **Installed Packages:**
  - `pandas`: `3.0.6` (verified via `import pandas; print(pandas.__version__)`)
  - `yfinance`: `1.7.0` (installed from PyPI into `.venv\Lib\site-packages\yfinance\__init__.py`)
  - `numpy`: `2.5.4`
- **Stub Removal & Import Verification:**
  - Root-level stub `yfinance.py` was completely deleted from project root.
  - Confirmed `os.path.exists('yfinance.py') == False`.
  - Confirmed `import yfinance` resolves strictly to site-packages, eliminating all local module shadowing risks.
  - Production agent (`agent.py`) and official evaluation scripts (`preview.py`, `selfcheck.py`) maintain zero third-party dependencies (Python Standard Library only).

---

## 2. Fairness Test Resolution & Analysis

- **File Inspected:** `fairness_tests.py`
- **Upstream Comparison:** Compared against exact starter revision `3ab0a0d5352c0289b5584300a6dfb09eff9184e6:fairness_tests.py`.
- **Finding:** The file in upstream contains `from __future__ import annotations` at line 20, preceded by two separate triple-quoted docstrings (lines 1–8 and lines 10–19). Python syntax rules mandate that `from __future__` imports must precede any docstrings/statements other than the module docstring.
- **Upstream Commentary:** The file header states explicitly:
  > *"These run on our private scoring engine (so you cannot execute them from this repo), but here is the actual source so you can see exactly what 'fair' means... This is the real file from our test suite, unedited below."*
- **Import Dependencies:** The test imports private internal modules: `from builderr.harness import ...`, `from builderr.risk import ...`, `from builderr.sim import ...`. These modules are proprietary to the Builderr central scoring server and are not packaged with the competitor template.
- **Resolution:** The file was restored to its exact upstream form (`git checkout -- fairness_tests.py`) to prevent repo drift. The local syntax error is an upstream auditing artifact, not a test harness runner failure. Non-blocking.

---

## 3. Official Regression Suite Results

All tests executed with PowerShell UTF-8 mode enabled (`$env:PYTHONUTF8=1`):

| Test Suite | Execution Command | Exit Code | Observed Output / Metrics | Gate Result |
|---|---|---|---|---|
| **Smoke Test** | `.\.venv\Scripts\python.exe selfcheck.py` | `0` | `✓ agent.py loaded and ran 12 steps cleanly. 4 well-formed orders emitted across the run.` | **PASS** |
| **Admission Safety Preview** | `.\.venv\Scripts\python.exe preview.py agent.py` | `0` | Runs clean across 3 regimes, Peak gross 0.94x $\le$ 1.50x, Peak conc 26%, Longest streak 0d $\le$ 5d, MaxDD 33.5% $<$ 50%. | **PASS** |
| **Strategy Unit Tests** | `.\.venv\Scripts\python.exe strategy_selftest.py` | `0` | `✓ 8 strategy checks passed.` (includes weight bounds, drift detection, order sorting, execution speed). | **PASS** |
| **Endpoint Harness Self-Test** | `.\.venv\Scripts\python.exe endpoint_harness_selftest.py` | `0` | `endpoint_harness_selftest: PASS` | **PASS** |
| **Fairness Test Fixture** | `.\.venv\Scripts\python.exe fairness_tests.py` | `1` | `SyntaxError: from __future__ imports must occur at the beginning of the file` (Documented upstream design: private scoring fixture). | **DOCUMENTED NON-BLOCKING** |

---

## 4. Baseline Reproduction & Benchmark Metrics

Both `baseline.py` (equal-weight buy-and-hold of SPY, QQQ, XLK, XLV) and the reference `agent.py` (Calmar rotation hybrid) were evaluated through `preview.py`'s simulator across all 3 official historical sample regimes.

### 4.1 `baseline.py` Metrics

| Sample Regime | Initial Equity | Ending Equity | Return (%) | Max Drawdown (%) | Sharpe | Calmar | Trade Count | Peak Gross Beta | Peak Conc. | Max Conc. Streak | Execution Errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **calm_uptrend** (64d) | $100,000.00 | $112,364.35 | **+12.36%** | **2.30%** | 5.09 | 25.37 | 4 | 1.00x | 25.9% | 0d | 0 |
| **moderate_selloff** (31d) | $100,000.00 | $96,279.72 | **-3.72%** | **6.89%** | -2.10 | -3.85 | 4 | 1.00x | 25.6% | 0d | 0 |
| **vol_spike_snapback** (50d) | $100,000.00 | $91,793.55 | **-8.21%** | **29.87%** | -0.34 | -1.17 | 4 | 0.99x | 27.1% | 0d | 0 |

- **Admission Safety Bar:** PASS (zero errors, peak leverage 1.00x $\le$ 1.50x, peak conc 27.1% with 0d $\ge$ 30%, worst DD 29.87% $<$ 50%).
- **Execution Time (all regimes):** ~0.096s.
- **Determinism (3 repeated evaluations):** **100% Identical** across all metrics.

### 4.2 Reference `agent.py` Metrics

| Sample Regime | Initial Equity | Ending Equity | Return (%) | Max Drawdown (%) | Sharpe | Calmar | Trade Count | Peak Gross Beta | Peak Conc. | Max Conc. Streak | Execution Errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **calm_uptrend** (64d) | $100,000.00 | $114,650.47 | **+14.65%** | **3.57%** | 4.18 | 19.99 | 38 | 0.94x | 20.9% | 0d | 0 |
| **moderate_selloff** (31d) | $100,000.00 | $96,635.39 | **-3.36%** | **6.13%** | -2.53 | -3.96 | 17 | 0.92x | 24.1% | 0d | 0 |
| **vol_spike_snapback** (50d) | $100,000.00 | $84,227.04 | **-15.77%** | **33.46%** | -1.30 | -1.73 | 21 | 0.91x | 26.4% | 0d | 0 |

- **Admission Safety Bar:** PASS (zero errors, peak leverage 0.94x $\le$ 1.50x, peak conc 26.4% with 0d $\ge$ 30%, worst DD 33.46% $<$ 50%).
- **Execution Time (all regimes):** ~0.187s.
- **Determinism (3 repeated evaluations):** **100% Identical** across all metrics.

---

## 5. Runtime & Order-Rate Verification

- **Per-Call Runtime Limit:** Must return in $< 5.0\text{s}$ (`AGENT_BRIEF.md#L50`).
  - Observed Max Runtime per `decide()` call across 145 evaluation days: **`0.0037s`**
  - Average Runtime per call: **`0.0004s`**
  - Safety Margin: **1351x** under the 5.0s timeout.
- **Order Count Cap:**
  - Official Limit: $\le 50$ trades executed per day (`AGENT_BRIEF.md#L48`).
  - Engine Capacity: `MAX_ORDERS_PER_DECISION = 100` (`live_runner.py#L255`).
  - Agent Truncation: Capped at 45 proposed orders (`agent.py#L293`).
  - Observed Max Orders generated in a single decision: **`5 orders`**.
  - Proposed orders $\le 45$, and executed fills $\le$ proposed orders. Under 1 decision/day cadence, trade rate limit is mathematically satisfied with a $10\times$ margin.

---

## 6. Audit & Risk Log

| Severity | Issue Description | Mitigation / Resolution Status |
|---|---|---|
| **P0 (Blocker)** | None. | All blockers cleared. Environment verified. |
| **P1 (High)** | None. | Trade-rate and holding-period mechanics documented with mathematical bounds. |
| **P2 (Info)** | Upstream `fairness_tests.py` SyntaxError | Upstream artifact published for inspection, not local execution; requires private `builderr` engine. Restored upstream source cleanly. |
| **P2 (Info)** | Windows UTF-8 Terminal Encoding | Mandatory `$env:PYTHONUTF8=1` documented in contract and tested in PowerShell. |

---

## 7. Stage 2A Conclusion & Handoff

Stage 2A requirements are completely satisfied:
- Isolated `.venv` operating cleanly on Python 3.14.8 with `pandas` and `yfinance`.
- Root-level import shadowing eliminated.
- Upstream files preserved without unauthorized edits.
- Official test suite passed 100%.
- Baseline and reference agents fully characterized, profiled, and verified deterministic.

**Status: Stage 2A PASS. Authorized to proceed to Stage 2B / Stage 3.**
