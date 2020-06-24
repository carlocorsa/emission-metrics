# Standard library imports
import os

# Third party imports
import numpy as np
import json
from netCDF4 import Dataset

# Local application imports
from rem.utils import stats, constants

# Local paths
DATA_PATH = "../data/"


def get_so2_regional_uncertainty(emission_region):
    """Get uncertainty in regional SO2 ERF.

    Parameters
    ----------
    emission_region: str
        The name of the emission region.
        Must be one of the following options:
        - NHML
        - US
        - China
        - EastAsia
        - India
        - Europe

    Returns
    -------
    ctl_pert_avg: float
        Average ERF difference between perturbation and
        control experiments.

    ctl_pert_std_err: float
        Standard error of the average ERF difference between
        perturbation and control experiments.
    """

    assert emission_region in constants.EMISS_REGIONS, \
        "{} is not an accepted emission region for SO2.".format(emission_region)

    # Load control and perturbation experiments
    path = os.path.join(DATA_PATH, 'SO2/TOA_RF_tseries/')
    ctl_path = os.path.join(path, 'HadGEM3_Atmos_Control_25yr_RF_tseries.nc')
    pert_path = os.path.join(path, 'HadGEM3_Atmos_noSO2_{}_25yr_RF_tseries.nc'.format(emission_region))

    ctl = Dataset(ctl_path, mode='r')
    pert = Dataset(pert_path, mode='r')

    # Compute regional radiative forcing
    ctl_erf = ctl.variables['field200'][:] - (ctl.variables['field201'][:] + ctl.variables['olr'][:])
    pert_erf = pert.variables['field200'][:] - (pert.variables['field201'][:] + pert.variables['olr'][:])

    # Compute radiative forcing stats
    ctl_erf_avg, ctl_erf_std, ctl_erf_std_err = stats.compute_stats(ctl_erf)
    pert_erf_avg, pert_erf_std, pert_erf_std_err = stats.compute_stats(pert_erf)

    # Compute covariance of control and perturbation experiments
    ctl_pert_erf_cov = stats.compute_covariance(ctl_erf, pert_erf, std_err=True)

    # Compute average and standard deviation of control and perturbation difference
    ctl_pert_avg = pert_erf_avg - ctl_erf_avg
    ctl_pert_std_err = np.sqrt(ctl_erf_std_err**2 + pert_erf_std_err**2 - 2 * ctl_pert_erf_cov)

    return ctl_pert_avg, ctl_pert_std_err


def get_bc_regional_uncertainty(emission_region):
    """Get uncertainty in regional SO2 ERF.

    Parameters
    ----------
    emission_region: str
        The name of the emission region.
        Must be one of the following options:
        - Global
        - Asia

    Returns
    -------
    ctl_pert_erf_avg: float
        Average ERF difference between perturbation and
        control experiments.

    ctl_pert_erf_std_err: float
        Standard error of the average ERF difference between
        perturbation and control experiments.

    ctl_pert_erfa_avg: float
        Average ERFa difference between perturbation and
        control experiments.

    ctl_pert_erfa_std_err: float
        Standard error of the average ERFa difference between
        perturbation and control experiments.
    """

    assert emission_region in constants.BC_EMISS_REGIONS, \
        "{} is not an accepted emission region for BC".format(emission_region)

    # Load change in radiative forcing
    with open(os.path.join(DATA_PATH, 'pdrmip/PDRMIP_mean_ERFt.json')) as f:
        mean_erf_t = json.load(f)
    with open(os.path.join(DATA_PATH, 'pdrmip/PDRMIP_mean_ERFa.json')) as f:
        mean_erf_a = json.load(f)

    # Remove model without BC experiments (MPI-ESM)
    mean_erf_t.pop('MPI-ESM', None)
    mean_erf_a.pop('MPI-ESM', None)

    # Select correct experiment name
    if emission_region == 'Global':
        pert_name = '10xBC_'
    else:
        pert_name = '10xBCAsia'

    # Load ERF for control and perturbation experiments
    ctl_erf = [mean_erf_t[k]['base'] for k, v in mean_erf_t.items() if 'base' in mean_erf_t[k].keys()]
    pert_erf = [mean_erf_t[k][pert_name] for k, v in mean_erf_t.items() if pert_name in mean_erf_t[k].keys()]

    # Load ERFa for control and perturbation experiments
    ctl_erfa = [mean_erf_a[k]['base'] for k, v in mean_erf_a.items() if 'base' in mean_erf_a[k].keys()]
    pert_erfa = [mean_erf_a[k][pert_name] for k, v in mean_erf_a.items() if pert_name in mean_erf_a[k].keys()]

    # Compute ERF stats
    ctl_erf_avg, ctl_erf_std, ctl_erf_std_err = stats.compute_stats(ctl_erf)
    pert_erf_avg, pert_erf_std, pert_erf_std_err = stats.compute_stats(pert_erf)

    # Compute ERFa stats
    ctl_erfa_avg, ctl_erfa_std, ctl_erfa_std_err = stats.compute_stats(ctl_erfa)
    pert_erfa_avg, pert_erfa_std, pert_erfa_std_err = stats.compute_stats(pert_erfa)

    # Compute covariance of control and perturbation experiments
    ctl_pert_erf_cov = stats.compute_covariance(ctl_erf, pert_erf, std_err=True)
    ctl_pert_erfa_cov = stats.compute_covariance(ctl_erfa, pert_erfa, std_err=True)

    # Compute ERF average and standard deviation of control and perturbation difference
    ctl_pert_erf_avg = pert_erf_avg - ctl_erf_avg
    ctl_pert_erf_std_err = np.sqrt(ctl_erf_std_err**2 + pert_erf_std_err**2 - 2 * ctl_pert_erf_cov)

    # Compute ERFa average and standard deviation of control and perturbation difference
    ctl_pert_erfa_avg = pert_erfa_avg - ctl_erfa_avg
    ctl_pert_erfa_std_err = np.sqrt(ctl_erfa_std_err**2 + pert_erfa_std_err**2 - 2 * ctl_pert_erfa_cov)

    return ctl_pert_erf_avg, ctl_pert_erf_std_err, ctl_pert_erfa_avg, ctl_pert_erfa_std_err


