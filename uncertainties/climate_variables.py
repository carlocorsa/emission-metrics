# Local application imports
from rem.simulations import input_selection
from rem.uncertainties import ctl_runs
from rem.utils import stats


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
                    reg_temp_avg[-1], glo_temp_avg, reg_temp_std_err[-1], glo_temp_std_err, reg_glo_temp_cov
                )
            )

            # Compute standard error of regional and global precipitation ratio
            precip_ratio_std_err.append(
                stats.compute_ratio_std(
                    reg_precip_avg[-1], glo_precip_avg, reg_precip_std_err[-1], glo_precip_std_err, reg_glo_precip_cov
                )
            )

    else:

        reg_temp_avg = temp_df.loc[response_region, 'avg']
        reg_temp_std_err = temp_df.loc[response_region, 'std_err']
        reg_glo_temp_cov = stats.compute_covariance(
            temp_df.loc[response_region][0:6], temp_df.loc['Global'][0:6], std_err=True
        )

        reg_precip_avg = precip_df.loc[response_region, 'avg']
        reg_precip_std_err = precip_df.loc[response_region, 'std_err']
        reg_glo_precip_cov = stats.compute_covariance(
            precip_df.loc[response_region][0:6], precip_df.loc['Global'][0:6], std_err=True
        )

        temp_ratio_std_err = stats.compute_ratio_std(
            reg_temp_avg, glo_temp_avg, reg_temp_std_err, glo_temp_std_err, reg_glo_temp_cov
        )
        precip_ratio_std_err = stats.compute_ratio_std(
            reg_precip_avg, glo_precip_avg, reg_precip_std_err, glo_precip_std_err, reg_glo_precip_cov
        )

    return reg_temp_avg, glo_temp_avg, temp_ratio_std_err, reg_precip_avg, glo_precip_avg, precip_ratio_std_err
