# Standard library imports
import os

# Third party imports
import pandas as pd

# Local application imports
from simulations import loading, variables, input_selection
from metrics import slp, co2
from uncertainties import propagation
from utils import constants

# Change pandas display format
pd.set_option('display.float_format', '{:.1E}'.format)

# Figure path
TABLE_PATH = "tables/"

# Define input variables
pollutants = ['SO2', 'BC', 'CH4', 'CO2']
emission_regions = {
    'SO2': constants.SO2_EMISS_REGIONS,
    'BC': constants.BC_EMISS_REGIONS,
    'CH4': ['Global'],
    'CO2': ['Global']
}
response_regions = input_selection.get_response_regions()
time_horizons = [20, 100]


# Define function to sum strings from two DataFrames
def sum_string(x, y):
    return x + u" \u00B1 " + y


# Create dictionaries to store results for different
# potentials, pollutants and time horizons
pot_dict = dict()
std_dict = dict()

for th in time_horizons:

    pot_dict[th] = dict()
    std_dict[th] = dict()

    for pol in pollutants:

        pot_dict[th][pol] = dict()
        std_dict[th][pol] = dict()

        for reg in emission_regions[pol]:

            pot_dict[th][pol][reg] = dict()
            std_dict[th][pol][reg] = dict()

            # Load and compute climate variables average variations
            grid_delta_temp, grid_delta_precip = loading.load_climate_variables(
                pollutant=pol,
                emission_region=reg
            )

            rr_temp_avg, temp_avg, rr_precip_avg, precip_avg = variables.compute_climate_variables(
                response_regions=response_regions,
                grid_delta_temp=grid_delta_temp,
                grid_delta_precip=grid_delta_precip
            )

            # Compute radiative efficiencies
            rr_rad_eff, rad_eff, rad_eff_a = variables.compute_radiative_efficiency(
                pollutant=pol,
                emission_region=reg,
                response_regions=response_regions
            )

            # Compute temperature and precipitation potentials
            if pol == 'CO2':

                iartp, artp = co2.compute_atp(
                    rad_eff=rr_rad_eff,
                    th=th
                )

                iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp = co2.compute_app(
                    rad_eff=rad_eff,
                    rad_eff_a=rad_eff_a,
                    th=th,
                    rr_precip_avg=rr_precip_avg,
                    precip_avg=precip_avg
                )

            else:

                iartp, artp = slp.compute_atp(
                    pollutant=pol,
                    rad_eff=rr_rad_eff,
                    th=th
                )

                iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp = slp.compute_app(
                    pollutant=pol,
                    rad_eff=rad_eff,
                    rad_eff_a=rad_eff_a,
                    th=th,
                    rr_precip_avg=rr_precip_avg,
                    precip_avg=precip_avg
                )

            # Compute uncertainties
            artp_std, arpp_std = propagation.get_potential_uncertainties(
                pollutant=pol,
                emission_region=reg,
                response_regions=response_regions,
                artp=artp,
                slow_arpp=slow_arpp,
                fast_arpp=fast_arpp
            )

            iartp_std, iarpp_std = propagation.get_potential_uncertainties(
                pollutant=pol,
                emission_region=reg,
                response_regions=response_regions,
                artp=iartp,
                slow_arpp=slow_iarpp,
                fast_arpp=fast_iarpp
            )

            # Store results in the dictionaries
            pot_dict[th][pol][reg]['ARTP'] = artp
            pot_dict[th][pol][reg]['ARPP'] = arpp
            pot_dict[th][pol][reg]['iARTP'] = iartp
            pot_dict[th][pol][reg]['iARPP'] = iarpp
            std_dict[th][pol][reg]['ARTP'] = artp_std
            std_dict[th][pol][reg]['ARPP'] = arpp_std
            std_dict[th][pol][reg]['iARTP'] = iartp_std
            std_dict[th][pol][reg]['iARPP'] = iarpp_std

            print("Time horizon: {:3d} | Pollutant: {:3s} | Region: {:10s} ".format(th, pol, reg))

# Create tables
response_regions = input_selection.get_response_regions()

df = dict()
df_1 = dict()
df_2 = dict()
pot = dict()
std = dict()
pots = dict()
stds = dict()

for name in ['ARTP', 'ARPP', 'iARTP', 'iARPP']:

    df[name] = dict()
    df_1[name] = dict()
    df_2[name] = dict()
    pot[name] = dict()
    std[name] = dict()
    pots[name] = dict()
    stds[name] = dict()

    for th in time_horizons:

        pots[name][th] = []
        stds[name][th] = []

        for pol in pollutants:
            for reg in emission_regions[pol]:
                if reg == 'China':
                    continue
                pots[name][th].append(pd.DataFrame(pot_dict[th][pol][reg][name], columns=[constants.NOTATIONS[pol]]).T)
                stds[name][th].append(pd.DataFrame(std_dict[th][pol][reg][name], columns=[constants.NOTATIONS[pol]]).T)
                pots[name][th][-1]['Emission Region'] = reg
                stds[name][th][-1]['Emission Region'] = reg

        pot[name][th] = pd.concat(pots[name][th])
        pot[name][th].set_index("Emission Region", append=True, inplace=True)
        pot[name][th].rename(columns={i: reg for i, reg in enumerate(response_regions)}, inplace=True)
        std[name][th] = pd.concat(stds[name][th])
        std[name][th].set_index("Emission Region", append=True, inplace=True)
        std[name][th].rename(columns={i: reg for i, reg in enumerate(response_regions)}, inplace=True)

        # Convert floats to strings
        for col in pot[name][th].columns:
            pot[name][th][col] = pot[name][th][col].map('{: .1e}'.format)
            std[name][th][col] = std[name][th][col].map('{: .1e}'.format)

        # Combine potential and uncertainty values in single columns
        df[name][th] = pot[name][th].combine(std[name][th], sum_string)

        # Split dataframes in two parts
        df_1[name][th] = df[name][th].iloc[:, 0:6]
        df_2[name][th] = df[name][th].iloc[:, 6:]

        # Save dataframe as a latex file
        template = r'''\documentclass[preview]{{standalone}}
        \usepackage[margin=1in]{{geometry}}
        \usepackage{{booktabs}}
        \usepackage{{dcolumn}}
        \usepackage{{caption}}
        \begin{{document}}
        \tiny
        \begin{{minipage}}{{\textwidth}}
        {}
        \end{{minipage}}
        \end{{document}}
        '''

        # Save first part of dataframe as a latex file
        latex_path_1 = os.path.join(TABLE_PATH, '{}_table_H{}_1.tex'.format(name, th))
        with open(latex_path_1, 'w') as f:
            f.write(template.format(df_1[name][th].to_latex()))

        # Save second part of dataframe as a latex file
        latex_path_2 = os.path.join(TABLE_PATH, '{}_table_H{}_2.tex'.format(name, th))
        with open(latex_path_2, 'w') as f:
            f.write(template.format(df_2[name][th].to_latex()))
