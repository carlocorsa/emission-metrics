# Third party imports
import numpy as np

# Local application imports
from utils import constants
from simulations import loading, regions, input_selection, scaling


def compute_climate_variables(response_regions, grid_delta_temp, grid_delta_precip):
    """Compute average regional and global temperature and precipitation
    variations between perturbation and control experiments.

    Parameters
    ----------
    response_regions: list of str
        List with names of the response regions.

    grid_delta_temp: ndarray of shape (145, 192)
        Array with gridded temperature differences.

    grid_delta_precip: ndarray of shape (145, 192)
        Array with gridded precipitation differences.

    Returns
    -------
    rr_temp_avg: array of floats
        Array of average regional temperature differences.

    temp_avg: float
        Average global temperature differences.

    rr_precip_avg: array of floats
        Array of average regional precipitation differences.

    precip_avg: float
        Average global precipitation differences.
    """

    # Get grid cell areas and the response region (rr) mask
    areas = loading.load_grid_areas()

    # Compute the regional differences
    rr_temp_avg = []
    rr_precip_avg = []

    for rr in response_regions:
        # Get the response region (rr) mask
        rr_mask = regions.get_region_mask(rr)

        # Get total area of the response region
        rr_masked_area = areas * rr_mask
        rr_area = np.ma.sum(np.ma.sum(rr_masked_area))

        # Compute the average regional temperature difference
        rr_delta_temp = grid_delta_temp * rr_mask
        rr_temp_avg.append(np.ma.sum(np.ma.sum(rr_delta_temp * rr_masked_area)) / rr_area)

        # Compute the average regional precipitation difference
        rr_delta_precip = grid_delta_precip * rr_mask
        rr_precip_avg.append(np.ma.sum(np.ma.sum(rr_delta_precip * rr_masked_area)) / rr_area)

    # Compute the global temperature and precipitation differences
    temp_avg = np.ma.sum(np.ma.sum(grid_delta_temp * areas)) / np.ma.sum(np.ma.sum(areas))
    precip_avg = np.ma.sum(np.ma.sum(grid_delta_precip * areas)) / np.ma.sum(np.ma.sum(areas))

    return np.array(rr_temp_avg), temp_avg, np.array(rr_precip_avg), precip_avg


def compute_radiative_efficiency(pollutant, emission_region, response_regions):
    """Compute radiative efficiency change in `response_region` due to
    perturbation in emissions of `pollutant` from `emission_region`.

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

    response_regions: list of strings
        List with response region names.

    Returns
    -------
    rr_rad_eff: array of floats
        Change in regional radiative efficiency for all
        regions in `response_regions`.

    rad_eff: float
        Change in global radiative efficiency.

    rad_eff_a: float
        Change in atmospheric component of the
        global radiative efficiency.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    # Get the effective radiative forcing
    _, erf, erf_a = input_selection.select_emission_region(pollutant, emission_region)

    # Get the pollutant emission mass
    delta_emiss_mass = loading.load_emissions(pollutant, emission_region)

    # Get the gridded climate responses
    grid_delta_temp, grid_delta_precip = loading.load_climate_variables(pollutant, emission_region)

    # Compute average climate variables
    rr_temp_avg, temp_avg, rr_precip_avg, precip_avg = compute_climate_variables(
        response_regions, grid_delta_temp, grid_delta_precip
    )

    # Compute regional and global radiative efficiency for the different pollutants
    if pollutant == 'SO2':
        rr_rad_eff = ((erf * scaling.get_mm_scaling(pollutant, 'temperature')[1]) * (rr_temp_avg / temp_avg) /
                      (delta_emiss_mass * constants.SPECS[pollutant]['tau']))

        rad_eff = ((erf * scaling.get_mm_scaling(pollutant, 'temperature')[1]) /
                   (delta_emiss_mass * constants.SPECS[pollutant]['tau']))

        rad_eff_a = ((erf_a * scaling.get_mm_scaling(pollutant, 'temperature')[1]) /
                     (delta_emiss_mass * constants.SPECS[pollutant]['tau']))

    elif pollutant == 'CO2':
        rr_rad_eff = erf * (rr_temp_avg / temp_avg) / delta_emiss_mass

        rad_eff = erf / delta_emiss_mass

        rad_eff_a = erf_a / delta_emiss_mass

    else:
        rr_rad_eff = erf * (rr_temp_avg / temp_avg) / (delta_emiss_mass * constants.SPECS[pollutant]['tau'])

        rad_eff = erf / (delta_emiss_mass * constants.SPECS[pollutant]['tau'])

        rad_eff_a = erf_a / (delta_emiss_mass * constants.SPECS[pollutant]['tau'])

    return rr_rad_eff, rad_eff, rad_eff_a


def get_scaled_climate_sensitivity(pollutant):
    """Get the scaled climate sensitivity for `pollutant`."""

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    c_scaled = [
        constants.C1 * scaling.get_mm_scaling(pollutant, 'temperature')[2],
        constants.C2 * scaling.get_mm_scaling(pollutant, 'temperature')[2]
    ]

    return c_scaled
