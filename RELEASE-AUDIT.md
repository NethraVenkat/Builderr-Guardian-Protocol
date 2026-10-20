# Final release audit ? October 20, 2026

Verdict: CONDITIONAL. Local technical verification does not establish organizer
admission or authorization to publish. This documentation-only audit branch
starts at release commit 5918e00fb453e8650ad2abaae58e489a01a4d521.
Research main and the historical-validation branch remain unchanged.
Use `git rev-parse HEAD` for the exact final audit candidate; its external receipt
records that SHA without a circular self-reference.

## Source and verification

E0 SHA-256: `46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd`.
Production algorithms, official scripts and historical expected fixtures are unchanged.
The 56 release tests passed, including strict source/manifest and historical
trace assertions. selfcheck.py, preview.py, strategy_selftest.py and the endpoint
harness self-test exited 0. The optional live-runner self-test initially failed
under `-S` because yfinance was unavailable with site packages disabled; it passed
with installed dependencies enabled. Both raw outputs are preserved. This does
not change E0's standard-library-only runtime requirement.

Independent telemetry matched research E0 orders, fills, positions, cash, equity,
turnover, slippage and metrics. Repeated replay matched. Decimal residual was
below $3e-11. The three public discovery windows retained returns +14.650467%,
-3.364614% and -15.772963%; maximum drawdowns 3.568219%, 6.132986% and 33.457653%.
These are previously inspected samples, not independent validation or forward
results. Additional real-market validation remains BLOCKED at data acceptance.

Last-session price poisoning left earlier equity unchanged. The caller must
still supply chronological, causal timestamps; arbitrary malformed timestamps
are not generally certified. The daily preview does not represent 60-second
holding clocks. A stale overweight portfolio produced 8 orders on each of 12
repeated calls (96 generated orders, not a claim of 96 executed trades). Therefore
<=45 per call does not certify arbitrary intraday retry schedules or fill counts.
Target caps and historical risk telemetry do not guarantee compliance after all
market gaps. Private enforcement, retries and exact branch loading remain unknown.

Observed latency: historical maximum 6.222ms; ten 1,000-ticker/220-bar calls
maximum 81.6804ms. Three cold processes took at most 158.18ms including startup;
module loading plus an empty-input decision took at most 76.39ms. These measured
cases are below five seconds, not universal runtime guarantees.

## Content, provenance and privacy

The initial release tree contains 70 tracked files. All were inventoried and
hashed; the table below distinguishes current support files from inherited
material. The new audit document brings the candidate to 71 tracked files.
Older files are retained to preserve history, not presented as current evidence.

- AGENT_BRIEF.md intentionally supplies instructions to an AI assistant. It is
  official starter material, not an accidentally copied conversation.
- ANATOMY.md has legacy Calmar-based scoring language. It is preserved official
  guidance; current challenge rules control. Earlier docs also contain historical
  PASS statements and obsolete hashes that must not certify the current agent.
- docs/ and scratch/ contain inherited research reports, generators, tests and
  backup scripts. They are not needed to execute E0. Machine-specific paths and
  local backup locations occur in seven files, including the inherited Mac plist.
  Those paths are already present in the base and its history. No new local paths
  or personal email addresses are added by this audit's publication changes.
- private_results.json, history.json and leaderboard.json are inherited published
  evaluation outputs. Their names alone do not establish confidential provenance.
  They are not evidence that this E0 candidate has been admitted or traded live.
- The inherited manual workflow and shell tooling can write leaderboard results
  and push. Neither was executed. Do not enable them as part of E0 submission.
- No chat transcript was identified. Generated ledger/report code is identifiable
  by its function, not by writing style. AI assistance is acknowledged in RELEASE.md;
  official attribution and LICENSE are preserved. The reviewed global rules did
  not specify a separate AI-use declaration; challenge-specific requests still apply.
- Provider market-data downloads, personal email drafts, new raw audit logs and
  external evidence archives are not copied into this candidate.

Inherited machine paths and historical artifacts remain a publication-review
condition. Removing them from the tip would not remove them from reachable
history. No deletion or history rewrite is performed. No blanket claim that
all inherited datasets are redistribution-cleared is made; upstream provenance
and repository license do not independently settle every third-party data right.

The full reachable history scan examined 1,740 unique file blobs. No matches
were found for the checked private-key and high-confidence token patterns.
This heuristic scan cannot prove the absence of all credentials or private data.

## Reproduction and external gates

