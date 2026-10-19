# Builderr Trading Agents — Competition Contract & Technical Specification

**Round:** Builderr Trading Agents — Round 2  
**Target:** 1st Place ($600 Prize + $100,000 Live Account Allocation)  
**Specification Status:** Authoritative Audit (Stage 1 Completed)  
**Audit Timestamp:** 2026-10-19T22:15:00+05:30  
**Upstream Starter HEAD Commit:** `3ab0a0d5352c0289b5584300a6dfb09eff9184e6`  

---

## 1. Official Project References & Sources

1. **Official Competition Portal:**  
   URL: `https://builderr.ai/trading-v0`  
   Authority: Primary authority for challenge rules, prize pool, timeline, live standings, and submission cutoff.

2. **Platform-Wide Guidelines:**  
   URL: `https://builderr.ai/guidelines`  
   Authority: Governing rules for all Builderr challenges (challenge page takes precedence over general text).

3. **Official Starter Repository:**  
   URL: `https://github.com/builderr-ai/builderr-trading-template`  
   Authority: Authoritative reference implementation for function interfaces, universe definitions, local preview harness, and submission templates.

4. **Technical Agent Brief:**  
   URL: `https://github.com/builderr-ai/builderr-trading-template/blob/main/AGENT_BRIEF.md`  
   Authority: Specification for `decide()` interface, parameter schemas, and auto-enforced trading limits.

5. **Official Starter Brief Markdown:**  
   URL: `https://builderr.ai/starter-briefs/trading-agent.md`  
   Authority: Summary guidelines and submission requirements.

6. **Round 1 Winner Archive & Strategy Breakdown:**  
   Project URL: `https://github.com/builderr-ai/builderr-trading-round-1-winner`  
   Explanation URL: `https://builderr.ai/trading-v0/winners/arnav`  
   Authority: Authoritative benchmark for Round 2. Winning agent ("Arnav") scored +5.91% return ($105,911 account value, 37 trades over 16 live market days ending July 2, 2026). Entrants must beat this benchmark.

---

## 2. Competition Parameters & Official Timeline

