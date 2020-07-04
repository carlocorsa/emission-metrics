# Standard library imports
import os

# Third party imports
import numpy as np
from netCDF4 import Dataset
from scipy.io import readsav

# Local application imports
from utils import constants
from simulations import regions

DATA_PATH = "data/"


def get_file_paths(pollutant, emission_region):
    """Get the paths of the control and perturbation files for the
    selected pollutant and emission region.

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    emission_region: str
        The name of the pollutant emission region.
        For SO2, CO2 and CH4, one of the following options:
        - NHML
        - US
        - China
        - EastAsia
        - India
        - Europe

        For BC, one of the following options:
        - Global
        - Asia

    Returns
    -------
    ctl_path: str
        Path of the control file.

    pert_path: str
        Path of the perturbation file for the emission of
        `pollutant` from `emission_region`.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    if pollutant == 'SO2':
        ctl_path = os.path.join(DATA_PATH, "SO2/ctl_150year_avg.nc")
        pert_file = os.listdir(os.path.join(DATA_PATH, "SO2/No_SO2_{}/".format(emission_region)))[0]
        pert_path = os.path.join(DATA_PATH, "SO2/No_SO2_{}/".format(emission_region), pert_file)
    else:
        ctl_path = os.path.join(DATA_PATH, "pdrmip/regridded_files/base_mm_mean.nc")

    if pollutant == 'BC':
        if emission_region == 'Global':
            pert_path = os.path.join(DATA_PATH, "pdrmip/regridded_files/10xBC_mm_mean.nc")
        if emission_region == 'Asia':
            pert_path = os.path.join(DATA_PATH, "pdrmip/regridded_files/10xBCAsia_mm_mean.nc")

    elif pollutant == 'CO2':
        pert_path = os.path.join(DATA_PATH, "pdrmip/regridded_files/2xCO2_mm_mean.nc")
    elif pollutant == 'CH4':
        pert_path = os.path.join(DATA_PATH, "pdrmip/regridded_files/3xCH4_mm_mean.nc")

    return ctl_path, pert_path


def load_grid_areas():
    """Load the area of the grid cells."""

    areas2d = readsav(os.path.join(DATA_PATH, "areas.sav"))
    areas = areas2d['areas2d']

    return areas


def load_climate_variables(pollutant, emission_region):
    """Load temperature and precipitation and compute
    differences between perturbation and control experiments.

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    emission_region: str
        The name of the pollutant emission region.
        For SO2, CO2 and CH4, one of the following options:
        - NHML
        - US
        - China
        - EastAsia
        - India
        - Europe

        For BC, one of the following options:
        - Global
        - Asia

    Returns
    -------
    grid_delta_temp: ndarray of shape (145, 192)
        Array with gridded temperature differences.

    grid_delta_precip: ndarray of shape (145, 192)
        Array with gridded precipitation differences.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    if pollutant == 'BC':
        assert emission_region in constants.BC_EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)
    else:
        assert emission_region in constants.EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)

    # Get control and perturbation file paths
    ctl_path, pert_path = get_file_paths(pollutant, emission_region)

    # Read netCDF files
    ctl_data = Dataset(ctl_path, mode='r')
    pert_data = Dataset(pert_path, mode='r')

    # Get temperature and precipitation variables
    temp = np.squeeze(ctl_data.variables['temp'])
    precip = np.squeeze(ctl_data.variables['precip'])
    pert_temp = np.squeeze(pert_data.variables['temp'])
    pert_precip = np.squeeze(pert_data.variables['precip'])

    # If precipitation unit is kg/m2/s convert it to mm/day
    if ctl_data.variables['precip'].units != 'mm/day':
        precip = precip * 86400
    if pert_data.variables['precip'].units != 'mm/day':
        pert_precip = pert_precip * 86400

    # Compute differences between perturbed and control run
    grid_delta_temp = pert_temp - temp
    grid_delta_precip = pert_precip - precip

    # Close datasets
    ctl_data.close()
    pert_data.close()

    return grid_delta_temp, grid_delta_precip


def load_emissions(pollutant, emission_region):
    """Get emissions for the specified pollutant and emission_region.

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    emission_region: str
        The name of the pollutant emission region.
        For SO2, CO2 and CH4, one of the following options:
        - NHML
        - US
        - China
        - EastAsia
        - India
        - Europe

        For BC, one of the following options:
        - Global
        - Asia

    Returns
    -------
    delta_emiss_mass: float
        Emission mass (Tg/yr) difference.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    # Load grid cell areas
    areas = load_grid_areas()

    if pollutant == 'SO2':
        # Get control and perturbation file paths
        ctl_path, pert_path = get_file_paths(pollutant, emission_region)

        # Read netCDF files
        ctl_data = Dataset(ctl_path, mode='r')
        pert_data = Dataset(pert_path, mode='r')

        # Load SO2 emissions
        ctl_so2_low = np.squeeze(ctl_data.variables['field569'])
        ctl_so2_high = np.squeeze(ctl_data.variables['field569_1'])
        ctl_so2 = ctl_so2_low + ctl_so2_high

        pert_so2_low = np.squeeze(pert_data.variables['field569'])
        pert_so2_high = np.squeeze(pert_data.variables['field569_1'])
        pert_so2 = pert_so2_low + pert_so2_high

        # Convert emissions from kg/m2/s to Tg/yr and
        # compute the mass released in each grid cell
        delta_so2 = areas * 2 * (3600 * 24 * 365 * 1e-9) * (pert_so2 - ctl_so2)

        # Compute the total emission mass
        delta_emiss_mass = np.ma.sum(np.ma.sum(delta_so2))

    elif pollutant == 'BC':
        # Load BC emissions
        emission_path = os.path.join(DATA_PATH, "pdrmip/emissions/regridded_aerocom_BC_emissions_2006.nc")
        emission_data = Dataset(emission_path, mode='r')
        bc_emissions = np.squeeze(emission_data.variables['emibc'])
        emission_data.close()

        # Get the emission difference (the factor 9 is because the experiments are 10xBC) from the emission region
        masked_delta_emissions = bc_emissions * regions.get_region_mask(emission_region) * 9

        # Convert emissions from kg/m2/s to Tg/yr and
        # compute the mass released in each grid cell
        masked_delta_emiss_mass = areas * masked_delta_emissions * 3600 * 24 * 365 * 1e-9

        # Compute the total emission mass
        delta_emiss_mass = np.ma.sum(np.ma.sum(masked_delta_emiss_mass))

    # TODO: add data source
    elif pollutant == 'CH4':
        delta_emiss_mass = 860.827

    elif pollutant == 'CO2':
        delta_emiss_mass = 2891000

    return delta_emiss_mass
