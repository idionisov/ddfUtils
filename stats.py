from typing import Union

import numpy as np
from scipy.optimize import root_scalar
from scipy.stats import beta, norm


def get_clopper_pearson_interval(
    passed: int,
    total: int,
    cl: float = 0.6826894921370859
) -> tuple:
    """
    Calculate Clopper-Pearson confidence interval for binomial proportion.

    Args:
        passed: Number of successes
        total: Total number of trials
        cl: Confidence level (default is 1-sigma)

    Returns:
        tuple: (efficiency, upper error, lower error)
    """
    efficiency = passed/total

    alpha = 1 - cl
    lower_bound = beta.ppf(alpha / 2, passed, total - passed + 1)
    upper_bound = beta.ppf(1 - alpha / 2, passed + 1, total - passed)

    return efficiency, abs(efficiency - upper_bound), abs(efficiency - lower_bound)




def get_bayesian_interval(
    passed:      Union[float, int],
    total:       Union[float, int],
    alpha_prior: float = 1,
    beta_prior:  float = 1,
    cl:          float = 0.6826894921370859
) -> tuple:
    """
    Calculate Bayesian confidence interval for binomial proportion.

    Args:
        passed: Number of successes
        total: Total number of trials
        alpha_prior: Prior alpha parameter for beta distribution
        beta_prior: Prior beta parameter for beta distribution
        cl: Confidence level (default is 1-sigma)

    Returns:
        tuple: (efficiency, upper error, lower error)
    """
    alpha_post = alpha_prior + passed
    beta_post = beta_prior + total - passed

    lower_bound = beta.ppf((1 - cl) / 2, alpha_post, beta_post)
    upper_bound = beta.ppf(1 - (1 - cl) / 2, alpha_post, beta_post)
    efficiency = passed/total

    return efficiency, abs(efficiency - upper_bound), abs(efficiency - lower_bound)



def get_eff_with_error(
    passed:      Union[int, float],
    total:       Union[int, float],
    stat_option:  str   = "Clopper Pearson",
    cl:          float = 0.6826894921370859
) -> tuple:
    """
    Calculate efficiency and errors using specified statistical method.

    Args:
        passed: Number of successes
        total: Total number of trials
        stat_option: Statistical method to use ('Clopper Pearson' or 'Bayesian')
        cl: Confidence level (default is 1-sigma)

    Returns:
        tuple: (efficiency, upper error, lower error)

    Raises:
        ValueError: If invalid statistical method is specified
    """
    stat_option = stat_option.lower()

    clopper_pearson_options = {"clopper_pearson", "kfcp", "clopper pearson",
                               "clopper-pearson", "clopper.pearson",
                               "clopper:pearson", "clopperpearson"}
    bayesian_options = {"bayesian", "kbbayesian"}
    allowed_options = clopper_pearson_options | bayesian_options  # Combine sets using union operator

    if stat_option in clopper_pearson_options:
        eff, deff_up, deff_low = get_clopper_pearson_interval(passed, total, cl=cl)
    elif stat_option in bayesian_options:  # Use bayesian_options directly here
        eff, deff_up, deff_low = get_bayesian_interval(passed, total, cl=cl)
    else:
        raise ValueError(f"Invalid statistic option '{stat_option}'! Allowed options are: {', '.join(allowed_options)}")

    return eff, deff_up, deff_low


def get_systematic_var_chi2_method(x, stat_vars, sys_vars):
    x = np.asarray(x)
    N = len(x)
    stat_vars = np.asarray(stat_vars)
    sys_vars = np.asarray(sys_vars)

    xVar = stat_vars + sys_vars


    def getChi2(s):
        if s < 0:
            return np.inf
        varTotal = xVar + s**2
        weights = 1 / varTotal
        xHat = np.sum(x * weights) / np.sum(weights)
        return np.sum((x - xHat)**2 / varTotal) - (N - 1)


    sMax = np.std(x) * 10 + 0.01
    chiLow = getChi2(1e-10)
    chiHigh = getChi2(sMax)

    if chiLow * chiHigh > 0:
        return 0.0

    result = root_scalar(getChi2, bracket=[1e-10, sMax], method='brentq')
    if not result.converged:
        raise RuntimeError("Root finding did not converge.")

    return result.root**2
