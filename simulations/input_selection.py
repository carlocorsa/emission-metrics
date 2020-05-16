import os
import json
import numpy as np

# Repo paths
PDRMIP_PATH = "../data/pdrmip/"


def select_emission_region(pollutant, region=None):
    """Select emission region and returns corresponding effective radiative forcing.

    Parameters
    ----------
    pollutant: str
        Name of pollutant. Can be any of the following:
        'SO2', 'BC', 'CO2', 'CH4'.

    region: int or None (default=None)
        The integer corresponding to an emission region, if specified.

        For SO2, CO2 and CH4, an integer between 1 and 6:
        1: Northern Hemisphere Mid Latitudes
        2: North America
        3: China
        4: East Asia
        5: India
        6: Europe

        For BC, an integer between 1 and 2:
        1: 'Global'
        2: 'Asia'

        If None, the user will need to choose the
        emission region interactively.

    Returns
    -------
    region_name: str
        Name of the selected emission region.

    region_erf_t: float
         Average difference in the effective radiative forcing
         between the perturbed and the control experiment
         for the selected emission region.

    region_erf_a:
         Average difference in the atmospheric component of the
         effective radiative forcing between the perturbed and
         the control experiment for the selected emission region.
    """

    with open(os.path.join(PDRMIP_PATH, 'PDRMIP_mean_dERFt.json')) as f:
        mean_erf_t_diff = json.load(f)
    with open(os.path.join(PDRMIP_PATH, 'PDRMIP_mean_dERFa.json')) as f:
        mean_erf_a_diff = json.load(f)

    emission_region_options = {
        1: 'NHML',
        2: 'US',
        3: 'China',
        4: 'EastAsia',
        5: 'India',
        6: 'Europe'
    }

    emission_region_options_bc = {
        1: 'Global',
        2: 'Asia'
    }

    if pollutant == 'SO2':
        erf_t = [0.906, 0.232, np.nan, 0.166, 0.101, 0.275]  # from HadGEM3 simulations
        fp = -0.4  # Kvalevag et al. (2013) used by Shine et al. (2015)
        erf_a = [i * fp for i in erf_t]

    elif pollutant == 'BC':
        erf_t = [
            np.mean([mean_erf_t_diff[k]['10xBC_'] for k, v in mean_erf_t_diff.items()
                     if '10xBC_' in mean_erf_t_diff[k].keys()]),
            np.mean([mean_erf_t_diff[k]['10xBCAsia'] for k, v in mean_erf_t_diff.items()
                     if '10xBCAsia' in mean_erf_t_diff[k].keys()])
        ]
        erf_a = [
            np.mean([mean_erf_a_diff[k]['10xBC_'] for k, v in mean_erf_a_diff.items()
                     if '10xBC_' in mean_erf_a_diff[k].keys()]),
            np.mean([mean_erf_a_diff[k]['10xBCAsia'] for k, v in mean_erf_a_diff.items()
                     if '10xBCAsia' in mean_erf_a_diff[k].keys()])
        ]

    # The effective radiative forcing is independent of the emission region for CO2 and CH4
    elif pollutant == 'CO2':
        erf_t = [np.mean([mean_erf_t_diff[k]['2xCO2'] for k, v in mean_erf_t_diff.items()])] * 6
        erf_a = [np.mean([mean_erf_a_diff[k]['2xCO2'] for k, v in mean_erf_a_diff.items()])] * 6

    elif pollutant == 'CH4':
        erf_t = [np.mean([mean_erf_t_diff[k]['3xCH4'] for k, v in mean_erf_t_diff.items()])] * 6
        erf_a = [np.mean([mean_erf_a_diff[k]['3xCH4'] for k, v in mean_erf_a_diff.items()])] * 6

    emission_region = 0
    if pollutant != 'BC':
        if not region:
            while 1 > emission_region or 6 < emission_region:
                try:
                    emission_region = int(input('Select an emission region (1-6):\n\n \
1: Northern Hemisphere Mid Latitudes\n \
2: North America\n \
3: China\n \
4: East Asia\n \
5: India\n \
6: Europe\n\n \
Your selection:  '))
                    if (1 > emission_region or 6 < emission_region) and emission_region % 1 == 0:
                        print('\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 6')
                except ValueError:
                    print('\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER')

            print(emission_region_options[emission_region])

        else:
            emission_region = region

        region_name = emission_region_options[emission_region]
        region_erf_t = erf_t[emission_region - 1]
        region_erf_a = erf_a[emission_region - 1]

        return region_name, region_erf_t, region_erf_a

    else:
        if not region:
            while 1 > emission_region or 2 < emission_region:
                try:
                    emission_region = int(input('Select an emission region (1-2):\n\n \
1: Global\n \
2: Asia\n\n \
Your selection:  '))
                    if (1 > emission_region or 2 < emission_region) and emission_region % 1 == 0:
                        print('\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 2')
                except ValueError:
                    print('\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER')

            print(emission_region_options_bc[emission_region])

        else:
            emission_region = region

        region_name = emission_region_options_bc[emission_region]
        region_erf_t = erf_t[emission_region - 1]
        region_erf_a = erf_a[emission_region - 1]

        return region_name, region_erf_t, region_erf_a
