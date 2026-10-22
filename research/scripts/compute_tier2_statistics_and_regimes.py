"""
Stage B2-N: Statistical Validation and Regime Robustness Analysis for Tier 2 (2020-2021).
Computes:
  1. Paired daily return differences: Frozen E0 vs Candidate A+E, Candidate A, and Candidate E.
  2. Parametric paired Student's t-test (t-statistic, p-value).
  3. Stationary block bootstrap (Politis & Romano) with block lengths L in {5, 10}, 10,000 replications, seed=42.
  4. Objective macroeconomic regime analysis across 6 predefined periods (505 sessions).
  5. Manifests: tier2_paired_strategy_statistics.json, tier2_regime_robustness_profile.json.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
import sys
import numpy as np

logger = logging.getLogger("tier2_stats")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PRIMARY_RESULTS_FILE = Path("research/manifests") / "tier2_four_way_results.json"
PAIRED_STATS_FILE = Path("research/manifests") / "tier2_paired_strategy_statistics.json"
REGIME_PROFILE_FILE = Path("research/manifests") / "tier2_regime_robustness_profile.json"
CACHE_FILE = Path("tiingo_cache") / "tier2_bars.json"

TIER2_REGIMES = [
    {
        "id": "REGIME_1_PRE_COVID",
        "name": "Pre-COVID Expansion",
        "start_date": "2020-01-02",
        "end_date": "2020-02-19",
        "description": "Steady market rise with low volatility prior to global pandemic lockdowns.",
    },
    {
        "id": "REGIME_2_COVID_CRASH",
        "name": "COVID-19 Market Shock",
        "start_date": "2020-02-20",
        "end_date": "2020-03-23",
        "description": "Severe liquidity crisis, S&P 500 -34% decline, VIX spikes to 82.",
    },
    {
        "id": "REGIME_3_POST_COVID_RECOVERY",
        "name": "Emergency Stimulus & Rebound",
        "start_date": "2020-03-24",
        "end_date": "2020-08-31",
        "description": "Historic Fed/Treasury stimulus, zero interest rates, aggressive V-shaped recovery.",
    },
    {
        "id": "REGIME_4_TECH_MOMENTUM",
        "name": "Tech Momentum Expansion",
        "start_date": "2020-09-01",
        "end_date": "2021-02-12",
        "description": "Mega-cap tech rally, work-from-home leaders, vaccine approvals.",
    },
    {
        "id": "REGIME_5_CYCLICAL_ROTATION",
        "name": "Reopening & Cyclical Rotation",
        "start_date": "2021-02-16",
        "end_date": "2021-11-05",
        "description": "Economic reopening, energy and financials surge, growth-to-value rotation.",
    },
    {
        "id": "REGIME_6_INFLATION_HAWKISH",
        "name": "Inflation Spike & Hawkish Pivot",
        "start_date": "2021-11-08",
        "end_date": "2021-12-31",
        "description": "CPI prints reach 40-year highs, Fed signals rate hikes, tech multiple compression.",
    },
]


def stationary_block_bootstrap(
    rets_a: np.ndarray,
    rets_b: np.ndarray,
    block_length: int = 5,
    num_replications: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """Stationary block bootstrap for paired return time series."""
    rng = np.random.RandomState(seed)
    n = len(rets_a)
    p = 1.0 / block_length

    delta_rets = rets_a - rets_b
    observed_mean_delta = float(np.mean(delta_rets))

    # Compute observed metrics
    def calc_sharpe(r):
        std = np.std(r, ddof=1)
        return (np.mean(r) / std * np.sqrt(252.0)) if std > 1e-9 else 0.0

    def calc_mdd(r):
        cum = np.cumprod(1.0 + r)
        peak = np.maximum.accumulate(cum)
        dd = (peak - cum) / peak
        return float(np.max(dd))

    obs_sharpe_delta = float(calc_sharpe(rets_a) - calc_sharpe(rets_b))
    obs_mdd_delta = float(calc_mdd(rets_a) - calc_mdd(rets_b))

    boot_mean_deltas = np.zeros(num_replications)
    boot_sharpe_deltas = np.zeros(num_replications)
    boot_mdd_deltas = np.zeros(num_replications)

    for b_idx in range(num_replications):
        # Generate stationary block bootstrap indices
        indices = np.zeros(n, dtype=int)
        curr_idx = rng.randint(0, n)
        for t in range(n):
            if rng.uniform(0.0, 1.0) < p:
                curr_idx = rng.randint(0, n)
            else:
                curr_idx = (curr_idx + 1) % n
            indices[t] = curr_idx

        b_a = rets_a[indices]
        b_b = rets_b[indices]
        boot_mean_deltas[b_idx] = np.mean(b_a - b_b)
        boot_sharpe_deltas[b_idx] = calc_sharpe(b_a) - calc_sharpe(b_b)
        boot_mdd_deltas[b_idx] = calc_mdd(b_a) - calc_mdd(b_b)

    ci_mean = np.percentile(boot_mean_deltas, [2.5, 97.5])
    ci_sharpe = np.percentile(boot_sharpe_deltas, [2.5, 97.5])
    ci_mdd = np.percentile(boot_mdd_deltas, [2.5, 97.5])

    # Empirical p-value that delta <= 0 (if hypothesized positive) or crossing 0
    p_value_zero = float(np.mean(boot_mean_deltas <= 0.0)) if observed_mean_delta > 0 else float(np.mean(boot_mean_deltas >= 0.0))

    return {
        "block_length": block_length,
        "replications": num_replications,
        "seed": seed,
        "observed_mean_daily_delta": round(observed_mean_delta, 6),
        "observed_annualized_delta": round(observed_mean_delta * 252.0, 4),
        "mean_delta_95_ci": [round(float(ci_mean[0]), 6), round(float(ci_mean[1]), 6)],
        "annualized_mean_delta_95_ci": [round(float(ci_mean[0] * 252.0), 4), round(float(ci_mean[1] * 252.0), 4)],
        "observed_sharpe_delta": round(obs_sharpe_delta, 4),
        "sharpe_delta_95_ci": [round(float(ci_sharpe[0]), 4), round(float(ci_sharpe[1]), 4)],
        "observed_mdd_delta_pct": round(obs_mdd_delta * 100.0, 2),
        "mdd_delta_95_ci_pct": [round(float(ci_mdd[0] * 100.0), 2), round(float(ci_mdd[1] * 100.0), 2)],
        "bootstrap_p_value_zero_cross": round(p_value_zero, 4),
    }


def analyze_statistics_and_regimes():
    with open(PRIMARY_RESULTS_FILE, "r", encoding="utf-8") as f:
        results = json.load(f)

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        preloaded_bars = json.load(f)

    # Reconstruct timeline from SPY
    timeline = [b["ts"] for b in preloaded_bars["SPY"] if "2020-01-01" <= b["ts"] <= "2021-12-31"]
    assert len(timeline) == 505, f"Expected 505 sessions, got {len(timeline)}"

    # Daily returns for each strategy
    curves = {name: np.array(data["equity_curve"]) for name, data in results.items()}
    daily_rets = {name: (curves[name][1:] / curves[name][:-1]) - 1.0 for name in curves}

    e0_rets = daily_rets["Frozen E0"]

    # ==========================================
    # 1. PAIRED STATISTICAL COMPARISONS
    # ==========================================
    logger.info("Computing paired strategy statistics and block bootstrap...")
    comparisons = {}

    for challenger in ["Candidate A+E", "Candidate A", "Candidate E"]:
        chall_rets = daily_rets[challenger]
        diff_rets = chall_rets - e0_rets

        # Parametric paired t-test
        mean_d = float(np.mean(diff_rets))
        std_d = float(np.std(diff_rets, ddof=1))
        n_d = len(diff_rets)
        se_d = std_d / math.sqrt(n_d) if n_d > 0 else 1.0
        t_stat = mean_d / se_d if se_d > 1e-12 else 0.0
        p_val = math.erfc(abs(t_stat) / math.sqrt(2.0))

        # Block bootstrap sensitivity: L = 5 and L = 10
        bb_5 = stationary_block_bootstrap(chall_rets, e0_rets, block_length=5, num_replications=10000, seed=42)
        bb_10 = stationary_block_bootstrap(chall_rets, e0_rets, block_length=10, num_replications=10000, seed=42)

        comparisons[f"Challenger: {challenger} vs Benchmark: Frozen E0"] = {
            "challenger": challenger,
            "benchmark": "Frozen E0",
            "sample_sessions": len(e0_rets),
            "parametric_t_test": {
                "t_statistic": round(float(t_stat), 4),
                "p_value_two_tailed": round(float(p_val), 6),
                "statistically_significant_005": bool(p_val < 0.05),
            },
            "block_bootstrap_length_5": bb_5,
            "block_bootstrap_length_10": bb_10,
            "interpretation": (
                f"{challenger} achieves lower Sharpe ({results[challenger]['metrics']['sharpe_ratio']} vs {results['Frozen E0']['metrics']['sharpe_ratio']}) "
                f"and lower ending NAV (${results[challenger]['metrics']['ending_nav']:,.2f} vs ${results['Frozen E0']['metrics']['ending_nav']:,.2f}). "
                f"The difference is statistically significant (p = {p_val:.4f})."
                if p_val < 0.05 else
                f"{challenger} and Frozen E0 return differences are not statistically distinguishable at alpha=0.05 (p = {p_val:.4f})."
            )
        }

    with open(PAIRED_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(comparisons, f, indent=2)
    logger.info(f"Wrote paired statistics to {PAIRED_STATS_FILE}.")

    # ==========================================
    # 2. OBJECTIVE REGIME ANALYSIS
    # ==========================================
    logger.info("Computing regime robustness across 6 predefined periods...")
    regime_results = []

    for reg in TIER2_REGIMES:
        s_date = reg["start_date"]
        e_date = reg["end_date"]

        # Indices in timeline
        reg_indices = [i for i, d in enumerate(timeline) if s_date <= d <= e_date]
        if not reg_indices:
            continue

        start_idx = reg_indices[0]
        end_idx = reg_indices[-1]

        reg_data = {
            "regime_id": reg["id"],
            "name": reg["name"],
            "start_date": s_date,
            "end_date": e_date,
            "sessions_count": len(reg_indices),
            "description": reg["description"],
            "strategy_performance": {},
        }

        for name in curves:
            # Segment equity curve
            # Starting NAV for regime is curve[start_idx - 1] if start_idx > 0 else 100k
            reg_start_nav = curves[name][start_idx - 1] if start_idx > 0 else 100_000.0
            reg_end_nav = curves[name][end_idx]
            reg_ret = (reg_end_nav / reg_start_nav) - 1.0

            # Daily returns in regime
            reg_rets = daily_rets[name][start_idx:end_idx] if end_idx > start_idx else daily_rets[name][start_idx:start_idx+1]
            n_reg = len(reg_rets)
            mean_r = np.mean(reg_rets) if n_reg > 0 else 0.0
            std_r = np.std(reg_rets, ddof=1) if n_reg > 1 else 0.0
            reg_sharpe = (mean_r / std_r * np.sqrt(252.0)) if std_r > 1e-9 else 0.0

            # Regime max drawdown
            seg_curve = curves[name][start_idx:end_idx + 1]
            peak = seg_curve[0]
            max_dd = 0.0
            for v in seg_curve:
                if v > peak:
                    peak = v
                dd = (peak - v) / peak if peak > 0 else 0.0
                if dd > max_dd:
                    max_dd = dd

            cagr = ((reg_end_nav / reg_start_nav) ** (252.0 / len(reg_indices)) - 1.0) if len(reg_indices) > 0 and (reg_end_nav / reg_start_nav) > 0 else 0.0

            reg_data["strategy_performance"][name] = {
                "starting_nav": round(float(reg_start_nav), 2),
                "ending_nav": round(float(reg_end_nav), 2),
                "regime_net_return_pct": round(float(reg_ret * 100.0), 2),
                "annualized_return_pct": round(float(cagr * 100.0), 2),
                "max_drawdown_pct": round(float(max_dd * 100.0), 2),
                "sharpe_ratio": round(float(reg_sharpe), 4),
            }

        regime_results.append(reg_data)

    with open(REGIME_PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "stage": "Stage B2-N Tier 2 Objective Macroeconomic Regime Robustness Profile",
            "observation_window": {"start": "2020-01-02", "end": "2021-12-31"},
            "total_regimes": len(regime_results),
            "regimes": regime_results,
        }, f, indent=2)
    logger.info(f"Wrote regime robustness profile to {REGIME_PROFILE_FILE}.")


if __name__ == "__main__":
    analyze_statistics_and_regimes()
