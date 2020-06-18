import numpy as np


def compute_stats(variable):
    """Compute average, standard deviation and
    ensemble standard deviation of `variable`."""

    avg = np.nanmean(variable)
    std = np.nanstd(variable)
    ens_std = std / np.sqrt(np.count_nonzero(~np.isnan(variable)))

    return avg, std, ens_std