Run the exact commands in RELEASE.md against a fresh checkout. Audit raw commands,
exit codes, hash inventories, independent traces and failed runs are preserved in
an external evidence archive; they are not runtime dependencies. Current authority:
https://builderr.ai/trading-v0 and https://builderr.ai/guidelines . The global rules
require honest evidence, an exact submitted version and no committed secrets.

Before publication, resolve inherited-content/privacy acceptance and confirm the
organizer can load the exact proposed branch/commit. Approval for the older release
branch would not authorize publication of this separate audit branch. No push,
email, deployment, default-branch change or submission is authorized by this report.

## Full initial public file inventory

| Path | Classification |
|---|---|
| `.gitattributes` | necessary testing/configuration |
| `.github/workflows/leaderboard.yml` | inherited upstream material |
| `.gitignore` | necessary testing/configuration |
| `AGENT_BRIEF.md` | inherited upstream material |
| `ANATOMY.md` | inherited upstream material |
| `LICENSE` | essential documentation |
| `README.md` | inherited upstream material |
| `RELEASE.md` | essential documentation |
| `START_HERE.md` | inherited upstream material |
| `SUBMISSION.md` | essential documentation |
| `agent.py` | required competition runtime |
| `ai_momentum.py` | inherited upstream material |
| `baseline.py` | inherited upstream material |
| `build_universe.py` | inherited upstream material |
| `capture_endpoint_orders.py` | inherited upstream material |
| `com.builderr.live-leaderboard.plist` | inherited upstream material |
| `docs/competition-contract.md` | inherited historical research |
| `docs/compliance-matrix.md` | inherited historical research |
| `docs/evidence-ledger.md` | inherited historical research |
| `docs/evidence-manifest.sha256` | inherited historical research |
| `docs/stage-status.md` | inherited historical research |
| `docs/stage2-baseline.md` | inherited historical research |
| `docs/stage2a-final-verification.md` | inherited historical research |
| `drawdown_momentum.py` | inherited upstream material |
| `endpoint_harness_selftest.py` | inherited upstream material |
| `endpoint_replay.py` | inherited upstream material |
| `endpoint_security.py` | inherited upstream material |
| `example_sector_rotation.py` | inherited upstream material |
| `example_vol_target.py` | inherited upstream material |
| `fairness_tests.py` | inherited upstream material |
| `full_test.py` | inherited upstream material |
| `history.json` | inherited upstream material |
| `house_barbell_realasset.py` | inherited upstream material |
| `leaderboard.json` | inherited upstream material |
| `live_runner.py` | inherited upstream material |
| `live_runner_selftest.py` | inherited upstream material |
| `local_test.py` | inherited upstream material |
| `market_open.py` | inherited upstream material |
| `momentum_v1.py` | inherited upstream material |
| `preview.py` | inherited upstream material |
| `private_results.json` | inherited upstream material |
| `qqq_benchmark.py` | inherited upstream material |
| `refresh_live_leaderboard.sh` | inherited upstream material |
| `release-manifest.sha256` | necessary testing/configuration |
| `requirements-test.txt` | necessary testing/configuration |
| `requirements.txt` | necessary testing/configuration |
| `sample_regimes.json.gz` | inherited upstream material |
| `scratch/analyze_vol_spike_attribution.py` | inherited historical research |
| `scratch/audit_test.py` | inherited historical research |
| `scratch/backup_and_verify_evidence.py` | inherited historical research |
| `scratch/baseline_check.py` | inherited historical research |
| `scratch/benchmark_runtime.py` | inherited historical research |
| `scratch/build_ledger_and_manifest.py` | inherited historical research |
| `scratch/deep_baseline_profile.py` | inherited historical research |
| `scratch/math_verify.py` | inherited historical research |
| `scratch/profile_cpu.py` | inherited historical research |
| `scratch/reproduce_baseline.py` | inherited historical research |
| `scratch/runtime_check.py` | inherited historical research |
| `scratch/test_adverse_inputs.py` | inherited historical research |
| `scratch/test_agent_features.py` | inherited historical research |
| `scratch/test_cadence.py` | inherited historical research |
| `scratch/test_hypotheses.py` | inherited historical research |
| `scratch/test_hypotheses_part2.py` | inherited historical research |
| `seed_dual_momentum.py` | inherited upstream material |
| `selfcheck.py` | inherited upstream material |
| `strategy_selftest.py` | inherited upstream material |
| `test_market_open.py` | inherited upstream material |
| `tests/e0_expected.json` | necessary testing/configuration |
| `tests/test_e0_release.py` | necessary testing/configuration |
| `universe.json` | inherited upstream material |
| `RELEASE-AUDIT.md` | New release audit documentation |