def get_global_uncertainty(pollutant):
    """Get uncertainty in global ERF.

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
    erf_avg: float
        Average ERF difference between perturbation and
        control experiments.

    erf_std_err: float
        Standard error of the average ERF difference between
        perturbation and control experiments.

    erfa_avg: float
        Average ERFa difference between perturbation and
        control experiments.

    erfa_std_err: float
        Standard error of the average ERFa difference between
        perturbation and control experiments.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    path = os.path.join(DATA_PATH, 'pdrmip/extracts/')

    ctl_file = 'HadGEM3_atmos_ctl_global_tseries_15.nc'

    if pollutant == 'SO2':
        pert_file = 'HadGEM3_atmos_5xSO4_global_tseries_15.nc'

    elif pollutant == 'CO2':
        pert_file = 'HadGEM3_atmos_2xCO2_global_tseries_15.nc'

    elif pollutant == 'CH4':
        pert_file = 'HadGEM3_atmos_3xCH4_global_tseries_15.nc'

    elif pollutant == 'BC':
        pert_file = 'HadGEM3_atmos_10xBC_global_tseries_15.nc'

    # Load data
    ctl = Dataset(os.path.join(path, ctl_file), mode='r')
    pert = Dataset(os.path.join(path, pert_file), mode='r')

    # Compute ERF
    ctl_erf = ctl.variables['field200'][:] - (ctl.variables['field201'][:] + ctl.variables['olr'][:])
    pert_erf = pert.variables['field200'][:] - (pert.variables['field201'][:] + pert.variables['olr'][:])

    # Compute atmospheric component of ERF
    ctl_erfa = ctl_erf - (ctl.variables['solar'][:] + ctl.variables['longwave'][:])
    pert_erfa = pert_erf - (pert.variables['solar'][:] + pert.variables['longwave'][:])

    # Compute ERF stats
    ctl_erf_avg, ctl_erf_std, ctl_erf_std_err = stats.compute_stats(ctl_erf)
    pert_erf_avg, pert_erf_std, pert_erf_std_err = stats.compute_stats(pert_erf)

    # Compute ERFa stats
    ctl_erfa_avg, ctl_erfa_std, ctl_erfa_std_err = stats.compute_stats(ctl_erfa)
    pert_erfa_avg, pert_erfa_std, pert_erfa_std_err = stats.compute_stats(pert_erfa)

    # Compute covariance of control and perturbation experiments
    ctl_pert_erf_cov = stats.compute_covariance(ctl_erf, pert_erf, std_err=True)
    ctl_pert_erfa_cov = stats.compute_covariance(ctl_erfa, pert_erfa, std_err=True)

    # Compute ERF average and standard deviation of control and perturbation difference
    ctl_pert_erf_avg = pert_erf_avg - ctl_erf_avg
    ctl_pert_erf_std_err = np.sqrt(ctl_erf_std_err**2 + pert_erf_std_err**2 - 2 * ctl_pert_erf_cov)

    # Compute ERFa average and standard deviation of control and perturbation difference
    ctl_pert_erfa_avg = pert_erfa_avg - ctl_erfa_avg
    ctl_pert_erfa_std_err = np.sqrt(ctl_erfa_std_err**2 + pert_erfa_std_err**2 - 2 * ctl_pert_erfa_cov)

    return ctl_pert_erf_avg, ctl_pert_erf_std_err, ctl_pert_erfa_avg, ctl_pert_erfa_std_err
