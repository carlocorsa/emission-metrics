import numpy as np
import os
import json
from netCDF4 import Dataset

# Local application imports
from rem.simulations import loading
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

    # Load grid cell areas
    areas = loading.load_grid_areas()
    total_area = np.ma.sum(np.ma.sum(areas))

    # Load control and perturbation experiments
    path = os.path.join(DATA_PATH, "SO2/TOA_RF_tseries/")
    ctl_path = os.path.join(path, "HadGEM3_Atmos_Control_25yr_RF_tseries.nc")
    pert_path = os.path.join(path, "HadGEM3_Atmos_noSO2_{}_25yr_RF_tseries.nc".format(emission_region))

    ctl = Dataset(ctl_path, mode='r')
    pert = Dataset(pert_path, mode='r')

    # Compute regional radiative forcing
    ctl_rf = ctl.variables['field200'][:] - (ctl.variables['field201'][:] + ctl.variables['olr'][:])
    pert_rf = pert.variables['field200'][:] - (pert.variables['field201'][:] + pert.variables['olr'][:])

    # Computer global radiative forcing
    ctl_rf_glo = np.squeeze(np.sum(np.sum(ctl_rf * areas, axis=3), axis=2)) / total_area
    pert_rf_glo = np.squeeze(np.sum(np.sum(pert_rf * areas, axis=3), axis=2)) / total_area

    # Compute radiative forcing stats
    ctl_rf_avg, ctl_rf_std, ctl_rf_std_err = stats.compute_stats(ctl_rf_glo)
    pert_rf_avg, pert_rf_std, pert_rf_std_err = stats.compute_stats(pert_rf_glo)

    # Compute covariance of control and perturbation experiments
    ctl_pert_rf_cov = stats.compute_covariance(ctl_rf_glo, pert_rf_glo, std_err=True)

    # Compute average and standard deviation of control and perturbation difference
    ctl_pert_avg = ctl_rf_avg - pert_rf_avg
    ctl_pert_std_err = np.sqrt(ctl_rf_std_err**2 + pert_rf_std_err**2 - 2 * ctl_pert_rf_cov)

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
    ctl_pert_rf_avg: float
        Average ERF difference between perturbation and
        control experiments.

    ctl_pert_rf_std_err: float
        Standard error of the average ERF difference between
        perturbation and control experiments.

    ctl_pert_rfa_avg: float
        Average ERFa difference between perturbation and
        control experiments.

    ctl_pert_rfa_std_err: float
        Standard error of the average ERFa difference between
        perturbation and control experiments.
    """

    assert emission_region in constants.BC_EMISS_REGIONS, \
        "{} is not an accepted emission region for BC".format(emission_region)

    # Load change in radiative forcing
    with open(os.path.join(DATA_PATH, 'pdrmip/PDRMIP_mean_dERFt.json')) as f:
        mean_derf_t = json.load(f)
    with open(os.path.join(DATA_PATH, 'pdrmip/PDRMIP_mean_dERFa.json')) as f:
        mean_derf_a = json.load(f)

    if emission_region == 'Global':
        n_exps = len([mean_derf_t[k]['10xBC_'] for k, v in mean_derf_t.items() if '10xBC_' in mean_derf_t[k].keys()])

        ctl_pert_rf_avg = np.mean(
            [mean_derf_t[k]['10xBC_'] for k, v in mean_derf_t.items() if '10xBC_' in mean_derf_t[k].keys()]
        )
        ctl_pert_rf_std = np.std(
            [mean_derf_t[k]['10xBC_'] for k, v in mean_derf_t.items() if '10xBC_' in mean_derf_t[k].keys()]
        )
        ctl_pert_rfa_avg = np.mean(
            [mean_derf_a[k]['10xBC_'] for k, v in mean_derf_a.items() if '10xBC_' in mean_derf_a[k].keys()]
        )
        ctl_pert_rfa_std = np.std(
            [mean_derf_a[k]['10xBC_'] for k, v in mean_derf_a.items() if '10xBC_' in mean_derf_a[k].keys()]
        )

    else:
        n_exps = len(
            [mean_derf_t[k]['10xBCAsia'] for k, v in mean_derf_t.items() if '10xBCAsia' in mean_derf_t[k].keys()]
        )

        ctl_pert_rf_avg = np.mean(
            [mean_derf_t[k]['10xBCAsia'] for k, v in mean_derf_t.items() if '10xBCAsia' in mean_derf_t[k].keys()]
        )
        ctl_pert_rf_std = np.std(
            [mean_derf_t[k]['10xBCAsia'] for k, v in mean_derf_t.items() if '10xBCAsia' in mean_derf_t[k].keys()]
        )
        ctl_pert_rfa_avg = np.mean(
            [mean_derf_a[k]['10xBCAsia'] for k, v in mean_derf_a.items() if '10xBCAsia' in mean_derf_a[k].keys()]
        )
        ctl_pert_rfa_std = np.std(
            [mean_derf_a[k]['10xBCAsia'] for k, v in mean_derf_a.items() if '10xBCAsia' in mean_derf_a[k].keys()]
        )

    ctl_pert_rf_std_err = ctl_pert_rf_std / np.sqrt(n_exps)
    ctl_pert_rfa_std_err = ctl_pert_rfa_std / np.sqrt(n_exps)

    return ctl_pert_rf_avg, ctl_pert_rf_std_err, ctl_pert_rfa_avg, ctl_pert_rfa_std_err
