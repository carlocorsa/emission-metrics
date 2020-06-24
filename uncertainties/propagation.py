import numpy as np
import pandas as pd

# Local application imports
from rem.simulations import input_selection, scaling
from rem.uncertainties import ctl_runs, erf
from rem.utils import stats, constants


def get_climate_stats(response_region):
    """Get regional and global temperature and precipitation stats.

    Parameters
    ----------
    response_region: str
        Name of the response region.
        If response_region='All regions', stats will be
        returned for all response regions.

    Returns
    -------
    reg_temp_avg: float or list
        Regional average temperature or list of regional average
        temperatures if response_region='All regions.

    glo_temp_avg: float
        Global average temperature.

    temp_ratio_std_err: float or list
        Standard error of the ratio between regional and global average temperatures
        list of standard errors if response_region='All regions.

    reg_precip_avg: float or list
        Regional average precipitation or list of regional average
        precipitations if response_region='All regions.

    glo_precip_avg: float
        Global average precipitation.

    precip_ratio_std_err: float or list
        Standard error of the ratio between regional and global average precipitations
        or list of standard errors if response_region='All regions.
    """

    if isinstance(response_region, list):
        response_region = 'All regions'

    # Get temperature and precipitation intermodel variability
    temp_df, precip_df = ctl_runs.get_model_variability(response_region)

    glo_temp_avg = temp_df.loc['Global', 'avg']
    glo_temp_std_err = temp_df.loc['Global', 'std_err']
    glo_precip_avg = precip_df.loc['Global', 'avg']
    glo_precip_std_err = precip_df.loc['Global', 'std_err']

    if response_region == 'All regions':

        region_names = input_selection.get_response_regions()
        n_regions = len(region_names)

        reg_temp_avg = []
        reg_temp_std_err = []
        temp_ratio_std_err = []
        reg_precip_avg = []
        reg_precip_std_err = []
        precip_ratio_std_err = []

        for i in range(n_regions):

            # Compute regional temperature average, standard error and covariance with global temperature
            reg_temp_avg.append(temp_df.loc[region_names[i], 'avg'])
            reg_temp_std_err.append(temp_df.loc[region_names[i], 'std_err'])
            reg_glo_temp_cov = stats.compute_covariance(
                temp_df.loc[region_names[i]][0:6], temp_df.loc['Global'][0:6], std_err=True
            )

            # Compute regional precipitation average, standard error and covariance with global precipitation
            reg_precip_avg.append(precip_df.loc[region_names[i], 'avg'])
            reg_precip_std_err.append(precip_df.loc[region_names[i], 'std_err'])
            reg_glo_precip_cov = stats.compute_covariance(
                precip_df.loc[region_names[i]][0:6], precip_df.loc['Global'][0:6], std_err=True
            )

            # Compute standard error of regional and global temperature ratio
            temp_ratio_std_err.append(
                stats.compute_ratio_std(
                    reg_temp_avg, glo_temp_avg, reg_temp_std_err, glo_temp_std_err, reg_glo_temp_cov
                )
            )

            # Compute standard error of regional and global precipitation ratio
            precip_ratio_std_err.append(
                stats.compute_ratio_std(
                    reg_precip_avg, glo_precip_avg, reg_precip_std_err, glo_precip_std_err, reg_glo_precip_cov
                )
            )

    else:

        reg_temp_avg = temp_df.loc[response_region, 'avg']
        reg_temp_std_err = temp_df.loc[response_region, 'std_err']
        reg_glo_temp_cov = stats.compute_covariance(
            temp_df.loc['Europe'][0:6], temp_df.loc['Global'][0:6], std_err=True
        )

        reg_precip_avg = precip_df.loc[response_region, 'avg']
        reg_precip_std_err = precip_df.loc[response_region, 'std_err']
        reg_glo_precip_cov = stats.compute_covariance(
            precip_df.loc['Europe'][0:6], precip_df.loc['Global'][0:6], std_err=True
        )

        temp_ratio_std_err = stats.compute_ratio_std(
            reg_temp_avg, glo_temp_avg, reg_temp_std_err, glo_temp_std_err, reg_glo_temp_cov
        )
        precip_ratio_std_err = stats.compute_ratio_std(
            reg_precip_avg, glo_precip_avg, reg_precip_std_err, glo_precip_std_err, reg_glo_precip_cov
        )

    return reg_temp_avg, glo_temp_avg, temp_ratio_std_err, reg_precip_avg, glo_precip_avg, precip_ratio_std_err


