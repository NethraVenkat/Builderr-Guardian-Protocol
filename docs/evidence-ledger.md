# Builderr Trading Agents — Zero-Data-Loss Evidence Ledger & Audit Manifest

**Project:** Builderr Trading Agents — Round 2  
**Audit Type:** Zero-Data-Loss Preservation Audit & Evidence Certification  
**Audit Date:** 2026-10-19T23:30:00+05:30  
**Workspace Path:** `C:\Users\Manish\Downloads\New folder\Builderr-Trading-Agent`  
**Repository Branch:** `main` (4 commits ahead of `origin/main`)  
**Upstream Starter Parent:** `3ab0a0d5352c0289b5584300a6dfb09eff9184e6`  
**Active Certified Head:** `54d867a78200b04c629d43a74882324e392fc358`  

---

## 1. Executive Summary & Zero-Data-Loss Guarantee

This evidence ledger establishes an immutable, cryptographic audit manifest of all project files, research artifacts, historical experiments, test scripts, and benchmark measurements accumulated from Stage 1 through the Master Efficiency Optimization investigation.

### Core Non-Negotiable Guarantees:
1. **Zero Evidence Lost:** All historical test suites (14 Python scripts) and empirical datasets (3 JSON records) are fully preserved, cataloged, hashed, and verified recoverable.
2. **Zero Production Mutation:** Production `agent.py`, official simulator `preview.py`, runner `live_runner.py`, and starter baseline `baseline.py` have **0 diff** against the upstream starter commit (`3ab0a0d`).
3. **Reproducibility Verified:** 100% of test scripts (14 research scripts + 3 core suites) run cleanly and reproducibly in the isolated Python 3.14.8 environment.
4. **Contradictions Reconciled:** All documented discrepancies across previous stages (Calmar vs return, runtime measurements, order emissions, audit fixtures) are transparently reconciled without deleting any historical claims.

---

## 2. Git Checkpoint History & Provenance Chain

The repository maintains an unbroken, non-rewritten chronological Git commit chain:

| Commit SHA | Stage / Audit Milestone | Author Date | Commit Subject | Verified Scope |
|---|---|---|---|---|
| `3ab0a0d` | **Upstream Starter** | 2026-10-19 | Refresh live leaderboard 2026-10-19T15:53:54Z | Official Builderr competition starter base. |
| `d1a36d0` | **Stage 1 Verification** | 2026-10-19 | docs: verify Builderr competition contract | Created competition contract, compliance matrix, and stage-status board. |
| `77de9e9` | **Stage 2A Initial Setup** | 2026-10-19 | feat(stage2a): repair environment, verify regression suite, and profile baselines | Cleaned fake root stub; established `.venv`; profiled baseline strategies. |
| `27fe351` | **Stage 2A Final Lock** | 2026-10-19 | test: independently certify Stage 2A baselines and runtime | Added math verifier, adverse input tests, feature unit tests; certified runtime. |
| `54d867a` | **Efficiency Optimization** | 2026-10-19 | test(research): add efficiency profiling and hypothesis suites; retain verified baseline | Added deep profiling, vol-spike attribution, hypothesis tests H1–H8, cProfile. |

---

## 3. Master Repository Inventory & SHA-256 Manifest

Every file in the repository (excluding `.git/`, `.venv/`, and `__pycache__/`) has been hashed using SHA-256:

### A. Core Production Strategy (1 file)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Upstream Diff |
|---|---:|---:|---|---|
| `agent.py` | 11,849 | 363 | `c2fb0d4bff5a4651fdebfa4ee2faa500699134a6dcb407e33ef74e130f33d976` | **0 lines (Identical)** |

### B. Official Evaluator & Runner Suite (9 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Notes / Upstream Diff |
|---|---:|---:|---|---|
| `preview.py` | 12,041 | 358 | `048ea2845a1a602c7cadd73ccc84058c2e821bb53e8a19c73bbd1cf7b01508f3` | **0 lines (Identical)** |
| `live_runner.py` | 35,608 | 988 | `57375968644d8bd5536ce094510c18c1e57a49cf0f02d3f20a03acb19464b422` | **0 lines (Identical)** |
| `selfcheck.py` | 5,678 | 171 | `58246dfccfb7c7dcfc8354a577cf4a16e6102635a6a6371d90cab6e345029a11` | **0 lines (Identical)** |
| `fairness_tests.py` | 5,273 | 140 | `156b340194ae102a01629ab18bbb0b3ce4875be5a60817433319134de32b9b58` | **0 lines (Upstream audit fixture)** |
| `strategy_selftest.py` | 4,865 | 146 | `8e8ed01b11e206ed952c74d765aa905e1a32118ee02ed06b1662374e1cb31456` | **0 lines (Identical)** |
| `endpoint_harness_selftest.py` | 3,561 | 96 | `7a0c0e2d64b811ad23cf6bb81dee08b9b5b6af1aabc6ea6a2edcf18895fee42b` | **0 lines (Identical)** |
| `live_runner_selftest.py` | 5,117 | 134 | `4779f8724159865baca04858f24593fe923682e5c6b52ce25772079cfa3d5207` | **0 lines (Identical)** |
| `local_test.py` | 2,872 | 79 | `5ce768429c9021678e1ea5f1094d57e0a7b76ff881ac9ec1195455d0e3f0361f` | **0 lines (Identical)** |
| `full_test.py` | 2,285 | 67 | `e54dea03623582b619d9757603a6b71bd1e7e96bf2e4898432111171af4ef086` | **0 lines (Identical)** |

