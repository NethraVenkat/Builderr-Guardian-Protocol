# Stage 11 publication and submission handoff

**Verdict: CONDITIONAL.** Local publication-readiness checks pass. External
publication, organizer contact and submission are separate, unapproved actions.
Named non-default branch selection is a critical unresolved integration condition.
Nothing here asserts organizer admission or live leaderboard participation.

## Immutable identity

Repository: https://github.com/NethraVenkat/Builderr-Guardian-Protocol

Branch: `release/e0-stage10`.
Stage 10 source checkpoint: `9fb6033d0cd023e0d997b0d914db5ce963b959fb`.
Guardian base verified October 20, 2026:
`7e4f0f4d78f4c8c072fd0a8c5f9cae9b19812f2f`.
Research main remains `2aa065c85e7e71d25b6d968ec1572bf84e42b9b1`.
The Stage 11 commit changes handoff documentation and hashes only. Obtain its
exact publication SHA with `git rev-parse HEAD` after committing and verification;
use that final SHA in the handoff rather than silently submitting Stage 10.
The separately preserved final receipt and rendered email identify that SHA.

Agent SHA-256 (unchanged):
`46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd`.
Runtime dependency: Python standard library only. Tests: requirements-test.txt.
Prospective branch URL (not live until a separately authorized push):
https://github.com/NethraVenkat/Builderr-Guardian-Protocol/tree/release/e0-stage10

## Current authority and unresolved integration

Reviewed October 20, 2026:
- https://builderr.ai/trading-v0
- https://builderr.ai/starter-briefs/trading-agent.md
- https://builderr.ai/guidelines
- https://github.com/builderr-ai/builderr-trading-template/blob/main/README.md
- https://github.com/builderr-ai/builderr-trading-template/blob/main/AGENT_BRIEF.md
- Public live_runner.py and .github/workflows/leaderboard.yml in that repository.

The round advertises open entries. Submission/revision cutoff: October 31, 2026,
23:59 IST. Paper scoring ends November 9; results by November 10. Up to four
revisions are allowed, with fresh forward scoring for revisions. The public page
advertises free/open entry; individual identity, previous entry/admission and
revisions consumed remain unverified. Prize eligibility also requires beating
the benchmark and exact-code review. Do not infer user-specific eligibility.

Accepted methods: public repository, private repository with read-only deploy key,
or HTTPS POST /decide endpoint; handoff is to submit@builderr.ai. Public repository
is the simplest existing route if the organizer confirms exact branch/commit use.
The reviewed instructions do NOT explicitly promise named-branch selection or
commit checkout. An email containing a branch URL is not proof of evaluation of
that branch. The public workflow is a manual recovery job; it says scheduled
scoring runs with private code outside the public repository. It does not expose
the entrant-cloning policy. Lack of public documentation is not proof that the
organizer rejects named branches. Obtain confirmation before formal submission.

Published calls are once per day; retries/restarts and daily accounting semantics
are unspecified. E0 emits <=45 orders per call. Twelve stale overweight calls can
exceed 50 generated orders in total. A prior unchanged-public-runner counterexample
executed 51 trades; no permissive behavior is exploited. Do not certify arbitrary
intraday schedules or introduce a new daily counter without approved remediation.
Published limits remain long-only, beta gross <=1.5x, no name >=30% for more than
five trading days, <=50 daily trades, >=60s hold, <=5s decision. README concentration
wording is less precise than the agent contract. Private sustained-breach timers,
holding enforcement and decision termination remain unverified.

Questions requiring organizer confirmation:
1. Will you evaluate release/e0-stage10 at the exact final supplied commit rather
   than the repository default branch? Can you confirm the loaded commit/hash?
2. Is decide called once per scored session? Can retries or process restarts create
   multiple executable decisions for the same session, and how are they deduplicated?
3. Does the 50/day count refer to orders, fills, partial fills or another counter?
   Which layer enforces daily trade, holding, leverage/concentration and timeout rules?
4. Is this entry eligible, is it treated as a first submission or revision, and how
   many revisions remain for the submitter? What is its first scored session?

## Verified local evidence

