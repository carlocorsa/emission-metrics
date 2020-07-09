# Third party imports
import numpy as np

# Local application imports
from utils import stats, constants

# Index of HadGEM3 - model used for SO2 simulations
HadGEM3 = 3


def get_mm_scaling(pollutant):
    """Get multi-model scaling factors for temperature, the radiative forcing and
    the climate sensitivity. Also computes the uncertainty associated with the
    climate sensitivity (used for the uncertainty propagation).

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    Returns
    -------
    temp_scaling: float
        The scaling factor for the temperature.

    rf_scaling: float
        The scaling factor for the radiative forcing.

    c_scaling: float
        The scaling factor for the climate sensitivity.

    c_scaling_error: float
        The uncertainty associated with the climate
        sensitivity scaling factor.

    c_scaling_prop: float
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    # Temperature, radiative forcing and precipitation variations between
    # CO2 perturbation and control experiments in the different PDRMIP models
    co2_dtemp = [2.70, 1.49, 2.73, 3.73, 2.15, 3.17, 2.47, 2.06, 1.46]
    co2_drf = [3.57, 4.06, 3.37, 3.64, 4.14, 3.62, 4.06, 3.50, 3.62]

    # Compute temperature stats (average, standard deviation and
    # ensemble standard deviation) for CO2 experiments
    co2_dtemp_avg, co2_dtemp_std, co2_dtemp_std_err = stats.compute_stats(co2_dtemp)

    # Compute radiative forcing stats CO2 experiments
    co2_drf_avg, co2_drf_std, co2_drf_std_err = stats.compute_stats(co2_drf)

    if pollutant == 'BC':
        dtemp = [1.31, 0.398, 1.66, 0.697, np.nan, 0.381, 0.166, 0.673, 0.159]
        drf = [1.55, 1.23, 1.19, 0.70, np.nan, 0.77, 0.41, 1.40, 0.63]

    # TODO: these values apply to SO4, check for SO2
    if pollutant == 'SO2':
        dtemp = [-2.71, -0.93, -2.72, -6.62, np.nan, -1.47, -1.12, -1.65, -1.17]
        drf = [-3.25, -2.79, -4.02, -8.26, np.nan, -2.04, -2.11, -3.79, -2.77]

    if pollutant == 'CO2':
        dtemp = [2.70, 1.49, 2.73, 3.73, 2.15, 3.17, 2.47, 2.06, 1.46]
        drf = [3.57, 4.06, 3.37, 3.64, 4.14, 3.62, 4.06, 3.50, 3.62]

    if pollutant == 'CH4':
        dtemp = [0.60, 0.42, 0.80, 1.20, 0.44, 1.07, 0.52, 0.67, 0.30]
        drf = [1.36, 1.34, 0.98, 1.39, 0.95, 1.27, 0.86, 1.24, 0.78]

    # Compute radiative forcing stats for `pollutant` experiments
    drf_avg, drf_std, drf_std_err = stats.compute_stats(drf)

    # Compute temperature stats for `pollutant` experiments
    dtemp_avg, dtemp_std, dtemp_std_err = stats.compute_stats(dtemp)

    # Compute climate sensitivity, radiative forcing and temperature scaling factors
    c_scaling = (dtemp_avg / co2_dtemp_avg) / (drf_avg / co2_drf_avg)
    rf_scaling = drf_avg / drf[HadGEM3]
    temp_scaling = dtemp_avg / dtemp[HadGEM3]

    # Compute climate sensitivity scaling factor for error propagation
    c_scaling_prop = (dtemp_avg / co2_dtemp_avg) * co2_drf_avg

    # Compute uncertainty in climate sensitivity scaling factor
    c_scaling_std_err = np.abs(c_scaling) * np.sqrt(
        (dtemp_std_err/dtemp_avg)**2 +
        (co2_dtemp_std_err/co2_dtemp_avg)**2 +
        (co2_drf_std_err/co2_drf_avg)**2 +
        (drf_std_err/drf_avg)**2
    )

    return temp_scaling, rf_scaling, c_scaling, c_scaling_std_err, c_scaling_prop
