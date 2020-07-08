# Standard library imports
import os

# Third party imports
from matplotlib import pyplot as plt

# Local application imports
from simulations import loading, variables, input_selection
from metrics import slp, co2
from uncertainties import propagation
from plotting import bar_plots

# Figure path
FIGURE_PATH = "figures/"

# Define input variables
pollutants = ['CH4', 'CO2']
emission_region = 'NHML'
response_regions = input_selection.get_response_regions()
time_horizons = [20, 100]

# Create dictionaries to store results for different
# potentials, pollutants and time horizons
pot_dict = dict()
std_dict = dict()

for pol in pollutants:

    pot_dict[pol] = dict()
    std_dict[pol] = dict()

    for th in time_horizons:

        pot_dict[pol][th] = dict()
        std_dict[pol][th] = dict()

        # Load and compute climate variables average variations
        grid_delta_temp, grid_delta_precip = loading.load_climate_variables(
            pollutant=pol,
            emission_region=emission_region
        )

        rr_temp_avg, temp_avg, rr_precip_avg, precip_avg = variables.compute_climate_variables(
            response_regions=response_regions,
            grid_delta_temp=grid_delta_temp,
            grid_delta_precip=grid_delta_precip
        )

        # Compute radiative efficiencies
        rr_rad_eff, rad_eff, rad_eff_a = variables.compute_radiative_efficiency(
            pollutant=pol,
            emission_region=emission_region,
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
            emission_region=emission_region,
            response_regions=response_regions,
            artp=artp,
            slow_arpp=slow_arpp,
            fast_arpp=fast_arpp
        )

        iartp_std, iarpp_std = propagation.get_potential_uncertainties(
            pollutant=pol,
            emission_region=emission_region,
            response_regions=response_regions,
            artp=iartp,
            slow_arpp=slow_iarpp,
            fast_arpp=fast_iarpp
        )

        # Store results in the dictionaries
        pot_dict[pol][th]['ARTP'] = artp
        pot_dict[pol][th]['ARPP'] = arpp
        pot_dict[pol][th]['iARTP'] = iartp
        pot_dict[pol][th]['iARPP'] = iarpp
        std_dict[pol][th]['ARTP'] = artp_std
        std_dict[pol][th]['ARPP'] = arpp_std
        std_dict[pol][th]['iARTP'] = iartp_std
        std_dict[pol][th]['iARPP'] = iarpp_std

        print("Pollutant: {:3s} | Time horizon: {:3d} ".format(pol, th))

# Choose potentials to plot for each pollutant
potentials = {
    'CH4': 'iARTP',
    'CO2': 'ARTP'
}

bar_plots.plot_ch4_co2_double_bars(pot_dict, std_dict, response_regions, potentials)

# Save figure
fig_name = 'CH4_CO2_ARTP_bar_plot.pdf'
plt.savefig(os.path.join(FIGURE_PATH, fig_name))
