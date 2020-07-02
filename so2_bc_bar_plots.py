# Standard library imports
import os

# Third party imports
from matplotlib import pyplot as plt

# Local application imports
from rem.simulations import loading, variables, input_selection
from rem.metrics import slp
from rem.uncertainties import propagation
from rem.utils import constants
from rem.plotting import bar_plots

# Figure path
FIGURE_PATH = "../figures/"

# Define input variables
pollutants = ['SO2', 'BC']
emission_regions = {
    'SO2': constants.EMISS_REGIONS,
    'BC': constants.BC_EMISS_REGIONS,
}
response_regions = input_selection.get_response_regions()
time_horizons = [20, 100]

# Create dictionaries to store results for different
# pollutants, emission regions and time horizons
iartp_dict = dict()
iarpp_dict = dict()
iartp_std_dict = dict()
iarpp_std_dict = dict()

for pol in pollutants:

    iartp_dict[pol] = dict()
    iarpp_dict[pol] = dict()
    iartp_std_dict[pol] = dict()
    iarpp_std_dict[pol] = dict()

    for reg in emission_regions[pol]:

        iartp_dict[pol][reg] = dict()
        iarpp_dict[pol][reg] = dict()
        iartp_std_dict[pol][reg] = dict()
        iarpp_std_dict[pol][reg] = dict()

        for th in time_horizons:

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

            # Compute temperature potentials
            iartp, artp = slp.compute_atp(
                pollutant=pol,
                rad_eff=rr_rad_eff,
                th=th
            )

            # Compute precipitation potentials
            iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp = slp.compute_app(
                pollutant=pol,
                rad_eff=rad_eff,
                rad_eff_a=rad_eff_a,
                th=th,
                rr_precip_avg=rr_precip_avg,
                precip_avg=precip_avg
            )

            # Compute uncertainties
            iartp_std, iarpp_std = propagation.get_potential_uncertainties(
                pollutant=pol,
                emission_region=reg,
                response_regions=response_regions,
                artp=iartp,
                slow_arpp=slow_iarpp,
                fast_arpp=fast_iarpp
            )

            # Store results in the dictionaries
            iartp_dict[pol][reg][th] = iartp
            iarpp_dict[pol][reg][th] = iarpp
            iartp_std_dict[pol][reg][th] = iartp_std
            iarpp_std_dict[pol][reg][th] = iarpp_std

            print("Pollutant: {:3s} | Region: {:10s} | Time horizon: {:3d} ".format(pol, reg, th))

# Plot iARTP
bar_plots.plot_so2_bc_double_bars(iartp_dict, iartp_std_dict, response_regions, potential_name="iARTP")

# Save figure
fig_name = 'SO2_BC_iARTP_bar_plot.pdf'
plt.savefig(os.path.join(FIGURE_PATH, fig_name))

# Plot iARPP
bar_plots.plot_so2_bc_double_bars(iarpp_dict, iarpp_std_dict, response_regions, potential_name="iARPP")

# Save figure
fig_name = 'SO2_BC_iARPP_bar_plot.pdf'
plt.savefig(os.path.join(FIGURE_PATH, fig_name))
