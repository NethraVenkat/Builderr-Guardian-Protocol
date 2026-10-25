# GUARDIAN ALPHA V30 — STAGE 3F ALL-VERSION PAPER-TRADING TOURNAMENT

**PARTIAL scientific completion: all 68 inventoried executable entries ran, but real historical evaluation is BLOCKED and exact official contract parity is PARTIAL.** This is an executed offline synthetic tournament, not a prospective performance certification. **BEST ON TESTED SAMPLE — NOT ESTABLISHED AS BEST PROSPECTIVELY.**

## Checkpoint and preservation

Branch `archive/v30-stage2h-final-evidence-freeze`; HEAD `4540ee49dac29e4599fbbeb96bbcffd2dafd6705`; parent `ce6b4c21b832044d0ffb45dce2ba949ab867d520`. Archive commit deltas are 198 and 87 added files. 334 explicitly allowlisted historical code/report/Stage3D–3E evidence files have unchanged before/after hashes. Tracked working-tree status remains empty. Tier3/cache contents were never inspected, including for availability. No original file was edited, no Git mutation occurred, and no external actions were taken.

| Protected source | Mode | SHA-256 | Match |
|---|---|---|---|
| agent.py | raw | 46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd | True |
| universe.json | lf | 66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd | True |
| research/strategies/v12_candidate_ae.py | lf | 978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793 | True |
| research/strategies/v30_candidate_d2_cash_cushion.py | raw | 5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215 | True |

Preservation hashing covers code, root/documentation reports and the uncommitted Stage3D–3E evidence allowlist; it deliberately does not claim byte verification of forbidden market data. The 285 archived paths are registered without opening raw observations. The Git checkpoint protects archive identity. No cache traversal or whole-repository content hash was attempted.

## Coverage, execution and timing

| Measure | Actual |
|---|---|
| candidate_entries | 68 |
| implementation_upper_bound_after_proven_wrapper_alias | 67 |
| unique_semantics_not_proved | True |
| duplicate_references | 37 |
| source_files | 41 |
| fully_successful_candidates | 68 |
| failed_candidates | 0 |
| base_simulations | 2176 |
| sensitivity_simulations | 12 |
| total_simulations | 2188 |
| total_scored_sessions | 331632 |
| measured_tournament_seconds | 1681.5472461 |
| sum_simulation_seconds | 1318.170541700063 |
| independent_verification_seconds | 1080.9286365000007 |
| measured_preparation_to_report_seconds | 2588.814744234085 |
| earlier_read_only_inspection | not covered by the preparation timer; no precise full-turn duration claimed |
| maximum_planned_minutes | 360 |
| all_preserved | True |
| preserved_files | 334 |

The 68 entries are distinct source/entry/parameter/dependency keys, not 68 proved different economic algorithms. C038/C039 are the same default class and its delegating module wrapper; both were run and flagged. After this alias the upper bound is 67 implementations; additional semantic equivalence is NOT VERIFIED. Historical renamed starter bots were followed through Git. V29/V29E publication/evidence stages did not establish separate trading logic. The prior 43-trial count includes accounting and parameter sweeps; undocumented missing configurations were not invented. Exact source references and 37 duplicate references are in the inventory and deduplication registers.

All inventoried entries completed 32 base runs: 30 stress paths of 126 scored sessions plus two independent 504-session long-cycle paths. Each has 220 warmup bars. E0/D2 completed 12 additional sensitivity runs in total. Failures and noncompliance are distinct. The tournament process exit code is 0.

Timing is actual machine-measured time. The six-hour allocation is a maximum plan, not elapsed work. Preparation-to-report timing excludes the earlier read-only inspection; this audit does not invent a precise whole-conversation duration. The verifier overlaps input-hash preparation with the final tournament runs and waits for the tournament exit receipt before reading the complete run set, so its wall time includes that wait. Runtime metadata and execution command/exit receipts are preserved.

## Data, fairness and contract limitations

Only new, independently seeded synthetic OHLCV paths were loaded. Symbols are identifiers from the frozen 1,000-name universe; 30 symbols referenced by strategy source have observations, equally available to every candidate. Invented weekday timestamps begin 2000-01-03 and end before 2022; they are not historical observations or an exchange holiday calendar. The 126-session evaluation window and 504-session evaluation window are recorded in every run manifest. No market observation, calibrated return statistic or old expected result seeded the generator.

Exact synthetic windows: warmup 2000-01-03 through 2000-11-03 (220 invented weekdays); short stress evaluation 2000-11-06 through 2001-04-30 (126 sessions); long-cycle evaluation 2000-11-06 through 2002-10-10 (504 sessions). These date labels are fictional time coordinates, not claims that those market observations were used.

Real Tiingo Tier1/Tier2 evaluation is BLOCKED by the no-cache rule. Tier2 is a reused development sample, never independent OOS. Tier3 remains sealed. The public sample fixture was not opened, hashed or decompressed: V29F records UNKNOWN underlying provenance/derived rights, conflicting with the later Stage3D assertion of permission. No legal grant is inferred from repository custody or software licensing.

| Rule | Implementation / qualification | Local evidence | Parity |
|---|---|---|---|
| Interface | decide(market_state, portfolio_state, cash) | AGENT_BRIEF.md; live_runner.py:418-437 | MATCH |
| Universe | frozen 1000 identifiers; 30 strategy-referenced identifiers have synthetic observations; all other symbols unavailable equally | universe.json; configuration_preregistered.json | PARTIAL universe coverage |
| Capital | $100,000; long only, no margin cash | live_runner.py:137,449-485 | MATCH |
| Warmup | 220 prior bars maximum supplied, including 220 initial bars per observed symbol | README.md; live_runner.py:136 | documented window; runner passes growing history |
| Decision/fill | prior completed bars; next session opening fill | live_runner.py:418-454 | MATCH on common domain |
| Preview distinction | preview starts cash-only on first evaluated day, then fills pending orders; scoring runner decides before first scored open | preview.py:run_regime; live_runner.py:run_bot | explicit difference |
| Prices to strategy | prior closes only; current opens never in strategy input | live_runner.py:418-425 | MATCH |
| Fees | zero explicit commission in base; 5bp plain/10bp leveraged slippage; adverse direction | live_runner.py:251-252,451-485 | MATCH base |
| Sell order | stable sells before buys; oversells clipped to held shares | live_runner.py:449-485 | MATCH |
| Buy limits | cash, 30% fill notional concentration room and beta-adjusted 1.5x room | live_runner.py:455-471 | MATCH base; close drift recorded separately |
| Orders/trades | 100 proposed orders; 50 actual fills maximum per day | live_runner.py:255; AGENT_BRIEF.md:48 | PARTIAL: runner lacks 50-fill clamp; published rule enforced here |
| Concentration | >=30% for >5 consecutive close marks is a breach | preview.py:149-158 | local-code interpretation; prose has inconsistent inequalities |
| Drawdown | initial cash included in peak; >=50% flagged, not retrospectively suppressed | preview.py:_max_drawdown/main | PARTIAL: fixes initial-peak omission and retains complete failed path |
| Missing bars | reject if no current open; carry last known close for existing positions | local source uses zero for missing marks despite Stage 3E carry claim | RESEARCH CORRECTION, not exact parity |
| Corporate actions | split shares and historical signal scale on ex-date; dividend entitlement receivable and cash at pay date | local runner has no action implementation | RESEARCH EXTENSION; parity UNKNOWN |
| Timeout | measure each decision; discard orders if >5 seconds after return | AGENT_BRIEF.md | PARTIAL: no preemptive timeout; measured decisions reported |
| Holding period | daily batch; no intraday fill timestamps; no exchange latency model | AGENT_BRIEF.md | NOT VERIFIED intraday 60-second enforcement |
| Valuation | cash plus closing position value plus dividend receivables; stale marks retained | source arithmetic plus explicit research extensions | PARTIAL overall |
| Benchmark | current baseline.py, four ETF equal initial allocations under same engine (C006); QQQ benchmark also runs as candidate | baseline.py; inventory.json | MATCH equal conditions |
| Scoring | compliant forward percentage return is the locally documented objective; synthetic runs cannot establish official score | docs/competition-contract.md section 5 | official unseen evaluator parity NOT VERIFIED |

All strategies receive fresh isolated source namespaces, original source/default parameters, independent cash/positions, equal prior-only histories and the same execution model. Class instances bind their existing decide method. Scratch adapters compile unchanged definition ASTs while omitting top-level old-data loaders and report writers; inputs/outputs are untranslated, no original file is modified, and AST/source identity is tested. This preserves decision code but does not certify equivalence to every original historical driver. Missing current bars reject fills and carry stale marks; stale-price liquidity is not assumed. Negative cash and short sales are blocked. Corporate actions are invented explicit split/ex-date/payment events; they are not a claim about the official evaluator.

Corporate-action NAV includes unpaid dividend receivables, while the original cash/positions/last_prices strategy interface does not expose receivables as spendable cash. This known interface limitation applies identically to all candidates. Split histories are adjusted only when the split is effective; no future action is revealed. The synthetic leveraged products use daily amplified latent-factor returns and invented expense drag; they are not calibrated replicas of actual ETF tracking behavior.

The benchmark is the preserved four-ETF baseline C006 under the same conditions. Sharpe uses arithmetic daily excess returns versus zero risk-free rate and sample standard deviation with 252 annualization; Sortino uses RMS of negative daily returns including zeros. Total return includes first-day P&L versus initial $100,000. CAGR and Calmar are N/A below 252 scored sessions, and ratios with zero denominators are N/A. Turnover is gross absolute fill notional / initial equity, not half-turnover. Monthly blocks are synthetic calendar bins with partial months explicitly flagged. VaR/ES are descriptive empirical 5% tails; no probability calibration is claimed. Decision runtime is measured; exchange latency is not modeled.

Reported peak exposure and drawdown are based on daily closing portfolio marks, not intraday high/low paths. Purchases are constrained by the reference opening-fill room calculations; price-driven later breaches are flagged rather than hidden by forced liquidation. Empirical tail metrics use ceil(0.05 × session count) observations, so finite-sample tail mass can exceed exactly 5%.

## Conditional findings

Risk-adjusted long-cycle leader among compliant paths: C008 (drawdown_momentum.py:decide), mean path Sharpe 4.281. Capital-preservation leader among candidates compliant on all stress paths: C003, worst stress drawdown 0.00%. These are different objectives, not a universal ranking.

| Synthetic path | Best compliant return entry | Return | Lowest raw return entry | Return | Lowest-entry compliance |
|---|---|---|---|---|---|
| bear_310601 | C003 | 0.00% | C015 | -37.95% | PASS |
| bear_310619 | C003 | 0.00% | C015 | -22.26% | PASS |
| bull_310601 | C015 | 35.02% | C003 | 0.00% | PASS |
| bull_310619 | C015 | 32.16% | C003 | 0.00% | PASS |
| corporate_actions_310601 | C015 | 12.57% | C055 | -4.83% | PASS |
| corporate_actions_310619 | C015 | 24.60% | C003 | 0.00% | PASS |
| crash_310601 | C003 | 0.00% | C015 | -54.12% | FAILED |
| crash_310619 | C003 | 0.00% | C015 | -57.77% | FAILED |
| fast_recovery_310601 | C017 | 66.25% | C019 | -30.42% | PASS |
| fast_recovery_310619 | C060 | 44.60% | C013 | -4.97% | PASS |
| high_volatility_310601 | C008 | 9.90% | C009 | -13.06% | PASS |
| high_volatility_310619 | C003 | 0.00% | C015 | -57.51% | FAILED |
| leveraged_decay_310601 | C032, C033 | 2.52% | C011 | -18.97% | PASS |
| leveraged_decay_310619 | C031 | 5.67% | C011 | -22.44% | PASS |
| liquidity_shock_310601 | C015 | 37.64% | C056 | -15.49% | PASS |
| liquidity_shock_310619 | C010 | 3.85% | C056 | -36.87% | PASS |
| long_cycle_310601 | C033 | 193.95% | C003 | 0.00% | PASS |
| long_cycle_310619 | C032 | 155.30% | C003 | 0.00% | PASS |
| missing_bars_310601 | C015 | 13.23% | C003 | 0.00% | PASS |
| missing_bars_310619 | C013 | 3.32% | C006 | -1.92% | PASS |
| opening_gap_310601 | C003 | 0.00% | C062 | -23.91% | PASS |
| opening_gap_310619 | C003 | 0.00% | C015 | -28.39% | PASS |
| sector_rotation_310601 | C054 | 15.58% | C008 | -2.17% | PASS |
| sector_rotation_310619 | C056 | 11.87% | C007 | -0.21% | FAILED |
| sideways_310601 | C010 | 0.67% | C015 | -4.66% | PASS |
| sideways_310619 | C003 | 0.00% | C015 | -15.24% | PASS |
| slow_recovery_310601 | C003 | 0.00% | C015 | -49.52% | FAILED |
| slow_recovery_310619 | C017 | 3.72% | C015 | -44.46% | FAILED |
| technology_drawdown_310601 | C042 | 5.33% | C015 | -21.39% | PASS |
| technology_drawdown_310619 | C014 | 0.94% | C015 | -29.59% | PASS |
| volatility_spike_310601 | C029 | 71.84% | C003 | 0.00% | PASS |
| volatility_spike_310619 | C017 | 3.56% | C015 | -25.21% | PASS |

Winner/loser explanations are conditional on the imposed scenario: bull paths reward sustained risk exposure; crash/bear and tech shocks punish prior holdings before any causal exit; cash-heavy rules can reduce losses while sacrificing rebounds; rotation and high volatility expose churn and whipsaw; transaction costs are charged to every actual fill. Exact source objectives, daily positions, cash fractions, turnover and fees allow these mechanisms to be audited. A low-return or noncompliant result is retained, not labeled an execution failure. No causal explanation beyond these observed paths establishes future superiority.

## E0 versus D2

E0 is C001 (`agent.py`); frozen D2 is C032. D2 source uses XLP 18%, XLU 18%, XLV 14%, with 50% target cash and no XLE during risk-off. An older Stage2E matrix describes different weights; the frozen source, not that erroneous summary, was executed. The paired table reports D2 minus E0; a negative drawdown difference means D2 reduced drawdown. Common defensive sessions use the E0 prior-data risk gate. False-alarm cash drag is only a retrospective diagnostic. Full cash/shortfall and return-sacrificed ratios are in the paired JSON.

| Dataset | Execution | E0 return | D2 return | Return delta | Drawdown delta | Mean cash delta |
|---|---|---|---|---|---|---|
| bear_310601 | base | -10.72% | -6.88% | 3.85% | -3.78% | 26.51% |
| bear_310619 | base | -10.16% | -7.06% | 3.10% | -3.10% | 27.52% |
| bull_310601 | base | 23.64% | 22.88% | -0.76% | -0.00% | 5.69% |
| bull_310619 | base | 12.55% | 10.92% | -1.63% | 0.40% | 10.88% |
| corporate_actions_310601 | base | 0.81% | -0.41% | -1.22% | -0.26% | 12.13% |
| corporate_actions_310619 | base | 12.75% | 12.22% | -0.53% | 0.04% | 3.54% |
| crash_310601 | base | -15.12% | -7.52% | 7.59% | -7.29% | 24.30% |
| crash_310619 | base | -16.66% | -8.50% | 8.16% | -8.09% | 31.69% |
| fast_recovery_310601 | base | 16.11% | 10.99% | -5.12% | 0.18% | 10.14% |
| fast_recovery_310619 | base | 28.80% | 29.70% | 0.90% | -4.98% | 10.71% |
| high_volatility_310601 | base | 1.74% | 2.71% | 0.97% | -2.89% | 26.85% |
| high_volatility_310619 | base | -11.70% | -4.59% | 7.11% | -8.79% | 31.37% |
| leveraged_decay_310601 | base | -0.01% | 2.52% | 2.53% | -1.01% | 28.84% |
| leveraged_decay_310619 | base | 2.99% | 5.31% | 2.32% | -0.00% | 27.94% |
| liquidity_shock_310601 | base | 13.65% | 14.24% | 0.60% | -0.48% | 2.50% |
| liquidity_shock_310619 | base | -13.51% | -13.07% | 0.45% | -0.43% | 8.54% |
| long_cycle_310601 | base | 181.39% | 191.84% | 10.45% | -4.19% | 12.35% |
| long_cycle_310601 | zero_cost | 186.28% | 196.67% | 10.39% | -4.10% | 12.22% |
| long_cycle_310601 | high_cost | 152.45% | 165.07% | 12.61% | -4.05% | 12.36% |
| long_cycle_310601 | close_fill | 183.85% | 194.75% | 10.90% | -4.01% | 12.26% |
| long_cycle_310619 | base | 142.97% | 155.30% | 12.33% | -4.58% | 14.16% |
| long_cycle_310619 | zero_cost | 146.45% | 158.75% | 12.30% | -4.51% | 14.15% |
| long_cycle_310619 | high_cost | 122.20% | 135.42% | 13.22% | -4.99% | 14.27% |
| long_cycle_310619 | close_fill | 142.54% | 153.48% | 10.94% | -4.09% | 14.12% |
| missing_bars_310601 | base | 11.25% | 11.22% | -0.03% | -0.92% | 12.84% |
| missing_bars_310619 | base | 2.13% | 2.14% | 0.01% | 0.18% | 17.08% |
| opening_gap_310601 | base | -20.23% | -20.62% | -0.39% | -0.15% | 20.36% |
| opening_gap_310619 | base | -18.61% | -19.06% | -0.45% | -0.28% | 16.85% |
| sector_rotation_310601 | base | 3.35% | 3.15% | -0.20% | -0.22% | 10.40% |
| sector_rotation_310619 | base | 5.19% | 4.87% | -0.32% | -0.04% | 15.49% |
| sideways_310601 | base | -4.20% | -3.16% | 1.04% | -1.66% | 14.49% |
| sideways_310619 | base | -2.54% | -0.79% | 1.75% | -2.14% | 28.39% |
| slow_recovery_310601 | base | -16.14% | -10.11% | 6.02% | -6.24% | 22.85% |
| slow_recovery_310619 | base | -8.21% | -1.36% | 6.85% | -6.78% | 23.34% |
| technology_drawdown_310601 | base | 3.14% | 2.13% | -1.01% | 0.42% | 16.45% |
| technology_drawdown_310619 | base | -1.46% | -1.32% | 0.15% | -0.90% | 24.10% |
| volatility_spike_310601 | base | 61.58% | 64.28% | 2.71% | -1.49% | 11.89% |
| volatility_spike_310619 | base | -4.93% | -2.04% | 2.89% | -4.49% | 18.97% |

Stage3B-R2 found that the small-sample joint HAC/bootstrap procedure did not control nominal test size: its report records 7.70–10.80% null-boundary rejection at N=30 against nominal 5%. That failed finding remains intact. This tournament performs no significance or confirmatory superiority test and does not reuse that procedure.

## Full risk-adjusted leaderboard

Long-cycle paths only, 504 sessions per seed. Sorted by mean of the two path Sharpes; noncompliant entries remain visible and are ineligible for the compliant-leader conclusion. Full hashes are provided in the inventory and machine-readable leaderboard.

| Entry | Sessions | Mean return | Mean CAGR | Mean Sharpe | Mean Sortino | Worst DD | Compliance |
|---|---|---|---|---|---|---|---|
| C008 | 1008 | 139.73% | 54.79% | 4.281 | 9.168 | 12.78% | PASS |
| C019 | 1008 | 165.95% | 62.90% | 4.087 | 8.609 | 17.74% | PASS |
| C033 | 1008 | 172.48% | 64.94% | 4.080 | 8.280 | 16.67% | PASS |
| C025 | 1008 | 159.69% | 61.01% | 4.055 | 8.456 | 17.47% | PASS |
| C068 | 1008 | 159.69% | 61.01% | 4.055 | 8.456 | 17.47% | PASS |
| C032 | 1008 | 173.57% | 65.31% | 4.054 | 8.076 | 15.10% | PASS |
| C013 | 1008 | 64.88% | 28.38% | 4.038 | 8.570 | 8.13% | PASS |
| C018 | 1008 | 158.29% | 60.58% | 4.024 | 8.388 | 17.72% | PASS |
| C049 | 1008 | 170.29% | 64.28% | 3.998 | 7.943 | 16.93% | PASS |
| C021 | 1008 | 151.84% | 58.58% | 3.964 | 8.196 | 17.95% | PASS |
| C064 | 1008 | 151.84% | 58.58% | 3.964 | 8.196 | 17.95% | PASS |
| C012 | 1008 | 69.10% | 30.04% | 3.944 | 9.065 | 13.91% | PASS |
| C031 | 1008 | 168.46% | 63.74% | 3.943 | 7.776 | 17.11% | PASS |
| C051 | 1008 | 158.27% | 60.68% | 3.939 | 8.208 | 16.93% | PASS |
| C022 | 1008 | 167.05% | 63.30% | 3.905 | 7.674 | 18.28% | PASS |
| C065 | 1008 | 167.05% | 63.30% | 3.905 | 7.674 | 18.28% | PASS |
| C048 | 1008 | 165.60% | 62.87% | 3.894 | 7.650 | 17.91% | PASS |
| C017 | 1008 | 145.70% | 56.63% | 3.866 | 7.398 | 16.39% | PASS |
| C009 | 1008 | 112.52% | 45.57% | 3.829 | 7.409 | 18.93% | FAILED |
| C026 | 1008 | 163.29% | 62.14% | 3.825 | 7.516 | 20.18% | PASS |
| C035 | 1008 | 162.13% | 61.83% | 3.824 | 7.485 | 19.09% | PASS |
| C020 | 1008 | 161.47% | 61.58% | 3.818 | 7.487 | 20.26% | PASS |
| C063 | 1008 | 161.47% | 61.58% | 3.818 | 7.487 | 20.26% | PASS |
| C038 | 1008 | 156.10% | 59.92% | 3.815 | 7.439 | 19.13% | PASS |
| C039 | 1008 | 156.10% | 59.92% | 3.815 | 7.439 | 19.13% | PASS |
| C036 | 1008 | 160.96% | 61.45% | 3.807 | 7.439 | 19.74% | PASS |
| C034 | 1008 | 159.95% | 61.15% | 3.807 | 7.444 | 19.27% | PASS |
| C024 | 1008 | 164.17% | 62.43% | 3.802 | 7.393 | 19.60% | PASS |
| C047 | 1008 | 164.17% | 62.43% | 3.802 | 7.393 | 19.60% | PASS |
| C067 | 1008 | 164.17% | 62.43% | 3.802 | 7.393 | 19.60% | PASS |
| C045 | 1008 | 163.17% | 62.11% | 3.800 | 7.384 | 19.71% | PASS |
| C046 | 1008 | 163.59% | 62.24% | 3.798 | 7.375 | 19.65% | PASS |
| C001 | 1008 | 162.18% | 61.81% | 3.792 | 7.360 | 19.68% | PASS |
| C002 | 1008 | 162.18% | 61.81% | 3.792 | 7.360 | 19.68% | PASS |
| C027 | 1008 | 162.18% | 61.81% | 3.792 | 7.360 | 19.68% | PASS |
| C029 | 1008 | 162.18% | 61.81% | 3.792 | 7.360 | 19.68% | PASS |
| C040 | 1008 | 159.55% | 61.01% | 3.791 | 7.353 | 19.63% | PASS |
| C041 | 1008 | 159.55% | 61.01% | 3.791 | 7.353 | 19.63% | PASS |
| C052 | 1008 | 162.32% | 61.84% | 3.789 | 7.344 | 20.01% | PASS |
| C037 | 1008 | 159.02% | 60.86% | 3.788 | 7.357 | 19.49% | PASS |
| C028 | 1008 | 158.50% | 60.68% | 3.776 | 7.330 | 19.36% | PASS |
| C030 | 1008 | 158.50% | 60.68% | 3.776 | 7.330 | 19.36% | PASS |
| C023 | 1008 | 160.70% | 61.34% | 3.762 | 7.292 | 20.64% | PASS |
| C066 | 1008 | 160.70% | 61.34% | 3.762 | 7.292 | 20.64% | PASS |
| C050 | 1008 | 122.72% | 49.19% | 3.708 | 7.203 | 17.82% | PASS |
| C062 | 1008 | 136.70% | 53.75% | 3.706 | 7.172 | 19.60% | PASS |
| C060 | 1008 | 137.22% | 53.92% | 3.705 | 7.121 | 17.59% | PASS |
| C014 | 1008 | 59.96% | 26.46% | 3.631 | 7.251 | 12.31% | PASS |
| C061 | 1008 | 134.09% | 52.91% | 3.618 | 6.893 | 18.53% | PASS |
| C057 | 1008 | 131.73% | 52.13% | 3.561 | 6.779 | 21.34% | PASS |
| C053 | 1008 | 132.24% | 52.30% | 3.561 | 6.736 | 19.18% | PASS |
| C059 | 1008 | 132.24% | 52.30% | 3.561 | 6.736 | 19.18% | PASS |
| C055 | 1008 | 132.53% | 52.33% | 3.558 | 6.795 | 21.31% | PASS |
| C011 | 1008 | 73.61% | 31.74% | 3.517 | 6.550 | 13.38% | PASS |
| C058 | 1008 | 128.10% | 50.90% | 3.470 | 6.558 | 23.45% | PASS |
| C054 | 1008 | 127.15% | 50.51% | 3.434 | 6.468 | 24.23% | PASS |
| C056 | 1008 | 126.38% | 50.25% | 3.426 | 6.451 | 23.61% | PASS |
| C042 | 1008 | 86.73% | 36.55% | 2.973 | 5.218 | 24.12% | FAILED |
| C016 | 1008 | 30.09% | 14.05% | 2.562 | 4.307 | 15.92% | FAILED |
| C004 | 1008 | 122.69% | 48.99% | 2.560 | 4.243 | 38.21% | PASS |
| C005 | 1008 | 139.99% | 53.44% | 2.491 | 4.233 | 44.05% | FAILED |
| C043 | 1008 | 65.94% | 28.81% | 2.490 | 4.177 | 31.91% | PASS |
| C010 | 1008 | 60.61% | 26.62% | 2.475 | 4.337 | 34.83% | PASS |
| C007 | 1008 | 47.69% | 21.50% | 2.366 | 3.836 | 24.64% | FAILED |
| C015 | 1008 | 132.02% | 51.82% | 2.199 | 3.507 | 50.19% | FAILED |
| C044 | 1008 | 76.11% | 32.59% | 2.147 | 3.382 | 36.60% | PASS |
| C006 | 1008 | 64.61% | 28.27% | 2.079 | 3.270 | 34.35% | FAILED |
| C003 | 1008 | 0.00% | 0.00% | N/A | N/A | 0.00% | PASS |

## Full capital-preservation leaderboard

