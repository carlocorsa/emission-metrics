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


def compute_covariance(var_a, var_b, std_err=False):
    """Compute covariance between variable A and variable B using Numpy function.
    If `std_err` is True, compute the covariance using the standard error instead
    of the standard deviation.

    Parameters
    ----------
    var_a: array-like
        Variable A.

    var_b: array-like
        Variable B.

    std_err: boolean (default=False)
        If True, compute the covariance using the standard error.
        If False, compute the covariance using the standard deviation.

    Return
    ------
    cov_ab: float
        Covariance between variable A and variable B.
    """

    cov_ab = np.cov(var_a, var_b, ddof=1)[0][1]

    if std_err:
        cov_ab = cov_ab / np.sqrt(np.count_nonzero(~np.isnan(var_a)) * np.count_nonzero(~np.isnan(var_b)))

    return cov_ab
