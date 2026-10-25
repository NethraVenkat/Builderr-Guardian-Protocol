"""
Guardian Alpha V30 Stage 3B-R2 Standalone Reproducible Simulation & Calibration Module.
Provides exact finite-sample AR(1) variance calculation, analytical power matrix generation,
and joint Newey-West HAC + Stationary Block Bootstrap empirical size & power calibration.
"""

import math
import time
import json
import numpy as np


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def exact_ar1_variance(N: int, rho: float, sigma: float) -> dict:
    """
    Compute exact finite-sample variance and effective sample size of the sample mean
    for a stationary AR(1) process with marginal standard deviation sigma and lag correlation rho.
    Formula: Var(Xbar) = (sigma^2 / N) * [1 + 2 * sum_{k=1}^{N-1} (1 - k/N) * rho^k].
    """
    if rho == 0.0:
        factor_exact = 1.0
        factor_asymp = 1.0
    else:
        s = sum((1.0 - k / N) * (rho ** k) for k in range(1, N))
        factor_exact = 1.0 + 2.0 * s
        factor_asymp = (1.0 + rho) / (1.0 - rho)

    var_exact = (sigma ** 2 / N) * factor_exact
    var_asymp = (sigma ** 2 / N) * factor_asymp

    se_exact = math.sqrt(max(var_exact, 1e-12))
    se_asymp = math.sqrt(max(var_asymp, 1e-12))

    n_eff_exact = N / factor_exact
    n_eff_asymp = N / factor_asymp

    rel_error_var = (var_asymp - var_exact) / var_exact if var_exact > 0 else 0.0
    rel_error_se = (se_asymp - se_exact) / se_exact if se_exact > 0 else 0.0

    return {
        "N": N,
        "rho": rho,
        "sigma": sigma,
        "factor_exact": factor_exact,
        "factor_asymp": factor_asymp,
        "var_exact": var_exact,
        "var_asymp": var_asymp,
        "se_exact": se_exact,
        "se_asymp": se_asymp,
        "n_eff_exact": n_eff_exact,
        "n_eff_asymp": n_eff_asymp,
        "rel_error_var_pct": rel_error_var * 100.0,
        "rel_error_se_pct": rel_error_se * 100.0
    }


def compute_analytical_power(
    N: int,
    rho: float,
    sigma: float,
    mu: float,
    hurdle: float = 10.0,
    alpha: float = 0.05
) -> dict:
    """
    Compute analytical power under both exact finite-N SE and asymptotic SE.
    """
    z_crit = 1.6448536269514722  # norm.ppf(0.95)
    var_stats = exact_ar1_variance(N, rho, sigma)

    # Power = P( (Xbar - hurdle) / SE > z_crit ) = 1 - Phi( z_crit - (mu - hurdle) / SE )
    se_exact = var_stats["se_exact"]
    se_asymp = var_stats["se_asymp"]

    z_exact = z_crit - (mu - hurdle) / se_exact
    z_asymp = z_crit - (mu - hurdle) / se_asymp

    power_exact = (1.0 - norm_cdf(z_exact)) * 100.0
    power_asymp = (1.0 - norm_cdf(z_asymp)) * 100.0

    if mu < hurdle:
        scenario_type = "TRUE_NULL_BELOW_HURDLE"
    elif math.isclose(mu, hurdle, abs_tol=1e-5):
        scenario_type = "NULL_BOUNDARY"
    else:
        scenario_type = "TRUE_ALTERNATIVE_ABOVE_HURDLE"

    return {
        **var_stats,
        "mu": mu,
        "hurdle": hurdle,
        "scenario_type": scenario_type,
        "power_exact_pct": power_exact,
        "power_asymp_pct": power_asymp,
        "power_diff_pct": power_exact - power_asymp
    }


def generate_216_analytical_matrix() -> list:
    """Generate all 216 analytical scenarios."""
    Ns = [30, 45, 60, 90]
    rhos = [0.00, 0.20, 0.40]
    sigmas = [25.0, 50.0, 100.0]
    mus = [0.0, 10.0, 15.0, 20.0, 25.0, 40.0]

    matrix = []
    for N in Ns:
        for rho in rhos:
            for sigma in sigmas:
                for mu in mus:
                    res = compute_analytical_power(N, rho, sigma, mu, hurdle=10.0, alpha=0.05)
                    matrix.append(res)
    return matrix