| Entry | Sessions | Worst DD | Worst return | Mean exposure | Trades | Catastrophe paths | Compliance |
|---|---|---|---|---|---|---|---|
| C003 | 3780 | 0.00% | 0.00% | 0.00% | 0 | 0 | PASS |
| C016 | 3780 | 20.66% | -17.39% | 28.31% | 30 | 0 | FAILED |
| C012 | 3780 | 24.08% | -11.12% | 37.64% | 279 | 0 | PASS |
| C013 | 3780 | 26.96% | -25.04% | 45.35% | 1245 | 0 | PASS |
| C011 | 3780 | 27.44% | -22.44% | 54.74% | 1349 | 0 | PASS |
| C014 | 3780 | 28.62% | -26.74% | 48.59% | 1320 | 0 | PASS |
| C017 | 3780 | 29.10% | -20.80% | 44.99% | 1239 | 0 | PASS |
| C051 | 3780 | 29.86% | -20.23% | 82.76% | 2022 | 0 | PASS |
| C055 | 3780 | 31.76% | -25.69% | 87.27% | 2691 | 0 | PASS |
| C054 | 3780 | 32.28% | -23.83% | 87.33% | 2243 | 0 | PASS |
| C053 | 3780 | 32.46% | -24.13% | 87.49% | 1757 | 0 | PASS |
| C061 | 3780 | 32.49% | -24.31% | 82.55% | 1730 | 0 | PASS |
| C059 | 3780 | 32.54% | -24.13% | 87.37% | 1756 | 0 | PASS |
| C060 | 3780 | 32.56% | -24.23% | 82.60% | 1673 | 0 | PASS |
| C008 | 3780 | 32.85% | -30.16% | 39.34% | 1746 | 0 | PASS |
| C057 | 3780 | 32.91% | -23.87% | 87.48% | 1743 | 0 | PASS |
| C058 | 3780 | 32.91% | -23.87% | 87.25% | 1818 | 0 | PASS |
| C062 | 3780 | 33.04% | -23.96% | 82.57% | 1661 | 0 | PASS |
| C050 | 3780 | 33.32% | -19.86% | 82.16% | 1792 | 0 | PASS |
| C009 | 3780 | 33.80% | -31.67% | 83.80% | 1453 | 0 | FAILED |
| C034 | 3780 | 34.16% | -20.37% | 83.23% | 2036 | 0 | PASS |
| C036 | 3780 | 34.28% | -20.22% | 83.66% | 2034 | 0 | PASS |
| C007 | 3780 | 34.29% | -30.04% | 58.15% | 60 | 0 | FAILED |
| C035 | 3780 | 34.32% | -20.37% | 83.66% | 2031 | 0 | PASS |
| C038 | 3780 | 34.41% | -19.54% | 80.97% | 1939 | 0 | PASS |
| C039 | 3780 | 34.41% | -19.54% | 80.97% | 1939 | 0 | PASS |
| C037 | 3780 | 34.92% | -20.03% | 83.51% | 1924 | 0 | PASS |
| C021 | 3780 | 35.25% | -20.72% | 76.93% | 1977 | 0 | PASS |
| C064 | 3780 | 35.25% | -20.72% | 76.93% | 1977 | 0 | PASS |
| C025 | 3780 | 35.27% | -21.02% | 72.30% | 2222 | 0 | PASS |
| C068 | 3780 | 35.27% | -21.02% | 72.30% | 2222 | 0 | PASS |
| C018 | 3780 | 35.33% | -23.19% | 75.05% | 1829 | 0 | PASS |
| C022 | 3780 | 35.42% | -20.69% | 77.81% | 1860 | 0 | PASS |
| C065 | 3780 | 35.42% | -20.69% | 77.81% | 1860 | 0 | PASS |
| C001 | 3780 | 35.47% | -20.23% | 83.47% | 1904 | 0 | PASS |
| C002 | 3780 | 35.47% | -20.23% | 83.47% | 1904 | 0 | PASS |
| C020 | 3780 | 35.47% | -20.23% | 83.50% | 1915 | 0 | PASS |
| C024 | 3780 | 35.47% | -20.23% | 83.21% | 1834 | 0 | PASS |
| C026 | 3780 | 35.47% | -20.23% | 83.44% | 1850 | 0 | PASS |
| C027 | 3780 | 35.47% | -20.23% | 83.45% | 1920 | 0 | PASS |
| C029 | 3780 | 35.47% | -20.23% | 83.47% | 1902 | 0 | PASS |
| C045 | 3780 | 35.47% | -20.23% | 83.46% | 1883 | 0 | PASS |
| C046 | 3780 | 35.47% | -20.23% | 83.38% | 1863 | 0 | PASS |
| C047 | 3780 | 35.47% | -20.23% | 83.21% | 1826 | 0 | PASS |
| C063 | 3780 | 35.47% | -20.23% | 83.50% | 1915 | 0 | PASS |
| C067 | 3780 | 35.47% | -20.23% | 83.21% | 1834 | 0 | PASS |
| C028 | 3780 | 35.47% | -20.41% | 83.28% | 2133 | 0 | PASS |
| C030 | 3780 | 35.47% | -20.41% | 83.27% | 2146 | 0 | PASS |
| C023 | 3780 | 35.47% | -20.67% | 80.90% | 2247 | 0 | PASS |
| C066 | 3780 | 35.47% | -20.67% | 80.90% | 2247 | 0 | PASS |
| C052 | 3780 | 35.47% | -23.35% | 82.05% | 2120 | 0 | PASS |
| C042 | 3780 | 35.50% | -32.38% | 98.26% | 1622 | 0 | FAILED |
| C048 | 3780 | 35.51% | -20.59% | 78.83% | 1812 | 0 | PASS |
| C031 | 3780 | 35.53% | -20.48% | 76.17% | 1799 | 0 | PASS |
| C033 | 3780 | 35.64% | -20.23% | 64.69% | 2133 | 0 | PASS |
| C032 | 3780 | 35.64% | -20.62% | 65.38% | 1775 | 0 | PASS |
| C040 | 3780 | 35.76% | -20.09% | 83.00% | 1920 | 0 | PASS |
| C041 | 3780 | 35.76% | -20.09% | 83.00% | 1920 | 0 | PASS |
| C049 | 3780 | 35.76% | -20.80% | 60.21% | 1741 | 0 | PASS |
| C056 | 3780 | 38.24% | -36.87% | 87.14% | 3761 | 0 | PASS |
| C043 | 3780 | 38.83% | -36.89% | 99.69% | 159 | 0 | PASS |
| C010 | 3780 | 38.86% | -36.70% | 88.00% | 127 | 0 | PASS |
| C019 | 3780 | 43.25% | -30.42% | 75.82% | 2201 | 0 | PASS |
| C006 | 3780 | 45.53% | -40.53% | 99.74% | 120 | 0 | FAILED |
| C044 | 3780 | 48.82% | -44.71% | 99.99% | 240 | 0 | PASS |
| C004 | 3780 | 49.83% | -44.90% | 99.77% | 495 | 0 | PASS |
| C005 | 3780 | 51.22% | -49.05% | 99.99% | 256 | 1 | FAILED |
| C015 | 3780 | 64.21% | -57.77% | 99.56% | 210 | 5 | FAILED |

## Full synthetic stress robustness leaderboard

Sort order is compliant-path count, then worst return. This is a declared engineering ordering; it is not an estimate of crash probabilities or forward expected return.

| Entry | Sessions | Compliant paths / 30 | Worst return | Median eligible rank | Compliance |
|---|---|---|---|---|---|
| C003 | 3780 | 30 | 0.00% | 32.5 | PASS |
| C012 | 3780 | 30 | -11.12% | 52.0 | PASS |
| C038 | 3780 | 30 | -19.54% | 29.0 | PASS |
| C039 | 3780 | 30 | -19.54% | 29.0 | PASS |
| C050 | 3780 | 30 | -19.86% | 34.0 | PASS |
| C037 | 3780 | 30 | -20.03% | 31.0 | PASS |
| C040 | 3780 | 30 | -20.09% | 32.5 | PASS |
| C041 | 3780 | 30 | -20.09% | 32.5 | PASS |
| C036 | 3780 | 30 | -20.22% | 32.0 | PASS |
| C001 | 3780 | 30 | -20.23% | 28.0 | PASS |
| C002 | 3780 | 30 | -20.23% | 28.0 | PASS |
| C020 | 3780 | 30 | -20.23% | 28.0 | PASS |
| C024 | 3780 | 30 | -20.23% | 29.0 | PASS |
| C026 | 3780 | 30 | -20.23% | 29.0 | PASS |
| C027 | 3780 | 30 | -20.23% | 28.5 | PASS |
| C029 | 3780 | 30 | -20.23% | 28.0 | PASS |
| C045 | 3780 | 30 | -20.23% | 29.5 | PASS |
| C046 | 3780 | 30 | -20.23% | 30.0 | PASS |
| C047 | 3780 | 30 | -20.23% | 29.0 | PASS |
| C051 | 3780 | 30 | -20.23% | 32.5 | PASS |
| C063 | 3780 | 30 | -20.23% | 28.0 | PASS |
| C067 | 3780 | 30 | -20.23% | 29.0 | PASS |
| C033 | 3780 | 30 | -20.23% | 12.5 | PASS |
| C034 | 3780 | 30 | -20.37% | 37.0 | PASS |
| C035 | 3780 | 30 | -20.37% | 33.0 | PASS |
| C028 | 3780 | 30 | -20.41% | 32.0 | PASS |
| C030 | 3780 | 30 | -20.41% | 32.0 | PASS |
| C031 | 3780 | 30 | -20.48% | 19.0 | PASS |
| C048 | 3780 | 30 | -20.59% | 18.5 | PASS |
| C032 | 3780 | 30 | -20.62% | 22.0 | PASS |
| C023 | 3780 | 30 | -20.67% | 39.0 | PASS |
| C066 | 3780 | 30 | -20.67% | 39.0 | PASS |
| C022 | 3780 | 30 | -20.69% | 18.5 | PASS |
| C065 | 3780 | 30 | -20.69% | 18.5 | PASS |
| C021 | 3780 | 30 | -20.72% | 26.0 | PASS |
| C064 | 3780 | 30 | -20.72% | 26.0 | PASS |
| C049 | 3780 | 30 | -20.80% | 13.5 | PASS |
| C017 | 3780 | 30 | -20.80% | 9.0 | PASS |
| C025 | 3780 | 30 | -21.02% | 37.5 | PASS |
| C068 | 3780 | 30 | -21.02% | 37.5 | PASS |
| C011 | 3780 | 30 | -22.44% | 49.5 | PASS |
| C018 | 3780 | 30 | -23.19% | 18.5 | PASS |
| C052 | 3780 | 30 | -23.35% | 29.5 | PASS |
| C054 | 3780 | 30 | -23.83% | 50.0 | PASS |
| C057 | 3780 | 30 | -23.87% | 29.0 | PASS |
| C058 | 3780 | 30 | -23.87% | 39.0 | PASS |
| C062 | 3780 | 30 | -23.96% | 15.5 | PASS |
| C053 | 3780 | 30 | -24.13% | 30.0 | PASS |
| C059 | 3780 | 30 | -24.13% | 29.0 | PASS |
| C060 | 3780 | 30 | -24.23% | 13.0 | PASS |
| C061 | 3780 | 30 | -24.31% | 23.0 | PASS |
| C013 | 3780 | 30 | -25.04% | 46.5 | PASS |
| C055 | 3780 | 30 | -25.69% | 36.0 | PASS |
| C014 | 3780 | 30 | -26.74% | 50.5 | PASS |
| C008 | 3780 | 30 | -30.16% | 42.0 | PASS |
| C019 | 3780 | 30 | -30.42% | 28.0 | PASS |
| C010 | 3780 | 30 | -36.70% | 51.5 | PASS |
| C056 | 3780 | 30 | -36.87% | 43.5 | PASS |
| C043 | 3780 | 30 | -36.89% | 55.0 | PASS |
| C044 | 3780 | 30 | -44.71% | 54.0 | PASS |
| C004 | 3780 | 30 | -44.90% | 49.5 | PASS |
| C005 | 3780 | 29 | -49.05% | 56 | FAILED |
| C009 | 3780 | 27 | -31.67% | 55 | FAILED |
| C042 | 3780 | 24 | -32.38% | 57.5 | FAILED |
| C015 | 3780 | 24 | -57.77% | 52.0 | FAILED |
| C006 | 3780 | 21 | -40.53% | 58 | FAILED |
| C016 | 3780 | 5 | -17.39% | 48 | FAILED |
| C007 | 3780 | 0 | -30.04% | None | FAILED |

## Full rule-compliance and evidence-quality boards

All entries share the same SYNTHETIC evidence grade. There is no meaningful evidence-quality superiority ranking from identical provenance. The table exposes session coverage and compliance instead of fabricating a score.

| Entry | Base runs | Successful | Sessions | Compliant paths / 32 | Execution status | Compliance |
|---|---|---|---|---|---|---|
| C001 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C002 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C003 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C004 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C008 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C010 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C011 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C012 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C013 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C014 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C017 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C018 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C019 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C020 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C021 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C022 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C023 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C024 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C025 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C026 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C027 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C028 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C029 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C030 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C031 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C032 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C033 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C034 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C035 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C036 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C037 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C038 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C039 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C040 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C041 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C043 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C044 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C045 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C046 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C047 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C048 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C049 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C050 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C051 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C052 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C053 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C054 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C055 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C056 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C057 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C058 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C059 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C060 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C061 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C062 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C063 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C064 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C065 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C066 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C067 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C068 | 32 | 32 | 4788 | 32 | EXECUTED SUCCESSFULLY | PASS |
| C005 | 32 | 32 | 4788 | 30 | EXECUTED SUCCESSFULLY | FAILED |
| C009 | 32 | 32 | 4788 | 28 | EXECUTED SUCCESSFULLY | FAILED |
| C015 | 32 | 32 | 4788 | 25 | EXECUTED SUCCESSFULLY | FAILED |
| C042 | 32 | 32 | 4788 | 25 | EXECUTED SUCCESSFULLY | FAILED |
| C006 | 32 | 32 | 4788 | 22 | EXECUTED SUCCESSFULLY | FAILED |
| C016 | 32 | 32 | 4788 | 5 | EXECUTED SUCCESSFULLY | FAILED |
| C007 | 32 | 32 | 4788 | 0 | EXECUTED SUCCESSFULLY | FAILED |

## Adversarial tests and independent verification

31/31 executed tests passed; 0 failed assertions and 0 test errors. The deliberate throwing strategy is a negative control with preserved failure receipt, not an unreported failed harness test. All 25 requested assurance areas map to the numbered controls and full-journal verifier. Independent verification status: **PASS**, 2188 journals, 331632 sessions, 0 failed runs. Its implementation reconstructs cash/shares/dividend receivables using Decimal, reconstructs causal input hashes independently, and recomputes return, drawdown, exposure, ratios, costs and monthly statistics without importing the harness metric function.

Independent means a separately implemented accounting/metric verifier within this audit, not an external quant review or second agent. Hostile-code sandbox escape, actual venue latency, hidden competition execution and real corporate-event coverage were not established. No original test suite that might load sealed data was run. The superseded first discovery inventory is preserved; no expensive evaluation was discarded or rerun to improve rankings.

## Acceptance gates

| Gate | Requirement | Verdict | Basis |
|---|---|---|---|
| A | Protected Git checkpoint | PASS | branch, HEAD, parent and protected hashes match before and after |
| B | Strategy inventory completeness | PARTIAL | 68 preserved executable entries covered; unreachable objects and undocumented sweeps cannot be certified exhaustive |
| C | Data eligibility | PASS | new synthetic observations only; real historical comparison BLOCKED |
| D | Competition contract parity | PARTIAL | common-domain parity tested; explicit timing/window, missing-bar, action, order-limit and risk differences |
| E | Simulator correctness | PASS | 31 executed controls plus independent journal reconstruction; limited to modeled cases |
| F | Equal-condition execution | PASS | same dataset hashes, starting equity, input windows and engine rules across all entries |
| G | All eligible strategies attempted | PASS | 68 entries x 32 base fixtures; sensitivity E0/D2 only |
| H | Performance metric accuracy | PASS | independent Decimal reconstruction of all journals and leaderboard inputs |
| I | Stress-test execution | PASS | 15 named stress families x 2 seeds x 68 entries; 2 long-cycle paths separately |
| J | Independent E0/D2 comparison | PARTIAL | paired executed descriptive comparison and independent accounting; no independent market sample or external reviewer |
| K | Compliance and risk verification | PASS | breaches explicitly retained; PASS here means verified classification, not every candidate compliant |
| L | Reproducibility and preservation | PASS | new artifacts only; source snapshots, raw journals, measured runs, checksums |
| M | Zero unauthorized Git/external actions | PASS | read-only Git; no broker, provider, credential, holdout or external network actions |
| N | Scientific integrity | PASS | synthetic/descriptive labels; no official score, significance, universal winner or promotion |

## Complete version inventory

Each ID links to the full inventory fields: source path/commit/raw and normalized hashes, original objective, interface, dependencies, extraction status, parameters and exact dependency snapshots. Creation-stage detail is derived only where source/commit documents it; otherwise it is not inferred from a result.

| ID | Source / entry | Git ref | Raw SHA-256 | Adapter |
|---|---|---|---|---|
| C001 | agent.py:decide | WORKTREE | 46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd | full source |
| C002 | agent.py:decide @0f8a0bb2 | 0f8a0bb262ffecf089418302526d64a658470a9d | af20692da88d23df55b75670b3c7aacaeb54005c7d2d0511dfb32100dc905b0c | full source |
| C003 | agent.py:decide @f5f0e4d4 | f5f0e4d48f61621567bd5b922631a2d872ac6a0f | 5d9212db038f6fb4f67bc4ac81d0f8846eaee817776596aad2823b3eb45443e4 | full source |
| C004 | ai_momentum.py:decide | WORKTREE | 42b2cb44fdfbaade9e9ca60a3ba508932f31ce3e0a2c6cff7d61a4aaacaa6fcd | full source |
| C005 | ai_momentum.py:decide @c7fddd33 | c7fddd33ec700e54305af64da7d8e559267e9f6a | f39c5ad45c8605899e91b890087ed2bfc36c963876234946d6da38ee8ba82da7 | full source |
| C006 | baseline.py:decide | WORKTREE | eb19b0e31d44961f804cb663abd03e1750a5f86da344eacc7b83a90e3b2cca6d | full source |
| C007 | baseline.py:decide @f5f0e4d4 | f5f0e4d48f61621567bd5b922631a2d872ac6a0f | f16de592b501981e4ca2191ee5642ec9715edfb749492e9721e8e830ddce811a | full source |
| C008 | drawdown_momentum.py:decide | WORKTREE | ec69adbe1bfcb881157e14eca0b0358a0133d008e4a60732c9301022a6aa5498 | full source |
| C009 | example_sector_rotation.py:decide | WORKTREE | 922aa2fcfb9c8077eb2abc152b0f7a09a6f89138ef64a6428561d06ed9e4901f | full source |
| C010 | example_sector_rotation.py:decide @8857f3ed | 8857f3edcf2d450c894f4201ce242545d566f14e | eabe4b656de941c02af21925bd0d5046bdb3a50202089791545bdc3d8e5769cb | full source |
| C011 | example_vol_target.py:decide | WORKTREE | 934d15636b7c7e0d3d9a708d0e24b83fa8383281d56a700ec2d25b8d9a723b49 | full source |
| C012 | example_vol_target.py:decide @8857f3ed | 8857f3edcf2d450c894f4201ce242545d566f14e | 5d60563377dfb42d34650c3da4a570357b9790fd64644d301b1c5dd01c3bdd42 | full source |
| C013 | house_barbell_realasset.py:decide | WORKTREE | 52a59d2aef92e6ed95a629f81718a893a74fd3c6127cbdf24ef9b3716d255310 | full source |
| C014 | house_barbell_realasset.py:decide @245e0fb8 | 245e0fb8eafb6a590c8cff6e36028ca83450127c | b16eb6840704e3e98767c9690a9b44fc97d919375c6cd6fb6705ec5ebcf8b6c7 | full source |
| C015 | momentum_v1.py:decide | WORKTREE | 40622061d4b84c15420aa998c1d6185d3887d0509314319c37cda36239c73158 | full source |
| C016 | qqq_benchmark.py:decide | WORKTREE | 1049b7840bd39bcc8e55d26dbf3e588f3cb190a7c43a1b8a52e15eb3b1f692f5 | full source |
| C017 | research/strategies/candidate_alpha.py:AdaptiveRiskParityCandidate | WORKTREE | 1bb1d5f23a9bc9514dd7da83e4c67d483377954c96b1f9dc96b871eae7479007 | full source |
| C018 | research/strategies/loss_reduction_candidates.py:FastExitDeRiskingCandidate | WORKTREE | e72b0f6630ae849387568ead2c3f4b45b64446d99bb42cc5d119eff325c022be | full source |
| C019 | research/strategies/loss_reduction_candidates.py:IntegratedLossReductionCandidate | WORKTREE | e72b0f6630ae849387568ead2c3f4b45b64446d99bb42cc5d119eff325c022be | full source |
| C020 | research/strategies/v11_candidates.py:CandidateA_AdaptiveRebalance | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C021 | research/strategies/v11_candidates.py:CandidateB_EmergencyDeRisking | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C022 | research/strategies/v11_candidates.py:CandidateC_SectorRiskBudgeting | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C023 | research/strategies/v11_candidates.py:CandidateD_RecoveryParticipation | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C024 | research/strategies/v11_candidates.py:CandidateE_CostAwareRebalancing | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C025 | research/strategies/v11_candidates.py:CandidateF_IntegratedRiskControl | WORKTREE | 017a89dfcb7b8f5370d6829c5f81a97138fdcd7fe12ef051065d8011418ae02d | full source |
| C026 | research/strategies/v12_candidate_ae.py:CandidateAE_Combined | WORKTREE | 406e8b9e8c4145faea764db41d6286b96b26e9b33808233458da584f9f245271 | full source |
| C027 | research/strategies/v30_candidate_c1_tight_vol_gate.py:decide | WORKTREE | c9423c7b459f72e3e73bcbf0b0ba9cc7dc1067f4982925f1126cd203438ff3d0 | full source |
| C028 | research/strategies/v30_candidate_c2_vol_acceleration.py:decide | WORKTREE | c8d3949f8d2a7c5610eacf44c13551a2bdb1c73b2d0a9c4064b4a893391ba798 | full source |
| C029 | research/strategies/v30_candidate_c3_vol_persistence.py:decide | WORKTREE | d0e2b8c00ea837891369377420770c203740eb1c8838c93a5886ac34f6558427 | full source |
| C030 | research/strategies/v30_candidate_c4_combined_gates.py:decide | WORKTREE | 25c90d7969b20b761d0d4d062ae80c981e90d07d3117e0c035fd3d39f99dfff0 | full source |
| C031 | research/strategies/v30_candidate_d1_energy_exit.py:decide | WORKTREE | fb90ef20bd5523a2cda21a54a1af13fa766e6983f4077a432595fde862819014 | full source |
| C032 | research/strategies/v30_candidate_d2_cash_cushion.py:decide | WORKTREE | 5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215 | full source |
| C033 | research/strategies/v30_candidate_d3_recovery_discipline.py:decide | WORKTREE | f5629690e77bcce9f37ad57bd04a4d7a9b6d37770012b2cac05909f253abc09e | full source |
| C034 | research/strategies/v30_candidate_p1_inverse_vol.py:decide | WORKTREE | 0f7875140cff89ea2f6e8f5319b3272cf62770d6546c66762765c20521187b65 | full source |
| C035 | research/strategies/v30_candidate_p2_capped_inverse_vol.py:decide | WORKTREE | 370b465eeffb41fa860ebdd557f34c1434e0e0754d32f74ed2bcf53780162f5a | full source |
| C036 | research/strategies/v30_candidate_p3_smoothed_inverse_vol.py:decide | WORKTREE | 20235faf8fb96d70acf0a464c96beff6d1019462f4cc30b2a4c77bcd75785ad0 | full source |
| C037 | research/strategies/v30_candidate_p4_blend_equal_inverse.py:decide | WORKTREE | 495bbf65690e6fe4661d93f309ebeaf250fa8a06b1c967ba181cffb3d47b883d | full source |
| C038 | research/strategies/v30_execution_safe_agent.py:V30ExecutionSafeAgent | WORKTREE | b2660488740275a0931129e39d4638ac8bbcfe092bd7060959ccaf8d72186fb6 | full source |
| C039 | research/strategies/v30_execution_safe_agent.py:decide | WORKTREE | b2660488740275a0931129e39d4638ac8bbcfe092bd7060959ccaf8d72186fb6 | full source |
| C040 | research/strategies/v30_execution_safe_agent_final.py:V30ExecutionSafeAgentFinal | WORKTREE | aaacaa8780f14df0b8ae5fb51fef1182f9b13cf9405b63e916119ad9c448b377 | full source |
| C041 | research/strategies/v30_execution_safe_agent_r.py:V30ExecutionSafeAgentR | WORKTREE | 143616dfd2a4da224a8f735d4cc472180b55715aec46b60538b7fa953382316f | full source |
| C042 | seed_dual_momentum.py:decide | WORKTREE | 7844dc0b492ed09fe0ed122e0b83bc6c12d946f885ce26d12fc7d783c8f2a29f | full source |
| C043 | seed_dual_momentum.py:decide @33d40c9f | 33d40c9f86e8aa2a4e020093cb5d71c6df1f45f5 | 749af760642237e88c6fed6bb3f6672d7a383605f47909d59abe9f64a8ea0420 | full source |
| C044 | soham_agent_v2.py:decide @f5f0e4d4 | f5f0e4d48f61621567bd5b922631a2d872ac6a0f | 9f208cd07a57d0fb444d99bd1c13fcae4ebb8b7764e060f52cfa69a2bcb3c65e | full source |
| C045 | make_h1_decide[0.02] | WORKTREE | 67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499 | AST definition |
| C046 | make_h1_decide[0.025] | WORKTREE | 67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499 | AST definition |
| C047 | make_h1_decide[0.03] | WORKTREE | 67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499 | AST definition |
| C048 | make_h5_decide['no_xle'] | WORKTREE | 67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499 | AST definition |
| C049 | make_h5_decide['conservative'] | WORKTREE | 67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499 | AST definition |
| C050 | make_h2_decide[] | WORKTREE | a3849549c2b02178815666ac4909ac4d366b3ea70903cee21b84b4f7d0b11e78 | AST definition |
| C051 | make_h3_decide[] | WORKTREE | a3849549c2b02178815666ac4909ac4d366b3ea70903cee21b84b4f7d0b11e78 | AST definition |
| C052 | make_h4_decide[] | WORKTREE | a3849549c2b02178815666ac4909ac4d366b3ea70903cee21b84b4f7d0b11e78 | AST definition |
| C053 | Baseline_Cadence_5 | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C054 | Cadence_3 | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C055 | Cadence_2 | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C056 | Cadence_1_Daily | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C057 | FastExit_Drop_3pct | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C058 | FastExit_Drop_2pct | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C059 | VolTrigger_35 | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C060 | No_XLE_Cadence_5 | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C061 | SectorCap_20pct | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C062 | Integrated_FastExit_NoXLE | WORKTREE | b1fcf4bf5d32d26bff339b5a4fab1afbbc4cec9c471c8c2d8b70b22981bfb26a | AST definition |
| C063 | scratch/test_candidates_a_to_f.py:CandidateA_AdaptiveRebalance | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |
| C064 | scratch/test_candidates_a_to_f.py:CandidateB_EmergencyDeRisking | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |
| C065 | scratch/test_candidates_a_to_f.py:CandidateC_SectorRiskBudgeting | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |
| C066 | scratch/test_candidates_a_to_f.py:CandidateD_RecoveryParticipation | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |
| C067 | scratch/test_candidates_a_to_f.py:CandidateE_CostAwareRebalancing | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |
| C068 | scratch/test_candidates_a_to_f.py:CandidateF_IntegratedRiskControl | WORKTREE | 8edd5a2649cac1f1e6f0bba579a62b28d62163aa9878447fda4f630edca13e0d | AST definition |

