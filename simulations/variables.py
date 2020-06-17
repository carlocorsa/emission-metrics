# Third party imports
import numpy as np

# Local application imports
from rem.simulations import loading, regions


def compute_variables(response_region, grid_delta_temp, grid_delta_precip):
    """Compute average regional and global temperature and precipitation
    variations between perturbation and control experiments.

    Parameters
    ----------
    response_region: str
        Name of the response region.

    grid_delta_temp: ndarray of shape (145, 192)
        Array with gridded temperature differences.

    grid_delta_precip: ndarray of shape (145, 192)
        Array with gridded precipitation differences.

    Returns
    -------
    rr_temp_avg: float
        Average regional temperature difference.

    temp_avg: float
        Global regional temperature difference.

    rr_precip_avg: float
        Average regional precipitation difference.

    precip_avg: float
        Global regional precipitation difference.
    """

    # Get grid cell areas and the response region (rr) mask
    areas = loading.load_grid_areas()
    rr_mask = regions.get_region_mask(response_region)

    # Get total area of the response region
    rr_masked_area = areas * rr_mask
    rr_area = np.ma.sum(np.ma.sum(rr_masked_area))

    # Compute the average regional (rr_temp_avg) and global (temp_avg) temperature difference
    rr_delta_temp = grid_delta_temp * rr_mask
    rr_temp_avg = np.ma.sum(np.ma.sum(rr_delta_temp * rr_masked_area)) / rr_area
    temp_avg = np.ma.sum(np.ma.sum(grid_delta_temp * areas)) / np.ma.sum(np.ma.sum(areas))

    # Compute the average regional (rr_precip_avg) and global (precip_avg) temperature difference
    rr_delta_precip = grid_delta_precip * rr_mask
    rr_precip_avg = np.ma.sum(np.ma.sum(rr_delta_precip * rr_masked_area)) / rr_area
    precip_avg = np.ma.sum(np.ma.sum(grid_delta_precip * areas)) / np.ma.sum(np.ma.sum(areas))

    return rr_temp_avg, temp_avg, rr_precip_avg, precip_avg