def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple:
    """Compute Wilson score confidence interval for binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    z = 1.959963984540054  # 95% two-sided normal quantile
    denominator = 1.0 + (z ** 2) / n
    centre_adjusted_probability = p + (z ** 2) / (2.0 * n)
    adjusted_standard_deviation = math.sqrt((p * (1.0 - p) + (z ** 2) / (4.0 * n)) / n)
    lower = (centre_adjusted_probability - z * adjusted_standard_deviation) / denominator
    upper = (centre_adjusted_probability + z * adjusted_standard_deviation) / denominator
    return (max(0.0, lower * 100.0), min(100.0, upper * 100.0))


def simulate_joint_calibration_scenario(
    N: int,
    rho: float,
    sigma: float,
    mu: float,
    hurdle: float = 10.0,
    M: int = 1000,
    B: int = 1000,
    seed: int = 20261025
) -> dict:
    """
    Execute seeded Monte Carlo simulation evaluating Newey-West HAC,
    Stationary Block Bootstrap, and their Joint Rule on the SAME synthetic samples.
    """
    t0 = time.time()
    np.random.seed(seed)

    # 1. AR(1) Data-Generation Process
    sigma_eps = sigma * math.sqrt(1.0 - rho ** 2) if rho < 1.0 else sigma
    burn_in = 50
    total_len = N + burn_in

    eps = np.random.normal(0.0, sigma_eps, size=(M, total_len))
    x = np.zeros((M, total_len))
    for t in range(1, total_len):
        x[:, t] = rho * x[:, t - 1] + eps[:, t]
    series = x[:, burn_in:] + mu  # shape (M, N)

    # 2. Newey-West HAC Test (One-sided at hurdle)
    means = np.mean(series, axis=1)  # shape (M,)
    q = int(math.floor(4.0 * (N / 100.0) ** (2.0 / 9.0)))
    demeaned = series - means[:, None]
    gamma0 = np.mean(demeaned ** 2, axis=1)
    hac_var = gamma0.copy()
    for j in range(1, q + 1):
        weight = 1.0 - j / (q + 1)
        gamma_j = np.mean(demeaned[:, j:] * demeaned[:, :-j], axis=1)
        hac_var += 2.0 * weight * gamma_j
    hac_var = np.maximum(hac_var, 1e-6)
    se_hac = np.sqrt(hac_var / N)
    t_hac = (means - hurdle) / se_hac

    z_crit = 1.6448536269514722
    rej_hac = (t_hac > z_crit)

    # 3. Stationary Block Bootstrap (Politis & Romano 1994)
    # Mean-centered under null: d_tilde has empirical mean exactly equal to hurdle
    d_tilde = series - means[:, None] + hurdle  # shape (M, N)

    b_len = int(math.ceil(N ** (1.0 / 3.0)))
    p_geom = 1.0 / b_len

    rej_boot = np.zeros(M, dtype=bool)
    p_boot_vals = np.zeros(M)

    # Pre-generate jump indicator pattern for B resamples of length N
    jumps = np.random.binomial(1, p_geom, size=(B, N))
    jumps[:, 0] = 1

    for m in range(M):
        random_starts = np.random.randint(0, N, size=(B, N))
        indices = np.zeros((B, N), dtype=int)
        curr = random_starts[:, 0]
        indices[:, 0] = curr
        for t in range(1, N):
            jump = jumps[:, t]
            curr = np.where(jump == 1, random_starts[:, t], (curr + 1) % N)
            indices[:, t] = curr

        boot_sample = d_tilde[m, indices]  # shape (B, N)
        boot_means = np.mean(boot_sample, axis=1)  # shape (B,)

        p_b = np.mean(boot_means >= means[m])
        p_boot_vals[m] = p_b
        rej_boot[m] = (p_b < 0.05)

    # 4. Joint Rejection Rule: Both must reject
    rej_joint = rej_hac & rej_boot

    k_hac = int(np.sum(rej_hac))
    k_boot = int(np.sum(rej_boot))
    k_joint = int(np.sum(rej_joint))

    hac_rate = (k_hac / M) * 100.0
    boot_rate = (k_boot / M) * 100.0
    joint_rate = (k_joint / M) * 100.0

    se_hac_mc = math.sqrt((hac_rate / 100.0) * (1.0 - hac_rate / 100.0) / M) * 100.0
    se_boot_mc = math.sqrt((boot_rate / 100.0) * (1.0 - boot_rate / 100.0) / M) * 100.0
    se_joint_mc = math.sqrt((joint_rate / 100.0) * (1.0 - joint_rate / 100.0) / M) * 100.0

    ci_hac = wilson_score_interval(k_hac, M)
    ci_boot = wilson_score_interval(k_boot, M)
    ci_joint = wilson_score_interval(k_joint, M)

    elapsed_s = time.time() - t0

    # Calibration classification:
    # At null boundary (mu == 10.0), nominal alpha is 5.0%.
    # If joint rejection exceeds 5.0% + 2 * SE_mc (approx 6.4%), classify FAILED.
    if math.isclose(mu, hurdle, abs_tol=1e-5):
        if joint_rate > 5.0 + 2.0 * se_joint_mc:
            calibration_status = "FAILED_SIZE_DISTORTION"
        elif joint_rate < 5.0 - 2.0 * se_joint_mc:
            calibration_status = "CONSERVATIVE_SIZE_DEFICIT"
        else:
            calibration_status = "CALIBRATED_NOMINAL_SIZE"
    elif mu < hurdle:
        calibration_status = "DEEP_NULL_CONTROLLED"
    else:
        calibration_status = "ADEQUATELY_POWERED" if joint_rate >= 80.0 else "UNDERPOWERED_ALTERNATIVE"

    return {
        "N": N,
        "rho": rho,
        "sigma": sigma,
        "mu": mu,
        "hurdle": hurdle,
        "M_runs": M,
        "B_resamples": B,
        "seed": seed,
        "elapsed_seconds": elapsed_s,
        "hac_rejection_pct": hac_rate,
        "hac_se_mc_pct": se_hac_mc,
        "hac_ci95_pct": list(ci_hac),
        "boot_rejection_pct": boot_rate,
        "boot_se_mc_pct": se_boot_mc,
        "boot_ci95_pct": list(ci_boot),
        "joint_rejection_pct": joint_rate,
        "joint_se_mc_pct": se_joint_mc,
        "joint_ci95_pct": list(ci_joint),
        "calibration_status": calibration_status
    }


def run_full_calibration_suite() -> list:
    """Run calibration across N in [30, 60, 90], rho in [0, 0.2, 0.4], mu in [0, 10, 15, 25]."""
    Ns = [30, 60, 90]
    rhos = [0.00, 0.20, 0.40]
    mus = [0.0, 10.0, 15.0, 25.0]
    sigma = 50.0

    results = []
    base_seed = 20261025
    scenario_idx = 0
    for N in Ns:
        for rho in rhos:
            for mu in mus:
                seed = base_seed + scenario_idx
                scenario_idx += 1
                res = simulate_joint_calibration_scenario(
                    N=N, rho=rho, sigma=sigma, mu=mu, hurdle=10.0,
                    M=1000, B=1000, seed=seed
                )
                results.append(res)
    return results


if __name__ == "__main__":
    print("Testing exact AR(1) variance for N=30, rho=0.20, sigma=50.0...")
    ex = exact_ar1_variance(30, 0.20, 50.0)
    print(f"Exact Var: {ex['var_exact']:.6f}, Asymp Var: {ex['var_asymp']:.6f}, Rel Error: {ex['rel_error_var_pct']:.4f}%")
    pow_stat = compute_analytical_power(30, 0.20, 50.0, 15.0, hurdle=10.0)
    print(f"Exact Power: {pow_stat['power_exact_pct']:.4f}%, Asymp Power: {pow_stat['power_asymp_pct']:.4f}%")