## Complete competition-style return boards

These are separate synthetic fixture leaderboards, not official competition ranks. An em dash in rank means noncompliant/ineligible for that path. Raw returns remain visible. Each path supplies the same observations and sessions to every entry. The full CSV includes source hashes, sample class, sessions, compliance and limitations for every row.

### bear_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C013 | 126 | -3.76% | 5.77% | PASS |
| 3 | C008 | 126 | -4.49% | 7.15% | PASS |
| 4 | C049 | 126 | -5.86% | 8.45% | PASS |
| 5 | C017 | 126 | -6.13% | 8.75% | PASS |
| 6 | C014 | 126 | -6.44% | 8.43% | PASS |
| 7 | C033 | 126 | -6.70% | 9.26% | PASS |
| 8 | C012 | 126 | -6.79% | 8.82% | PASS |
| 9 | C011 | 126 | -6.86% | 8.89% | PASS |
| 10 | C032 | 126 | -6.88% | 9.42% | PASS |
| 11 | C009 | 126 | -8.21% | 10.00% | PASS |
| 12 | C060 | 126 | -8.28% | 11.31% | PASS |
| 12 | C062 | 126 | -8.28% | 11.31% | PASS |
| 14 | C031 | 126 | -8.57% | 11.07% | PASS |
| 15 | C022 | 126 | -8.76% | 11.25% | PASS |
| 15 | C065 | 126 | -8.76% | 11.25% | PASS |
| 17 | C018 | 126 | -8.85% | 11.33% | PASS |
| 17 | C048 | 126 | -8.85% | 11.33% | PASS |
| 19 | C025 | 126 | -8.89% | 11.39% | PASS |
| 19 | C068 | 126 | -8.89% | 11.39% | PASS |
| 21 | C019 | 126 | -8.91% | 11.83% | PASS |
| 22 | C055 | 126 | -9.32% | 12.27% | PASS |
| 23 | C061 | 126 | -9.34% | 12.37% | PASS |
| 24 | C056 | 126 | -9.39% | 12.39% | PASS |
| 25 | C054 | 126 | -10.13% | 13.14% | PASS |
| 26 | C053 | 126 | -10.19% | 13.20% | PASS |
| 26 | C057 | 126 | -10.19% | 13.20% | PASS |
| 26 | C058 | 126 | -10.19% | 13.20% | PASS |
| 26 | C059 | 126 | -10.19% | 13.20% | PASS |
| 30 | C050 | 126 | -10.29% | 12.67% | PASS |
| — | C016 | 126 | -10.39% | 11.18% | FAILED |
| 31 | C038 | 126 | -10.54% | 12.91% | PASS |
| 31 | C039 | 126 | -10.54% | 12.91% | PASS |
| 33 | C021 | 126 | -10.58% | 13.06% | PASS |
| 33 | C064 | 126 | -10.58% | 13.06% | PASS |
| 35 | C028 | 126 | -10.65% | 13.13% | PASS |
| 35 | C030 | 126 | -10.65% | 13.13% | PASS |
| 37 | C040 | 126 | -10.71% | 13.19% | PASS |
| 37 | C041 | 126 | -10.71% | 13.19% | PASS |
| 39 | C001 | 126 | -10.72% | 13.20% | PASS |
| 39 | C002 | 126 | -10.72% | 13.20% | PASS |
| 39 | C020 | 126 | -10.72% | 13.20% | PASS |
| 39 | C023 | 126 | -10.72% | 13.20% | PASS |
| 39 | C024 | 126 | -10.72% | 13.20% | PASS |
| 39 | C026 | 126 | -10.72% | 13.20% | PASS |
| 39 | C027 | 126 | -10.72% | 13.20% | PASS |
| 39 | C029 | 126 | -10.72% | 13.20% | PASS |
| 39 | C045 | 126 | -10.72% | 13.20% | PASS |
| 39 | C046 | 126 | -10.72% | 13.20% | PASS |
| 39 | C047 | 126 | -10.72% | 13.20% | PASS |
| 39 | C051 | 126 | -10.72% | 13.20% | PASS |
| 39 | C052 | 126 | -10.72% | 13.20% | PASS |
| 39 | C063 | 126 | -10.72% | 13.20% | PASS |
| 39 | C066 | 126 | -10.72% | 13.20% | PASS |
| 39 | C067 | 126 | -10.72% | 13.20% | PASS |
| 55 | C037 | 126 | -10.78% | 13.20% | PASS |
| 56 | C035 | 126 | -10.85% | 13.23% | PASS |
| 57 | C034 | 126 | -10.85% | 13.22% | PASS |
| 58 | C036 | 126 | -10.88% | 13.26% | PASS |
| 59 | C042 | 126 | -15.03% | 17.05% | PASS |
| — | C007 | 126 | -17.86% | 19.04% | FAILED |
| 60 | C010 | 126 | -20.70% | 22.44% | PASS |
| 61 | C043 | 126 | -23.81% | 25.80% | PASS |
| 62 | C006 | 126 | -24.00% | 25.87% | PASS |
| 63 | C005 | 126 | -28.04% | 29.96% | PASS |
| 63 | C044 | 126 | -28.04% | 29.96% | PASS |
| 65 | C004 | 126 | -29.24% | 31.11% | PASS |
| 66 | C015 | 126 | -37.95% | 40.25% | PASS |

### bear_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| — | C016 | 126 | -4.90% | 6.10% | FAILED |
| 2 | C012 | 126 | -5.93% | 5.93% | PASS |
| 3 | C013 | 126 | -6.96% | 6.96% | PASS |
| 4 | C032 | 126 | -7.06% | 7.06% | PASS |
| 5 | C011 | 126 | -7.19% | 7.28% | PASS |
| 6 | C049 | 126 | -7.29% | 7.29% | PASS |
| 7 | C014 | 126 | -7.46% | 7.46% | PASS |
| 8 | C033 | 126 | -8.11% | 8.11% | PASS |
| 9 | C017 | 126 | -8.15% | 8.70% | PASS |
| 10 | C008 | 126 | -8.26% | 8.26% | PASS |
| 11 | C051 | 126 | -8.33% | 8.33% | PASS |
| 12 | C031 | 126 | -8.53% | 8.53% | PASS |
| 13 | C022 | 126 | -8.86% | 8.86% | PASS |
| 13 | C065 | 126 | -8.86% | 8.86% | PASS |
| 15 | C018 | 126 | -8.92% | 8.92% | PASS |
| 16 | C025 | 126 | -8.93% | 8.93% | PASS |
| 16 | C068 | 126 | -8.93% | 8.93% | PASS |
| 18 | C048 | 126 | -9.30% | 9.30% | PASS |
| — | C007 | 126 | -9.30% | 10.34% | FAILED |
| 19 | C050 | 126 | -9.60% | 9.60% | PASS |
| 20 | C058 | 126 | -9.64% | 10.65% | PASS |
| 21 | C038 | 126 | -9.79% | 9.79% | PASS |
| 21 | C039 | 126 | -9.79% | 9.79% | PASS |
| 23 | C021 | 126 | -10.09% | 10.09% | PASS |
| 23 | C064 | 126 | -10.09% | 10.09% | PASS |
| 25 | C034 | 126 | -10.13% | 10.13% | PASS |
| 26 | C035 | 126 | -10.13% | 10.13% | PASS |
| 26 | C036 | 126 | -10.13% | 10.13% | PASS |
| 28 | C037 | 126 | -10.14% | 10.14% | PASS |
| 29 | C040 | 126 | -10.15% | 10.15% | PASS |
| 29 | C041 | 126 | -10.15% | 10.15% | PASS |
| 31 | C001 | 126 | -10.16% | 10.16% | PASS |
| 31 | C002 | 126 | -10.16% | 10.16% | PASS |
| 31 | C020 | 126 | -10.16% | 10.16% | PASS |
| 31 | C027 | 126 | -10.16% | 10.16% | PASS |
| 31 | C028 | 126 | -10.16% | 10.16% | PASS |
| 31 | C029 | 126 | -10.16% | 10.16% | PASS |
| 31 | C030 | 126 | -10.16% | 10.16% | PASS |
| 31 | C045 | 126 | -10.16% | 10.16% | PASS |
| 31 | C052 | 126 | -10.16% | 10.16% | PASS |
| 31 | C063 | 126 | -10.16% | 10.16% | PASS |
| 41 | C024 | 126 | -10.18% | 10.18% | PASS |
| 41 | C026 | 126 | -10.18% | 10.18% | PASS |
| 41 | C046 | 126 | -10.18% | 10.18% | PASS |
| 41 | C047 | 126 | -10.18% | 10.18% | PASS |
| 41 | C067 | 126 | -10.18% | 10.18% | PASS |
| 46 | C019 | 126 | -10.38% | 10.38% | PASS |
| 47 | C060 | 126 | -10.52% | 11.36% | PASS |
| 47 | C062 | 126 | -10.52% | 11.36% | PASS |
| 49 | C061 | 126 | -11.03% | 12.05% | PASS |
| 50 | C056 | 126 | -11.32% | 12.38% | PASS |
| 51 | C053 | 126 | -11.43% | 12.41% | PASS |
| 51 | C057 | 126 | -11.43% | 12.41% | PASS |
| 51 | C059 | 126 | -11.43% | 12.41% | PASS |
| 54 | C009 | 126 | -11.78% | 11.78% | PASS |
| 55 | C054 | 126 | -11.83% | 12.48% | PASS |
| 56 | C055 | 126 | -12.70% | 12.70% | PASS |
| 57 | C042 | 126 | -12.91% | 12.91% | PASS |
| 58 | C023 | 126 | -13.10% | 13.10% | PASS |
| 58 | C066 | 126 | -13.10% | 13.10% | PASS |
| 60 | C010 | 126 | -14.20% | 16.06% | PASS |
| 61 | C043 | 126 | -14.42% | 16.34% | PASS |
| 62 | C006 | 126 | -14.83% | 15.76% | PASS |
| 63 | C044 | 126 | -16.37% | 18.45% | PASS |
| 64 | C004 | 126 | -17.77% | 19.01% | PASS |
| 65 | C005 | 126 | -20.78% | 23.28% | PASS |
| 66 | C015 | 126 | -22.26% | 25.21% | PASS |

### bull_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 35.02% | 9.95% | PASS |
| 2 | C005 | 126 | 32.71% | 9.00% | PASS |
| 3 | C004 | 126 | 26.93% | 7.44% | PASS |
| 4 | C019 | 126 | 26.37% | 4.72% | PASS |
| 5 | C055 | 126 | 25.72% | 3.77% | PASS |
| 6 | C054 | 126 | 25.09% | 4.03% | PASS |
| 7 | C022 | 126 | 24.76% | 4.31% | PASS |
| 7 | C025 | 126 | 24.76% | 4.31% | PASS |
| 7 | C065 | 126 | 24.76% | 4.31% | PASS |
| 7 | C068 | 126 | 24.76% | 4.31% | PASS |
| 11 | C023 | 126 | 24.50% | 4.31% | PASS |
| 11 | C066 | 126 | 24.50% | 4.31% | PASS |
| 13 | C017 | 126 | 24.43% | 3.88% | PASS |
| 14 | C056 | 126 | 24.42% | 4.09% | PASS |
| 15 | C028 | 126 | 24.34% | 4.11% | PASS |
| 15 | C030 | 126 | 24.34% | 4.11% | PASS |
| 17 | C052 | 126 | 24.26% | 4.31% | PASS |
| 18 | C053 | 126 | 24.05% | 4.54% | PASS |
| 18 | C057 | 126 | 24.05% | 4.54% | PASS |
| 18 | C059 | 126 | 24.05% | 4.54% | PASS |
| 21 | C061 | 126 | 23.87% | 4.49% | PASS |
| 22 | C037 | 126 | 23.75% | 4.32% | PASS |
| 23 | C001 | 126 | 23.64% | 4.31% | PASS |
| 23 | C002 | 126 | 23.64% | 4.31% | PASS |
| 23 | C020 | 126 | 23.64% | 4.31% | PASS |
| 23 | C021 | 126 | 23.64% | 4.31% | PASS |
| 23 | C024 | 126 | 23.64% | 4.31% | PASS |
| 23 | C026 | 126 | 23.64% | 4.31% | PASS |
| 23 | C027 | 126 | 23.64% | 4.31% | PASS |
| 23 | C029 | 126 | 23.64% | 4.31% | PASS |
| 23 | C045 | 126 | 23.64% | 4.31% | PASS |
| 23 | C046 | 126 | 23.64% | 4.31% | PASS |
| 23 | C047 | 126 | 23.64% | 4.31% | PASS |
| 23 | C063 | 126 | 23.64% | 4.31% | PASS |
| 23 | C064 | 126 | 23.64% | 4.31% | PASS |
| 23 | C067 | 126 | 23.64% | 4.31% | PASS |
| 37 | C040 | 126 | 23.57% | 4.31% | PASS |
| 37 | C041 | 126 | 23.57% | 4.31% | PASS |
| 39 | C060 | 126 | 23.56% | 4.25% | PASS |
| 39 | C062 | 126 | 23.56% | 4.25% | PASS |
| 41 | C018 | 126 | 23.26% | 4.31% | PASS |
| 41 | C048 | 126 | 23.26% | 4.31% | PASS |
| 43 | C033 | 126 | 23.21% | 4.31% | PASS |
| 44 | C031 | 126 | 23.18% | 4.31% | PASS |
| 45 | C035 | 126 | 22.91% | 4.52% | PASS |
| 46 | C032 | 126 | 22.88% | 4.31% | PASS |
| 47 | C034 | 126 | 22.82% | 4.52% | PASS |
| 48 | C049 | 126 | 22.75% | 4.31% | PASS |
| 49 | C036 | 126 | 22.51% | 4.46% | PASS |
| 50 | C038 | 126 | 22.49% | 4.15% | PASS |
| 50 | C039 | 126 | 22.49% | 4.15% | PASS |
| 52 | C044 | 126 | 22.41% | 6.85% | PASS |
| 53 | C010 | 126 | 22.16% | 5.52% | PASS |
| 54 | C050 | 126 | 21.53% | 3.70% | PASS |
| 55 | C008 | 126 | 21.22% | 4.08% | PASS |
| 56 | C043 | 126 | 20.77% | 6.11% | PASS |
| 57 | C058 | 126 | 20.57% | 5.59% | PASS |
| 58 | C042 | 126 | 20.54% | 3.79% | PASS |
| 59 | C006 | 126 | 20.22% | 5.68% | PASS |
| 60 | C051 | 126 | 20.03% | 6.49% | PASS |
| 61 | C009 | 126 | 17.03% | 2.90% | PASS |
| 62 | C011 | 126 | 16.65% | 2.43% | PASS |
| 63 | C014 | 126 | 15.29% | 2.24% | PASS |
| 64 | C013 | 126 | 14.32% | 2.24% | PASS |
| — | C007 | 126 | 13.93% | 4.70% | FAILED |
| 65 | C012 | 126 | 9.04% | 3.92% | PASS |
| — | C016 | 126 | 8.64% | 2.96% | FAILED |
| 66 | C003 | 126 | 0.00% | 0.00% | PASS |

### bull_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 32.16% | 8.13% | PASS |
| 2 | C004 | 126 | 22.03% | 6.09% | PASS |
| 3 | C005 | 126 | 19.84% | 5.03% | PASS |
| 3 | C044 | 126 | 19.84% | 5.03% | PASS |
| 5 | C006 | 126 | 16.06% | 4.37% | PASS |
| 6 | C028 | 126 | 13.08% | 6.01% | PASS |
| 7 | C001 | 126 | 12.55% | 6.19% | PASS |
| 7 | C002 | 126 | 12.55% | 6.19% | PASS |
| 7 | C020 | 126 | 12.55% | 6.19% | PASS |
| 7 | C021 | 126 | 12.55% | 6.19% | PASS |
| 7 | C029 | 126 | 12.55% | 6.19% | PASS |
| 7 | C052 | 126 | 12.55% | 6.19% | PASS |
| 7 | C063 | 126 | 12.55% | 6.19% | PASS |
| 7 | C064 | 126 | 12.55% | 6.19% | PASS |
| 15 | C024 | 126 | 12.52% | 6.19% | PASS |
| 15 | C026 | 126 | 12.52% | 6.19% | PASS |
| 15 | C045 | 126 | 12.52% | 6.19% | PASS |
| 15 | C046 | 126 | 12.52% | 6.19% | PASS |
| 15 | C047 | 126 | 12.52% | 6.19% | PASS |
| 15 | C067 | 126 | 12.52% | 6.19% | PASS |
| 21 | C037 | 126 | 12.47% | 6.19% | PASS |
| 22 | C040 | 126 | 12.45% | 6.03% | PASS |
| 22 | C041 | 126 | 12.45% | 6.03% | PASS |
| 24 | C030 | 126 | 12.42% | 6.02% | PASS |
| 25 | C053 | 126 | 12.40% | 5.47% | PASS |
| 25 | C057 | 126 | 12.40% | 5.47% | PASS |
| 25 | C059 | 126 | 12.40% | 5.47% | PASS |
| 28 | C034 | 126 | 12.36% | 6.14% | PASS |
| 29 | C035 | 126 | 12.33% | 6.16% | PASS |
| 30 | C036 | 126 | 12.29% | 6.14% | PASS |
| 31 | C019 | 126 | 12.22% | 7.25% | PASS |
| 32 | C061 | 126 | 12.04% | 5.47% | PASS |
| 33 | C038 | 126 | 11.98% | 5.98% | PASS |
| 33 | C039 | 126 | 11.98% | 5.98% | PASS |
| 35 | C060 | 126 | 11.96% | 5.47% | PASS |
| 35 | C062 | 126 | 11.96% | 5.47% | PASS |
| 37 | C018 | 126 | 11.91% | 6.44% | PASS |
| 37 | C048 | 126 | 11.91% | 6.44% | PASS |
| 39 | C027 | 126 | 11.84% | 6.20% | PASS |
| 40 | C031 | 126 | 11.78% | 6.46% | PASS |
| 41 | C042 | 126 | 11.61% | 4.90% | PASS |
| 42 | C033 | 126 | 11.52% | 6.34% | PASS |
| 43 | C043 | 126 | 11.37% | 2.68% | PASS |
| 44 | C023 | 126 | 11.10% | 6.16% | PASS |
| 44 | C066 | 126 | 11.10% | 6.16% | PASS |
| 46 | C032 | 126 | 10.92% | 6.59% | PASS |
| 47 | C051 | 126 | 10.91% | 6.04% | PASS |
| 48 | C056 | 126 | 10.73% | 5.61% | PASS |
| 49 | C022 | 126 | 10.63% | 7.10% | PASS |
| 49 | C065 | 126 | 10.63% | 7.10% | PASS |
| 51 | C049 | 126 | 10.58% | 6.66% | PASS |
| 52 | C025 | 126 | 10.57% | 6.16% | PASS |
| 52 | C068 | 126 | 10.57% | 6.16% | PASS |
| 54 | C054 | 126 | 10.39% | 6.55% | PASS |
| — | C007 | 126 | 10.17% | 3.21% | FAILED |
| 55 | C058 | 126 | 10.09% | 6.14% | PASS |
| 56 | C009 | 126 | 10.09% | 5.33% | PASS |
| 57 | C050 | 126 | 10.02% | 5.56% | PASS |
| 58 | C017 | 126 | 9.81% | 7.41% | PASS |
| 59 | C055 | 126 | 9.22% | 6.87% | PASS |
| 60 | C008 | 126 | 8.37% | 5.18% | PASS |
| 61 | C011 | 126 | 7.99% | 3.54% | PASS |
| 62 | C014 | 126 | 7.71% | 2.75% | PASS |
| — | C016 | 126 | 6.61% | 2.05% | FAILED |
| 63 | C010 | 126 | 6.46% | 1.49% | PASS |
| 64 | C013 | 126 | 5.58% | 3.57% | PASS |
| 65 | C012 | 126 | 3.71% | 1.26% | PASS |
| 66 | C003 | 126 | 0.00% | 0.00% | PASS |

### corporate_actions_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 12.57% | 5.73% | PASS |
| 2 | C004 | 126 | 11.92% | 5.06% | PASS |
| 3 | C005 | 126 | 11.81% | 5.21% | PASS |
| 4 | C044 | 126 | 8.63% | 3.84% | PASS |
| 5 | C006 | 126 | 7.06% | 3.65% | PASS |
| 6 | C008 | 126 | 6.41% | 3.70% | PASS |
| 7 | C043 | 126 | 4.98% | 3.31% | PASS |
| — | C007 | 126 | 4.17% | 2.46% | FAILED |
| 8 | C042 | 126 | 3.45% | 4.01% | PASS |
| 9 | C010 | 126 | 3.21% | 1.61% | PASS |
| 10 | C009 | 126 | 2.66% | 4.48% | PASS |
| — | C016 | 126 | 2.38% | 1.54% | FAILED |
| 11 | C050 | 126 | 2.30% | 5.10% | PASS |
| 12 | C012 | 126 | 1.81% | 1.21% | PASS |
| 13 | C034 | 126 | 1.36% | 5.61% | PASS |
| 14 | C027 | 126 | 1.35% | 6.25% | PASS |
| 15 | C035 | 126 | 1.28% | 5.89% | PASS |
| 16 | C011 | 126 | 1.26% | 4.23% | PASS |
| 17 | C036 | 126 | 1.21% | 5.92% | PASS |
| 18 | C014 | 126 | 1.10% | 3.90% | PASS |
| 19 | C053 | 126 | 1.03% | 5.54% | PASS |
| 19 | C057 | 126 | 1.03% | 5.54% | PASS |
| 19 | C059 | 126 | 1.03% | 5.54% | PASS |
| 22 | C037 | 126 | 0.98% | 6.10% | PASS |
| 23 | C024 | 126 | 0.84% | 6.25% | PASS |
| 23 | C026 | 126 | 0.84% | 6.25% | PASS |
| 23 | C046 | 126 | 0.84% | 6.25% | PASS |
| 23 | C047 | 126 | 0.84% | 6.25% | PASS |
| 23 | C067 | 126 | 0.84% | 6.25% | PASS |
| 28 | C001 | 126 | 0.81% | 6.25% | PASS |
| 28 | C002 | 126 | 0.81% | 6.25% | PASS |
| 28 | C020 | 126 | 0.81% | 6.25% | PASS |
| 28 | C021 | 126 | 0.81% | 6.25% | PASS |
| 28 | C029 | 126 | 0.81% | 6.25% | PASS |
| 28 | C045 | 126 | 0.81% | 6.25% | PASS |
| 28 | C052 | 126 | 0.81% | 6.25% | PASS |
| 28 | C063 | 126 | 0.81% | 6.25% | PASS |
| 28 | C064 | 126 | 0.81% | 6.25% | PASS |
| 37 | C040 | 126 | 0.77% | 6.11% | PASS |
| 37 | C041 | 126 | 0.77% | 6.11% | PASS |
| 39 | C038 | 126 | 0.66% | 6.08% | PASS |
| 39 | C039 | 126 | 0.66% | 6.08% | PASS |
| 41 | C061 | 126 | 0.57% | 5.59% | PASS |
| 42 | C022 | 126 | 0.47% | 6.08% | PASS |
| 42 | C065 | 126 | 0.47% | 6.08% | PASS |
| 44 | C060 | 126 | 0.42% | 5.47% | PASS |
| 44 | C062 | 126 | 0.42% | 5.47% | PASS |
| 46 | C051 | 126 | 0.41% | 5.41% | PASS |
| 47 | C013 | 126 | 0.27% | 3.90% | PASS |
| 48 | C019 | 126 | 0.24% | 6.41% | PASS |
| 49 | C030 | 126 | 0.20% | 6.25% | PASS |
| 50 | C018 | 126 | 0.12% | 6.17% | PASS |
| 50 | C048 | 126 | 0.12% | 6.17% | PASS |
| 52 | C031 | 126 | 0.11% | 6.08% | PASS |
| 53 | C033 | 126 | 0.08% | 6.05% | PASS |
| 54 | C003 | 126 | 0.00% | 0.00% | PASS |
| 55 | C028 | 126 | -0.33% | 6.26% | PASS |
| 56 | C032 | 126 | -0.41% | 5.99% | PASS |
| 57 | C023 | 126 | -0.81% | 7.57% | PASS |
| 57 | C066 | 126 | -0.81% | 7.57% | PASS |
| 59 | C025 | 126 | -1.10% | 7.48% | PASS |
| 59 | C068 | 126 | -1.10% | 7.48% | PASS |
| 61 | C058 | 126 | -1.18% | 6.53% | PASS |
| 62 | C049 | 126 | -1.52% | 6.28% | PASS |
| 63 | C054 | 126 | -2.39% | 7.02% | PASS |
| 64 | C056 | 126 | -2.96% | 7.88% | PASS |
| 65 | C017 | 126 | -4.37% | 6.48% | PASS |
| 66 | C055 | 126 | -4.83% | 9.08% | PASS |

