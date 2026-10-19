# Builderr Trading Agents — Permanent Stage Status Board

**Project:** Builderr Trading Agents — Round 2  
**Target:** 1st Place ($600 Prize out of $1,000 Pool + Potential $100,000 Live Account Deployment)  
**Last Updated:** 2026-10-19T23:05:00+05:30  
**Repository Branch:** `main`  
**Upstream Starter HEAD:** `3ab0a0d5352c0289b5584300a6dfb09eff9184e6`  

---

## Stage Progress Board

| # | Stage Name | Status | Verification Evidence | Blockers | Commit SHA | Next Action |
|---|---|---|---|---|---|---|
| **1** | **Official Rules and Contract** | **PASS** | Audited live competition page (`builderr.ai/trading-v0`), guidelines, starter brief, and Round 1 winner repository. Cloned upstream starter at commit `3ab0a0d`. Confirmed function signature `decide(market_state, portfolio_state, cash)`, exact trading caps (1.5x beta-gross, 30% concentration over 5d, 50 trades/day, 60s min hold, 5s timeout, long-only), execution fill rules, and scoring reset on revisions. Analyzed Calmar vs forward-return docstring drift. Executed `selfcheck.py`, `preview.py`, `strategy_selftest.py`, and `endpoint_harness_selftest.py`. Created `docs/competition-contract.md` and `docs/compliance-matrix.md`. | None | `d1a36d0` | Hand off to Stage 2 for environment setup and baseline replication. |
| **2** | **Starter Reproduction & Environment Repair (Stage 2A)** | **PASS** | Created isolated `.venv` (Python 3.14.8, pandas 3.0.6, yfinance 1.7.0, numpy 2.5.4). Deleted root stub `yfinance.py`; verified zero module shadowing. Diagnosed `fairness_tests.py` SyntaxError as upstream audit fixture; restored upstream source without corruption. Verified full regression suite (selfcheck, preview, strategy_selftest, endpoint_harness_selftest all PASS). Measured `decide()` max runtime 0.0028s (limit 5.0s) and max orders 5 (limit 45 agent / 50 rule). Profiled and verified 100% determinism of `baseline.py` (+12.36%, -3.72%, -8.21%) and `agent.py` (+14.65%, -3.36%, -15.77%). Documented in `docs/stage2-baseline.md` and `docs/stage2a-final-verification.md`. | None | `77de9e9` | Hand off to Stage 3 for simulator and execution audit. |
| **3** | **Simulator and Execution Audit** | **NOT_STARTED** | Preliminary inspection of `preview.py` and `live_runner.py` fill models completed in Stage 1. | None | TBD | Audit exact slippage, order-book queuing, partial fills, and mark-to-market mechanics. |
| **4** | **Historical Data and Leakage Audit** | **NOT_STARTED** | Warmup bar structure (~220 days) and date filtering inspected in Stage 1. | None | TBD | Validate data sanitization, verify timestamp alignment, and audit for zero lookahead across regimes. |
| **5** | **Baseline and Winner Benchmark** | **NOT_STARTED** | Round 1 winner performance (+5.91%, 37 trades) documented from official archive. | None | TBD | Profile baseline agent and replicate benchmark behavior locally against sample regimes. |
| **6** | **Strategy Research and Experiments** | **NOT_STARTED** | None. (Strict Stage 1 constraint: no speculative optimization permitted). | None | TBD | Formulate falsifiable trading hypotheses based on momentum, trend-following, and regime detection. |
| **7** | **Strategy Selection and Optimization** | **NOT_STARTED** | None. | None | TBD | Select top candidate strategy based on out-of-sample forward return and drawdown containment. |
| **8** | **Portfolio Risk Controls** | **NOT_STARTED** | Beta multiplier definitions (3x, 2x, 1x) and concentration checks audited in Stage 1. | None | TBD | Build dedicated risk-overlay layer to programmatically guarantee zero cap breaches. |
| **9** | **Final Agent Integration** | **NOT_STARTED** | Reference structure in `agent.py` audited in Stage 1. | None | TBD | Integrate core alpha strategy with risk management layer into compliant `agent.py`. |
| **10** | **Comprehensive Verification** | **NOT_STARTED** | None. | None | TBD | Execute end-to-end multi-regime backtests, stress tests, secret scans, and deterministic replays. |
| **11** | **Submission Readiness** | **NOT_STARTED** | Submission routes (public repo, private deploy key, endpoint) evaluated in Stage 1. | None | TBD | Package private repository, configure read-only deploy key, and prepare submission email. |
| **12** | **Forward Monitoring and Revisions** | **NOT_STARTED** | Revision allowance (up to 4 revisions, score resets forward) documented in Stage 1. | None | TBD | Monitor live leaderboard P&L and evaluate necessity of forward revisions before cutoff. |
