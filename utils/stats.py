import numpy as np


def compute_stats(variable):
    """Compute average, standard deviation and
    standard error of `variable`."""

    avg = np.nanmean(variable)
    std = np.nanstd(variable, ddof=1)
    std_err = std / np.sqrt(np.count_nonzero(~np.isnan(variable)))

    return avg, std, std_err


def compute_ratio_std(avg_a, avg_b, std_a, std_b, cov):
    """Compute the standard deviation of the ratio of two variables.
    (https://en.wikipedia.org/wiki/Propagation_of_uncertainty)

    Parameters
    ----------
    avg_a: float
        Average of variable A.

    avg_b: float
        Average of variable B.

    std_a: float
        Standard deviation of variable A.

    std_b: float
        Standard deviation of variable B.

    cov: float
        Covariance between variables A and B.
    """

    ratio_std = abs(avg_a / avg_b) * np.sqrt(
        (std_a / avg_a) ** 2 +
        (std_b / avg_b) ** 2 +
        2 * cov / (avg_a * avg_b)
    )

    return ratio_std