Clean-checkout rerun: 56 passed, exit 0. selfcheck.py, preview.py and
strategy_selftest.py each exit 0. The agent runs with -I -S and an explicit local
package path, without site-package runtime dependencies. All economic traces
match research E0: timestamped orders, fills, quantities, cash, holdings, equity,
turnover, slippage and metrics; another deterministic replay matches exactly.
Independent Decimal accounting residual < $3e-11. No new strategy/H6.1 changes.

| Regime | Return | Maximum drawdown | Trades |
|---|---:|---:|---:|
| Calm uptrend | +14.650467% | 3.568219% | 38 |
| Moderate selloff | -3.364614% | 6.132986% | 17 |
| Volatility spike | -15.772963% | 33.457653% | 21 |

Observed maximum historical latency 4.055200ms; maximum across ten 1,000-ticker,
220-bar calls 78.785500ms. These are measurements, not worst-case guarantees.
Public samples are diagnostics, not expected forward returns or official scores.
Known preview missing-close behavior and other inherited limitations remain.

All 19 unpublished research commits and prior failed outputs are preserved locally.
At stage start full research publication spans 264 changed paths; Stage 10 spans
two commits/seven paths. Stage 11 adds only this handoff document and updates
RELEASE.md, .gitattributes and the release manifest. The actual final scope is
recorded in the receipt. Inherited public scratch/docs remain in the base; this
is a minimal new diff, not an entirely research-free repository. Private raw
results, contact details, bundles and backup archives are not added to this branch.

## Safe publication procedure - NOT authorized or executed

Run from the release worktree after separate explicit push approval:

```powershell
git status --short --branch
git rev-parse HEAD
git ls-remote guardian refs/heads/main refs/heads/release/e0-stage10
```

Require a clean tree, the approved final SHA, unchanged expected Guardian main,
and an absent destination branch (or a separately verified/authorized matching
state). Stop on an unexplained change. Then the intended non-force mapping is:

```powershell
git push guardian refs/heads/release/e0-stage10:refs/heads/release/e0-stage10
```

After an authorized push, independently verify the remote branch SHA and agent
hash before any separately authorized email/submission. Never push research main,
upstream origin, or force-update a ref. Do not change the default-branch setting.

If the organizer requires default-branch execution, the alternative is a separately
approved normal fast-forward update of Guardian main FROM the isolated release
branch, provided the live base remains its ancestor. This would not publish the
19 research-only commits or alter local research main. It is NOT authorized by
approval to push the named release branch. If the base moves, stop and re-audit;
do not force-push, rebase or rewrite history. Do not create another repository or
change visibility without separate approval.

## Prepared email templates - local drafts only

A rendered private draft contains the submitter identity and actual final SHA;
contact details are intentionally not committed here. The formal submission draft
must NOT be sent before branch-selection confirmation and authorized publication.

Clarification subject: Builderr Trading Round 2 - exact branch and scheduling confirmation

Hello Builderr team,

I am preparing an E0 Python entry in NethraVenkat/Builderr-Guardian-Protocol on
release/e0-stage10. Before publication/submission, can you confirm that you can
load the supplied non-default branch at an exact commit, rather than main?
Please also confirm once-daily scheduling and retry/deduplication behavior, how
the 50-trade daily limit is counted/enforced, and entry/revision eligibility.
Local checks pass; I am not claiming admission or requesting a scored run yet.

Thank you,
[Submitter name]

Formal submission subject: builderr submission - [Submitter name]

Hello Builderr team,

Please review my Trading Round 2 E0 entry at the repository and branch above,
pinned to [FINAL VERIFIED PUBLICATION SHA]. Please confirm that exact commit is
loaded; do not substitute the default branch. Agent SHA-256 is recorded above.
It requires only Python's standard library. The 56 release tests and three
local checks pass; the public historical baseline is unchanged. These results
are local diagnostics, not official admission or forward-performance claims.
The agent assumes the published once-daily decision schedule and emits at most
45 orders per call. Please confirm retry handling, eligibility/revisions remaining,
and the first scored session if admitted. RELEASE.md contains reproduction steps.

Thank you,
[Submitter name]
