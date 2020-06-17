# Standard library imports
import os

# Third party imports
import numpy as np
from netCDF4 import Dataset
from scipy.io import readsav

# Local application imports
from rem.simulations import regions

DATA_PATH = "../data/"

# List of available pollutants
POLLUTANT_OPTIONS = ['SO2', 'BC', 'CO2', 'CH4']


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

    assert pollutant in POLLUTANT_OPTIONS, "{} is not an accepted pollutant".format(pollutant)

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


def get_bc_emissions(emission_region):
    """Load BC AeroCom (https://aerocom.met.no/) emissions
    for the specified `emission_region`."""

    # Load grid cell areas
    areas = load_grid_areas()

    # Load BC emissions
    emission_path = os.path.join(DATA_PATH, "pdrmip/emissions/regridded_aerocom_BC_emissions_2006.nc")
    emission_data = Dataset(emission_path, mode='r')
    bc_emissions = np.squeeze(emission_data.variables['emibc'])
    emission_data.close()

    # TODO: check whether emission region should always be Asia
    # Get the emission difference (the factor 9 is because the experiments are 10xBC) from the emission region
    masked_delta_emissions = bc_emissions * regions.get_region_mask(emission_region) * 9

    # Compute the mass released in each grid cell
    masked_delta_emission_mass = areas * masked_delta_emissions

    # Compute the total emission mass
    delta_emission_mass = np.ma.sum(np.ma.sum(masked_delta_emission_mass))

    return delta_emission_mass


def load_grid_areas():
    """Load the area of the grid cells."""

    areas2d = readsav(os.path.join(DATA_PATH, "areas.sav"))
    areas = areas2d['areas2d']

    return areas


def load_variables(pollutant, emission_region):
    """Load temperature, precipitation and emission and compute
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

    delta_emiss_mass: float
        Emission mass (Tg/yr) difference.
    """

    assert pollutant in POLLUTANT_OPTIONS, "{} is not an accepted pollutant".format(pollutant)

    # Load grid cell areas
    areas = load_grid_areas()

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

    if pollutant == 'SO2':

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
        delta_emiss_mass = get_bc_emissions(emission_region)

    # TODO: add data source
    elif pollutant == 'CH4':
        delta_emiss_mass = 860.827

    elif pollutant == 'CO2':
        delta_emiss_mass = 2891000

    ctl_data.close()
    pert_data.close()

    return grid_delta_temp, grid_delta_precip, delta_emiss_mass