def error_prop(pollutant, k, fp, opath, gpath, response_region, emission_region):

    k_std = constants.SPECS[pollutant]['k_std']

    # Get temperature and precipitation stats
    reg_temp_avg, glo_temp_avg, temp_ratio_std_err, \
        reg_precip_avg, glo_precip_avg, precip_ratio_std_err = get_climate_stats(response_region)

    # Get ERF regional uncertainties
    if pollutant == 'CO2' or pollutant == 'CH4':
        reg_erf_avg = 1
        reg_erf_std_err = 0
        reg_erfa_avg = 1
        reg_erfa_std_err = 0

    elif pollutant == 'SO2':
        reg_erf_avg, reg_erf_std_err = erf.get_so2_regional_uncertainty(opath, gpath, pollutant, emission_region)
        reg_erfa_avg = fp * reg_erf_avg
        reg_erfa_std_err = np.abs(fp) * reg_erf_std_err

    else:
        reg_erf_avg, reg_erf_std_err, reg_erfa_avg, reg_erfa_std_err = erf.get_bc_regional_uncertainty(emission_region)

    # Get ERF global uncertainties
    glo_erf_avg, glo_erf_std_err, glo_erfa_avg, glo_erfa_std_err = erf.get_global_uncertainty(pollutant)

    # Get uncertainty in scaling factor of climate sensitivity
    c_scaling_avg, c_scaling_std_err = scaling.get_mm_scaling(pollutant, 'temperature')[2:4]

    if response_region == 'All regions':

        artp_total_std = []
        slow_arpp_total_std = []
        fast_arpp_total_std = []
        for i in range(input_selection.select_response_region('len')):

            # The following needs to be multiplied by the total function to obtain the final uncertainty
            artp_total_std.append(
                np.sqrt(
                    (reg_erf_std_err / reg_erf_avg) ** 2 +
                    (glo_erf_std_err / glo_erf_avg) ** 2 +
                    (temp_ratio_std_err[i] / (reg_temp_avg[i] / glo_temp_avg)) ** 2 +
                    (c_scaling_std_err / c_scaling_avg) ** 2
                )
            )

            slow_arpp_total_std.append(
                np.sqrt(
                    (reg_erf_std_err / reg_erf_avg) ** 2 +
                    (glo_erf_std_err / glo_erf_avg) ** 2 +
                    (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2 +
                    (c_scaling_std_err / c_scaling_avg) ** 2 +
                    (k_std / k) ** 2
                )
            )

            fast_arpp_total_std.append(
                np.sqrt(
                    (reg_erfa_std_err / reg_erfa_avg) ** 2 +
                    (glo_erfa_std_err / glo_erfa_avg) ** 2 +
                    (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2
                )
            )

    else:

        # The following needs to be multiplied by the total function to obtain the final uncertainty
        artp_total_std = np.sqrt(
            (reg_erf_std_err / reg_erf_avg) ** 2 +
            (glo_erf_std_err / glo_erf_avg) ** 2 +
            (temp_ratio_std_err / (reg_temp_avg / glo_temp_avg)) ** 2 +
            (c_scaling_std_err / c_scaling_avg) ** 2
        )

        slow_arpp_total_std = np.sqrt(
            (reg_erf_std_err / reg_erf_avg) ** 2 +
            (glo_erf_std_err / glo_erf_avg) ** 2 +
            (precip_ratio_std_err / (reg_precip_avg / glo_precip_avg)) ** 2 +
            (c_scaling_std_err / c_scaling_avg) ** 2 +
            (k_std / k) ** 2
        )

        fast_arpp_total_std = np.sqrt(
            (reg_erfa_std_err / reg_erfa_avg) ** 2 +
            (glo_erfa_std_err / glo_erfa_avg) ** 2 +
            (precip_ratio_std_err / (reg_precip_avg / glo_precip_avg)) ** 2
        )

    if isinstance(artp_total_std, pd.Series):
        artp_total_std = artp_total_std.tolist()
    if isinstance(slow_arpp_total_std, pd.Series):
        slow_arpp_total_std = slow_arpp_total_std.tolist()
    if isinstance(fast_arpp_total_std, pd.Series):
        fast_arpp_total_std = fast_arpp_total_std.tolist()

    return artp_total_std, slow_arpp_total_std, fast_arpp_total_std