### C. Official Starter Strategy References (9 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Upstream Diff |
|---|---:|---:|---|---|
| `baseline.py` | 1,639 | 43 | `eb19b0e31d44961f804cb663abd03e1750a5f86da344eacc7b83a90e3b2cca6d` | **0 lines (Identical)** |
| `ai_momentum.py` | 5,429 | 147 | `42b2cb44fdfbaade9e9ca60a3ba508932f31ce3e0a2c6cff7d61a4aaacaa6fcd` | **0 lines (Identical)** |
| `drawdown_momentum.py` | 10,530 | 241 | `ec69adbe1bfcb881157e14eca0b0358a0133d008e4a60732c9301022a6aa5498` | **0 lines (Identical)** |
| `example_sector_rotation.py` | 3,947 | 113 | `922aa2fcfb9c8077eb2abc152b0f7a09a6f89138ef64a6428561d06ed9e4901f` | **0 lines (Identical)** |
| `example_vol_target.py` | 3,691 | 112 | `934d15636b7c7e0d3d9a708d0e24b83fa8383281d56a700ec2d25b8d9a723b49` | **0 lines (Identical)** |
| `house_barbell_realasset.py` | 8,106 | 174 | `52a59d2aef92e6ed95a629f81718a893a74fd3c6127cbdf24ef9b3716d255310` | **0 lines (Identical)** |
| `momentum_v1.py` | 1,636 | 54 | `40622061d4b84c15420aa998c1d6185d3887d0509314319c37cda36239c73158` | **0 lines (Identical)** |
| `qqq_benchmark.py` | 1,418 | 31 | `1049b7840bd39bcc8e55d26dbf3e588f3cb190a7c43a1b8a52e15eb3b1f692f5` | **0 lines (Identical)** |
| `seed_dual_momentum.py` | 5,691 | 142 | `7844dc0b492ed09fe0ed122e0b83bc6c12d946f885ce26d12fc7d783c8f2a29f` | **0 lines (Identical)** |

### D. Official Market Data & Universe Files (8 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Upstream Diff |
|---|---:|---:|---|---|
| `sample_regimes.json.gz` | 412,567 | binary | `ebda311e99e4ec19ec76452ef0ce03d9eeaf663b6e3da58268a5e5690ca4116a` | **0 bytes (Identical)** |
| `universe.json` | 12,492 | 1,007 | `c9d5c3c70af5948cf303a6f8c215f380ac4010d166edf734fd3375ceb0ab97df` | **0 lines (Identical)** |
| `history.json` | 79,950 | 4,672 | `2061a7b55149aa1d52ea3f79af3e35e1c39d65ab4a24d3197104cdb6a56ae0db` | **0 lines (Identical)** |
| `leaderboard.json` | 19,344 | 824 | `2bb4e768ef36674199459d2f35dadea4076ace7c1b842528dd4633f923bba2a6` | **0 lines (Identical)** |
| `private_results.json` | 88,651 | 5,026 | `7244412e20e181fa874aee9f993627ac047b89878366042bfe32732166e0c774` | **0 lines (Identical)** |
| `build_universe.py` | 4,744 | 121 | `684465dfe68e826b2e0957cbd469ca8365c7361ed2d23aff767bd879d847644f` | **0 lines (Identical)** |
| `market_open.py` | 1,085 | 34 | `c749f4f925619c131b2a06f6c890d1391e8a049d21f8b889885491e23f49940c` | **0 lines (Identical)** |
| `test_market_open.py` | 519 | 18 | `8dc352cb67deb98e734a2cfed4989e650050721346ba2391177716d696781868` | **0 lines (Identical)** |

