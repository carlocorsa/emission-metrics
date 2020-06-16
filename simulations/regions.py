# Standard library imports
import os

# Third party imports
import numpy as np
from netCDF4 import Dataset

DATA_PATH = "../data/ctl/ctl_0/"


def get_region_mask(region):
    """Get the grid mask for the specified region."""

    path = os.path.join(DATA_PATH, "xizka_150year_avg.nc")
    data = Dataset(path, mode='r')

    lat = data.variables['latitude'][:]
    lon = data.variables['longitude'][:]

    data.close()

    if region == 'Global':
        lon_min = 0.
        lon_max = 360.
        lat_min = -90.
        lat_max = 90.

    elif region == 'Tropics':
        lon_min = 0.
        lon_max = 360.
        lat_min = -30.
        lat_max = 30.

    elif region == 'NHML':
        lon_min = 0.
        lon_max = 360.
        lat_min = 30.
        lat_max = 60.

    elif region == 'NHHL':
        lon_min = 0.
        lon_max = 360.
        lat_min = 60.
        lat_max = 90.

    elif region == 'SHML':
        lon_min = 0.
        lon_max = 360.
        lat_min = -60.
        lat_max = -30.

    elif region == 'SHHL':
        lon_min = 0.
        lon_max = 360.
        lat_min = -90.
        lat_max = -60.

    elif region == 'Europe':
        lon_min = -10.
        lon_max = 40.
        lat_min = 37.
        lat_max = 70.

    elif region == 'US':
        lon_min = 235.
        lon_max = 290.
        lat_min = 30.
        lat_max = 50.

    elif region == 'China':
        lon_min = 80.
        lon_max = 120.
        lat_min = 20.
        lat_max = 50.

    elif region == 'East Asia':
        lon_min = 105.
        lon_max = 145.
        lat_min = 20.
        lat_max = 45.

    elif region == 'India':
        lon_min = 70.
        lon_max = 90.
        lat_min = 10.
        lat_max = 30.

    elif region == 'Sahel':
        lon_min = -17.
        lon_max = 38.
        lat_min = 9.
        lat_max = 19.

    elif region == 'Asia':
        lon_min = 60.
        lon_max = 140.
        lat_min = 10.
        lat_max = 50.

    else:
        print('Region not available or not existent')
        return

    # Create grid mask
    grid = [[0 for _j in range(192)] for _i in range(145)]
    ind = []
    for x in range(192):
        for y in range(145):
            if (lon[x] >= lon_min) and (lon[x] <= lon_max) and (lat[y] >= lat_min) and (lat[y] <= lat_max):
                grid[y][x] = 1
                ind.append(x+192*y)
              
    return np.int64(grid)