### corporate_actions_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 24.60% | 7.09% | PASS |
| 2 | C005 | 126 | 22.04% | 6.54% | PASS |
| 3 | C010 | 126 | 18.62% | 3.81% | PASS |
| 4 | C004 | 126 | 18.20% | 6.30% | PASS |
| 5 | C044 | 126 | 16.91% | 4.53% | PASS |
| 6 | C019 | 126 | 16.12% | 5.70% | PASS |
| 7 | C043 | 126 | 15.33% | 4.83% | PASS |
| 8 | C025 | 126 | 13.51% | 5.83% | PASS |
| 8 | C068 | 126 | 13.51% | 5.83% | PASS |
| 10 | C020 | 126 | 13.43% | 5.58% | PASS |
| 10 | C063 | 126 | 13.43% | 5.58% | PASS |
| 12 | C026 | 126 | 13.29% | 5.58% | PASS |
| 13 | C018 | 126 | 13.16% | 5.56% | PASS |
| 14 | C046 | 126 | 12.76% | 6.12% | PASS |
| 15 | C001 | 126 | 12.75% | 6.12% | PASS |
| 15 | C002 | 126 | 12.75% | 6.12% | PASS |
| 15 | C021 | 126 | 12.75% | 6.12% | PASS |
| 15 | C023 | 126 | 12.75% | 6.12% | PASS |
| 15 | C027 | 126 | 12.75% | 6.12% | PASS |
| 15 | C029 | 126 | 12.75% | 6.12% | PASS |
| 15 | C045 | 126 | 12.75% | 6.12% | PASS |
| 15 | C052 | 126 | 12.75% | 6.12% | PASS |
| 15 | C064 | 126 | 12.75% | 6.12% | PASS |
| 15 | C066 | 126 | 12.75% | 6.12% | PASS |
| 25 | C028 | 126 | 12.71% | 6.11% | PASS |
| 25 | C030 | 126 | 12.71% | 6.11% | PASS |
| 27 | C040 | 126 | 12.68% | 5.94% | PASS |
| 27 | C041 | 126 | 12.68% | 5.94% | PASS |
| 29 | C024 | 126 | 12.63% | 6.12% | PASS |
| 29 | C047 | 126 | 12.63% | 6.12% | PASS |
| 29 | C067 | 126 | 12.63% | 6.12% | PASS |
| 32 | C006 | 126 | 12.60% | 4.72% | PASS |
| 33 | C037 | 126 | 12.51% | 6.06% | PASS |
| 34 | C048 | 126 | 12.46% | 6.14% | PASS |
| 35 | C031 | 126 | 12.44% | 6.13% | PASS |
| 36 | C038 | 126 | 12.40% | 5.91% | PASS |
| 36 | C039 | 126 | 12.40% | 5.91% | PASS |
| 38 | C035 | 126 | 12.33% | 6.03% | PASS |
| 39 | C033 | 126 | 12.28% | 5.63% | PASS |
| 40 | C032 | 126 | 12.22% | 6.16% | PASS |
| 41 | C009 | 126 | 12.21% | 5.33% | PASS |
| 42 | C022 | 126 | 12.20% | 6.13% | PASS |
| 42 | C065 | 126 | 12.20% | 6.13% | PASS |
| 44 | C036 | 126 | 12.07% | 6.00% | PASS |
| — | C007 | 126 | 11.93% | 2.95% | FAILED |
| 45 | C049 | 126 | 11.86% | 6.26% | PASS |
| 46 | C034 | 126 | 11.78% | 5.90% | PASS |
| 47 | C008 | 126 | 11.72% | 7.20% | PASS |
| 48 | C042 | 126 | 11.33% | 4.05% | PASS |
| 49 | C057 | 126 | 10.84% | 6.45% | PASS |
| 49 | C058 | 126 | 10.84% | 6.45% | PASS |
| 51 | C062 | 126 | 10.43% | 6.56% | PASS |
| 52 | C053 | 126 | 10.18% | 7.01% | PASS |
| 52 | C059 | 126 | 10.18% | 7.01% | PASS |
| 54 | C061 | 126 | 10.02% | 7.08% | PASS |
| 55 | C060 | 126 | 9.72% | 7.15% | PASS |
| 56 | C050 | 126 | 9.69% | 5.69% | PASS |
| 57 | C017 | 126 | 8.56% | 9.96% | PASS |
| 58 | C056 | 126 | 8.40% | 6.80% | PASS |
| 59 | C054 | 126 | 7.75% | 8.02% | PASS |
| 60 | C055 | 126 | 7.75% | 7.11% | PASS |
| 61 | C051 | 126 | 6.77% | 7.05% | PASS |
| — | C016 | 126 | 6.70% | 1.74% | FAILED |
| 62 | C011 | 126 | 6.13% | 6.56% | PASS |
| 63 | C014 | 126 | 5.67% | 5.93% | PASS |
| 64 | C013 | 126 | 5.14% | 6.37% | PASS |
| 65 | C012 | 126 | 3.60% | 2.30% | PASS |
| 66 | C003 | 126 | 0.00% | 0.00% | PASS |

### crash_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C017 | 126 | -5.89% | 9.65% | PASS |
| 3 | C049 | 126 | -6.51% | 10.30% | PASS |
| 4 | C033 | 126 | -7.38% | 11.12% | PASS |
| 5 | C032 | 126 | -7.52% | 11.26% | PASS |
| 6 | C012 | 126 | -9.98% | 12.68% | PASS |
| 7 | C062 | 126 | -10.14% | 13.80% | PASS |
| 8 | C060 | 126 | -10.15% | 13.81% | PASS |
| 9 | C031 | 126 | -10.48% | 14.10% | PASS |
| 10 | C025 | 126 | -10.60% | 14.22% | PASS |
| 10 | C068 | 126 | -10.60% | 14.22% | PASS |
| 12 | C022 | 126 | -10.62% | 14.24% | PASS |
| 12 | C065 | 126 | -10.62% | 14.24% | PASS |
| 14 | C011 | 126 | -10.92% | 13.60% | PASS |
| 15 | C018 | 126 | -10.98% | 14.58% | PASS |
| 16 | C048 | 126 | -11.17% | 14.76% | PASS |
| 17 | C019 | 126 | -11.22% | 14.90% | PASS |
| 18 | C061 | 126 | -12.75% | 16.31% | PASS |
| 19 | C021 | 126 | -13.98% | 17.46% | PASS |
| 19 | C064 | 126 | -13.98% | 17.46% | PASS |
| 21 | C057 | 126 | -14.13% | 17.63% | PASS |
| 21 | C058 | 126 | -14.13% | 17.63% | PASS |
| 21 | C059 | 126 | -14.13% | 17.63% | PASS |
| 24 | C053 | 126 | -14.15% | 17.64% | PASS |
| 25 | C024 | 126 | -14.63% | 18.09% | PASS |
| 25 | C047 | 126 | -14.63% | 18.09% | PASS |
| 25 | C067 | 126 | -14.63% | 18.09% | PASS |
| 28 | C038 | 126 | -14.78% | 18.07% | PASS |
| 28 | C039 | 126 | -14.78% | 18.07% | PASS |
| 30 | C046 | 126 | -14.85% | 18.29% | PASS |
| 31 | C045 | 126 | -14.89% | 18.33% | PASS |
| 32 | C026 | 126 | -14.91% | 18.35% | PASS |
| 33 | C040 | 126 | -15.07% | 18.49% | PASS |
| 33 | C041 | 126 | -15.07% | 18.49% | PASS |
| 35 | C001 | 126 | -15.12% | 18.55% | PASS |
| 35 | C002 | 126 | -15.12% | 18.55% | PASS |
| 35 | C020 | 126 | -15.12% | 18.55% | PASS |
| 35 | C023 | 126 | -15.12% | 18.55% | PASS |
| 35 | C027 | 126 | -15.12% | 18.55% | PASS |
| 35 | C028 | 126 | -15.12% | 18.55% | PASS |
| 35 | C029 | 126 | -15.12% | 18.55% | PASS |
| 35 | C030 | 126 | -15.12% | 18.55% | PASS |
| 35 | C052 | 126 | -15.12% | 18.55% | PASS |
| 35 | C063 | 126 | -15.12% | 18.55% | PASS |
| 35 | C066 | 126 | -15.12% | 18.55% | PASS |
| — | C016 | 126 | -15.32% | 16.35% | FAILED |
| 46 | C035 | 126 | -15.32% | 18.67% | PASS |
| 47 | C036 | 126 | -15.34% | 18.69% | PASS |
| 48 | C034 | 126 | -15.34% | 18.69% | PASS |
| 49 | C037 | 126 | -15.38% | 18.76% | PASS |
| 50 | C050 | 126 | -15.58% | 18.34% | PASS |
| 51 | C056 | 126 | -16.35% | 19.60% | PASS |
| 52 | C055 | 126 | -16.46% | 19.72% | PASS |
| 53 | C054 | 126 | -16.49% | 19.84% | PASS |
| 54 | C051 | 126 | -18.33% | 19.38% | PASS |
| 55 | C013 | 126 | -25.04% | 26.96% | PASS |
| 56 | C014 | 126 | -26.74% | 28.62% | PASS |
| — | C007 | 126 | -27.20% | 28.79% | FAILED |
| 57 | C008 | 126 | -30.16% | 32.85% | PASS |
| 58 | C009 | 126 | -31.67% | 33.80% | PASS |
| 59 | C042 | 126 | -32.38% | 34.35% | PASS |
| 60 | C010 | 126 | -36.70% | 38.86% | PASS |
| 61 | C043 | 126 | -36.89% | 38.83% | PASS |
| — | C006 | 126 | -38.33% | 40.38% | FAILED |
| 62 | C004 | 126 | -41.21% | 43.72% | PASS |
| 63 | C044 | 126 | -41.27% | 43.27% | PASS |
| — | C005 | 126 | -49.05% | 51.22% | FAILED |
| — | C015 | 126 | -54.12% | 56.24% | FAILED |

### crash_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C008 | 126 | -5.40% | 5.48% | PASS |
| 3 | C017 | 126 | -6.00% | 6.05% | PASS |
| 4 | C049 | 126 | -6.85% | 7.51% | PASS |
| 5 | C013 | 126 | -6.91% | 6.91% | PASS |
| 6 | C033 | 126 | -7.69% | 8.51% | PASS |
| 7 | C032 | 126 | -8.50% | 9.06% | PASS |
| 8 | C012 | 126 | -10.48% | 10.67% | PASS |
| 9 | C022 | 126 | -11.50% | 12.22% | PASS |
| 9 | C031 | 126 | -11.50% | 12.22% | PASS |
| 9 | C065 | 126 | -11.50% | 12.22% | PASS |
| 12 | C025 | 126 | -11.67% | 12.36% | PASS |
| 12 | C068 | 126 | -11.67% | 12.36% | PASS |
| 14 | C014 | 126 | -11.83% | 11.94% | PASS |
| 15 | C011 | 126 | -12.02% | 12.28% | PASS |
| 16 | C019 | 126 | -12.16% | 12.84% | PASS |
| 17 | C062 | 126 | -12.16% | 12.88% | PASS |
| 18 | C060 | 126 | -12.16% | 12.88% | PASS |
| 19 | C018 | 126 | -12.16% | 12.84% | PASS |
| 20 | C048 | 126 | -12.16% | 12.89% | PASS |
| 21 | C010 | 126 | -12.64% | 13.38% | PASS |
| 22 | C009 | 126 | -13.78% | 14.07% | PASS |
| 23 | C061 | 126 | -15.33% | 15.71% | PASS |
| 24 | C021 | 126 | -15.54% | 15.95% | PASS |
| 24 | C064 | 126 | -15.54% | 15.95% | PASS |
| 26 | C038 | 126 | -16.12% | 16.62% | PASS |
| 26 | C039 | 126 | -16.12% | 16.62% | PASS |
| 28 | C016 | 126 | -16.56% | 16.80% | PASS |
| 29 | C024 | 126 | -16.63% | 17.12% | PASS |
| 29 | C047 | 126 | -16.63% | 17.12% | PASS |
| 29 | C067 | 126 | -16.63% | 17.12% | PASS |
| 32 | C001 | 126 | -16.66% | 17.15% | PASS |
| 32 | C002 | 126 | -16.66% | 17.15% | PASS |
| 32 | C020 | 126 | -16.66% | 17.15% | PASS |
| 32 | C023 | 126 | -16.66% | 17.15% | PASS |
| 32 | C026 | 126 | -16.66% | 17.15% | PASS |
| 32 | C027 | 126 | -16.66% | 17.15% | PASS |
| 32 | C028 | 126 | -16.66% | 17.15% | PASS |
| 32 | C029 | 126 | -16.66% | 17.15% | PASS |
| 32 | C030 | 126 | -16.66% | 17.15% | PASS |
| 32 | C034 | 126 | -16.66% | 17.15% | PASS |
| 32 | C035 | 126 | -16.66% | 17.15% | PASS |
| 32 | C036 | 126 | -16.66% | 17.15% | PASS |
| 32 | C037 | 126 | -16.66% | 17.15% | PASS |
| 32 | C040 | 126 | -16.66% | 17.15% | PASS |
| 32 | C041 | 126 | -16.66% | 17.15% | PASS |
| 32 | C045 | 126 | -16.66% | 17.15% | PASS |
| 32 | C046 | 126 | -16.66% | 17.15% | PASS |
| 32 | C050 | 126 | -16.66% | 17.15% | PASS |
| 32 | C051 | 126 | -16.66% | 17.15% | PASS |
| 32 | C052 | 126 | -16.66% | 17.15% | PASS |
| 32 | C054 | 126 | -16.66% | 17.15% | PASS |
| 32 | C055 | 126 | -16.66% | 17.15% | PASS |
| 32 | C056 | 126 | -16.66% | 17.15% | PASS |
| 32 | C057 | 126 | -16.66% | 17.15% | PASS |
| 32 | C058 | 126 | -16.66% | 17.15% | PASS |
| 32 | C059 | 126 | -16.66% | 17.15% | PASS |
| 32 | C063 | 126 | -16.66% | 17.15% | PASS |
| 32 | C066 | 126 | -16.66% | 17.15% | PASS |
| 60 | C053 | 126 | -16.67% | 17.15% | PASS |
| 61 | C043 | 126 | -25.88% | 26.28% | PASS |
| 62 | C042 | 126 | -26.68% | 27.08% | PASS |
| — | C007 | 126 | -27.83% | 28.14% | FAILED |
| — | C006 | 126 | -40.53% | 41.13% | FAILED |
| 63 | C005 | 126 | -44.71% | 45.37% | PASS |
| 63 | C044 | 126 | -44.71% | 45.37% | PASS |
| 65 | C004 | 126 | -44.78% | 45.48% | PASS |
| — | C015 | 126 | -57.77% | 58.52% | FAILED |

### fast_recovery_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C017 | 126 | 66.25% | 8.18% | PASS |
| 2 | C051 | 126 | 52.45% | 15.27% | PASS |
| 3 | C054 | 126 | 41.80% | 26.30% | PASS |
| 4 | C004 | 126 | 41.04% | 39.42% | PASS |
| 5 | C053 | 126 | 40.64% | 27.18% | PASS |
| 6 | C059 | 126 | 40.22% | 27.06% | PASS |
| 7 | C061 | 126 | 39.56% | 27.26% | PASS |
| 8 | C056 | 126 | 39.38% | 28.00% | PASS |
| 9 | C057 | 126 | 38.56% | 27.06% | PASS |
| 9 | C058 | 126 | 38.56% | 27.06% | PASS |
| 11 | C060 | 126 | 37.63% | 27.27% | PASS |
| 12 | C015 | 126 | 36.83% | 49.20% | PASS |
| 13 | C055 | 126 | 36.51% | 29.87% | PASS |
| 14 | C062 | 126 | 35.52% | 27.08% | PASS |
| 15 | C005 | 126 | 32.43% | 36.07% | PASS |
| 15 | C044 | 126 | 32.43% | 36.07% | PASS |
| — | C006 | 126 | 30.57% | 33.59% | FAILED |
| 17 | C052 | 126 | 20.86% | 35.47% | PASS |
| — | C007 | 126 | 20.47% | 23.04% | FAILED |
| 18 | C043 | 126 | 18.78% | 19.20% | PASS |
| 19 | C036 | 126 | 17.57% | 34.28% | PASS |
| 20 | C024 | 126 | 17.33% | 35.47% | PASS |
| 20 | C026 | 126 | 17.33% | 35.47% | PASS |
| 20 | C047 | 126 | 17.33% | 35.47% | PASS |
| 20 | C067 | 126 | 17.33% | 35.47% | PASS |
| 24 | C034 | 126 | 17.30% | 34.16% | PASS |
| 25 | C046 | 126 | 17.25% | 35.47% | PASS |
| 26 | C035 | 126 | 17.10% | 34.32% | PASS |
| 27 | C038 | 126 | 16.60% | 34.41% | PASS |
| 27 | C039 | 126 | 16.60% | 34.41% | PASS |
| 29 | C045 | 126 | 16.28% | 35.47% | PASS |
| 30 | C037 | 126 | 16.14% | 34.92% | PASS |
| 31 | C001 | 126 | 16.11% | 35.47% | PASS |
| 31 | C002 | 126 | 16.11% | 35.47% | PASS |
| 31 | C020 | 126 | 16.11% | 35.47% | PASS |
| 31 | C027 | 126 | 16.11% | 35.47% | PASS |
| 31 | C029 | 126 | 16.11% | 35.47% | PASS |
| 31 | C063 | 126 | 16.11% | 35.47% | PASS |
| 37 | C023 | 126 | 16.06% | 35.47% | PASS |
| 37 | C066 | 126 | 16.06% | 35.47% | PASS |
| 39 | C040 | 126 | 15.63% | 35.76% | PASS |
| 39 | C041 | 126 | 15.63% | 35.76% | PASS |
| 41 | C008 | 126 | 15.58% | 9.62% | PASS |
| 42 | C022 | 126 | 14.08% | 35.42% | PASS |
| 42 | C065 | 126 | 14.08% | 35.42% | PASS |
| 44 | C048 | 126 | 13.57% | 35.51% | PASS |
| 45 | C031 | 126 | 13.08% | 35.53% | PASS |
| 46 | C028 | 126 | 12.84% | 35.47% | PASS |
| 46 | C030 | 126 | 12.84% | 35.47% | PASS |
| 48 | C011 | 126 | 12.47% | 27.09% | PASS |
| — | C016 | 126 | 11.42% | 14.34% | FAILED |
| 49 | C010 | 126 | 11.13% | 9.70% | PASS |
| 50 | C032 | 126 | 10.99% | 35.64% | PASS |
| 51 | C033 | 126 | 10.50% | 35.64% | PASS |
| 52 | C049 | 126 | 9.20% | 35.76% | PASS |
| 53 | C012 | 126 | 8.21% | 9.26% | PASS |
| 54 | C050 | 126 | 6.82% | 33.32% | PASS |
| 55 | C014 | 126 | 5.30% | 24.53% | PASS |
| — | C042 | 126 | 3.96% | 35.50% | FAILED |
| 56 | C013 | 126 | 2.26% | 24.58% | PASS |
| 57 | C003 | 126 | 0.00% | 0.00% | PASS |
| — | C009 | 126 | -1.20% | 32.07% | FAILED |
| 58 | C025 | 126 | -19.83% | 35.27% | PASS |
| 58 | C068 | 126 | -19.83% | 35.27% | PASS |
| 60 | C021 | 126 | -20.72% | 35.25% | PASS |
| 60 | C064 | 126 | -20.72% | 35.25% | PASS |
| 62 | C018 | 126 | -23.19% | 35.33% | PASS |
| 63 | C019 | 126 | -30.42% | 43.25% | PASS |

### fast_recovery_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C060 | 126 | 44.60% | 13.45% | PASS |
| 2 | C061 | 126 | 44.39% | 15.08% | PASS |
| 3 | C055 | 126 | 44.23% | 14.87% | PASS |
| 4 | C059 | 126 | 44.23% | 15.98% | PASS |
| 5 | C053 | 126 | 44.05% | 15.98% | PASS |
| 6 | C056 | 126 | 43.18% | 15.17% | PASS |
| 7 | C017 | 126 | 42.61% | 9.32% | PASS |
| 8 | C054 | 126 | 41.83% | 15.50% | PASS |
| 9 | C062 | 126 | 40.88% | 13.45% | PASS |
| 10 | C057 | 126 | 40.86% | 15.98% | PASS |
| 10 | C058 | 126 | 40.86% | 15.98% | PASS |
| 12 | C033 | 126 | 33.56% | 9.46% | PASS |
| 13 | C049 | 126 | 32.09% | 10.80% | PASS |
| 14 | C052 | 126 | 31.61% | 16.92% | PASS |
| 15 | C048 | 126 | 31.42% | 14.39% | PASS |
| 16 | C028 | 126 | 31.10% | 16.61% | PASS |
| 16 | C030 | 126 | 31.10% | 16.61% | PASS |
| 18 | C038 | 126 | 30.49% | 16.14% | PASS |
| 18 | C039 | 126 | 30.49% | 16.14% | PASS |
| 20 | C018 | 126 | 29.85% | 14.39% | PASS |
| 21 | C022 | 126 | 29.82% | 13.95% | PASS |
| 21 | C065 | 126 | 29.82% | 13.95% | PASS |
| 23 | C032 | 126 | 29.70% | 11.94% | PASS |
| 24 | C025 | 126 | 29.59% | 13.95% | PASS |
| 24 | C068 | 126 | 29.59% | 13.95% | PASS |
| 26 | C026 | 126 | 29.55% | 16.92% | PASS |
| 27 | C051 | 126 | 29.37% | 15.77% | PASS |
| 28 | C031 | 126 | 29.34% | 13.95% | PASS |
| 29 | C045 | 126 | 29.02% | 16.92% | PASS |
| 30 | C024 | 126 | 28.92% | 16.92% | PASS |
| 30 | C047 | 126 | 28.92% | 16.92% | PASS |
| 30 | C067 | 126 | 28.92% | 16.92% | PASS |
| 33 | C001 | 126 | 28.80% | 16.92% | PASS |
| 33 | C002 | 126 | 28.80% | 16.92% | PASS |
| 33 | C020 | 126 | 28.80% | 16.92% | PASS |
| 33 | C023 | 126 | 28.80% | 16.92% | PASS |
| 33 | C027 | 126 | 28.80% | 16.92% | PASS |
| 33 | C029 | 126 | 28.80% | 16.92% | PASS |
| 33 | C063 | 126 | 28.80% | 16.92% | PASS |
| 33 | C066 | 126 | 28.80% | 16.92% | PASS |
| 41 | C037 | 126 | 28.63% | 16.83% | PASS |
| 42 | C036 | 126 | 28.60% | 16.88% | PASS |
| 43 | C019 | 126 | 28.59% | 14.52% | PASS |
| 44 | C046 | 126 | 28.51% | 16.92% | PASS |
| 45 | C035 | 126 | 28.45% | 16.86% | PASS |
| 46 | C034 | 126 | 28.42% | 16.86% | PASS |
| 47 | C040 | 126 | 28.35% | 16.89% | PASS |
| 47 | C041 | 126 | 28.35% | 16.89% | PASS |
| 49 | C050 | 126 | 25.30% | 15.81% | PASS |
| 50 | C004 | 126 | 25.29% | 37.72% | PASS |
| 51 | C021 | 126 | 24.88% | 16.92% | PASS |
| 51 | C064 | 126 | 24.88% | 16.92% | PASS |
| 53 | C010 | 126 | 20.09% | 35.50% | PASS |
| 54 | C044 | 126 | 18.06% | 36.60% | PASS |
| 55 | C043 | 126 | 17.83% | 32.46% | PASS |
| — | C006 | 126 | 15.63% | 32.60% | FAILED |
| 56 | C015 | 126 | 15.58% | 48.79% | PASS |
| 57 | C005 | 126 | 14.44% | 44.30% | PASS |
| 58 | C008 | 126 | 11.39% | 12.15% | PASS |
| — | C007 | 126 | 11.28% | 22.08% | FAILED |
| 59 | C042 | 126 | 7.08% | 29.51% | PASS |
| — | C016 | 126 | 5.61% | 13.53% | FAILED |
| 60 | C012 | 126 | 3.74% | 9.78% | PASS |
| 61 | C011 | 126 | 1.09% | 27.44% | PASS |
| 62 | C003 | 126 | 0.00% | 0.00% | PASS |
| 63 | C014 | 126 | -1.76% | 24.51% | PASS |
| 64 | C009 | 126 | -4.58% | 32.21% | PASS |
| 65 | C013 | 126 | -4.97% | 24.48% | PASS |

### high_volatility_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C008 | 126 | 9.90% | 4.23% | PASS |
| 2 | C056 | 126 | 6.54% | 12.12% | PASS |
| 3 | C055 | 126 | 5.46% | 12.12% | PASS |
| 4 | C017 | 126 | 4.97% | 7.09% | PASS |
| 5 | C059 | 126 | 3.66% | 12.13% | PASS |
| 6 | C049 | 126 | 2.98% | 8.49% | PASS |
| 7 | C032 | 126 | 2.71% | 9.40% | PASS |
| 7 | C033 | 126 | 2.71% | 9.40% | PASS |
| 9 | C031 | 126 | 2.56% | 10.61% | PASS |
| 10 | C048 | 126 | 1.96% | 11.18% | PASS |
| 11 | C054 | 126 | 1.94% | 12.18% | PASS |
| 12 | C034 | 126 | 1.92% | 12.14% | PASS |
| 12 | C035 | 126 | 1.92% | 12.14% | PASS |
| 12 | C050 | 126 | 1.92% | 12.14% | PASS |
| 15 | C036 | 126 | 1.91% | 12.15% | PASS |
| 16 | C018 | 126 | 1.91% | 11.18% | PASS |
| 17 | C040 | 126 | 1.85% | 12.19% | PASS |
| 17 | C041 | 126 | 1.85% | 12.19% | PASS |
| 19 | C037 | 126 | 1.83% | 12.21% | PASS |
| 20 | C020 | 126 | 1.80% | 12.30% | PASS |
| 20 | C063 | 126 | 1.80% | 12.30% | PASS |
| 22 | C046 | 126 | 1.76% | 12.32% | PASS |
| 23 | C001 | 126 | 1.74% | 12.30% | PASS |
| 23 | C002 | 126 | 1.74% | 12.30% | PASS |
| 23 | C027 | 126 | 1.74% | 12.30% | PASS |
| 23 | C028 | 126 | 1.74% | 12.30% | PASS |
| 23 | C029 | 126 | 1.74% | 12.30% | PASS |
| 23 | C030 | 126 | 1.74% | 12.30% | PASS |
| 23 | C051 | 126 | 1.74% | 12.30% | PASS |
| 30 | C026 | 126 | 1.72% | 12.30% | PASS |
| 31 | C038 | 126 | 1.70% | 12.11% | PASS |
| 31 | C039 | 126 | 1.70% | 12.11% | PASS |
| 33 | C024 | 126 | 1.68% | 12.27% | PASS |
| 33 | C047 | 126 | 1.68% | 12.27% | PASS |
| 33 | C067 | 126 | 1.68% | 12.27% | PASS |
| 36 | C045 | 126 | 1.56% | 12.50% | PASS |
| 37 | C021 | 126 | 1.27% | 12.13% | PASS |
| 37 | C064 | 126 | 1.27% | 12.13% | PASS |
| 39 | C022 | 126 | 1.21% | 10.96% | PASS |
| 39 | C065 | 126 | 1.21% | 10.96% | PASS |
| 41 | C058 | 126 | 0.58% | 13.28% | PASS |
| 42 | C060 | 126 | 0.49% | 12.38% | PASS |
| 43 | C062 | 126 | 0.48% | 12.46% | PASS |
| 44 | C053 | 126 | 0.21% | 13.59% | PASS |
| 45 | C013 | 126 | 0.19% | 9.54% | PASS |
| 46 | C057 | 126 | 0.16% | 13.61% | PASS |
| 47 | C003 | 126 | 0.00% | 0.00% | PASS |
| 48 | C061 | 126 | -0.02% | 13.33% | PASS |
| 49 | C019 | 126 | -0.31% | 15.35% | PASS |
| 50 | C043 | 126 | -0.69% | 25.97% | PASS |
| — | C042 | 126 | -0.70% | 22.20% | FAILED |
| 51 | C014 | 126 | -2.31% | 11.47% | PASS |
| 52 | C004 | 126 | -2.31% | 27.50% | PASS |
| 53 | C010 | 126 | -2.97% | 25.70% | PASS |
| — | C016 | 126 | -3.01% | 12.35% | FAILED |
| 54 | C025 | 126 | -3.11% | 14.67% | PASS |
| 54 | C068 | 126 | -3.11% | 14.67% | PASS |
| 56 | C005 | 126 | -3.64% | 27.70% | PASS |
| 56 | C044 | 126 | -3.64% | 27.70% | PASS |
| — | C007 | 126 | -4.93% | 18.83% | FAILED |
| 58 | C052 | 126 | -5.01% | 17.36% | PASS |
| 59 | C023 | 126 | -5.63% | 18.18% | PASS |
| 59 | C066 | 126 | -5.63% | 18.18% | PASS |
| 61 | C015 | 126 | -9.46% | 38.30% | PASS |
| 62 | C012 | 126 | -9.73% | 24.08% | PASS |
| 63 | C006 | 126 | -10.27% | 26.65% | PASS |
| 64 | C011 | 126 | -10.55% | 23.59% | PASS |
| 65 | C009 | 126 | -13.06% | 28.82% | PASS |