| Parameter | Official Value | Verification Source |
|---|---|---|
| **Competition Name** | Builderr Trading Agent Challenge — Round 2 | `https://builderr.ai/trading-v0` |
| **Round ID** | `trading-v0-round-2` | `live_runner.py#L138` |
| **Starting Account Equity** | $100,000.00 USD (simulated paper account) | `https://builderr.ai/trading-v0`, `preview.py#L42` |
| **Total Prize Pool** | $1,000 USD (backed by Soham Sinha) | `https://builderr.ai/trading-v0`, `README.md#L127` |
| **Prize Distribution** | 1st: $600 (60%) \| 2nd: $250 (25%) \| 3rd: $150 (15%) | `https://builderr.ai/trading-v0`, `live_runner.py#L258` |
| **Round Start Date** | July 7, 2026 (US market open) | `https://builderr.ai/trading-v0`, `live_runner.py#L140` |
| **Submission & Revision Deadline** | **October 31, 2026, 23:59 IST** | `https://builderr.ai/trading-v0`, `README.md#L121` |
| **Paper Trading End Date** | **November 9, 2026** (16:00 ET US market close) | `https://builderr.ai/trading-v0`, `live_runner.py#L141-L144` |
| **Results Publication Date** | **By November 10, 2026** | `https://builderr.ai/trading-v0`, `live_runner.py#L143` |
| **Primary Objective Metric** | Maximum eligible forward paper-account percentage return | `https://builderr.ai/trading-v0#scoring`, `live_runner.py#L493` |
| **Benchmark Requirement** | Beat previous round's winning agent ("Arnav") | `https://builderr.ai/trading-v0`, `live_runner.py#L260` |
| **Revision Allowance** | Up to 4 revisions before the October 31 cutoff | `https://builderr.ai/trading-v0`, `README.md#L133` |
| **Revision Scoring Effect** | Revisions **reset** scoring forward from the first session after receipt; earlier results are dropped | `live_runner.py#L179-L181, L208-L210` |
| **Real Capital Execution** | Winner (#1) may have their code run on a real $100,000 Nasdaq account with public weekly P&L tracking | `https://builderr.ai/trading-v0`, `README.md#L127` |

---

## 3. Decision Interface & Data Contract

### 3.1 Python Entrypoint Function
The agent must implement exactly one required entrypoint function in `agent.py`:

```python
def decide(
    market_state: dict[str, list[dict[str, object]]],
    portfolio_state: dict[str, object],
    cash: float
) -> list[dict[str, object]]:
    """Generate daily portfolio rebalance orders.
    
    Args:
        market_state: Mapping of ticker -> list of historical daily bars (oldest first).
        portfolio_state: Current portfolio snapshot including cash, positions, last_prices.
        cash: Current available cash float (identical to portfolio_state["cash"]).
        
    Returns:
        List of order dicts: [{"ticker": str, "side": "buy"|"sell", "quantity": float|int}, ...]
    """
    return []
```

### 3.2 Input Schemas

#### A. `market_state`
- **Type:** `dict[str, list[dict]]`
- **Keys:** Ticker symbol string in uppercase (e.g., `"SPY"`, `"QQQ"`, `"AAPL"`, `"NVDA"`).
- **Values:** Chronological list of daily bar dictionaries (~220 bars warmup, oldest at index 0, latest completed bar at index -1).
- **Bar Schema:**
  ```python
  {
      "ts": str,       # Date in ISO format: "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS+00:00"
      "open": float,   # Opening price > 0.0
      "high": float,   # Session high > 0.0
      "low": float,    # Session low > 0.0
      "close": float,  # Closing price > 0.0
      "volume": int|float # Session volume >= 0
  }
  ```
- **Execution Timing & Information Set:** In live scoring (`live_runner.py#L418`), `market_state` contains only bars where `ts < date` (bars strictly prior to the current session date). The agent decides based on information through the prior close.

#### B. `portfolio_state`
- **Type:** `dict[str, object]`
- **Structure:**
  ```python
  {
      "cash": float,       # Current available spendable cash balance
      "positions": [       # List of open position records
          {
              "ticker": str,      # Uppercase ticker symbol
              "quantity": float,  # Number of shares held (> 0.0)
              "avg_cost": float   # Volume-weighted average entry price
          },
          ...
      ],
      "last_prices": {     # Mapping of ticker -> most recent closing price
          "SPY": float,
          "QQQ": float,
          ...
      }
  }
  ```

#### C. `cash`
- **Type:** `float`
- **Semantics:** Convenience copy of `portfolio_state["cash"]`. Spendable buying power without margin borrowing.

### 3.3 Output Schema (`orders`)
- **Type:** `list[dict[str, object]]`
- **Order Dict Format:**
  ```python
  {
      "ticker": str,   # Ticker symbol in universe (case-insensitive, normalized to upper)
      "side": str,     # Exactly "buy" or "sell"
      "quantity": float|int # Finite positive share quantity (> 0.0)
  }
  ```
- **Empty Order List:** Returning `[]` signifies no rebalancing action for the current session.
- **Maximum Orders:** Engine accepts up to 100 orders per decision (`MAX_ORDERS_PER_DECISION = 100` in `live_runner.py#L255`). In `agent.py`, reference caps orders to 45.

---

## 4. Exact Trading Rules & Limits

| Rule | Threshold / Formula | Engine Enforcement | Source Reference |
|---|---|---|---|
| **Directionality** | Long-only | No short selling; sell quantity capped at `min(quantity, held_shares)`. Short orders rejected. | `AGENT_BRIEF.md#L45`, `live_runner.py#L445, L478` |
| **Gross Exposure (Leverage)** | $\le 1.5\times$ Equity ($\sum \|w_i\| \cdot \beta_i \le 1.50$) | Verified at fills and marked close. Purchases scaled or rejected if beta room exceeded. | `preview.py#L37`, `live_runner.py#L254, L465` |
| **Leveraged ETF Multipliers** | 3.0× for 3x ETFs; 2.0× for 2x ETFs; 1.0× all others | Applied to calculate gross beta-adjusted exposure. | `AGENT_BRIEF.md#L52`, `preview.py#L35-L36` |
| **Position Concentration Cap** | $\le 30\%$ of equity per ticker | Single position $> 30\%$ equity for $> 5$ consecutive trading days triggers disqualification. At fill time, purchase notional capped to $0.30 \cdot \text{Equity} - \text{held\_value}$. | `AGENT_BRIEF.md#L47`, `preview.py#L149-L158`, `live_runner.py#L460` |
| **Execution Sequencing** | Sells executed before Buys | Sells execute first, replenishing cash. Buys execute second with available cash. | `live_runner.py#L449-L475`, `agent.py#L254` |
| **Execution Price & Slippage** | Filled at day's OPEN with model slippage | Plain equities: 5 bps ($0.05\%$) slippage. Leveraged ETFs ($\beta > 1$): 10 bps ($0.10\%$) slippage. Buy fill: $\text{open} \cdot (1 + \text{slip})$. Sell fill: $\text{open} \cdot (1 - \text{slip})$. | `preview.py#L40-L41, L111-L133`, `live_runner.py#L251-L252, L451-L454` |
| **Trading Universe** | Frozen snapshot of top ~1,000 liquid US names | Only tickers in `universe.json` are tradeable; outside orders silently ignored. | `universe.json`, `AGENT_BRIEF.md#L56-L61` |
| **Decision Frequency** | Once per trading day | Daily cadence during regular market sessions. | `AGENT_BRIEF.md#L39` |
| **Trade Rate Cap** | $\le 50$ trades per day | Max 50 trades executed per day. | `AGENT_BRIEF.md#L48` |
| **Minimum Holding Period** | $\ge 60$ seconds | Documented operational limit. | `AGENT_BRIEF.md#L49` |
| **Decision Timeout** | $\le 5.0$ seconds runtime | Each `decide()` call must return within 5 seconds. Timeout results in empty order execution for that session. | `AGENT_BRIEF.md#L50`, `README.md#L72` |
| **External Data & Lookahead** | Strict prohibition on lookahead bias | Querying future information or external APIs reflecting future regime data causes instant disqualification. | `README.md#L75-L86`, `builderr.ai/guidelines` |
| **Catastrophic Drawdown Limit** | Drawdown $< 50\%$ across all admission regimes | $> 50\%$ drawdown in any admission regime causes immediate rejection. | `preview.py#L39, L248` |

### 4.1 Beta Multiplier Table

- **3.0× Multiplier:** `TQQQ`, `SOXL`, `UPRO`, `SPXL`, `TNA`, `FAS`, `TECL`, `LABU`, `CURE`, `DRN`, `UDOW`, `NAIL`
- **2.0× Multiplier:** `QLD`, `SSO`, `DDM`, `ROM`, `UWM`, `AGQ`
- **1.0× Multiplier:** All other equities, sector ETFs, and broad market ETFs (e.g., `SPY`, `QQQ`, `AAPL`, `NVDA`, `SMH`)

---

## 5. Scoring & Ranking Methodology

1. **Phase 1 — Admission Gate (Smoke Screen):**
   - Evaluated using `python preview.py` across 3 public sample market windows (`calm_uptrend`, `moderate_selloff`, `vol_spike_snapback`).
   - Gates: Zero execution errors, gross beta exposure $\le 1.50\times$, position concentration $\ge 30\%$ for no more than 5 consecutive days, and maximum drawdown $< 50\%$.
   - Admission is binary (`PASS` / `FAIL`). Preview metrics do **not** contribute to leaderboard rank.

2. **Phase 2 — Live Forward Scoring (Leaderboard Ranking):**
   - Evaluated on live market prices starting from each bot's official `ENTRY` session through November 9, 2026.
   - Initial equity: $100,000.00.
   - Metric: Percentage account return: $\text{Return} = \frac{\text{Ending Equity} - 100,000}{100,000}$.
   - Benchmark: Must beat Arnav's final return (+5.91% in Round 1, re-scored forward in Round 2).

3. **Phase 3 — Winner Verification & Audit Gate:**
   - Top 3 leaderboard finishes are **provisional**.
   - Entrants must provide read-only source access to the exact scored agent version.
   - Builderr audits code for reproducibility from saved point-in-time inputs and screens for lookahead bias and rule violations.
   - Non-reproducible or non-compliant entries are disqualified; the next eligible entry moves up.

---

## 6. Analysis of Documentation Discrepancies (Task F)

An exhaustive Git audit of `agent.py`, `README.md`, `START_HERE.md`, and `ANATOMY.md` resolved the discrepancy between "Calmar Rotation Hybrid" and "Forward-Return Rotation Hybrid":

1. **Historical Root:**
   - In Round 1 (June 2 – July 2, 2026), the competition objective was explicitly **Calmar Ratio** (annualized return divided by maximum drawdown).
   - In commit `0f8a0bb262` (June 1, 2026), the starter template introduced `agent.py` with docstring:
     `"""Calmar Rotation Hybrid. Contest objective: maximize 60-day forward Calmar, not raw return."""`
2. **Round 2 Transition:**
   - For Round 2 (launched July 7, 2026), the organizers updated the competition rules to rank by **forward percentage return** over the live paper account.
   - In commit `978a9322df` (July 7, 2026), `README.md` was updated to:
     `## Submitted agent: Forward-Return Rotation Hybrid`
     `agent.py is a no-network, no-LLM strategy built for the live forward-return ranking (Round 2: July 7 – November 9, 2026): Ranked by forward return...`
   - However, the author neglected to update the docstring at the top of `agent.py`, as well as legacy commentary in `START_HERE.md` and `ANATOMY.md`.
3. **Conclusion:**
   - The discrepancy is **documentation drift**.
   - The official, binding competition metric for Round 2 is **Paper-Account Forward Return** (with an admission safety check gating against $> 50\%$ drawdown).

---

## 7. Submission Routes & Security Audit

| Option | Mechanics | Edge Protection | Operational Complexity | Recommendation |
|---|---|---|---|---|
| **Public GitHub Repo** | Push to public repo; email URL to `submit@builderr.ai`. | None (code visible to all competitors). | Lowest (zero setup). | Acceptable for open-source strategies; not recommended for proprietary edge. |
| **Private Repo + Deploy Key** | Keep repo private; email `submit@builderr.ai` to request a read-only deploy key; paste key into `Settings -> Deploy keys` (write access OFF); notify Builderr; delete key after clone. | High (code remains private during live round). | Low (~2 minutes setup, 1 email exchange). | **RECOMMENDED**. Strongest balance of IP protection and audit reproducibility. |
| **HTTPS Endpoint Mode** | Host endpoint serving `POST /decide` returning `{orders: [...]}`; email endpoint URL. Pre-session captures hashed for replay. | Highest during live round, but provisional top-3 must provide full source code for audit before prize release. | High (requires 24/7 server hosting, HTTPS, DNS compliance). | Unnecessary operational overhead for pure Python strategies. |

---

## 8. Stage 2 Readiness Specification

Stage 2 focuses on environment reproduction, baseline verification, and determinism testing.

- **Target Python Version:** Python 3.10 to 3.14 (Verified working on local Python 3.14.8).
- **Core Dependencies:** Zero third-party dependencies required for `agent.py`, `selfcheck.py`, and `preview.py` (Standard Library only).
- **Windows Platform Requirement:** PowerShell environment variable `$env:PYTHONUTF8=1` must be set to prevent `UnicodeEncodeError` when printing checkmark characters (`✓`, `✗`).
- **Reproducibility Commands:**
  ```powershell
  # 1. Smoke test on synthetic bars
  $env:PYTHONUTF8=1; python selfcheck.py
  
  # 2. Admission safety preview across 3 public market regimes
  $env:PYTHONUTF8=1; python preview.py
  
  # 3. Strategy unit checks
  $env:PYTHONUTF8=1; python strategy_selftest.py
  ```
- **Preserved Starter Files:** `agent.py`, `baseline.py`, `preview.py`, `selfcheck.py`, `strategy_selftest.py`, `sample_regimes.json.gz`, `universe.json`, `requirements.txt`.