### E. Official Documentation & Infrastructure Config (13 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Provenance |
|---|---:|---:|---|---|
| `README.md` | 13,193 | 163 | `c31dee55a36cf1fc9d7905da9e786b8a170a400ba89d93c80da00b2c916cc632` | Upstream Starter |
| `AGENT_BRIEF.md` | 6,488 | 112 | `3844e636d513cf8499b21d3c97d6f0922a5a89a4a34415c4de013f5ec7a6827d` | Upstream Starter |
| `ANATOMY.md` | 4,467 | 71 | `8af52774532587374b14b78c74cdc5925c03ee30137805c2712044abb7ee1ee1` | Upstream Starter |
| `START_HERE.md` | 3,580 | 92 | `1401a8de56dbadd401053871c8b5e9b90cb26f00f21791afd7279c5452470eaf` | Upstream Starter |
| `LICENSE` | 1,086 | 21 | `017f73d78451e6b27d18d19bb6d3555db1c0fd1801c45794ba6e7675b891ef0d` | Upstream Starter |
| `requirements.txt` | 49 | 1 | `fdf3a2633ddad4e124c2a80cda57c1fe13b83da6ef7892fffec634d98b701f0c` | Upstream Starter |
| `.gitignore` | 239 | 16 | `500143d827220ab3b22b829b3cdde42aeb0affed47a748f78f400730b5ffb8fd` | Modified to ignore `scratch/*.json` |
| `.github/workflows/leaderboard.yml` | 1,010 | 31 | `1b0df7efb8f555afa73ed7e20a30acb38af7b19c910e863ce57bd6abf95ce282` | Upstream Starter |
| `com.builderr.live-leaderboard.plist` | 1,098 | 30 | `d6a926aaa2f4c5b2d9d7d5b1889e4d3bfd595411ce496e40200ed1a20e7e6b44` | Upstream Starter |
| `refresh_live_leaderboard.sh` | 1,295 | 38 | `ce1db89e9ceb9aed1d8c7c3d23cea34e3405fa00073f46cb1bc4d2a30c72dccb` | Upstream Starter |
| `capture_endpoint_orders.py` | 5,600 | 137 | `978925ef033cfa09a1c47c1323b6edceb96bf084bd1cd065e89a0904a4bcfccc` | Upstream Starter |
| `endpoint_replay.py` | 2,399 | 55 | `1c0847876abb0bb661c1c3cb749f72d5351ac3bcb490780080de973c9cd3f2fa` | Upstream Starter |
| `endpoint_security.py` | 4,464 | 112 | `09d888cf432ad944ff8c4cd8e38ac6282d4915b5b86313ef7f9208b4e44f7356` | Upstream Starter |

### F. Stage Documentation & Audit Checkpoints (5 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Purpose |
|---|---:|---:|---|---|
| `docs/competition-contract.md` | 16,366 | 241 | `bba31c1d602d9267731f0a6df2b1283545211113a4a8cf7d494f5c3d2c7a283b` | Formal specification of rules, limits, and scoring |
| `docs/compliance-matrix.md` | 8,290 | 38 | `44627f9b422cf87af66be91fc80c72414810763a51c0f236ade6f583d25d2d76` | Traceability matrix for each competition limit |
| `docs/stage-status.md` | 6,242 | 43 | `0a10e4721e8994668f44966b037ac64a7fdd185e6c2ea1345fedafd244c9f2ae` | Permanent progress board across all stages |
| `docs/stage2-baseline.md` | 8,300 | 122 | `b33a8267d73d7f753518bd1a13d4943613e7ff2da30a794e5fe0ebd5dd265c81` | Stage 2 baseline reproduction and profiling |
| `docs/stage2a-final-verification.md` | 14,446 | 219 | `a446d757e6dcbe34fa02ca7128dedb66fcbd9df984c857f7fa8b8845f7c3f36d` | Stage 2A final certification and remediation |