### high_volatility_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C008 | 126 | -1.70% | 3.88% | PASS |
| 3 | C049 | 126 | -4.21% | 8.04% | PASS |
| 4 | C033 | 126 | -4.44% | 8.73% | PASS |
| 5 | C032 | 126 | -4.59% | 8.72% | PASS |
| 6 | C013 | 126 | -5.52% | 7.59% | PASS |
| 7 | C031 | 126 | -6.46% | 11.83% | PASS |
| 8 | C060 | 126 | -6.99% | 12.57% | PASS |
| 9 | C062 | 126 | -7.01% | 12.57% | PASS |
| 10 | C048 | 126 | -7.08% | 12.58% | PASS |
| 11 | C018 | 126 | -7.08% | 12.48% | PASS |
| 12 | C017 | 126 | -7.20% | 8.41% | PASS |
| 13 | C010 | 126 | -7.43% | 13.02% | PASS |
| 14 | C019 | 126 | -7.62% | 12.20% | PASS |
| 15 | C025 | 126 | -9.01% | 13.08% | PASS |
| 15 | C068 | 126 | -9.01% | 13.08% | PASS |
| 17 | C022 | 126 | -9.46% | 13.38% | PASS |
| 17 | C065 | 126 | -9.46% | 13.38% | PASS |
| 19 | C012 | 126 | -10.98% | 13.02% | PASS |
| 20 | C061 | 126 | -11.30% | 16.20% | PASS |
| 21 | C038 | 126 | -11.50% | 17.37% | PASS |
| 21 | C039 | 126 | -11.50% | 17.37% | PASS |
| 23 | C056 | 126 | -11.56% | 17.43% | PASS |
| 24 | C024 | 126 | -11.62% | 17.22% | PASS |
| 24 | C047 | 126 | -11.62% | 17.22% | PASS |
| 24 | C067 | 126 | -11.62% | 17.22% | PASS |
| 27 | C054 | 126 | -11.64% | 17.38% | PASS |
| 28 | C055 | 126 | -11.64% | 17.42% | PASS |
| 29 | C020 | 126 | -11.66% | 17.51% | PASS |
| 29 | C058 | 126 | -11.66% | 17.51% | PASS |
| 29 | C063 | 126 | -11.66% | 17.51% | PASS |
| 32 | C040 | 126 | -11.70% | 17.51% | PASS |
| 32 | C041 | 126 | -11.70% | 17.51% | PASS |
| 32 | C001 | 126 | -11.70% | 17.51% | PASS |
| 32 | C002 | 126 | -11.70% | 17.51% | PASS |
| 32 | C027 | 126 | -11.70% | 17.51% | PASS |
| 32 | C028 | 126 | -11.70% | 17.51% | PASS |
| 32 | C029 | 126 | -11.70% | 17.51% | PASS |
| 32 | C030 | 126 | -11.70% | 17.51% | PASS |
| 32 | C034 | 126 | -11.70% | 17.51% | PASS |
| 32 | C035 | 126 | -11.70% | 17.51% | PASS |
| 32 | C036 | 126 | -11.70% | 17.51% | PASS |
| 32 | C037 | 126 | -11.70% | 17.51% | PASS |
| 32 | C050 | 126 | -11.70% | 17.51% | PASS |
| 32 | C051 | 126 | -11.70% | 17.51% | PASS |
| 46 | C026 | 126 | -11.72% | 17.42% | PASS |
| 46 | C057 | 126 | -11.72% | 17.42% | PASS |
| 48 | C059 | 126 | -11.74% | 17.44% | PASS |
| 49 | C045 | 126 | -11.74% | 17.35% | PASS |
| 50 | C046 | 126 | -11.75% | 17.36% | PASS |
| 51 | C053 | 126 | -11.77% | 17.51% | PASS |
| 52 | C014 | 126 | -12.30% | 15.17% | PASS |
| 53 | C021 | 126 | -12.48% | 16.26% | PASS |
| 53 | C064 | 126 | -12.48% | 16.26% | PASS |
| 55 | C023 | 126 | -14.98% | 17.12% | PASS |
| 55 | C066 | 126 | -14.98% | 17.12% | PASS |
| 57 | C009 | 126 | -16.57% | 20.74% | PASS |
| 58 | C011 | 126 | -16.91% | 22.33% | PASS |
| — | C016 | 126 | -17.39% | 20.66% | FAILED |
| 59 | C043 | 126 | -22.17% | 26.17% | PASS |
| 60 | C052 | 126 | -23.35% | 23.55% | PASS |
| — | C007 | 126 | -30.04% | 34.29% | FAILED |
| 61 | C042 | 126 | -30.25% | 32.25% | PASS |
| — | C006 | 126 | -40.48% | 45.53% | FAILED |
| 62 | C005 | 126 | -42.05% | 48.82% | PASS |
| 62 | C044 | 126 | -42.05% | 48.82% | PASS |
| 64 | C004 | 126 | -44.90% | 49.83% | PASS |
| — | C015 | 126 | -57.51% | 64.21% | FAILED |

### leveraged_decay_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C032 | 126 | 2.52% | 4.58% | PASS |
| 1 | C033 | 126 | 2.52% | 4.58% | PASS |
| 3 | C008 | 126 | 2.45% | 4.97% | PASS |
| 4 | C019 | 126 | 1.84% | 4.69% | PASS |
| 5 | C031 | 126 | 1.63% | 4.58% | PASS |
| 6 | C049 | 126 | 1.16% | 4.58% | PASS |
| 7 | C018 | 126 | 0.84% | 4.58% | PASS |
| 7 | C048 | 126 | 0.84% | 4.58% | PASS |
| 9 | C017 | 126 | 0.77% | 4.93% | PASS |
| 10 | C023 | 126 | 0.71% | 5.51% | PASS |
| 10 | C066 | 126 | 0.71% | 5.51% | PASS |
| 12 | C026 | 126 | 0.09% | 5.43% | PASS |
| 13 | C060 | 126 | 0.05% | 4.85% | PASS |
| 13 | C062 | 126 | 0.05% | 4.85% | PASS |
| 15 | C024 | 126 | 0.05% | 5.45% | PASS |
| 15 | C047 | 126 | 0.05% | 5.45% | PASS |
| 15 | C067 | 126 | 0.05% | 5.45% | PASS |
| 18 | C003 | 126 | 0.00% | 0.00% | PASS |
| 19 | C001 | 126 | -0.01% | 5.59% | PASS |
| 19 | C002 | 126 | -0.01% | 5.59% | PASS |
| 19 | C020 | 126 | -0.01% | 5.59% | PASS |
| 19 | C021 | 126 | -0.01% | 5.59% | PASS |
| 19 | C027 | 126 | -0.01% | 5.59% | PASS |
| 19 | C028 | 126 | -0.01% | 5.59% | PASS |
| 19 | C029 | 126 | -0.01% | 5.59% | PASS |
| 19 | C030 | 126 | -0.01% | 5.59% | PASS |
| 19 | C040 | 126 | -0.01% | 5.59% | PASS |
| 19 | C041 | 126 | -0.01% | 5.59% | PASS |
| 19 | C051 | 126 | -0.01% | 5.59% | PASS |
| 19 | C052 | 126 | -0.01% | 5.59% | PASS |
| 19 | C063 | 126 | -0.01% | 5.59% | PASS |
| 19 | C064 | 126 | -0.01% | 5.59% | PASS |
| 33 | C046 | 126 | -0.01% | 5.46% | PASS |
| 34 | C045 | 126 | -0.02% | 5.50% | PASS |
| 35 | C037 | 126 | -0.04% | 5.59% | PASS |
| 36 | C035 | 126 | -0.09% | 5.57% | PASS |
| 36 | C036 | 126 | -0.09% | 5.57% | PASS |
| 38 | C034 | 126 | -0.11% | 5.57% | PASS |
| 39 | C038 | 126 | -0.17% | 5.71% | PASS |
| 39 | C039 | 126 | -0.17% | 5.71% | PASS |
| 41 | C059 | 126 | -0.37% | 5.60% | PASS |
| 42 | C054 | 126 | -0.39% | 5.60% | PASS |
| 43 | C025 | 126 | -0.44% | 5.24% | PASS |
| 43 | C068 | 126 | -0.44% | 5.24% | PASS |
| 45 | C053 | 126 | -0.76% | 5.55% | PASS |
| 45 | C057 | 126 | -0.76% | 5.55% | PASS |
| 47 | C058 | 126 | -0.78% | 5.56% | PASS |
| 48 | C022 | 126 | -0.83% | 5.68% | PASS |
| 48 | C065 | 126 | -0.83% | 5.68% | PASS |
| 50 | C061 | 126 | -0.91% | 5.48% | PASS |
| 51 | C056 | 126 | -0.91% | 5.62% | PASS |
| 52 | C050 | 126 | -1.47% | 5.59% | PASS |
| 53 | C013 | 126 | -3.14% | 6.32% | PASS |
| 54 | C010 | 126 | -3.22% | 9.20% | PASS |
| 55 | C055 | 126 | -3.53% | 8.19% | PASS |
| — | C016 | 126 | -3.99% | 6.68% | FAILED |
| 56 | C012 | 126 | -5.10% | 7.64% | PASS |
| 57 | C014 | 126 | -5.74% | 8.76% | PASS |
| 58 | C042 | 126 | -6.88% | 11.01% | PASS |
| 59 | C004 | 126 | -8.12% | 13.47% | PASS |
| 60 | C009 | 126 | -8.14% | 12.17% | PASS |
| 61 | C044 | 126 | -8.18% | 12.17% | PASS |
| — | C007 | 126 | -9.55% | 12.12% | FAILED |
| 62 | C043 | 126 | -14.35% | 17.16% | PASS |
| 63 | C005 | 126 | -16.07% | 20.67% | PASS |
| 64 | C006 | 126 | -16.65% | 19.47% | PASS |
| 65 | C015 | 126 | -18.80% | 23.67% | PASS |
| 66 | C011 | 126 | -18.97% | 21.13% | PASS |

### leveraged_decay_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C031 | 126 | 5.67% | 5.19% | PASS |
| 2 | C018 | 126 | 5.52% | 5.19% | PASS |
| 2 | C048 | 126 | 5.52% | 5.19% | PASS |
| 4 | C032 | 126 | 5.31% | 5.19% | PASS |
| 4 | C033 | 126 | 5.31% | 5.19% | PASS |
| 6 | C060 | 126 | 5.29% | 5.34% | PASS |
| 6 | C062 | 126 | 5.29% | 5.34% | PASS |
| 8 | C049 | 126 | 4.41% | 5.19% | PASS |
| 9 | C019 | 126 | 4.40% | 5.45% | PASS |
| 10 | C022 | 126 | 3.33% | 5.19% | PASS |
| 10 | C065 | 126 | 3.33% | 5.19% | PASS |
| 12 | C026 | 126 | 3.09% | 5.19% | PASS |
| 13 | C045 | 126 | 3.04% | 5.19% | PASS |
| 14 | C024 | 126 | 3.03% | 5.19% | PASS |
| 14 | C046 | 126 | 3.03% | 5.19% | PASS |
| 14 | C047 | 126 | 3.03% | 5.19% | PASS |
| 14 | C067 | 126 | 3.03% | 5.19% | PASS |
| 18 | C034 | 126 | 2.99% | 5.20% | PASS |
| 18 | C035 | 126 | 2.99% | 5.20% | PASS |
| 18 | C036 | 126 | 2.99% | 5.20% | PASS |
| 21 | C001 | 126 | 2.99% | 5.19% | PASS |
| 21 | C002 | 126 | 2.99% | 5.19% | PASS |
| 21 | C020 | 126 | 2.99% | 5.19% | PASS |
| 21 | C021 | 126 | 2.99% | 5.19% | PASS |
| 21 | C027 | 126 | 2.99% | 5.19% | PASS |
| 21 | C028 | 126 | 2.99% | 5.19% | PASS |
| 21 | C029 | 126 | 2.99% | 5.19% | PASS |
| 21 | C030 | 126 | 2.99% | 5.19% | PASS |
| 21 | C051 | 126 | 2.99% | 5.19% | PASS |
| 21 | C063 | 126 | 2.99% | 5.19% | PASS |
| 21 | C064 | 126 | 2.99% | 5.19% | PASS |
| 32 | C037 | 126 | 2.98% | 5.19% | PASS |
| 33 | C038 | 126 | 2.98% | 4.96% | PASS |
| 33 | C039 | 126 | 2.98% | 4.96% | PASS |
| 35 | C040 | 126 | 2.97% | 5.18% | PASS |
| 35 | C041 | 126 | 2.97% | 5.18% | PASS |
| 37 | C053 | 126 | 2.75% | 5.34% | PASS |
| 37 | C057 | 126 | 2.75% | 5.34% | PASS |
| 37 | C058 | 126 | 2.75% | 5.34% | PASS |
| 40 | C023 | 126 | 2.48% | 5.19% | PASS |
| 40 | C066 | 126 | 2.48% | 5.19% | PASS |
| 42 | C050 | 126 | 2.39% | 4.47% | PASS |
| 43 | C025 | 126 | 2.37% | 5.19% | PASS |
| 43 | C068 | 126 | 2.37% | 5.19% | PASS |
| 45 | C008 | 126 | 2.37% | 5.21% | PASS |
| 46 | C061 | 126 | 2.36% | 5.34% | PASS |
| 47 | C052 | 126 | 2.24% | 5.19% | PASS |
| 48 | C017 | 126 | 1.97% | 4.64% | PASS |
| 49 | C003 | 126 | 0.00% | 0.00% | PASS |
| 50 | C056 | 126 | -0.14% | 6.04% | PASS |
| 51 | C055 | 126 | -0.29% | 6.16% | PASS |
| 51 | C059 | 126 | -0.29% | 6.16% | PASS |
| 53 | C054 | 126 | -0.60% | 6.47% | PASS |
| 54 | C013 | 126 | -2.11% | 4.89% | PASS |
| 55 | C012 | 126 | -2.43% | 5.33% | PASS |
| 56 | C014 | 126 | -2.74% | 5.48% | PASS |
| 57 | C016 | 126 | -3.84% | 5.63% | PASS |
| — | C007 | 126 | -6.30% | 8.51% | FAILED |
| 58 | C006 | 126 | -6.99% | 10.68% | PASS |
| 59 | C042 | 126 | -7.31% | 13.40% | PASS |
| 60 | C044 | 126 | -9.57% | 13.43% | PASS |
| 61 | C009 | 126 | -9.82% | 13.83% | PASS |
| 62 | C010 | 126 | -10.04% | 13.82% | PASS |
| 63 | C004 | 126 | -11.02% | 15.46% | PASS |
| 64 | C043 | 126 | -12.24% | 15.94% | PASS |
| 65 | C005 | 126 | -18.28% | 22.36% | PASS |
| 66 | C015 | 126 | -21.37% | 25.63% | PASS |
| 67 | C011 | 126 | -22.44% | 24.75% | PASS |

### liquidity_shock_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 37.64% | 5.72% | PASS |
| 2 | C005 | 126 | 34.86% | 5.40% | PASS |
| 3 | C004 | 126 | 33.37% | 5.06% | PASS |
| 4 | C010 | 126 | 27.10% | 3.76% | PASS |
| 5 | C044 | 126 | 25.04% | 3.86% | PASS |
| 6 | C006 | 126 | 24.01% | 3.33% | PASS |
| 7 | C043 | 126 | 22.54% | 3.27% | PASS |
| 8 | C017 | 126 | 22.43% | 5.21% | PASS |
| 9 | C019 | 126 | 20.12% | 5.72% | PASS |
| 10 | C008 | 126 | 18.91% | 5.11% | PASS |
| — | C007 | 126 | 15.28% | 2.21% | FAILED |
| 11 | C050 | 126 | 14.37% | 4.85% | PASS |
| 12 | C049 | 126 | 14.32% | 6.62% | PASS |
| 13 | C032 | 126 | 14.24% | 6.80% | PASS |
| 13 | C033 | 126 | 14.24% | 6.80% | PASS |
| 15 | C018 | 126 | 13.97% | 7.15% | PASS |
| 15 | C048 | 126 | 13.97% | 7.15% | PASS |
| 17 | C022 | 126 | 13.90% | 7.05% | PASS |
| 17 | C025 | 126 | 13.90% | 7.05% | PASS |
| 17 | C065 | 126 | 13.90% | 7.05% | PASS |
| 17 | C068 | 126 | 13.90% | 7.05% | PASS |
| 21 | C001 | 126 | 13.65% | 7.27% | PASS |
| 21 | C002 | 126 | 13.65% | 7.27% | PASS |
| 21 | C020 | 126 | 13.65% | 7.27% | PASS |
| 21 | C021 | 126 | 13.65% | 7.27% | PASS |
| 21 | C023 | 126 | 13.65% | 7.27% | PASS |
| 21 | C027 | 126 | 13.65% | 7.27% | PASS |
| 21 | C029 | 126 | 13.65% | 7.27% | PASS |
| 21 | C052 | 126 | 13.65% | 7.27% | PASS |
| 21 | C063 | 126 | 13.65% | 7.27% | PASS |
| 21 | C064 | 126 | 13.65% | 7.27% | PASS |
| 21 | C066 | 126 | 13.65% | 7.27% | PASS |
| 32 | C031 | 126 | 13.62% | 7.06% | PASS |
| 33 | C046 | 126 | 13.18% | 7.38% | PASS |
| 34 | C024 | 126 | 13.18% | 7.39% | PASS |
| 34 | C026 | 126 | 13.18% | 7.39% | PASS |
| 34 | C047 | 126 | 13.18% | 7.39% | PASS |
| 34 | C067 | 126 | 13.18% | 7.39% | PASS |
| 38 | C045 | 126 | 13.14% | 7.38% | PASS |
| 39 | C037 | 126 | 13.04% | 7.40% | PASS |
| 40 | C042 | 126 | 12.92% | 5.51% | PASS |
| 41 | C038 | 126 | 12.80% | 7.05% | PASS |
| 41 | C039 | 126 | 12.80% | 7.05% | PASS |
| 43 | C036 | 126 | 12.01% | 7.49% | PASS |
| 44 | C040 | 126 | 11.94% | 7.22% | PASS |
| 44 | C041 | 126 | 11.94% | 7.22% | PASS |
| 46 | C009 | 126 | 11.85% | 5.81% | PASS |
| 47 | C034 | 126 | 11.69% | 7.50% | PASS |
| 48 | C035 | 126 | 11.68% | 7.50% | PASS |
| 49 | C011 | 126 | 10.46% | 3.55% | PASS |
| — | C016 | 126 | 10.01% | 1.53% | FAILED |
| 50 | C014 | 126 | 9.85% | 3.88% | PASS |
| 51 | C013 | 126 | 9.57% | 3.51% | PASS |
| 52 | C028 | 126 | 9.03% | 7.78% | PASS |
| 52 | C030 | 126 | 9.03% | 7.78% | PASS |
| 54 | C061 | 126 | 8.92% | 6.93% | PASS |
| 55 | C060 | 126 | 8.91% | 6.99% | PASS |
| 55 | C062 | 126 | 8.91% | 6.99% | PASS |
| 57 | C053 | 126 | 8.65% | 6.98% | PASS |
| 57 | C057 | 126 | 8.65% | 6.98% | PASS |
| 57 | C059 | 126 | 8.65% | 6.98% | PASS |
| 60 | C012 | 126 | 4.03% | 2.62% | PASS |
| 61 | C058 | 126 | 2.93% | 11.27% | PASS |
| 62 | C003 | 126 | 0.00% | 0.00% | PASS |
| 63 | C051 | 126 | -2.29% | 15.43% | PASS |
| 64 | C055 | 126 | -3.61% | 11.68% | PASS |
| 65 | C054 | 126 | -3.96% | 11.91% | PASS |
| 66 | C056 | 126 | -15.49% | 21.46% | PASS |

### liquidity_shock_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C010 | 126 | 3.85% | 4.96% | PASS |
| 2 | C043 | 126 | 2.60% | 5.60% | PASS |
| 3 | C015 | 126 | 2.16% | 7.95% | PASS |
| 4 | C006 | 126 | 1.93% | 5.87% | PASS |
| 5 | C005 | 126 | 1.64% | 7.58% | PASS |
| — | C007 | 126 | 0.94% | 4.26% | FAILED |
| — | C016 | 126 | 0.50% | 2.42% | FAILED |
| 6 | C044 | 126 | 0.49% | 6.27% | PASS |
| 7 | C004 | 126 | 0.44% | 7.53% | PASS |
| 8 | C003 | 126 | 0.00% | 0.00% | PASS |
| 9 | C012 | 126 | -1.55% | 4.55% | PASS |
| 10 | C011 | 126 | -1.94% | 5.62% | PASS |
| 11 | C013 | 126 | -3.64% | 6.65% | PASS |
| 12 | C014 | 126 | -4.34% | 7.30% | PASS |
| 13 | C022 | 126 | -9.67% | 12.55% | PASS |
| 13 | C065 | 126 | -9.67% | 12.55% | PASS |
| 15 | C033 | 126 | -9.93% | 12.81% | PASS |
| 16 | C017 | 126 | -10.85% | 14.01% | PASS |
| 17 | C050 | 126 | -11.63% | 14.19% | PASS |
| 18 | C042 | 126 | -11.66% | 13.78% | PASS |
| 19 | C021 | 126 | -12.02% | 14.83% | PASS |
| 19 | C064 | 126 | -12.02% | 14.83% | PASS |
| 21 | C018 | 126 | -12.67% | 15.46% | PASS |
| 22 | C038 | 126 | -12.95% | 15.60% | PASS |
| 22 | C039 | 126 | -12.95% | 15.60% | PASS |
| 24 | C032 | 126 | -13.07% | 15.84% | PASS |
| 25 | C040 | 126 | -13.33% | 16.09% | PASS |
| 25 | C041 | 126 | -13.33% | 16.09% | PASS |
| 27 | C031 | 126 | -13.41% | 16.18% | PASS |
| 28 | C048 | 126 | -13.49% | 16.25% | PASS |
| 29 | C037 | 126 | -13.50% | 16.26% | PASS |
| 30 | C001 | 126 | -13.51% | 16.27% | PASS |
| 30 | C002 | 126 | -13.51% | 16.27% | PASS |
| 30 | C020 | 126 | -13.51% | 16.27% | PASS |
| 30 | C027 | 126 | -13.51% | 16.27% | PASS |
| 30 | C029 | 126 | -13.51% | 16.27% | PASS |
| 30 | C045 | 126 | -13.51% | 16.27% | PASS |
| 30 | C046 | 126 | -13.51% | 16.27% | PASS |
| 30 | C052 | 126 | -13.51% | 16.27% | PASS |
| 30 | C063 | 126 | -13.51% | 16.27% | PASS |
| 39 | C024 | 126 | -13.53% | 16.29% | PASS |
| 39 | C026 | 126 | -13.53% | 16.29% | PASS |
| 39 | C047 | 126 | -13.53% | 16.29% | PASS |
| 39 | C067 | 126 | -13.53% | 16.29% | PASS |
| 43 | C049 | 126 | -13.55% | 16.31% | PASS |
| 44 | C019 | 126 | -13.58% | 16.51% | PASS |
| 45 | C009 | 126 | -13.59% | 15.54% | PASS |
| 46 | C034 | 126 | -13.67% | 16.43% | PASS |
| 47 | C025 | 126 | -13.82% | 16.57% | PASS |
| 47 | C068 | 126 | -13.82% | 16.57% | PASS |
| 49 | C035 | 126 | -14.04% | 16.79% | PASS |
| 50 | C028 | 126 | -14.26% | 17.00% | PASS |
| 50 | C030 | 126 | -14.26% | 17.00% | PASS |
| 52 | C008 | 126 | -14.48% | 16.71% | PASS |
| 53 | C036 | 126 | -14.57% | 17.30% | PASS |
| 54 | C023 | 126 | -14.96% | 17.68% | PASS |
| 54 | C066 | 126 | -14.96% | 17.68% | PASS |
| 56 | C051 | 126 | -15.86% | 18.54% | PASS |
| 57 | C061 | 126 | -16.74% | 19.19% | PASS |
| 58 | C053 | 126 | -16.87% | 19.31% | PASS |
| 58 | C057 | 126 | -16.87% | 19.31% | PASS |
| 58 | C058 | 126 | -16.87% | 19.31% | PASS |
| 58 | C059 | 126 | -16.87% | 19.31% | PASS |
| 62 | C060 | 126 | -16.92% | 19.36% | PASS |
| 62 | C062 | 126 | -16.92% | 19.36% | PASS |
| 64 | C054 | 126 | -18.38% | 20.77% | PASS |
| 65 | C055 | 126 | -22.23% | 24.27% | PASS |
| 66 | C056 | 126 | -36.87% | 38.24% | PASS |

