# E0 release candidate

Status: locally verified candidate; organizer admission remains pending.

This release is based on Guardian main `7e4f0f4d78f4c8c072fd0a8c5f9cae9b19812f2f`.
The production file is copied byte-for-byte from verified research commit
`2aa065c85e7e71d25b6d968ec1572bf84e42b9b1`.
Its SHA-256 is `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd`.
Use `git rev-parse HEAD` to identify the exact release commit being reviewed.
No H6.1 overlay, strategy change, or evaluator change is included.

## Scope and dependencies

Relative to the Guardian base, the release changes agent.py and adds release
documentation (this guide, SUBMISSION.md and RELEASE-AUDIT.md), the manifest,
requirements-test.txt, tests/test_e0_release.py, tests/e0_expected.json and
.gitattributes. The latter pins LF checkout endings for the selected release files
so byte hashes remain identical on Windows as well as other platforms.
The agent requires only Python's standard library; requirements.txt is unchanged.
Pytest is a test-only dependency, pinned separately in requirements-test.txt.
Validation used Python 3.14.8; this is not a cross-version guarantee.

Guardian's existing history already contains older research/docs/examples.
Those inherited files are preserved, not newly copied from the research branch.
The 19 unpublished research commits, external archives, bundles and scratch work
are not part of this release commit. Historical docs/evidence manifests describe
older checkpoints; use release-manifest.sha256 for the current selected files.
Do not run broad pytest discovery over inherited historical scratch experiments.

Essential runtime: agent.py plus Python. Review/support files: requirements.txt,
LICENSE, README.md, AGENT_BRIEF.md, universe.json, preview.py,
sample_regimes.json.gz, selfcheck.py and strategy_selftest.py.
The self-contained release tests require no scratch modules or external archive.
No API key, endpoint or external service is needed to run E0. Inherited historical
files do contain developer paths and backup locations; see RELEASE-AUDIT.md for
the publication-content review.
Official optional live-runner tooling has separate dependencies and is not part
of the agent's runtime requirements.

## Reproduce checks

Use a fresh checkout of the final release commit. Its Git attributes preserve
canonical LF bytes even when global core.autocrlf is enabled. A preliminary
Windows clone converted files to CRLF: 54 tests passed and the two strict hash
checks correctly failed. Those outputs are preserved; no trading-source change
was made to resolve the checkout issue.

From the repository root, in a Python environment:

```text
python -m pip install -r requirements-test.txt
python -X utf8 selfcheck.py
python -X utf8 preview.py
python -X utf8 strategy_selftest.py
python -m pytest tests/test_e0_release.py -v -ra -p no:cacheprovider
```

The 56 release tests cover numeric input rejection and state preservation,
valid-call recovery, order schema/universe, cash sizing, target caps, repeated
calls, sell quantities, runtime, manifest hashes and historical regression.
An exact agent hash assertion intentionally prevents silently changing this
candidate. Any later authorized repair requires a new independently verified
source pin and evidence. Test fixtures must not be edited simply to obtain PASS.

The expected historical metrics and canonical timestamped decision/portfolio
hashes were generated using unchanged official preview.py and the verified
research source. Independent audit telemetry also compares every fill, holding,
equity, cash balance, turnover and slippage value between research and release,
with an additional deterministic replay and Decimal accounting reconstruction.
All economic outputs match exactly; maximum accounting residual < $3e-11.

| Public regime | Return | Max drawdown | Sharpe | Calmar | Trades |
|---|---:|---:|---:|---:|---:|
| calm_uptrend | 14.650467% | 3.568219% | 4.176699 | 19.985822 | 38 |
| moderate_selloff | -3.364614% | 6.132986% | -2.530669 | -3.960029 | 17 |
| vol_spike_snapback | -15.772963% | 33.457653% | -1.295210 | -1.730564 | 21 |

Stage 10 measured historical max decision latency: 3.893200 ms. Ten heavy-input decisions
(1,000 tickers, 220 bars each) had a maximum of 46.876200 ms. These measurements
are below the published five-second limit, not a worst-case guarantee.
The private raw audit and reproducible comparison script are preserved separately;
they are not dependencies of this branch or its release tests.

## Compliance limits and admission

The published contract calls decide(market_state, portfolio_state, cash) once
per day. Output is capped at 45 orders per call. This bounds generated orders below 50 for one invocation per day. It does not
independently prove a limit on fills if partial fills or retries are counted
separately. Repeated stale,
overweight intraday calls can emit more than 50 orders in total; no universal
daily counter or retry idempotence is claimed. Confirm actual integration before
submission. The unchanged public runner accepted 51 executed trades in the audit;
this candidate does not exploit that permissive behavior.

All historical beta/concentration checks pass (peak beta <=0.936301, peak name
concentration <=26.4000%, no concentration breach streak). Target caps cannot
prevent every market-gap breach. Caller-provided timestamps and cutoffs must be
causal. Private leverage-duration, minimum-hold and timeout enforcement remain
unverified. Local preview success is not official organizer admission or evidence
of superior future returns. The known missing-close preview defect is preserved.

Official authority: https://builderr.ai/trading-v0 and
https://builderr.ai/starter-briefs/trading-agent.md . Last reviewed October 20,
2026: submission/revision cutoff October 31, 2026, 23:59 IST; up to four revisions.
Eligibility, revisions already used, and actual admission require organizer review.
The agent's legacy Calmar objective comment is historical; current ranking is
forward return, as explained in the unchanged official README.

## Publication plan - requires separate authorization

No push, deployment, email or submission was performed during preparation.
Before any authorized push, re-read Guardian's live main and proposed release
branch refs. Stop if the base or destination has changed unexpectedly. Publish
only this isolated release branch with a normal non-force push to Guardian.
Do not push research main, change remote visibility, or push to origin.
Use the exact published commit and branch when requesting organizer review.


## Stage 11 handoff

See SUBMISSION.md for the current publication gates, organizer branch-selection
questions and unsent email templates. Stage 11 preserves the exact Stage 10 agent
and fixtures. Local verification passes; named-branch execution and organizer
admission remain unverified. No external action is authorized by these documents.

## Provenance and current audit

AI tools assisted development, testing and documentation. The source and executed
evidence determine the claims; no authorship is inferred from writing style.
See RELEASE-AUDIT.md for the full file inventory, inherited historical artifacts,
security-scan scope and outstanding publication conditions. Official files,
including ANATOMY.md and earlier audit reports, may describe older objectives or
checkpoints; use the current challenge rules and this guide for this candidate.