### G. Research & Hypothesis Test Suites (14 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Stage Added | Purpose |
|---|---:|---:|---|---|---|
| `scratch/audit_test.py` | 2,885 | 65 | `e95445ed1a8446fab5fd41a525114f74f97f3878acca49ae0e00f5813c116610` | Stage 1.5 | Import isolation and module shadowing tests |
| `scratch/baseline_check.py` | 3,802 | 91 | `c83a5fae1e8cdac739d6f3e2ae8013bbdb8665f4edfd7dc67c1a1b25acd3a07f` | Stage 2A | Initial baseline reproduction against 3 regimes |
| `scratch/runtime_check.py` | 4,834 | 142 | `dc458ddbd427b1a09b02aaace3fd48f70f0d08fe3ba7ccd5f93dc8e82171a145` | Stage 2A | Execution latency and scaling verification |
| `scratch/benchmark_runtime.py` | 3,304 | 93 | `e27d9ca4d279b39fb1d49cbdf1cf3005c768da720ad5ceab32775ec38fec01cb` | Stage 2A Cert | Extended latency benchmarking (100 runs) |
| `scratch/math_verify.py` | 7,267 | 203 | `71800cc8dfcc86d007d0f325f92f3547c0785418d95a7c16e0d1425f1c93e2b4` | Stage 2A Cert | Mathematical correctness of Sharpe, Calmar, MDD |
| `scratch/reproduce_baseline.py` | 1,542 | 50 | `27b5afb5e75bf003a7dc92ab695ad028c8009313ecf7aaf529734e2a82b8ed54` | Stage 2A Cert | Bit-exact deterministic verification script |
| `scratch/test_adverse_inputs.py` | 3,011 | 76 | `70c3c0e5d0b3cfc11401c9a6d275e56447a90b1894b96cb26c1b1ca02966660d` | Stage 2A Cert | Zero cash, missing bars, NaN, empty state tests |
| `scratch/test_agent_features.py` | 6,115 | 149 | `8f2bed2a3091d0009e77b505f7da3bfb1b18f7b9e5151069f875d14a15266726` | Stage 2A Cert | Unit tests for SMA, closes, volatility, targets |
| `scratch/deep_baseline_profile.py` | 11,148 | 267 | `5ff43d95a5fd28aed907a59b252bf696f6a7fb912d45e1e8e628316817a8ae28` | Efficiency Opt | Full multi-regime profiling and trade logging |
| `scratch/analyze_vol_spike_attribution.py` | 1,218 | 34 | `cb953b63f66bd24fa66bbfdaa2f61b636c0039188def27ca660d5b4beccce845` | Efficiency Opt | Daily chronological attribution of COVID crash |
| `scratch/test_hypotheses.py` | 14,881 | 345 | `67fbd18e90f206c890b42c35040d7fcc165ff7cafbeae897d4e2111be92c4499` | Efficiency Opt | Hypothesis tests for H1 (min_trade) and H5 (XLE) |
| `scratch/test_hypotheses_part2.py` | 14,973 | 336 | `a3849549c2b02178815666ac4909ac4d366b3ea70903cee21b84b4f7d0b11e78` | Efficiency Opt | Hypothesis tests for H2 (inv vol), H3 (20d), H4 |
| `scratch/test_cadence.py` | 7,205 | 180 | `f169a009557cbfdf55a46659c0d774b94063684961cbbc3271f65d7eabea5408` | Efficiency Opt | Cadence sensitivity analysis (3d, 5d, 7d, 10d) |
| `scratch/profile_cpu.py` | 1,225 | 44 | `83c49eb29d7d9274cdd2da8cccba336275193a43320985b77b643a0121730a02` | Efficiency Opt | `cProfile` analysis over 500 rebalance cycles |

### H. Scratch Empirical Evidence Datasets (3 files)
| File Relative Path | Size (Bytes) | Lines | SHA-256 Hash | Generated By |
|---|---:|---:|---|---|
| `scratch/agent_day_logs.json` | 68,043 | 2,806 | `aedc87dde1ee704f010c5ba3d9a3b21f8e91ab61db0ff4235cf9536c8c27e379` | `scratch/deep_baseline_profile.py` |
| `scratch/deep_profile_metrics.json` | 4,836 | 144 | `f3884d234231be2d4642bc9239a70f36db4103efa54feed9b74fe745f6f010b0` | `scratch/deep_baseline_profile.py` |
| `scratch/hypotheses_results.json` | 8,128 | 266 | `460d5520416b597a256f015d84e44bd8b881853d6438a361d5c8a6441e3594a6` | `scratch/test_hypotheses.py` |

### I. External Audit Artifacts (Outside Repository Git Tree)
| External File Path | Size (Bytes) | SHA-256 Hash | Origin |
|---|---:|---|---|
| `<artifactDir>/stage1.5_gate_report.md` | 5,459 | `310b4f02d822050c1153fe019ae8a2e4ec206fd7b4a6d383f0b523e3c931eda6` | Independent Stage 1.5 Gate Report |

---

## 4. Reconciled Measurements & Discrepancies Registry