### long_cycle_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| — | C005 | 504 | 205.50% | 41.30% | FAILED |
| 1 | C033 | 504 | 193.95% | 12.81% | PASS |
| 2 | C032 | 504 | 191.84% | 14.25% | PASS |
| 3 | C049 | 504 | 191.56% | 14.05% | PASS |
| 4 | C019 | 504 | 191.10% | 15.16% | PASS |
| 5 | C031 | 504 | 187.97% | 15.82% | PASS |
| 6 | C022 | 504 | 187.41% | 16.07% | PASS |
| 6 | C065 | 504 | 187.41% | 16.07% | PASS |
| 8 | C048 | 504 | 184.26% | 16.84% | PASS |
| 9 | C046 | 504 | 183.45% | 18.33% | PASS |
| 10 | C024 | 504 | 183.43% | 18.39% | PASS |
| 10 | C026 | 504 | 183.43% | 18.39% | PASS |
| 10 | C047 | 504 | 183.43% | 18.39% | PASS |
| 10 | C067 | 504 | 183.43% | 18.39% | PASS |
| 14 | C052 | 504 | 182.83% | 18.06% | PASS |
| 15 | C045 | 504 | 182.80% | 18.34% | PASS |
| 16 | C025 | 504 | 181.40% | 15.49% | PASS |
| 16 | C068 | 504 | 181.40% | 15.49% | PASS |
| 18 | C001 | 504 | 181.39% | 18.44% | PASS |
| 18 | C002 | 504 | 181.39% | 18.44% | PASS |
| 18 | C020 | 504 | 181.39% | 18.44% | PASS |
| 18 | C023 | 504 | 181.39% | 18.44% | PASS |
| 18 | C027 | 504 | 181.39% | 18.44% | PASS |
| 18 | C029 | 504 | 181.39% | 18.44% | PASS |
| 18 | C063 | 504 | 181.39% | 18.44% | PASS |
| 18 | C066 | 504 | 181.39% | 18.44% | PASS |
| 26 | C018 | 504 | 179.43% | 16.08% | PASS |
| 27 | C036 | 504 | 178.56% | 18.34% | PASS |
| 28 | C035 | 504 | 178.26% | 18.33% | PASS |
| 29 | C040 | 504 | 177.84% | 18.36% | PASS |
| 29 | C041 | 504 | 177.84% | 18.36% | PASS |
| 31 | C028 | 504 | 176.95% | 18.46% | PASS |
| 31 | C030 | 504 | 176.95% | 18.46% | PASS |
| 33 | C034 | 504 | 176.23% | 18.25% | PASS |
| 34 | C038 | 504 | 175.57% | 17.80% | PASS |
| 34 | C039 | 504 | 175.57% | 17.80% | PASS |
| 36 | C037 | 504 | 175.40% | 18.52% | PASS |
| 37 | C021 | 504 | 171.18% | 16.95% | PASS |
| 37 | C064 | 504 | 171.18% | 16.95% | PASS |
| — | C015 | 504 | 169.59% | 50.19% | FAILED |
| 39 | C051 | 504 | 167.70% | 16.85% | PASS |
| 40 | C017 | 504 | 164.44% | 16.18% | PASS |
| 41 | C060 | 504 | 154.12% | 15.08% | PASS |
| 41 | C062 | 504 | 154.12% | 15.08% | PASS |
| 43 | C055 | 504 | 154.02% | 17.79% | PASS |
| 44 | C054 | 504 | 151.08% | 18.98% | PASS |
| 45 | C008 | 504 | 151.02% | 10.00% | PASS |
| 46 | C056 | 504 | 150.31% | 17.89% | PASS |
| 47 | C061 | 504 | 150.30% | 17.10% | PASS |
| 48 | C053 | 504 | 148.51% | 17.98% | PASS |
| 48 | C057 | 504 | 148.51% | 17.98% | PASS |
| 48 | C059 | 504 | 148.51% | 17.98% | PASS |
| 51 | C004 | 504 | 147.64% | 37.70% | PASS |
| 52 | C058 | 504 | 147.07% | 19.15% | PASS |
| 53 | C009 | 504 | 135.28% | 12.83% | PASS |
| 54 | C050 | 504 | 134.11% | 16.91% | PASS |
| 55 | C042 | 504 | 100.68% | 22.99% | PASS |
| 56 | C044 | 504 | 90.63% | 36.30% | PASS |
| 57 | C011 | 504 | 79.59% | 12.47% | PASS |
| 58 | C006 | 504 | 71.90% | 34.10% | PASS |
| 59 | C013 | 504 | 71.10% | 8.13% | PASS |
| 60 | C012 | 504 | 69.33% | 10.82% | PASS |
| 61 | C043 | 504 | 68.55% | 31.91% | PASS |
| 62 | C014 | 504 | 65.12% | 12.31% | PASS |
| — | C007 | 504 | 53.70% | 24.64% | FAILED |
| 63 | C010 | 504 | 47.23% | 34.83% | PASS |
| — | C016 | 504 | 32.40% | 15.92% | FAILED |
| 64 | C003 | 504 | 0.00% | 0.00% | PASS |

### long_cycle_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C032 | 504 | 155.30% | 15.10% | PASS |
| 2 | C033 | 504 | 151.02% | 16.67% | PASS |
| 3 | C049 | 504 | 149.02% | 16.93% | PASS |
| 4 | C031 | 504 | 148.95% | 17.11% | PASS |
| 5 | C051 | 504 | 148.84% | 16.93% | PASS |
| 6 | C048 | 504 | 146.95% | 17.91% | PASS |
| 7 | C022 | 504 | 146.69% | 18.28% | PASS |
| 7 | C065 | 504 | 146.69% | 18.28% | PASS |
| 9 | C035 | 504 | 146.01% | 19.09% | PASS |
| 10 | C024 | 504 | 144.92% | 19.60% | PASS |
| 10 | C047 | 504 | 144.92% | 19.60% | PASS |
| 10 | C067 | 504 | 144.92% | 19.60% | PASS |
| 13 | C046 | 504 | 143.72% | 19.65% | PASS |
| 14 | C034 | 504 | 143.67% | 19.27% | PASS |
| 15 | C045 | 504 | 143.54% | 19.71% | PASS |
| 16 | C036 | 504 | 143.36% | 19.74% | PASS |
| 17 | C026 | 504 | 143.15% | 20.18% | PASS |
| 18 | C001 | 504 | 142.97% | 19.68% | PASS |
| 18 | C002 | 504 | 142.97% | 19.68% | PASS |
| 18 | C027 | 504 | 142.97% | 19.68% | PASS |
| 18 | C029 | 504 | 142.97% | 19.68% | PASS |
| 22 | C037 | 504 | 142.65% | 19.49% | PASS |
| 23 | C052 | 504 | 141.81% | 20.01% | PASS |
| 24 | C020 | 504 | 141.55% | 20.26% | PASS |
| 24 | C063 | 504 | 141.55% | 20.26% | PASS |
| 26 | C040 | 504 | 141.26% | 19.63% | PASS |
| 26 | C041 | 504 | 141.26% | 19.63% | PASS |
| 28 | C019 | 504 | 140.81% | 17.74% | PASS |
| 29 | C028 | 504 | 140.06% | 19.36% | PASS |
| 29 | C030 | 504 | 140.06% | 19.36% | PASS |
| 31 | C023 | 504 | 140.01% | 20.64% | PASS |
| 31 | C066 | 504 | 140.01% | 20.64% | PASS |
| 33 | C025 | 504 | 137.98% | 17.47% | PASS |
| 33 | C068 | 504 | 137.98% | 17.47% | PASS |
| 35 | C018 | 504 | 137.16% | 17.72% | PASS |
| 36 | C038 | 504 | 136.64% | 19.13% | PASS |
| 36 | C039 | 504 | 136.64% | 19.13% | PASS |
| 38 | C021 | 504 | 132.50% | 17.95% | PASS |
| 38 | C064 | 504 | 132.50% | 17.95% | PASS |
| 40 | C008 | 504 | 128.43% | 12.78% | PASS |
| 41 | C017 | 504 | 126.95% | 16.39% | PASS |
| 42 | C060 | 504 | 120.32% | 17.59% | PASS |
| 43 | C062 | 504 | 119.27% | 19.60% | PASS |
| 44 | C061 | 504 | 117.89% | 18.53% | PASS |
| 45 | C053 | 504 | 115.97% | 19.18% | PASS |
| 45 | C059 | 504 | 115.97% | 19.18% | PASS |
| 47 | C057 | 504 | 114.95% | 21.34% | PASS |
| 48 | C050 | 504 | 111.33% | 17.82% | PASS |
| 49 | C055 | 504 | 111.04% | 21.31% | PASS |
| 50 | C058 | 504 | 109.14% | 23.45% | PASS |
| 51 | C054 | 504 | 103.23% | 24.23% | PASS |
| 52 | C056 | 504 | 102.45% | 23.61% | PASS |
| 53 | C004 | 504 | 97.75% | 38.21% | PASS |
| 54 | C015 | 504 | 94.45% | 47.36% | PASS |
| — | C009 | 504 | 89.75% | 18.93% | FAILED |
| 55 | C005 | 504 | 74.47% | 44.05% | PASS |
| 56 | C010 | 504 | 73.99% | 18.64% | PASS |
| — | C042 | 504 | 72.78% | 24.12% | FAILED |
| 57 | C012 | 504 | 68.87% | 13.91% | PASS |
| 58 | C011 | 504 | 67.64% | 13.38% | PASS |
| 59 | C043 | 504 | 63.33% | 24.84% | PASS |
| 60 | C044 | 504 | 61.59% | 36.60% | PASS |
| 61 | C013 | 504 | 58.66% | 8.08% | PASS |
| — | C006 | 504 | 57.32% | 34.35% | FAILED |
| 62 | C014 | 504 | 54.80% | 11.73% | PASS |
| — | C007 | 504 | 41.69% | 23.10% | FAILED |
| — | C016 | 504 | 27.77% | 12.48% | FAILED |
| 63 | C003 | 504 | 0.00% | 0.00% | PASS |

### missing_bars_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C015 | 126 | 13.23% | 14.62% | PASS |
| 2 | C017 | 126 | 13.07% | 5.01% | PASS |
| 3 | C004 | 126 | 12.26% | 11.34% | PASS |
| 4 | C005 | 126 | 12.26% | 13.58% | PASS |
| 5 | C025 | 126 | 11.66% | 5.43% | PASS |
| 5 | C068 | 126 | 11.66% | 5.43% | PASS |
| 7 | C022 | 126 | 11.61% | 5.43% | PASS |
| 7 | C065 | 126 | 11.61% | 5.43% | PASS |
| 9 | C024 | 126 | 11.61% | 5.75% | PASS |
| 9 | C026 | 126 | 11.61% | 5.75% | PASS |
| 9 | C067 | 126 | 11.61% | 5.75% | PASS |
| 12 | C020 | 126 | 11.53% | 5.92% | PASS |
| 12 | C021 | 126 | 11.53% | 5.92% | PASS |
| 12 | C023 | 126 | 11.53% | 5.92% | PASS |
| 12 | C063 | 126 | 11.53% | 5.92% | PASS |
| 12 | C064 | 126 | 11.53% | 5.92% | PASS |
| 12 | C066 | 126 | 11.53% | 5.92% | PASS |
| 18 | C031 | 126 | 11.27% | 6.33% | PASS |
| 19 | C040 | 126 | 11.26% | 6.77% | PASS |
| 19 | C041 | 126 | 11.26% | 6.77% | PASS |
| 21 | C001 | 126 | 11.25% | 6.86% | PASS |
| 21 | C002 | 126 | 11.25% | 6.86% | PASS |
| 21 | C027 | 126 | 11.25% | 6.86% | PASS |
| 21 | C029 | 126 | 11.25% | 6.86% | PASS |
| 21 | C045 | 126 | 11.25% | 6.86% | PASS |
| 21 | C046 | 126 | 11.25% | 6.86% | PASS |
| 21 | C047 | 126 | 11.25% | 6.86% | PASS |
| 21 | C052 | 126 | 11.25% | 6.86% | PASS |
| 29 | C032 | 126 | 11.22% | 5.94% | PASS |
| 30 | C037 | 126 | 11.22% | 6.87% | PASS |
| 31 | C036 | 126 | 11.15% | 6.91% | PASS |
| 32 | C049 | 126 | 10.99% | 5.70% | PASS |
| 33 | C048 | 126 | 10.82% | 6.42% | PASS |
| 34 | C018 | 126 | 10.78% | 5.51% | PASS |
| 35 | C038 | 126 | 10.75% | 6.56% | PASS |
| 35 | C039 | 126 | 10.75% | 6.56% | PASS |
| 37 | C033 | 126 | 10.66% | 6.00% | PASS |
| 38 | C010 | 126 | 10.65% | 8.08% | PASS |
| 39 | C056 | 126 | 10.60% | 6.44% | PASS |
| 40 | C055 | 126 | 10.30% | 7.02% | PASS |
| 41 | C035 | 126 | 10.05% | 7.93% | PASS |
| 42 | C034 | 126 | 10.05% | 7.93% | PASS |
| 43 | C008 | 126 | 9.60% | 4.10% | PASS |
| 44 | C053 | 126 | 9.58% | 7.01% | PASS |
| 44 | C057 | 126 | 9.58% | 7.01% | PASS |
| 44 | C059 | 126 | 9.58% | 7.01% | PASS |
| 47 | C060 | 126 | 9.57% | 6.62% | PASS |
| 47 | C062 | 126 | 9.57% | 6.62% | PASS |
| 49 | C061 | 126 | 9.51% | 6.90% | PASS |
| 50 | C054 | 126 | 9.47% | 6.84% | PASS |
| 51 | C051 | 126 | 9.45% | 7.38% | PASS |
| 52 | C050 | 126 | 9.23% | 6.59% | PASS |
| 53 | C044 | 126 | 9.08% | 10.20% | PASS |
| 54 | C019 | 126 | 9.03% | 7.67% | PASS |
| 55 | C043 | 126 | 8.92% | 8.57% | PASS |
| 56 | C028 | 126 | 8.68% | 7.76% | PASS |
| 56 | C030 | 126 | 8.68% | 7.76% | PASS |
| 58 | C058 | 126 | 8.57% | 7.87% | PASS |
| 59 | C006 | 126 | 7.87% | 9.69% | PASS |
| 60 | C011 | 126 | 6.56% | 5.46% | PASS |
| 61 | C009 | 126 | 6.32% | 6.30% | PASS |
| 62 | C014 | 126 | 5.84% | 4.56% | PASS |
| — | C007 | 126 | 5.70% | 6.91% | FAILED |
| 63 | C042 | 126 | 5.67% | 8.31% | PASS |
| 64 | C012 | 126 | 3.89% | 6.38% | PASS |
| — | C016 | 126 | 2.95% | 4.39% | FAILED |
| 65 | C013 | 126 | 2.81% | 5.06% | PASS |
| 66 | C003 | 126 | 0.00% | 0.00% | PASS |

### missing_bars_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C013 | 126 | 3.32% | 1.46% | PASS |
| 2 | C058 | 126 | 3.30% | 3.97% | PASS |
| 3 | C060 | 126 | 2.90% | 4.40% | PASS |
| 3 | C062 | 126 | 2.90% | 4.40% | PASS |
| — | C009 | 126 | 2.81% | 2.40% | FAILED |
| 5 | C053 | 126 | 2.66% | 4.46% | PASS |
| 5 | C057 | 126 | 2.66% | 4.46% | PASS |
| 5 | C059 | 126 | 2.66% | 4.46% | PASS |
| 8 | C061 | 126 | 2.53% | 4.63% | PASS |
| 9 | C034 | 126 | 2.51% | 3.89% | PASS |
| 10 | C040 | 126 | 2.39% | 4.16% | PASS |
| 10 | C041 | 126 | 2.39% | 4.16% | PASS |
| 12 | C018 | 126 | 2.39% | 4.38% | PASS |
| 13 | C035 | 126 | 2.38% | 4.14% | PASS |
| 14 | C031 | 126 | 2.37% | 4.34% | PASS |
| 15 | C050 | 126 | 2.34% | 2.84% | PASS |
| 16 | C055 | 126 | 2.32% | 3.55% | PASS |
| 17 | C048 | 126 | 2.32% | 4.40% | PASS |
| 18 | C036 | 126 | 2.29% | 4.15% | PASS |
| 19 | C024 | 126 | 2.23% | 4.36% | PASS |
| 19 | C026 | 126 | 2.23% | 4.36% | PASS |
| 19 | C067 | 126 | 2.23% | 4.36% | PASS |
| 22 | C020 | 126 | 2.19% | 4.40% | PASS |
| 22 | C021 | 126 | 2.19% | 4.40% | PASS |
| 22 | C063 | 126 | 2.19% | 4.40% | PASS |
| 22 | C064 | 126 | 2.19% | 4.40% | PASS |
| 26 | C047 | 126 | 2.17% | 4.37% | PASS |
| 27 | C037 | 126 | 2.14% | 4.27% | PASS |
| 28 | C032 | 126 | 2.14% | 4.59% | PASS |
| 29 | C001 | 126 | 2.13% | 4.41% | PASS |
| 29 | C002 | 126 | 2.13% | 4.41% | PASS |
| 29 | C027 | 126 | 2.13% | 4.41% | PASS |
| 29 | C029 | 126 | 2.13% | 4.41% | PASS |
| 29 | C052 | 126 | 2.13% | 4.41% | PASS |
| 34 | C038 | 126 | 2.12% | 4.15% | PASS |
| 34 | C039 | 126 | 2.12% | 4.15% | PASS |
| 36 | C045 | 126 | 2.11% | 4.43% | PASS |
| 36 | C046 | 126 | 2.11% | 4.43% | PASS |
| — | C042 | 126 | 1.87% | 3.84% | FAILED |
| 38 | C022 | 126 | 1.81% | 4.73% | PASS |
| 38 | C065 | 126 | 1.81% | 4.73% | PASS |
| 40 | C019 | 126 | 1.60% | 6.10% | PASS |
| 41 | C014 | 126 | 1.58% | 2.11% | PASS |
| 42 | C028 | 126 | 1.43% | 4.00% | PASS |
| 42 | C030 | 126 | 1.43% | 4.00% | PASS |
| 44 | C049 | 126 | 1.04% | 5.76% | PASS |
| 45 | C005 | 126 | 0.97% | 6.70% | PASS |
| 45 | C044 | 126 | 0.97% | 6.70% | PASS |
| 47 | C004 | 126 | 0.91% | 7.35% | PASS |
| — | C016 | 126 | 0.90% | 2.73% | FAILED |
| 48 | C015 | 126 | 0.86% | 10.52% | PASS |
| 49 | C051 | 126 | 0.77% | 4.41% | PASS |
| 50 | C010 | 126 | 0.32% | 1.72% | PASS |
| 51 | C054 | 126 | 0.08% | 4.66% | PASS |
| 52 | C056 | 126 | 0.07% | 4.26% | PASS |
| 53 | C011 | 126 | 0.01% | 3.31% | PASS |
| 54 | C003 | 126 | 0.00% | 0.00% | PASS |
| 55 | C025 | 126 | -0.09% | 5.01% | PASS |
| 55 | C068 | 126 | -0.09% | 5.01% | PASS |
| — | C007 | 126 | -0.18% | 5.04% | FAILED |
| 57 | C023 | 126 | -0.42% | 5.19% | PASS |
| 57 | C066 | 126 | -0.42% | 5.19% | PASS |
| 59 | C012 | 126 | -0.44% | 2.17% | PASS |
| 60 | C043 | 126 | -0.73% | 3.35% | PASS |
| 61 | C017 | 126 | -1.56% | 7.34% | PASS |
| 62 | C008 | 126 | -1.61% | 5.30% | PASS |
| 63 | C033 | 126 | -1.65% | 6.10% | PASS |
| 64 | C006 | 126 | -1.92% | 7.79% | PASS |

### opening_gap_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C010 | 126 | -3.56% | 6.74% | PASS |
| 3 | C012 | 126 | -4.09% | 7.69% | PASS |
| — | C016 | 126 | -4.79% | 10.51% | FAILED |
| 4 | C014 | 126 | -10.26% | 16.62% | PASS |
| 5 | C043 | 126 | -10.62% | 18.08% | PASS |
| 6 | C013 | 126 | -11.00% | 16.69% | PASS |
| — | C007 | 126 | -12.10% | 19.77% | FAILED |
| 7 | C005 | 126 | -14.09% | 26.56% | PASS |
| 7 | C044 | 126 | -14.09% | 26.56% | PASS |
| 9 | C015 | 126 | -14.24% | 32.31% | PASS |
| 10 | C011 | 126 | -14.39% | 21.05% | PASS |
| 11 | C004 | 126 | -14.59% | 27.66% | PASS |
| 12 | C006 | 126 | -14.79% | 26.14% | PASS |
| 13 | C038 | 126 | -19.54% | 28.97% | PASS |
| 13 | C039 | 126 | -19.54% | 28.97% | PASS |
| 15 | C052 | 126 | -19.68% | 29.86% | PASS |
| 16 | C050 | 126 | -19.86% | 28.59% | PASS |
| 17 | C037 | 126 | -20.03% | 29.59% | PASS |
| 18 | C040 | 126 | -20.09% | 29.59% | PASS |
| 18 | C041 | 126 | -20.09% | 29.59% | PASS |
| 20 | C036 | 126 | -20.22% | 29.56% | PASS |
| 21 | C001 | 126 | -20.23% | 29.86% | PASS |
| 21 | C002 | 126 | -20.23% | 29.86% | PASS |
| 21 | C020 | 126 | -20.23% | 29.86% | PASS |
| 21 | C024 | 126 | -20.23% | 29.86% | PASS |
| 21 | C026 | 126 | -20.23% | 29.86% | PASS |
| 21 | C027 | 126 | -20.23% | 29.86% | PASS |
| 21 | C029 | 126 | -20.23% | 29.86% | PASS |
| 21 | C045 | 126 | -20.23% | 29.86% | PASS |
| 21 | C046 | 126 | -20.23% | 29.86% | PASS |
| 21 | C047 | 126 | -20.23% | 29.86% | PASS |
| 21 | C051 | 126 | -20.23% | 29.86% | PASS |
| 21 | C063 | 126 | -20.23% | 29.86% | PASS |
| 21 | C067 | 126 | -20.23% | 29.86% | PASS |
| 34 | C033 | 126 | -20.23% | 30.43% | PASS |
| 35 | C008 | 126 | -20.36% | 28.44% | PASS |
| 36 | C034 | 126 | -20.37% | 29.82% | PASS |
| 36 | C035 | 126 | -20.37% | 29.82% | PASS |
| 38 | C028 | 126 | -20.41% | 29.57% | PASS |
| 38 | C030 | 126 | -20.41% | 29.57% | PASS |
| 40 | C021 | 126 | -20.47% | 29.75% | PASS |
| 40 | C064 | 126 | -20.47% | 29.75% | PASS |
| 42 | C031 | 126 | -20.48% | 29.76% | PASS |
| 43 | C048 | 126 | -20.59% | 29.72% | PASS |
| 44 | C032 | 126 | -20.62% | 29.71% | PASS |
| 45 | C023 | 126 | -20.67% | 29.86% | PASS |
| 45 | C066 | 126 | -20.67% | 29.86% | PASS |
| 47 | C022 | 126 | -20.69% | 29.76% | PASS |
| 47 | C065 | 126 | -20.69% | 29.76% | PASS |
| 49 | C018 | 126 | -20.69% | 29.69% | PASS |
| 50 | C049 | 126 | -20.80% | 29.84% | PASS |
| 51 | C017 | 126 | -20.80% | 29.10% | PASS |
| 52 | C025 | 126 | -21.02% | 29.84% | PASS |
| 52 | C068 | 126 | -21.02% | 29.84% | PASS |
| 54 | C042 | 126 | -21.06% | 30.98% | PASS |
| 55 | C009 | 126 | -21.68% | 30.03% | PASS |
| 56 | C019 | 126 | -21.96% | 31.19% | PASS |
| 57 | C055 | 126 | -22.40% | 31.76% | PASS |
| 58 | C056 | 126 | -22.66% | 32.06% | PASS |
| 59 | C053 | 126 | -23.01% | 32.46% | PASS |
| 60 | C061 | 126 | -23.07% | 32.49% | PASS |
| 61 | C059 | 126 | -23.10% | 32.54% | PASS |
| 62 | C060 | 126 | -23.37% | 32.56% | PASS |
| 63 | C057 | 126 | -23.51% | 32.91% | PASS |
| 63 | C058 | 126 | -23.51% | 32.91% | PASS |
| 65 | C054 | 126 | -23.64% | 32.28% | PASS |
| 66 | C062 | 126 | -23.91% | 33.04% | PASS |

