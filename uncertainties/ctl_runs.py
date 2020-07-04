# Standard library imports
import os

# Third party imports
import pandas as pd
import numpy as np
from netCDF4 import Dataset

# Local application imports
from simulations import loading, regions

# Local paths
DATA_PATH = "data/ctl/"

# Number of control simulations
N = 6


def get_model_variability(response_regions):
    """Get temperature and precipitation averages from different simulations
    and corresponding standard deviations.

    Parameters
    ----------
    response_regions: list of str
        Names of the response regions in which to
        measure model variability.

    Returns
    -------
    region_temp_df: DataFrame
        DataFrame with regional and global model temperature
        averages and corresponding standard deviations.

    region_precip_df: DataFrame
        DataFrame with regional and global model precipitation
        averages and corresponding standard deviations.
    """

    # Load grid cell areas
    areas = loading.load_grid_areas()

    # Create DataFrames filled with NaN values
    n_regions = len(response_regions)

    temp_avg = [[np.nan for _ in range(N)] for __ in range(n_regions)]
    precip_avg = [[np.nan for _ in range(N)] for __ in range(n_regions)]

    columns = ['Model1', 'Model2', 'Model3', 'Model4', 'Model5', 'Model6']
    region_temp_df = pd.DataFrame(index=response_regions, columns=columns)
    region_precip_df = pd.DataFrame(index=response_regions, columns=columns)
    
    for i in range(N):
        # Load control files
        file_name = '{}_150.nc'.format(i)
        data = Dataset(os.path.join(DATA_PATH, file_name), mode='r')
        temp = data.variables['temp'][0][0]
        precip = data.variables['precip'][0][0]

        # Loop through relevant regions
        for j in range(n_regions):
            region = response_regions[j]

            # Compute average regional temperature and precipitation
            region_mask = regions.get_region_mask(region)
            region_masked_area = areas * region_mask
            total_area = np.ma.sum(np.ma.sum(region_masked_area))
            
            region_temp = temp * region_mask
            region_temp_avg = (np.ma.sum(np.ma.sum(region_temp * region_masked_area)) / total_area)
            temp_avg[j][i] = region_temp_avg

            region_precip = precip * region_mask
            region_precip_avg = (np.ma.sum(np.ma.sum(region_precip * region_masked_area)) / total_area)
            precip_avg[j][i] = region_precip_avg

    for i, column in enumerate(region_temp_df.columns):
        region_temp_df[column] = [avg[i] for avg in temp_avg]
        region_precip_df[column] = [avg[i] for avg in precip_avg]
    
    region_temp_df['avg'] = region_temp_df[columns].mean(axis=1)
    region_temp_df['std'] = region_temp_df[columns].std(axis=1)
    region_temp_df['std_err'] = region_temp_df[columns].std(axis=1) / np.sqrt(N)

    region_precip_df['avg'] = region_precip_df[columns].mean(axis=1)
    region_precip_df['std'] = region_precip_df[columns].std(axis=1)
    region_precip_df['std_err'] = region_precip_df[columns].std(axis=1) / np.sqrt(N)
      
    return region_temp_df, region_precip_df