| Issue / Metric | Historical Record A | Historical Record B | Verified Ground Truth & Reconciliation |
|---|---|---|---|
| **Primary Scoring Metric** | `preview.py` docstrings mentioned Calmar Ratio | `AGENT_BRIEF.md` and `builderr.ai/trading-v0` state Forward Return | **Reconciled:** Official competition ranking is strictly determined by **Cumulative Forward Return** on the \$100,000 paper account from the first scored session. Sharpe and Calmar are informational risk statistics computed for internal admission profiling. |
| **Decision Runtime** | Stage 2A measured **2.84 ms** max latency (`scratch/runtime_check.py`) | Efficiency Audit measured **6.87 ms** max latency (`scratch/profile_cpu.py`) | **Reconciled:** In normal execution, rebalancing occurs once every 5 days; on 4 out of 5 days, `decide()` short-circuits in ~0.05 ms, yielding an average of ~0.5 ms and peak of ~2.84 ms. When forced to execute full `target_weights()` on every step under `cProfile` instrumentation, runtime is ~6.87 ms. Both are >700x faster than the 5.0s hard cutoff. |
| **Smoke Test Order Count** | `selfcheck.py` previously logged 4 emitted orders | Recent runs logged 5 emitted orders | **Reconciled:** `selfcheck.py` generates orders for top momentum assets where proposed dollar allocation exceeds `min_trade` (\$1,500). Due to integer share rounding (`int(notional / price)`), the 5th ticker may fluctuate around \$1,500 depending on mock price bars. Both 4 and 5 orders comply with all limits (limit: <= 50 orders). |
| **`fairness_tests.py` SyntaxError** | Initial audit flagged misplaced `from __future__` import on line 20 | Verified as upstream audit-only reference file | **Reconciled:** Upstream starter repository committed `fairness_tests.py` as a published reference for the private scoring cluster. It imports unreleased private packages (`builderr.harness`). Preserved without modification to maintain 100% upstream source integrity. |
| **XLE Defensive Performance** | `agent.py` designated `XLE` as a defensive sector asset | In 2020 COVID crash, `XLE` collapsed -50%, causing -15.77% bot return | **Reconciled:** Removing XLE improved 2020 by +1.34%, but severely degraded the 2022 moderate selloff by -2.16% (where XLE gained +30%). Hardcoding the removal of XLE is in-sample overfitting. Verified baseline retained. |

---

## 5. Non-Destructive Recoverability Verification

All 14 research scripts were executed sequentially and verified non-destructive. Execution output:

```text
scratch\analyze_vol_spike_attribution.py      : PASS (0.28s, stdout: 6932 chars, stderr: 0 chars)
scratch\audit_test.py                         : PASS (0.39s, stdout: 282 chars, stderr: 370 chars)
scratch\baseline_check.py                     : PASS (3.19s, stdout: 2839 chars, stderr: 0 chars)
scratch\benchmark_runtime.py                  : PASS (1.25s, stdout: 646 chars, stderr: 0 chars)
scratch\deep_baseline_profile.py              : PASS (1.42s, stdout: 3698 chars, stderr: 0 chars)
scratch\math_verify.py                        : PASS (0.24s, stdout: 811 chars, stderr: 0 chars)
scratch\profile_cpu.py                        : PASS (14.70s, stdout: 2896 chars, stderr: 0 chars)
scratch\reproduce_baseline.py                 : PASS (1.45s, stdout: 3100 chars, stderr: 0 chars)
scratch\runtime_check.py                      : PASS (1.27s, stdout: 1043 chars, stderr: 0 chars)
scratch\test_adverse_inputs.py                : PASS (0.15s, stdout: 520 chars, stderr: 0 chars)
scratch\test_agent_features.py                : PASS (0.13s, stdout: 777 chars, stderr: 0 chars)
scratch\test_cadence.py                       : PASS (1.53s, stdout: 1609 chars, stderr: 0 chars)
scratch\test_hypotheses.py                    : PASS (2.93s, stdout: 3446 chars, stderr: 0 chars)
scratch\test_hypotheses_part2.py              : PASS (2.61s, stdout: 1822 chars, stderr: 0 chars)
```

Core suite execution output:
- `selfcheck.py`: **PASS** (12 steps clean, 5 orders).
- `preview.py`: **PASS** (+14.65%, -3.36%, -15.77%, peak gross beta 0.94x, max drawdown 33.5% < 50%).
- `strategy_selftest.py`: **PASS** (8/8 unit tests passed).

---

## 6. Zero-Data-Loss Certification Statement

1. **Every meaningful file, test script, and experimental record is accounted for.**
2. **All cryptographic hashes match the repository working tree.**
3. **No file has been deleted, overwritten, or modified in an untracked manner.**
4. **Production strategy `agent.py` is identical to upstream `3ab0a0d`.**
5. **Stage 3 remains BLOCKED until authorized by project leadership.**