### opening_gap_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C013 | 126 | -2.81% | 4.18% | PASS |
| 3 | C017 | 126 | -3.37% | 9.24% | PASS |
| 4 | C009 | 126 | -5.16% | 9.24% | PASS |
| 5 | C011 | 126 | -5.32% | 9.40% | PASS |
| 6 | C012 | 126 | -6.36% | 8.07% | PASS |
| 7 | C014 | 126 | -6.58% | 8.90% | PASS |
| — | C016 | 126 | -7.81% | 11.16% | FAILED |
| 8 | C033 | 126 | -12.11% | 15.72% | PASS |
| 9 | C050 | 126 | -14.00% | 17.97% | PASS |
| — | C042 | 126 | -14.56% | 20.24% | FAILED |
| — | C007 | 126 | -15.80% | 21.06% | FAILED |
| 10 | C022 | 126 | -17.54% | 21.16% | PASS |
| 10 | C065 | 126 | -17.54% | 21.16% | PASS |
| 12 | C038 | 126 | -17.66% | 21.51% | PASS |
| 12 | C039 | 126 | -17.66% | 21.51% | PASS |
| 14 | C023 | 126 | -18.36% | 22.36% | PASS |
| 14 | C066 | 126 | -18.36% | 22.36% | PASS |
| 16 | C045 | 126 | -18.61% | 22.60% | PASS |
| 17 | C024 | 126 | -18.61% | 22.60% | PASS |
| 17 | C046 | 126 | -18.61% | 22.60% | PASS |
| 17 | C047 | 126 | -18.61% | 22.60% | PASS |
| 17 | C067 | 126 | -18.61% | 22.60% | PASS |
| 21 | C001 | 126 | -18.61% | 22.60% | PASS |
| 21 | C002 | 126 | -18.61% | 22.60% | PASS |
| 21 | C027 | 126 | -18.61% | 22.60% | PASS |
| 21 | C028 | 126 | -18.61% | 22.60% | PASS |
| 21 | C029 | 126 | -18.61% | 22.60% | PASS |
| 21 | C030 | 126 | -18.61% | 22.60% | PASS |
| 21 | C052 | 126 | -18.61% | 22.60% | PASS |
| 28 | C026 | 126 | -18.62% | 22.61% | PASS |
| 29 | C020 | 126 | -18.62% | 22.61% | PASS |
| 29 | C063 | 126 | -18.62% | 22.61% | PASS |
| 31 | C031 | 126 | -18.80% | 22.41% | PASS |
| 32 | C048 | 126 | -18.88% | 22.46% | PASS |
| 33 | C040 | 126 | -18.91% | 22.63% | PASS |
| 33 | C041 | 126 | -18.91% | 22.63% | PASS |
| 35 | C032 | 126 | -19.06% | 22.32% | PASS |
| 36 | C051 | 126 | -19.09% | 22.60% | PASS |
| 37 | C037 | 126 | -19.21% | 23.11% | PASS |
| 38 | C049 | 126 | -19.65% | 22.73% | PASS |
| 39 | C036 | 126 | -19.87% | 23.73% | PASS |
| 40 | C035 | 126 | -19.91% | 23.76% | PASS |
| 41 | C034 | 126 | -19.96% | 23.75% | PASS |
| 42 | C018 | 126 | -20.16% | 22.06% | PASS |
| 43 | C025 | 126 | -20.24% | 22.05% | PASS |
| 43 | C068 | 126 | -20.24% | 22.05% | PASS |
| 45 | C021 | 126 | -20.30% | 22.10% | PASS |
| 45 | C064 | 126 | -20.30% | 22.10% | PASS |
| 47 | C019 | 126 | -20.30% | 22.32% | PASS |
| 48 | C044 | 126 | -22.39% | 29.70% | PASS |
| 49 | C004 | 126 | -22.54% | 31.02% | PASS |
| — | C006 | 126 | -22.71% | 29.75% | FAILED |
| 50 | C054 | 126 | -23.83% | 29.29% | PASS |
| 51 | C057 | 126 | -23.87% | 29.21% | PASS |
| 51 | C058 | 126 | -23.87% | 29.21% | PASS |
| 53 | C043 | 126 | -23.89% | 30.60% | PASS |
| 54 | C062 | 126 | -23.96% | 28.94% | PASS |
| 55 | C053 | 126 | -24.13% | 29.21% | PASS |
| 56 | C059 | 126 | -24.13% | 29.21% | PASS |
| 57 | C060 | 126 | -24.23% | 29.00% | PASS |
| 58 | C061 | 126 | -24.31% | 29.21% | PASS |
| 59 | C008 | 126 | -24.94% | 25.80% | PASS |
| 60 | C005 | 126 | -25.03% | 34.42% | PASS |
| 61 | C056 | 126 | -25.61% | 29.70% | PASS |
| 62 | C055 | 126 | -25.69% | 30.11% | PASS |
| 63 | C010 | 126 | -26.94% | 33.93% | PASS |
| 64 | C015 | 126 | -28.39% | 38.39% | PASS |

### sector_rotation_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C054 | 126 | 15.58% | 3.49% | PASS |
| 2 | C060 | 126 | 15.38% | 3.65% | PASS |
| 2 | C062 | 126 | 15.38% | 3.65% | PASS |
| 4 | C053 | 126 | 15.00% | 3.64% | PASS |
| 4 | C057 | 126 | 15.00% | 3.64% | PASS |
| 4 | C059 | 126 | 15.00% | 3.64% | PASS |
| 7 | C061 | 126 | 14.92% | 3.65% | PASS |
| 8 | C058 | 126 | 13.41% | 4.80% | PASS |
| 9 | C055 | 126 | 12.78% | 4.85% | PASS |
| 10 | C056 | 126 | 11.67% | 4.58% | PASS |
| 11 | C051 | 126 | 9.59% | 3.82% | PASS |
| 12 | C015 | 126 | 9.22% | 8.89% | PASS |
| 13 | C006 | 126 | 7.35% | 6.72% | PASS |
| 14 | C014 | 126 | 7.17% | 4.00% | PASS |
| 15 | C042 | 126 | 7.14% | 3.88% | PASS |
| 16 | C004 | 126 | 6.93% | 5.98% | PASS |
| 17 | C005 | 126 | 6.66% | 5.59% | PASS |
| 17 | C044 | 126 | 6.66% | 5.59% | PASS |
| 19 | C043 | 126 | 6.28% | 3.07% | PASS |
| 20 | C019 | 126 | 6.07% | 5.53% | PASS |
| 21 | C013 | 126 | 5.85% | 5.22% | PASS |
| 22 | C017 | 126 | 5.57% | 4.97% | PASS |
| 23 | C050 | 126 | 5.54% | 5.53% | PASS |
| 24 | C038 | 126 | 5.26% | 5.31% | PASS |
| 24 | C039 | 126 | 5.26% | 5.31% | PASS |
| 26 | C011 | 126 | 5.21% | 4.01% | PASS |
| 27 | C022 | 126 | 3.59% | 5.93% | PASS |
| 27 | C025 | 126 | 3.59% | 5.93% | PASS |
| 27 | C065 | 126 | 3.59% | 5.93% | PASS |
| 27 | C068 | 126 | 3.59% | 5.93% | PASS |
| 31 | C028 | 126 | 3.48% | 6.21% | PASS |
| 31 | C030 | 126 | 3.48% | 6.21% | PASS |
| 33 | C024 | 126 | 3.43% | 6.21% | PASS |
| 33 | C026 | 126 | 3.43% | 6.21% | PASS |
| 33 | C047 | 126 | 3.43% | 6.21% | PASS |
| 33 | C067 | 126 | 3.43% | 6.21% | PASS |
| 37 | C046 | 126 | 3.41% | 6.21% | PASS |
| 38 | C045 | 126 | 3.39% | 6.21% | PASS |
| 39 | C001 | 126 | 3.35% | 6.21% | PASS |
| 39 | C002 | 126 | 3.35% | 6.21% | PASS |
| 39 | C020 | 126 | 3.35% | 6.21% | PASS |
| 39 | C021 | 126 | 3.35% | 6.21% | PASS |
| 39 | C023 | 126 | 3.35% | 6.21% | PASS |
| 39 | C027 | 126 | 3.35% | 6.21% | PASS |
| 39 | C029 | 126 | 3.35% | 6.21% | PASS |
| 39 | C052 | 126 | 3.35% | 6.21% | PASS |
| 39 | C063 | 126 | 3.35% | 6.21% | PASS |
| 39 | C064 | 126 | 3.35% | 6.21% | PASS |
| 39 | C066 | 126 | 3.35% | 6.21% | PASS |
| 50 | C031 | 126 | 3.33% | 5.97% | PASS |
| 51 | C018 | 126 | 3.24% | 6.08% | PASS |
| 51 | C048 | 126 | 3.24% | 6.08% | PASS |
| 53 | C040 | 126 | 3.16% | 6.02% | PASS |
| 53 | C041 | 126 | 3.16% | 6.02% | PASS |
| 55 | C032 | 126 | 3.15% | 6.00% | PASS |
| 56 | C037 | 126 | 3.10% | 6.14% | PASS |
| 57 | C035 | 126 | 2.94% | 6.20% | PASS |
| 58 | C036 | 126 | 2.86% | 6.19% | PASS |
| 59 | C034 | 126 | 2.56% | 6.20% | PASS |
| 60 | C049 | 126 | 2.46% | 7.03% | PASS |
| 61 | C012 | 126 | 2.45% | 1.95% | PASS |
| 62 | C033 | 126 | 1.20% | 7.79% | PASS |
| — | C007 | 126 | 1.01% | 4.65% | FAILED |
| — | C016 | 126 | 0.77% | 3.09% | FAILED |
| 63 | C009 | 126 | 0.45% | 6.31% | PASS |
| 64 | C003 | 126 | 0.00% | 0.00% | PASS |
| 65 | C010 | 126 | -0.01% | 5.91% | PASS |
| 66 | C008 | 126 | -2.17% | 7.91% | PASS |

### sector_rotation_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C056 | 126 | 11.87% | 3.25% | PASS |
| 2 | C055 | 126 | 11.69% | 3.44% | PASS |
| 3 | C054 | 126 | 11.39% | 3.32% | PASS |
| 4 | C053 | 126 | 9.35% | 3.09% | PASS |
| 4 | C058 | 126 | 9.35% | 3.09% | PASS |
| 4 | C059 | 126 | 9.35% | 3.09% | PASS |
| 7 | C060 | 126 | 9.24% | 3.01% | PASS |
| 8 | C061 | 126 | 9.22% | 3.01% | PASS |
| 9 | C057 | 126 | 8.83% | 3.14% | PASS |
| 10 | C062 | 126 | 8.66% | 3.11% | PASS |
| 11 | C015 | 126 | 8.66% | 11.50% | PASS |
| 12 | C005 | 126 | 8.53% | 10.82% | PASS |
| 13 | C010 | 126 | 7.83% | 3.95% | PASS |
| 14 | C044 | 126 | 7.22% | 7.79% | PASS |
| 15 | C004 | 126 | 6.47% | 9.84% | PASS |
| 16 | C049 | 126 | 6.11% | 4.23% | PASS |
| 17 | C051 | 126 | 5.99% | 3.30% | PASS |
| 18 | C009 | 126 | 5.94% | 2.43% | PASS |
| 19 | C017 | 126 | 5.76% | 3.58% | PASS |
| 20 | C022 | 126 | 5.63% | 4.34% | PASS |
| 20 | C065 | 126 | 5.63% | 4.34% | PASS |
| 22 | C024 | 126 | 5.28% | 4.34% | PASS |
| 22 | C047 | 126 | 5.28% | 4.34% | PASS |
| 22 | C067 | 126 | 5.28% | 4.34% | PASS |
| 25 | C046 | 126 | 5.26% | 4.34% | PASS |
| 26 | C026 | 126 | 5.22% | 4.34% | PASS |
| 27 | C011 | 126 | 5.20% | 2.63% | PASS |
| 28 | C001 | 126 | 5.19% | 4.34% | PASS |
| 28 | C002 | 126 | 5.19% | 4.34% | PASS |
| 28 | C020 | 126 | 5.19% | 4.34% | PASS |
| 28 | C021 | 126 | 5.19% | 4.34% | PASS |
| 28 | C027 | 126 | 5.19% | 4.34% | PASS |
| 28 | C029 | 126 | 5.19% | 4.34% | PASS |
| 28 | C045 | 126 | 5.19% | 4.34% | PASS |
| 28 | C052 | 126 | 5.19% | 4.34% | PASS |
| 28 | C063 | 126 | 5.19% | 4.34% | PASS |
| 28 | C064 | 126 | 5.19% | 4.34% | PASS |
| 38 | C019 | 126 | 5.18% | 4.40% | PASS |
| 39 | C031 | 126 | 5.02% | 4.32% | PASS |
| 40 | C018 | 126 | 5.02% | 4.32% | PASS |
| 40 | C048 | 126 | 5.02% | 4.32% | PASS |
| 42 | C038 | 126 | 4.98% | 4.14% | PASS |
| 42 | C039 | 126 | 4.98% | 4.14% | PASS |
| 44 | C037 | 126 | 4.98% | 4.30% | PASS |
| 45 | C025 | 126 | 4.97% | 4.31% | PASS |
| 45 | C068 | 126 | 4.97% | 4.31% | PASS |
| 47 | C040 | 126 | 4.91% | 4.23% | PASS |
| 47 | C041 | 126 | 4.91% | 4.23% | PASS |
| 49 | C034 | 126 | 4.89% | 4.25% | PASS |
| 50 | C032 | 126 | 4.87% | 4.30% | PASS |
| 51 | C028 | 126 | 4.80% | 4.28% | PASS |
| 51 | C030 | 126 | 4.80% | 4.28% | PASS |
| 53 | C035 | 126 | 4.80% | 4.25% | PASS |
| 54 | C023 | 126 | 4.74% | 4.30% | PASS |
| 54 | C066 | 126 | 4.74% | 4.30% | PASS |
| 56 | C036 | 126 | 4.72% | 4.29% | PASS |
| 57 | C050 | 126 | 4.56% | 3.72% | PASS |
| 58 | C043 | 126 | 3.76% | 6.02% | PASS |
| 59 | C042 | 126 | 3.49% | 6.05% | PASS |
| 60 | C006 | 126 | 3.11% | 7.04% | PASS |
| 61 | C033 | 126 | 2.79% | 4.37% | PASS |
| 62 | C014 | 126 | 1.78% | 1.77% | PASS |
| 63 | C008 | 126 | 1.09% | 4.37% | PASS |
| — | C016 | 126 | 0.87% | 3.81% | FAILED |
| 64 | C012 | 126 | 0.56% | 2.32% | PASS |
| 65 | C013 | 126 | 0.46% | 1.95% | PASS |
| 66 | C003 | 126 | 0.00% | 0.00% | PASS |
| — | C007 | 126 | -0.21% | 7.17% | FAILED |

### sideways_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C010 | 126 | 0.67% | 6.99% | PASS |
| — | C007 | 126 | 0.53% | 5.22% | FAILED |
| 2 | C006 | 126 | 0.06% | 7.30% | PASS |
| 3 | C003 | 126 | 0.00% | 0.00% | PASS |
| 4 | C012 | 126 | -0.34% | 1.98% | PASS |
| — | C016 | 126 | -0.63% | 3.48% | FAILED |
| 5 | C017 | 126 | -0.76% | 3.88% | PASS |
| 6 | C043 | 126 | -0.78% | 7.83% | PASS |
| 7 | C060 | 126 | -0.87% | 3.86% | PASS |
| 7 | C062 | 126 | -0.87% | 3.86% | PASS |
| 9 | C061 | 126 | -1.48% | 4.30% | PASS |
| 10 | C053 | 126 | -1.63% | 4.50% | PASS |
| 10 | C057 | 126 | -1.63% | 4.50% | PASS |
| 10 | C058 | 126 | -1.63% | 4.50% | PASS |
| 10 | C059 | 126 | -1.63% | 4.50% | PASS |
| 14 | C044 | 126 | -1.82% | 8.13% | PASS |
| 15 | C011 | 126 | -1.89% | 4.23% | PASS |
| 16 | C014 | 126 | -2.09% | 4.30% | PASS |
| 17 | C042 | 126 | -2.26% | 5.96% | PASS |
| 18 | C055 | 126 | -2.30% | 5.77% | PASS |
| 19 | C054 | 126 | -2.47% | 5.00% | PASS |
| 20 | C009 | 126 | -2.79% | 4.83% | PASS |
| 21 | C050 | 126 | -2.99% | 5.02% | PASS |
| 22 | C049 | 126 | -2.99% | 4.53% | PASS |
| 23 | C056 | 126 | -3.00% | 5.28% | PASS |
| 24 | C032 | 126 | -3.16% | 4.80% | PASS |
| 25 | C019 | 126 | -3.23% | 5.19% | PASS |
| 26 | C004 | 126 | -3.25% | 9.34% | PASS |
| 27 | C008 | 126 | -3.34% | 4.39% | PASS |
| 28 | C031 | 126 | -3.39% | 5.29% | PASS |
| 29 | C018 | 126 | -3.41% | 5.39% | PASS |
| 29 | C048 | 126 | -3.41% | 5.39% | PASS |
| 31 | C035 | 126 | -3.67% | 6.00% | PASS |
| 32 | C033 | 126 | -3.71% | 5.19% | PASS |
| 33 | C051 | 126 | -3.72% | 5.46% | PASS |
| 34 | C025 | 126 | -3.74% | 5.64% | PASS |
| 34 | C068 | 126 | -3.74% | 5.64% | PASS |
| 36 | C036 | 126 | -3.79% | 6.12% | PASS |
| 37 | C005 | 126 | -3.93% | 10.89% | PASS |
| 38 | C022 | 126 | -3.93% | 5.77% | PASS |
| 38 | C065 | 126 | -3.93% | 5.77% | PASS |
| 40 | C037 | 126 | -3.98% | 6.27% | PASS |
| 41 | C034 | 126 | -3.99% | 6.18% | PASS |
| 42 | C038 | 126 | -4.05% | 6.21% | PASS |
| 42 | C039 | 126 | -4.05% | 6.21% | PASS |
| 44 | C040 | 126 | -4.09% | 6.35% | PASS |
| 44 | C041 | 126 | -4.09% | 6.35% | PASS |
| 46 | C013 | 126 | -4.15% | 5.14% | PASS |
| 47 | C046 | 126 | -4.20% | 6.45% | PASS |
| 48 | C001 | 126 | -4.20% | 6.46% | PASS |
| 48 | C002 | 126 | -4.20% | 6.46% | PASS |
| 48 | C020 | 126 | -4.20% | 6.46% | PASS |
| 48 | C021 | 126 | -4.20% | 6.46% | PASS |
| 48 | C023 | 126 | -4.20% | 6.46% | PASS |
| 48 | C027 | 126 | -4.20% | 6.46% | PASS |
| 48 | C028 | 126 | -4.20% | 6.46% | PASS |
| 48 | C029 | 126 | -4.20% | 6.46% | PASS |
| 48 | C030 | 126 | -4.20% | 6.46% | PASS |
| 48 | C045 | 126 | -4.20% | 6.46% | PASS |
| 48 | C052 | 126 | -4.20% | 6.46% | PASS |
| 48 | C063 | 126 | -4.20% | 6.46% | PASS |
| 48 | C064 | 126 | -4.20% | 6.46% | PASS |
| 48 | C066 | 126 | -4.20% | 6.46% | PASS |
| 62 | C024 | 126 | -4.23% | 6.48% | PASS |
| 62 | C026 | 126 | -4.23% | 6.48% | PASS |
| 62 | C047 | 126 | -4.23% | 6.48% | PASS |
| 62 | C067 | 126 | -4.23% | 6.48% | PASS |
| 66 | C015 | 126 | -4.66% | 12.22% | PASS |

### sideways_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C008 | 126 | -0.66% | 0.97% | PASS |
| 3 | C032 | 126 | -0.79% | 1.67% | PASS |
| 4 | C013 | 126 | -0.89% | 1.12% | PASS |
| 5 | C031 | 126 | -1.16% | 2.32% | PASS |
| 6 | C049 | 126 | -1.16% | 2.06% | PASS |
| 7 | C022 | 126 | -1.17% | 2.32% | PASS |
| 7 | C065 | 126 | -1.17% | 2.32% | PASS |
| 9 | C018 | 126 | -1.40% | 2.63% | PASS |
| 9 | C048 | 126 | -1.40% | 2.63% | PASS |
| 11 | C010 | 126 | -1.60% | 2.74% | PASS |
| — | C009 | 126 | -1.62% | 2.74% | FAILED |
| 12 | C025 | 126 | -2.10% | 3.09% | PASS |
| 12 | C068 | 126 | -2.10% | 3.09% | PASS |
| 14 | C019 | 126 | -2.12% | 2.63% | PASS |
| 15 | C038 | 126 | -2.40% | 3.69% | PASS |
| 15 | C039 | 126 | -2.40% | 3.69% | PASS |
| 17 | C046 | 126 | -2.50% | 3.80% | PASS |
| 18 | C045 | 126 | -2.51% | 3.80% | PASS |
| 19 | C037 | 126 | -2.52% | 3.80% | PASS |
| 20 | C001 | 126 | -2.54% | 3.80% | PASS |
| 20 | C002 | 126 | -2.54% | 3.80% | PASS |
| 20 | C020 | 126 | -2.54% | 3.80% | PASS |
| 20 | C021 | 126 | -2.54% | 3.80% | PASS |
| 20 | C027 | 126 | -2.54% | 3.80% | PASS |
| 20 | C028 | 126 | -2.54% | 3.80% | PASS |
| 20 | C029 | 126 | -2.54% | 3.80% | PASS |
| 20 | C030 | 126 | -2.54% | 3.80% | PASS |
| 20 | C051 | 126 | -2.54% | 3.80% | PASS |
| 20 | C052 | 126 | -2.54% | 3.80% | PASS |
| 20 | C063 | 126 | -2.54% | 3.80% | PASS |
| 20 | C064 | 126 | -2.54% | 3.80% | PASS |
| 20 | C040 | 126 | -2.54% | 3.80% | PASS |
| 20 | C041 | 126 | -2.54% | 3.80% | PASS |
| 34 | C024 | 126 | -2.54% | 3.80% | PASS |
| 34 | C026 | 126 | -2.54% | 3.80% | PASS |
| 34 | C034 | 126 | -2.54% | 3.80% | PASS |
| 34 | C035 | 126 | -2.54% | 3.80% | PASS |
| 34 | C036 | 126 | -2.54% | 3.80% | PASS |
| 34 | C047 | 126 | -2.54% | 3.80% | PASS |
| 34 | C050 | 126 | -2.54% | 3.80% | PASS |
| 34 | C067 | 126 | -2.54% | 3.80% | PASS |
| 42 | C017 | 126 | -2.54% | 2.54% | PASS |
| 43 | C014 | 126 | -2.63% | 2.88% | PASS |
| 44 | C060 | 126 | -2.73% | 2.74% | PASS |
| 45 | C012 | 126 | -2.80% | 3.30% | PASS |
| 46 | C023 | 126 | -2.82% | 3.80% | PASS |
| 46 | C066 | 126 | -2.82% | 3.80% | PASS |
| 48 | C016 | 126 | -2.97% | 4.01% | PASS |
| 49 | C033 | 126 | -3.21% | 3.29% | PASS |
| 50 | C011 | 126 | -3.23% | 3.41% | PASS |
| 51 | C053 | 126 | -3.82% | 3.84% | PASS |
| 51 | C059 | 126 | -3.82% | 3.84% | PASS |
| 53 | C061 | 126 | -3.82% | 3.85% | PASS |
| 54 | C058 | 126 | -4.02% | 4.05% | PASS |
| 55 | C062 | 126 | -5.18% | 5.19% | PASS |
| 56 | C056 | 126 | -5.23% | 5.26% | PASS |
| — | C042 | 126 | -5.43% | 7.02% | FAILED |
| 57 | C043 | 126 | -5.73% | 7.02% | PASS |
| 58 | C057 | 126 | -6.00% | 6.02% | PASS |
| 59 | C055 | 126 | -6.08% | 6.10% | PASS |
| 60 | C054 | 126 | -6.08% | 6.10% | PASS |
| — | C007 | 126 | -6.48% | 7.31% | FAILED |
| 61 | C006 | 126 | -9.64% | 11.13% | PASS |
| 62 | C005 | 126 | -9.92% | 11.24% | PASS |
| 62 | C044 | 126 | -9.92% | 11.24% | PASS |
| 64 | C004 | 126 | -10.10% | 11.24% | PASS |
| 65 | C015 | 126 | -15.24% | 17.09% | PASS |

### slow_recovery_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C003 | 126 | 0.00% | 0.00% | PASS |
| 2 | C008 | 126 | -3.23% | 5.09% | PASS |
| 3 | C017 | 126 | -6.09% | 10.10% | PASS |
| 4 | C033 | 126 | -6.92% | 9.76% | PASS |
| 5 | C013 | 126 | -7.00% | 8.41% | PASS |
| 6 | C049 | 126 | -9.16% | 11.25% | PASS |
| 7 | C032 | 126 | -10.11% | 12.19% | PASS |
| 8 | C014 | 126 | -10.27% | 12.11% | PASS |
| 9 | C012 | 126 | -11.12% | 13.04% | PASS |
| 10 | C060 | 126 | -11.57% | 14.70% | PASS |
| 11 | C011 | 126 | -11.76% | 13.55% | PASS |
| 12 | C025 | 126 | -11.79% | 14.57% | PASS |
| 12 | C068 | 126 | -11.79% | 14.57% | PASS |
| 14 | C031 | 126 | -12.50% | 14.67% | PASS |
| 15 | C022 | 126 | -12.52% | 14.67% | PASS |
| 15 | C065 | 126 | -12.52% | 14.67% | PASS |
| 17 | C062 | 126 | -12.82% | 14.70% | PASS |
| 18 | C018 | 126 | -12.91% | 15.12% | PASS |
| 19 | C048 | 126 | -13.07% | 15.24% | PASS |
| 20 | C019 | 126 | -13.13% | 15.46% | PASS |
| — | C016 | 126 | -13.18% | 15.05% | FAILED |
| 21 | C009 | 126 | -13.60% | 15.47% | PASS |
| 22 | C061 | 126 | -13.62% | 16.76% | PASS |
| 23 | C054 | 126 | -14.64% | 17.95% | PASS |
| 24 | C058 | 126 | -14.73% | 17.91% | PASS |
| 25 | C059 | 126 | -14.73% | 17.91% | PASS |
| 26 | C053 | 126 | -14.76% | 17.93% | PASS |
| 27 | C051 | 126 | -14.86% | 17.19% | PASS |
| 28 | C056 | 126 | -14.91% | 17.82% | PASS |
| 29 | C055 | 126 | -15.16% | 18.12% | PASS |
| 30 | C038 | 126 | -15.44% | 17.69% | PASS |
| 30 | C039 | 126 | -15.44% | 17.69% | PASS |
| 32 | C023 | 126 | -15.62% | 18.43% | PASS |
| 32 | C066 | 126 | -15.62% | 18.43% | PASS |
| 34 | C050 | 126 | -15.68% | 17.65% | PASS |
| 35 | C021 | 126 | -15.77% | 17.94% | PASS |
| 35 | C064 | 126 | -15.77% | 17.94% | PASS |
| 37 | C057 | 126 | -15.81% | 17.91% | PASS |
| 38 | C024 | 126 | -16.06% | 18.32% | PASS |
| 38 | C047 | 126 | -16.06% | 18.32% | PASS |
| 38 | C067 | 126 | -16.06% | 18.32% | PASS |
| 41 | C034 | 126 | -16.07% | 18.34% | PASS |
| 42 | C046 | 126 | -16.07% | 18.38% | PASS |
| 43 | C036 | 126 | -16.08% | 18.33% | PASS |
| 44 | C035 | 126 | -16.08% | 18.34% | PASS |
| 45 | C037 | 126 | -16.10% | 18.38% | PASS |
| 46 | C026 | 126 | -16.11% | 18.41% | PASS |
| 47 | C040 | 126 | -16.11% | 18.41% | PASS |
| 47 | C041 | 126 | -16.11% | 18.41% | PASS |
| 49 | C001 | 126 | -16.14% | 18.43% | PASS |
| 49 | C002 | 126 | -16.14% | 18.43% | PASS |
| 49 | C020 | 126 | -16.14% | 18.43% | PASS |
| 49 | C027 | 126 | -16.14% | 18.43% | PASS |
| 49 | C028 | 126 | -16.14% | 18.43% | PASS |
| 49 | C029 | 126 | -16.14% | 18.43% | PASS |
| 49 | C030 | 126 | -16.14% | 18.43% | PASS |
| 49 | C045 | 126 | -16.14% | 18.43% | PASS |
| 49 | C052 | 126 | -16.14% | 18.43% | PASS |
| 49 | C063 | 126 | -16.14% | 18.43% | PASS |
| — | C007 | 126 | -22.90% | 26.03% | FAILED |
| 59 | C042 | 126 | -22.95% | 25.23% | PASS |
| 60 | C010 | 126 | -31.14% | 35.16% | PASS |
| 61 | C043 | 126 | -33.56% | 36.50% | PASS |
| — | C006 | 126 | -34.04% | 37.79% | FAILED |
| 62 | C044 | 126 | -37.54% | 41.00% | PASS |
| 63 | C004 | 126 | -39.83% | 43.27% | PASS |
| 64 | C005 | 126 | -45.18% | 48.63% | PASS |
| — | C015 | 126 | -49.52% | 53.34% | FAILED |

