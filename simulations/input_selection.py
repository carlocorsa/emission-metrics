# Standard library imports
import os

# Third party imports
import json
import numpy as np

# Local application imports
from utils import constants

# Local paths
PDRMIP_PATH = "data/pdrmip/"

# Response regions dictionary
RESPONSE_REGION_OPTIONS = {
    1: 'Global',
    2: 'Tropics',
    3: 'NHML',
    4: 'NHHL',
    5: 'SHML',
    6: 'SHHL',
    7: 'Europe',
    8: 'US',
    9: 'China',
    10: 'East Asia',
    11: 'India',
    12: 'Sahel',
    13: 'All Regions'
}

# Emission scenarios dictionary
SCENARIO_OPTIONS = {
    1: 'sustained',
    2: 'linear',
    3: 'quadratic'
}


def select_emission_region(pollutant, region=None):
    """Select emission region and returns corresponding effective radiative forcing.

    Parameters
    ----------
    pollutant: str
        Name of pollutant. Can be any of the following:
        'SO2', 'BC', 'CO2', 'CH4'.

    region: str or None (default=None)
        The name of emission region, if specified.

        For SO2, CO2 and CH4, must be one of the following options:
        - Northern Hemisphere Mid Latitudes
        - North America
        - China
        - East Asia
        - India
        - Europe

        For BC, must be one of the following options:
        - Global
        - Asia

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

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    with open(os.path.join(PDRMIP_PATH, "PDRMIP_mean_dERFt.json")) as f:
        mean_delta_erf_t = json.load(f)
    with open(os.path.join(PDRMIP_PATH, "PDRMIP_mean_dERFa.json")) as f:
        mean_delta_erf_a = json.load(f)

    emission_region_options = {
        1: 'NHML',
        2: 'US',
        3: 'China',
        4: 'EastAsia',
        5: 'India',
        6: 'Europe'
    }

    bc_emission_region_options = {
        1: 'Global',
        2: 'Asia'
    }

    if pollutant == 'SO2':
        erf_t = [0.906, 0.232, np.nan, 0.166, 0.101, 0.275]  # from HadGEM3 simulations
        fp = -0.4  # Kvalevag et al. (2013) used by Shine et al. (2015)
        erf_a = [i * fp for i in erf_t]

    elif pollutant == 'BC':
        erf_t = [
            np.mean([mean_delta_erf_t[k]['10xBC_'] for k, v in mean_delta_erf_t.items()
                     if '10xBC_' in mean_delta_erf_t[k].keys()]),
            np.mean([mean_delta_erf_t[k]['10xBCAsia'] for k, v in mean_delta_erf_t.items()
                     if '10xBCAsia' in mean_delta_erf_t[k].keys()])
        ]
        erf_a = [
            np.mean([mean_delta_erf_a[k]['10xBC_'] for k, v in mean_delta_erf_a.items()
                     if '10xBC_' in mean_delta_erf_a[k].keys()]),
            np.mean([mean_delta_erf_a[k]['10xBCAsia'] for k, v in mean_delta_erf_a.items()
                     if '10xBCAsia' in mean_delta_erf_a[k].keys()])
        ]

    # The effective radiative forcing is independent of the emission region for CO2 and CH4
    elif pollutant == 'CO2':
        erf_t = np.mean([mean_delta_erf_t[k]['2xCO2'] for k, v in mean_delta_erf_t.items()])
        erf_a = np.mean([mean_delta_erf_a[k]['2xCO2'] for k, v in mean_delta_erf_a.items()])

    elif pollutant == 'CH4':
        erf_t = np.mean([mean_delta_erf_t[k]['3xCH4'] for k, v in mean_delta_erf_t.items()])
        erf_a = np.mean([mean_delta_erf_a[k]['3xCH4'] for k, v in mean_delta_erf_a.items()])

    emission_region = 0
    if pollutant == 'SO2':
        if region is None:
            while 1 > emission_region or 6 < emission_region:
                try:
                    emission_region = int(input(
                        "Select an emission region (1-6):\n\n"
                        "1: Northern Hemisphere Mid Latitudes\n"
                        "2: North America\n"
                        "3: China\n"
                        "4: East Asia\n"
                        "5: India\n"
                        "6: Europe\n\n"
                        "Your selection:  "
                    ))
                    if (1 > emission_region or 6 < emission_region) and emission_region % 1 == 0:
                        print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 6")
                except ValueError:
                    print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

            region_name = emission_region_options[emission_region]
            region_erf_t = erf_t[emission_region - 1]
            region_erf_a = erf_a[emission_region - 1]

            print(emission_region_options[emission_region])

        else:
            assert region in constants.SO2_EMISS_REGIONS, \
                "region for {} must be one of {}".format(pollutant, constants.SO2_EMISS_REGIONS)

            region_name = region
            region_id = next(k for k, v in emission_region_options.items() if v == region_name)
            region_erf_t = erf_t[region_id - 1]
            region_erf_a = erf_a[region_id - 1]

        return region_name, region_erf_t, region_erf_a

    elif pollutant == 'BC':
        if region is None:
            while 1 > emission_region or 2 < emission_region:
                try:
                    emission_region = int(input(
                        "Select an emission region (1-2):\n\n"
                        "1: Global\n"
                        "2: Asia\n\n"
                        "Your selection:  "
                    ))

                    if (1 > emission_region or 2 < emission_region) and emission_region % 1 == 0:
                        print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 2")
                except ValueError:
                    print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

            region_name = bc_emission_region_options[emission_region]
            region_erf_t = erf_t[emission_region - 1]
            region_erf_a = erf_a[emission_region - 1]

            print(bc_emission_region_options[emission_region])

        else:
            assert region in constants.BC_EMISS_REGIONS, \
                "region for {} must be one of {}".format(pollutant, constants.BC_EMISS_REGIONS)

            region_name = region
            region_id = next(k for k, v in bc_emission_region_options.items() if v == region_name)
            region_erf_t = erf_t[region_id - 1]
            region_erf_a = erf_a[region_id - 1]

        return region_name, region_erf_t, region_erf_a

    else:
        if region is None:
            region_name = 'Global'
            print(region_name)

        else:
            region_name = region

        region_erf_t = erf_t
        region_erf_a = erf_a

        return region_name, region_erf_t, region_erf_a


def select_response_region(region_id=None):
    """Interactively select response region.

    Parameters
    ----------
    region_id: int or None (default=None)
        The integer corresponding to a response region, if specified.

        1: Global
        2: Tropics
        3: North Hemisphere Mid Latitudes
        4: North Hemisphere High Latitudes
        5: South Hemisphere Mid Latitudes
        6: South Hemisphere High Latitudes
        7: Europe
        8: North America
        9: China
        10: East Asia
        11: India
        12: Sahel
        13: All regions

        If None, the user will need to choose the
        response region interactively.
    """

    n_regions = len(RESPONSE_REGION_OPTIONS)

    if region_id is None:
    
        response_region = 0
        while 1 > response_region or n_regions < response_region:
            try:
                response_region = int(input(
                    "Select a response region (1-{}) or all response region ({}):\n\n"
                    "1: Global\n"
                    "2: Tropics\n"
                    "3: Northern Hemisphere Mid Latitudes\n"
                    "4: Northern Hemisphere High Latitudes\n"
                    "5: Southern Hemisphere Mid Latitudes\n"
                    "6: Southern Hemisphere High Latitudes\n"
                    "7: Europe\n"
                    "8: United States\n"
                    "9: China\n"
                    "10: East Asia\n"
                    "11: India\n"
                    "12: Sahel\n"
                    "13: All regions\n\n"
                    "Your selection:  ".format(n_regions-1, n_regions)
                ))

                if (1 > response_region or n_regions < response_region) and response_region % 1 == 0:
                    print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND {}".format(n_regions))
            except ValueError:
                print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

        print(RESPONSE_REGION_OPTIONS[response_region])

        if response_region == n_regions:
            return list(RESPONSE_REGION_OPTIONS.values())
        else:
            return RESPONSE_REGION_OPTIONS[response_region]

    else:
        assert region_id in range(1, 14), "region_id must be an integer between 1 and 13"
        if region_id == n_regions:
            return list(RESPONSE_REGION_OPTIONS.values())
        else:
            return RESPONSE_REGION_OPTIONS[region_id]


def get_response_regions():
    """Return the names of all response regions."""
    return list(RESPONSE_REGION_OPTIONS.values())[:-1]


def select_pollutant():
    """Interactively select the pollutant to use."""

    pollutant_id = 0
    while 1 > pollutant_id or 4 < pollutant_id:
        try:
            pollutant_id = int(input(
                "Select a type of pollutant (1-4):\n\n"
                "1: Sulfur dioxide (SO2)\n"
                "2: Black carbon   (BC)\n"
                "3: Carbon dioxide (CO2)\n"
                "4: Methane        (CH4)\n\n"
                "Your selection:  "
            ))

            if (1 > pollutant_id or 4 < pollutant_id) and pollutant_id % 1 == 0:
                print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 4")
        except ValueError:
            print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

    print(constants.POLLUTANTS[pollutant_id - 1])

    return constants.POLLUTANTS[pollutant_id - 1]


def select_magnitude():
    """Interactively select the magnitude to use."""

    magnitude = -1
    while 0 > magnitude or 1000 < magnitude:
        try:
            magnitude = float(input(
                "Select by how much the emission will "
                "be changed (percentage of current emission):\n"
                "   0 = total reduction (zero emission)\n"
                " 100 = no change (100% of current emission)\n"
                "1000 = 10 times current emissions\n\n"
                "Your selection: "
            ))

            if 0 > magnitude or 1000 < magnitude:
                print("\nPLEASE SELECT A NUMBER BETWEEN 0 AND 1000")
        except ValueError:
            print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER A NUMBER (EITHER INTEGER OR FLOAT)")

    return magnitude


def select_time_horizon():
    """Interactively select a time horizon between 5 and 500 years."""

    answer = 'nah'
    while answer not in ['yes', 'y', 'YES', 'Y', 'no', 'n', 'NO', 'N']:

        answer = str(input("Do you want to use a standard time horizon of 100 yr? "))

        if answer in ['yes', 'y', 'YES', 'Y']:
            answer = 'yes'
            time_horizon = 100

        elif answer in ['no', 'n', 'NO', 'N']:
            answer = 'no'
            time_horizon = 0

            while 5 > time_horizon or 500 < time_horizon:
                try:
                    time_horizon = int(input("Select a time horizon between 5 and 500 yr: "))
                    if 5 > time_horizon or 500 < time_horizon:
                        print("\nPLEASE SELECT A NUMBER BETWEEN 5 AND 500")
                except ValueError:
                    print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER\n")

    return time_horizon


def select_scenarios():
    """Interactively select the scenario types, time horizons and magnitudes."""

    th = select_time_horizon()

    magnitude = [None, None, None]
    answer = 'nah'
    while answer not in ['yes', 'y', 'YES', 'Y', 'no', 'n', 'NO', 'N']:

        answer = str(input("Do you want to plot the temperature response for different emissions scenarios? "))

        if answer in ['no', 'n', 'NO', 'N']:
            scen = ['none'] * 4
            return th, scen, magnitude

        elif answer in ['yes', 'y', 'YES', 'Y']:
            scen = {
                0: 'none',
                1: 'sustained',
                2: 'linear',
                3: 'quadratic'
            }
            ths = [0, 0, 0]
            scenarios = [0, 0, 0, 0]
            print("\nYou can choose up to 3 different scenarios. "
                  "If you want to have 2 scenarios only, select the second time horizon equal to {}.".format(th))

            while 1 > scenarios[0] or 3 < scenarios[0]:
                try:
                    scenarios[0] = int(input(
                        "Select a first scenario (1-3):\n\n"
                        "1: sustained\n"
                        "2: linear\n"
                        "3: quadratic\n\n"
                        "Your selection:  "
                    ))

                    if (1 > scenarios[0] or 3 < scenarios[0]) and scenarios[0] % 1 == 0:
                        print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 3")
                except ValueError:
                    print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

            while 5 > ths[0] or th < ths[0]:
                try:
                    ths[0] = int(input(
                        "Select a time horizon between 5 and {} yr for the first scenario: ".format(str(th))
                    ))

                    if 5 > ths[0] or th < ths[0]:
                        print("\nPLEASE SELECT A NUMBER BETWEEN 5 AND {}".format(th))
                except ValueError:
                    print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER\n")

            magnitude[0] = select_magnitude()

            if ths[0] < th:
                while 1 > scenarios[1] or 3 < scenarios[1]:
                    try:
                        scenarios[1] = int(input(
                            "Select a second scenario (1-3):\n\n"
                            "1: sustained\n"
                            "2: linear\n"
                            "3: quadratic\n\n"
                            "Your selection:  "
                        ))
                        if (1 > scenarios[1] or 3 < scenarios[1]) and scenarios[1] % 1 == 0:
                            print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 3")
                    except ValueError:
                        print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

                while ths[0] > ths[1] or th < ths[1]:
                    try:
                        ths[1] = int(input(
                            "Select a time horizon between {} and {} yr for the second scenario: ".format(
                                str(ths[0]), str(th))
                        ))

                        if ths[0] > ths[1] or th < ths[1]:
                            print("\nPLEASE SELECT A NUMBER BETWEEN {} AND {}".format(ths[0], th))
                    except ValueError:
                        print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER\n")

                magnitude[1] = select_magnitude()

                if ths[1] < th:
                    while 1 > scenarios[2] or 3 < scenarios[2]:
                        try:
                            scenarios[2] = int(input(
                                "Select a third scenario (1-3):\n\n"
                                "1: sustained\n"
                                "2: linear\n"
                                "3: quadratic\n\n"
                                "Your selection:  "
                            ))

                            if (1 > scenarios[1] or 3 < scenarios[1]) and scenarios[1] % 1 == 0:
                                print("\nPLEASE SELECT AN INTEGER BETWEEN 1 AND 3")
                        except ValueError:
                            print("\nTHE SELECTION IS NOT VALID, PLEASE ENTER AN INTEGER")

                    magnitude[2] = select_magnitude()
                    ths[2] = th
                else:
                    print("\nBy choosing the second time horizon equal to {}, """
                          "there will be two scenarios only.".format(th))
            else:
                print(
                    "\nBy choosing the first time horizon equal to {}, there will be one scenario only.".format(th))

            return ths, [scen[i] for i in scenarios], magnitude