### slow_recovery_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C017 | 126 | 3.72% | 5.21% | PASS |
| 2 | C049 | 126 | 0.04% | 7.35% | PASS |
| 3 | C003 | 126 | 0.00% | 0.00% | PASS |
| 4 | C032 | 126 | -1.36% | 8.68% | PASS |
| 5 | C008 | 126 | -1.98% | 2.22% | PASS |
| 6 | C013 | 126 | -2.38% | 4.69% | PASS |
| 7 | C033 | 126 | -2.61% | 10.11% | PASS |
| 8 | C062 | 126 | -2.75% | 12.10% | PASS |
| 9 | C011 | 126 | -3.26% | 10.25% | PASS |
| 10 | C031 | 126 | -4.24% | 11.37% | PASS |
| 11 | C022 | 126 | -4.48% | 11.61% | PASS |
| 11 | C065 | 126 | -4.48% | 11.61% | PASS |
| 13 | C060 | 126 | -4.80% | 12.09% | PASS |
| 14 | C048 | 126 | -4.91% | 12.10% | PASS |
| 15 | C019 | 126 | -5.54% | 11.80% | PASS |
| 16 | C018 | 126 | -5.92% | 12.04% | PASS |
| 17 | C057 | 126 | -6.15% | 15.46% | PASS |
| 18 | C014 | 126 | -6.23% | 8.74% | PASS |
| 19 | C054 | 126 | -6.49% | 15.46% | PASS |
| 20 | C055 | 126 | -6.64% | 15.46% | PASS |
| 21 | C056 | 126 | -6.70% | 15.46% | PASS |
| 22 | C061 | 126 | -6.77% | 14.16% | PASS |
| 23 | C009 | 126 | -7.17% | 12.58% | PASS |
| 24 | C058 | 126 | -7.31% | 15.46% | PASS |
| 25 | C023 | 126 | -7.60% | 14.90% | PASS |
| 25 | C066 | 126 | -7.60% | 14.90% | PASS |
| 27 | C038 | 126 | -7.75% | 14.80% | PASS |
| 27 | C039 | 126 | -7.75% | 14.80% | PASS |
| 29 | C012 | 126 | -7.95% | 9.89% | PASS |
| 30 | C036 | 126 | -7.95% | 15.46% | PASS |
| 31 | C034 | 126 | -7.97% | 15.46% | PASS |
| 31 | C035 | 126 | -7.97% | 15.46% | PASS |
| 33 | C059 | 126 | -8.00% | 15.46% | PASS |
| 34 | C053 | 126 | -8.04% | 15.49% | PASS |
| 35 | C046 | 126 | -8.13% | 15.40% | PASS |
| 36 | C037 | 126 | -8.15% | 15.46% | PASS |
| 37 | C024 | 126 | -8.18% | 15.37% | PASS |
| 37 | C047 | 126 | -8.18% | 15.37% | PASS |
| 37 | C067 | 126 | -8.18% | 15.37% | PASS |
| 40 | C001 | 126 | -8.21% | 15.46% | PASS |
| 40 | C002 | 126 | -8.21% | 15.46% | PASS |
| 40 | C020 | 126 | -8.21% | 15.46% | PASS |
| 40 | C026 | 126 | -8.21% | 15.46% | PASS |
| 40 | C027 | 126 | -8.21% | 15.46% | PASS |
| 40 | C028 | 126 | -8.21% | 15.46% | PASS |
| 40 | C029 | 126 | -8.21% | 15.46% | PASS |
| 40 | C030 | 126 | -8.21% | 15.46% | PASS |
| 40 | C045 | 126 | -8.21% | 15.46% | PASS |
| 40 | C051 | 126 | -8.21% | 15.46% | PASS |
| 40 | C063 | 126 | -8.21% | 15.46% | PASS |
| 51 | C040 | 126 | -8.30% | 15.46% | PASS |
| 51 | C041 | 126 | -8.30% | 15.46% | PASS |
| 53 | C052 | 126 | -8.57% | 15.79% | PASS |
| 54 | C050 | 126 | -8.75% | 15.46% | PASS |
| 55 | C010 | 126 | -8.88% | 12.58% | PASS |
| 56 | C025 | 126 | -9.91% | 14.77% | PASS |
| 56 | C068 | 126 | -9.91% | 14.77% | PASS |
| 58 | C021 | 126 | -10.01% | 15.01% | PASS |
| 58 | C064 | 126 | -10.01% | 15.01% | PASS |
| 60 | C016 | 126 | -11.31% | 13.94% | PASS |
| — | C042 | 126 | -17.00% | 23.14% | FAILED |
| 61 | C043 | 126 | -17.43% | 23.12% | PASS |
| — | C007 | 126 | -18.94% | 24.03% | FAILED |
| — | C006 | 126 | -29.40% | 36.52% | FAILED |
| 62 | C004 | 126 | -31.73% | 39.38% | PASS |
| 63 | C005 | 126 | -32.45% | 39.46% | PASS |
| 63 | C044 | 126 | -32.45% | 39.46% | PASS |
| — | C015 | 126 | -44.46% | 51.51% | FAILED |

### technology_drawdown_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C042 | 126 | 5.33% | 4.97% | PASS |
| 2 | C056 | 126 | 4.32% | 4.81% | PASS |
| 3 | C051 | 126 | 3.87% | 4.68% | PASS |
| 4 | C055 | 126 | 3.82% | 5.02% | PASS |
| 5 | C034 | 126 | 3.43% | 4.90% | PASS |
| 6 | C035 | 126 | 3.34% | 5.09% | PASS |
| 7 | C036 | 126 | 3.32% | 5.11% | PASS |
| 8 | C024 | 126 | 3.24% | 5.34% | PASS |
| 8 | C026 | 126 | 3.24% | 5.34% | PASS |
| 8 | C047 | 126 | 3.24% | 5.34% | PASS |
| 8 | C067 | 126 | 3.24% | 5.34% | PASS |
| 12 | C040 | 126 | 3.24% | 5.26% | PASS |
| 12 | C041 | 126 | 3.24% | 5.26% | PASS |
| 14 | C037 | 126 | 3.17% | 5.29% | PASS |
| 15 | C046 | 126 | 3.14% | 5.36% | PASS |
| 16 | C001 | 126 | 3.14% | 5.36% | PASS |
| 16 | C002 | 126 | 3.14% | 5.36% | PASS |
| 16 | C020 | 126 | 3.14% | 5.36% | PASS |
| 16 | C021 | 126 | 3.14% | 5.36% | PASS |
| 16 | C027 | 126 | 3.14% | 5.36% | PASS |
| 16 | C029 | 126 | 3.14% | 5.36% | PASS |
| 16 | C045 | 126 | 3.14% | 5.36% | PASS |
| 16 | C052 | 126 | 3.14% | 5.36% | PASS |
| 16 | C063 | 126 | 3.14% | 5.36% | PASS |
| 16 | C064 | 126 | 3.14% | 5.36% | PASS |
| 26 | C050 | 126 | 3.11% | 3.95% | PASS |
| 27 | C038 | 126 | 3.11% | 5.18% | PASS |
| 27 | C039 | 126 | 3.11% | 5.18% | PASS |
| 29 | C022 | 126 | 2.65% | 5.38% | PASS |
| 29 | C065 | 126 | 2.65% | 5.38% | PASS |
| 31 | C028 | 126 | 2.61% | 5.31% | PASS |
| 31 | C030 | 126 | 2.61% | 5.31% | PASS |
| 33 | C023 | 126 | 2.61% | 5.84% | PASS |
| 33 | C066 | 126 | 2.61% | 5.84% | PASS |
| 35 | C031 | 126 | 2.37% | 5.71% | PASS |
| 36 | C053 | 126 | 2.29% | 5.54% | PASS |
| 36 | C057 | 126 | 2.29% | 5.54% | PASS |
| 36 | C059 | 126 | 2.29% | 5.54% | PASS |
| 39 | C018 | 126 | 2.25% | 5.83% | PASS |
| 39 | C048 | 126 | 2.25% | 5.83% | PASS |
| 41 | C025 | 126 | 2.15% | 5.86% | PASS |
| 41 | C068 | 126 | 2.15% | 5.86% | PASS |
| 43 | C058 | 126 | 2.14% | 5.48% | PASS |
| 44 | C032 | 126 | 2.13% | 5.79% | PASS |
| 45 | C019 | 126 | 2.12% | 6.54% | PASS |
| 46 | C061 | 126 | 1.91% | 5.76% | PASS |
| 47 | C049 | 126 | 1.36% | 6.23% | PASS |
| 48 | C060 | 126 | 1.09% | 6.00% | PASS |
| 48 | C062 | 126 | 1.09% | 6.00% | PASS |
| 50 | C003 | 126 | 0.00% | 0.00% | PASS |
| 51 | C012 | 126 | -1.98% | 6.54% | PASS |
| — | C007 | 126 | -2.23% | 9.29% | FAILED |
| 52 | C043 | 126 | -2.76% | 12.13% | PASS |
| — | C016 | 126 | -5.02% | 8.70% | FAILED |
| 53 | C010 | 126 | -5.13% | 13.96% | PASS |
| 54 | C006 | 126 | -6.84% | 15.64% | PASS |
| 55 | C011 | 126 | -7.44% | 14.21% | PASS |
| 56 | C033 | 126 | -8.64% | 14.53% | PASS |
| 57 | C009 | 126 | -9.02% | 15.09% | PASS |
| 58 | C005 | 126 | -10.68% | 20.94% | PASS |
| 58 | C044 | 126 | -10.68% | 20.94% | PASS |
| 60 | C014 | 126 | -12.35% | 17.19% | PASS |
| 61 | C054 | 126 | -12.94% | 19.88% | PASS |
| 62 | C013 | 126 | -13.42% | 17.16% | PASS |
| 63 | C004 | 126 | -14.14% | 25.12% | PASS |
| 64 | C008 | 126 | -17.83% | 22.13% | PASS |
| 65 | C017 | 126 | -18.07% | 24.86% | PASS |
| 66 | C015 | 126 | -21.39% | 32.73% | PASS |

### technology_drawdown_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C014 | 126 | 0.94% | 2.72% | PASS |
| 2 | C013 | 126 | 0.74% | 2.16% | PASS |
| 3 | C003 | 126 | 0.00% | 0.00% | PASS |
| 4 | C043 | 126 | -0.07% | 4.87% | PASS |
| 5 | C010 | 126 | -0.08% | 2.50% | PASS |
| 6 | C017 | 126 | -0.77% | 5.43% | PASS |
| 7 | C060 | 126 | -0.86% | 5.14% | PASS |
| 7 | C062 | 126 | -0.86% | 5.14% | PASS |
| 9 | C023 | 126 | -0.88% | 4.62% | PASS |
| 9 | C066 | 126 | -0.88% | 4.62% | PASS |
| 11 | C033 | 126 | -0.93% | 3.91% | PASS |
| 12 | C019 | 126 | -0.94% | 5.23% | PASS |
| 13 | C061 | 126 | -1.10% | 5.66% | PASS |
| 14 | C049 | 126 | -1.10% | 4.10% | PASS |
| 15 | C018 | 126 | -1.21% | 4.58% | PASS |
| 15 | C048 | 126 | -1.21% | 4.58% | PASS |
| 17 | C053 | 126 | -1.24% | 5.87% | PASS |
| 17 | C057 | 126 | -1.24% | 5.87% | PASS |
| 17 | C059 | 126 | -1.24% | 5.87% | PASS |
| 20 | C031 | 126 | -1.28% | 4.53% | PASS |
| 21 | C032 | 126 | -1.32% | 4.28% | PASS |
| 22 | C025 | 126 | -1.35% | 4.65% | PASS |
| 22 | C068 | 126 | -1.35% | 4.65% | PASS |
| 24 | C036 | 126 | -1.39% | 5.10% | PASS |
| 25 | C038 | 126 | -1.39% | 4.96% | PASS |
| 25 | C039 | 126 | -1.39% | 4.96% | PASS |
| 27 | C040 | 126 | -1.39% | 5.10% | PASS |
| 27 | C041 | 126 | -1.39% | 5.10% | PASS |
| 29 | C035 | 126 | -1.45% | 5.14% | PASS |
| 30 | C037 | 126 | -1.46% | 5.16% | PASS |
| 31 | C001 | 126 | -1.46% | 5.18% | PASS |
| 31 | C002 | 126 | -1.46% | 5.18% | PASS |
| 31 | C020 | 126 | -1.46% | 5.18% | PASS |
| 31 | C021 | 126 | -1.46% | 5.18% | PASS |
| 31 | C027 | 126 | -1.46% | 5.18% | PASS |
| 31 | C028 | 126 | -1.46% | 5.18% | PASS |
| 31 | C029 | 126 | -1.46% | 5.18% | PASS |
| 31 | C030 | 126 | -1.46% | 5.18% | PASS |
| 31 | C051 | 126 | -1.46% | 5.18% | PASS |
| 31 | C052 | 126 | -1.46% | 5.18% | PASS |
| 31 | C063 | 126 | -1.46% | 5.18% | PASS |
| 31 | C064 | 126 | -1.46% | 5.18% | PASS |
| 43 | C034 | 126 | -1.47% | 5.12% | PASS |
| 43 | C050 | 126 | -1.47% | 5.12% | PASS |
| 45 | C024 | 126 | -1.47% | 5.18% | PASS |
| 45 | C026 | 126 | -1.47% | 5.18% | PASS |
| 45 | C045 | 126 | -1.47% | 5.18% | PASS |
| 45 | C046 | 126 | -1.47% | 5.18% | PASS |
| 45 | C047 | 126 | -1.47% | 5.18% | PASS |
| 45 | C067 | 126 | -1.47% | 5.18% | PASS |
| 51 | C042 | 126 | -1.59% | 6.35% | PASS |
| 52 | C058 | 126 | -1.73% | 6.40% | PASS |
| 53 | C022 | 126 | -1.99% | 5.21% | PASS |
| 53 | C065 | 126 | -1.99% | 5.21% | PASS |
| 55 | C009 | 126 | -2.32% | 6.11% | PASS |
| 56 | C056 | 126 | -2.50% | 6.62% | PASS |
| 57 | C012 | 126 | -2.92% | 5.02% | PASS |
| 58 | C011 | 126 | -3.30% | 6.81% | PASS |
| 59 | C055 | 126 | -3.69% | 6.67% | PASS |
| 60 | C054 | 126 | -3.92% | 7.38% | PASS |
| 61 | C008 | 126 | -4.01% | 5.98% | PASS |
| — | C016 | 126 | -7.61% | 10.47% | FAILED |
| — | C007 | 126 | -9.07% | 13.11% | FAILED |
| 62 | C006 | 126 | -12.30% | 18.82% | PASS |
| 63 | C005 | 126 | -19.34% | 25.42% | PASS |
| 63 | C044 | 126 | -19.34% | 25.42% | PASS |
| 65 | C004 | 126 | -20.22% | 26.78% | PASS |
| 66 | C015 | 126 | -29.59% | 37.47% | PASS |

### volatility_spike_310601 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C029 | 126 | 71.84% | 9.26% | PASS |
| 2 | C062 | 126 | 67.50% | 7.03% | PASS |
| 3 | C057 | 126 | 66.12% | 8.97% | PASS |
| 4 | C033 | 126 | 65.81% | 6.93% | PASS |
| 5 | C049 | 126 | 64.73% | 7.47% | PASS |
| 6 | C032 | 126 | 64.28% | 7.76% | PASS |
| — | C015 | 126 | 63.68% | 41.97% | FAILED |
| 7 | C060 | 126 | 63.15% | 7.76% | PASS |
| 8 | C031 | 126 | 62.79% | 8.62% | PASS |
| 9 | C048 | 126 | 62.68% | 8.66% | PASS |
| 10 | C018 | 126 | 62.63% | 8.69% | PASS |
| 11 | C061 | 126 | 62.58% | 8.12% | PASS |
| 12 | C022 | 126 | 61.90% | 9.11% | PASS |
| 12 | C065 | 126 | 61.90% | 9.11% | PASS |
| 14 | C053 | 126 | 61.60% | 8.98% | PASS |
| 15 | C001 | 126 | 61.58% | 9.26% | PASS |
| 15 | C002 | 126 | 61.58% | 9.26% | PASS |
| 15 | C020 | 126 | 61.58% | 9.26% | PASS |
| 15 | C027 | 126 | 61.58% | 9.26% | PASS |
| 15 | C063 | 126 | 61.58% | 9.26% | PASS |
| 20 | C045 | 126 | 61.51% | 9.29% | PASS |
| 21 | C021 | 126 | 61.36% | 9.37% | PASS |
| 21 | C064 | 126 | 61.36% | 9.37% | PASS |
| 23 | C040 | 126 | 61.18% | 9.20% | PASS |
| 23 | C041 | 126 | 61.18% | 9.20% | PASS |
| 25 | C028 | 126 | 60.94% | 9.25% | PASS |
| 25 | C030 | 126 | 60.94% | 9.25% | PASS |
| 27 | C037 | 126 | 60.68% | 9.23% | PASS |
| 28 | C038 | 126 | 60.63% | 8.68% | PASS |
| 28 | C039 | 126 | 60.63% | 8.68% | PASS |
| 30 | C046 | 126 | 60.45% | 9.30% | PASS |
| 31 | C036 | 126 | 60.36% | 9.19% | PASS |
| 32 | C035 | 126 | 59.58% | 9.23% | PASS |
| 33 | C034 | 126 | 59.50% | 9.20% | PASS |
| 34 | C026 | 126 | 59.33% | 9.14% | PASS |
| 35 | C051 | 126 | 59.25% | 8.93% | PASS |
| 36 | C024 | 126 | 59.00% | 9.33% | PASS |
| 36 | C047 | 126 | 59.00% | 9.33% | PASS |
| 36 | C067 | 126 | 59.00% | 9.33% | PASS |
| 39 | C050 | 126 | 57.68% | 8.93% | PASS |
| 40 | C052 | 126 | 57.23% | 11.70% | PASS |
| 41 | C025 | 126 | 55.93% | 12.46% | PASS |
| 41 | C068 | 126 | 55.93% | 12.46% | PASS |
| 43 | C019 | 126 | 55.57% | 12.76% | PASS |
| 44 | C023 | 126 | 55.30% | 12.81% | PASS |
| 44 | C066 | 126 | 55.30% | 12.81% | PASS |
| 46 | C004 | 126 | 51.60% | 26.37% | PASS |
| 47 | C043 | 126 | 46.69% | 20.82% | PASS |
| 48 | C042 | 126 | 46.58% | 20.74% | PASS |
| 49 | C010 | 126 | 45.01% | 21.58% | PASS |
| 50 | C009 | 126 | 44.65% | 21.95% | PASS |
| 51 | C054 | 126 | 39.62% | 9.12% | PASS |
| 52 | C058 | 126 | 37.20% | 9.13% | PASS |
| 53 | C055 | 126 | 36.42% | 9.13% | PASS |
| 54 | C005 | 126 | 36.30% | 24.88% | PASS |
| 54 | C044 | 126 | 36.30% | 24.88% | PASS |
| 56 | C006 | 126 | 34.49% | 20.65% | PASS |
| 57 | C056 | 126 | 33.42% | 8.84% | PASS |
| 58 | C008 | 126 | 33.23% | 5.26% | PASS |
| 59 | C059 | 126 | 32.88% | 8.83% | PASS |
| 60 | C011 | 126 | 31.52% | 19.71% | PASS |
| 61 | C012 | 126 | 29.86% | 18.69% | PASS |
| 62 | C014 | 126 | 24.98% | 9.45% | PASS |
| 63 | C013 | 126 | 24.54% | 7.53% | PASS |
| 64 | C017 | 126 | 24.17% | 6.43% | PASS |
| — | C007 | 126 | 19.31% | 17.19% | FAILED |
| — | C016 | 126 | 9.13% | 12.58% | FAILED |
| 65 | C003 | 126 | 0.00% | 0.00% | PASS |

### volatility_spike_310619 — SYNTHETIC

| Eligible rank | Entry | Sessions | Return | Max DD | Compliance |
|---|---|---|---|---|---|
| 1 | C017 | 126 | 3.56% | 6.36% | PASS |
| 2 | C049 | 126 | 0.06% | 6.84% | PASS |
| 3 | C003 | 126 | 0.00% | 0.00% | PASS |
| 4 | C062 | 126 | -1.60% | 12.28% | PASS |
| 5 | C060 | 126 | -1.66% | 12.28% | PASS |
| 6 | C032 | 126 | -2.04% | 9.49% | PASS |
| 7 | C061 | 126 | -2.24% | 12.87% | PASS |
| 8 | C055 | 126 | -2.43% | 13.90% | PASS |
| 9 | C056 | 126 | -2.44% | 13.88% | PASS |
| 10 | C033 | 126 | -2.46% | 9.65% | PASS |
| 11 | C059 | 126 | -2.59% | 14.07% | PASS |
| 12 | C057 | 126 | -2.77% | 13.96% | PASS |
| 13 | C058 | 126 | -2.92% | 14.04% | PASS |
| 14 | C053 | 126 | -2.95% | 14.05% | PASS |
| 15 | C008 | 126 | -2.99% | 4.03% | PASS |
| 16 | C054 | 126 | -3.23% | 14.32% | PASS |
| 17 | C031 | 126 | -3.48% | 11.85% | PASS |
| 18 | C048 | 126 | -3.75% | 12.25% | PASS |
| 19 | C018 | 126 | -4.47% | 12.22% | PASS |
| 20 | C012 | 126 | -4.69% | 8.04% | PASS |
| 21 | C026 | 126 | -4.74% | 13.84% | PASS |
| 22 | C045 | 126 | -4.81% | 13.90% | PASS |
| 23 | C036 | 126 | -4.85% | 13.92% | PASS |
| 24 | C035 | 126 | -4.88% | 13.92% | PASS |
| 25 | C034 | 126 | -4.88% | 13.92% | PASS |
| 26 | C037 | 126 | -4.92% | 13.96% | PASS |
| 27 | C001 | 126 | -4.93% | 13.98% | PASS |
| 27 | C002 | 126 | -4.93% | 13.98% | PASS |
| 27 | C020 | 126 | -4.93% | 13.98% | PASS |
| 27 | C027 | 126 | -4.93% | 13.98% | PASS |
| 27 | C029 | 126 | -4.93% | 13.98% | PASS |
| 27 | C063 | 126 | -4.93% | 13.98% | PASS |
| 33 | C040 | 126 | -4.99% | 13.98% | PASS |
| 33 | C041 | 126 | -4.99% | 13.98% | PASS |
| 35 | C038 | 126 | -5.10% | 14.05% | PASS |
| 35 | C039 | 126 | -5.10% | 14.05% | PASS |
| 37 | C028 | 126 | -5.11% | 13.98% | PASS |
| 37 | C030 | 126 | -5.11% | 13.98% | PASS |
| 39 | C024 | 126 | -5.32% | 14.28% | PASS |
| 39 | C047 | 126 | -5.32% | 14.28% | PASS |
| 39 | C067 | 126 | -5.32% | 14.28% | PASS |
| 42 | C046 | 126 | -5.36% | 14.28% | PASS |
| 43 | C051 | 126 | -6.04% | 13.98% | PASS |
| 44 | C050 | 126 | -6.34% | 14.12% | PASS |
| 45 | C021 | 126 | -6.77% | 14.47% | PASS |
| 45 | C064 | 126 | -6.77% | 14.47% | PASS |
| 47 | C016 | 126 | -7.09% | 12.69% | PASS |
| 48 | C022 | 126 | -7.16% | 15.26% | PASS |
| 48 | C065 | 126 | -7.16% | 15.26% | PASS |
| 50 | C019 | 126 | -8.10% | 12.09% | PASS |
| 51 | C023 | 126 | -8.18% | 16.90% | PASS |
| 51 | C066 | 126 | -8.18% | 16.90% | PASS |
| 53 | C011 | 126 | -8.43% | 15.67% | PASS |
| 54 | C052 | 126 | -8.70% | 17.79% | PASS |
| — | C007 | 126 | -9.57% | 19.22% | FAILED |
| 55 | C025 | 126 | -9.85% | 15.00% | PASS |
| 55 | C068 | 126 | -9.85% | 15.00% | PASS |
| 57 | C014 | 126 | -11.37% | 16.08% | PASS |
| 58 | C013 | 126 | -12.03% | 13.98% | PASS |
| 59 | C043 | 126 | -12.37% | 28.93% | PASS |
| 60 | C010 | 126 | -13.02% | 29.00% | PASS |
| — | C006 | 126 | -15.17% | 28.85% | FAILED |
| 61 | C004 | 126 | -15.99% | 33.54% | PASS |
| 62 | C044 | 126 | -16.26% | 33.32% | PASS |
| 63 | C009 | 126 | -17.77% | 23.73% | PASS |
| 64 | C042 | 126 | -17.92% | 26.88% | PASS |
| 65 | C005 | 126 | -23.37% | 40.63% | PASS |
| 66 | C015 | 126 | -25.21% | 43.43% | PASS |

## Git status and new artifacts

Exact scoped status is in `git_status_after.txt`; tracked-only status is empty. Scope excludes `tiingo_cache`, scratch and existing private/history/leaderboard result files so sealed paths are not enumerated. Existing Stage3D–3E untracked files remain untracked. New Stage3F outputs are untracked. This deliberately does not claim a full untracked scan of prohibited directories.

Every pre-closure new artifact is listed with size and SHA-256 in `artifact_checksums.json`; that manifest excludes itself. The subsequent `final_audit_receipt.json` checks leaderboards, preservation and every listed checksum. `closure_checksums.json` hashes the base manifest and final audit receipt, and excludes itself, avoiding circular hashes. Together these registers identify every artifact, including their explicitly excluded terminal manifest. The inventory includes initial/revised discovery evidence, source snapshots, generator/configuration, compressed synthetic inputs, every decision/fill journal, daily CSV, per-run receipt, full metrics/leaderboards, paired comparison, tests, independent verification, preservation certificates and scripts. No old evidence was overwritten. A human can reproduce into a separately named Stage3F output directory; existing run directories are never overwritten.

## Human decisions and stop boundary

No result justifies changing the frozen official submission. No promotion, submission replacement or DEC-06 activation is authorized. Required unresolved decisions are rights-cleared explicit non-cache historical inputs if a real-data comparison is desired, clarification of contradictory competition rules/hidden evaluator behavior, and a genuinely unseen authorized evaluation design. Restoring missing sweep configurations would expand coverage but must not invent old versions. Preserve the synthetic results as engineering/descriptive research. **Stage3F stops here.**
