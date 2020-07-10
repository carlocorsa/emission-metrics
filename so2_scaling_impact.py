# Standard library imports
import os

# Third party imports
import numpy as np
from matplotlib import pyplot as plt

# Local application imports
from simulations import loading, variables
from metrics import slp
from plotting import sensitivity

# Figure path
FIGURE_PATH = "figures/"

# Define input variables
pollutant = 'SO2'
emission_region = 'Europe'
response_regions = ['Global']
time_horizon = 100
time_step = 0.03
n_steps = 1 / time_step

# Load and compute climate variables average variations
grid_delta_temp, grid_delta_precip = loading.load_climate_variables(
    pollutant=pollutant,
    emission_region=emission_region
)

rr_temp_avg, temp_avg, rr_precip_avg, precip_avg = variables.compute_climate_variables(
    response_regions=response_regions,
    grid_delta_temp=grid_delta_temp,
    grid_delta_precip=grid_delta_precip
)

# Compute radiative efficiencies
rr_rad_eff, rad_eff, rad_eff_a = variables.compute_radiative_efficiency(
    pollutant=pollutant,
    emission_region=emission_region,
    response_regions=response_regions
)

# Compute temperature potentials with and without scalings at each time step
artp_dict = dict()
iartp_dict = dict()

artp_dict['artp'] = []
iartp_dict['iartp'] = []
artp_dict['no_c_artp'] = []
iartp_dict['no_c_iartp'] = []
artp_dict['no_erf_artp'] = []
iartp_dict['no_erf_iartp'] = []
artp_dict['no_c_no_erf_artp'] = []
iartp_dict['no_c_no_erf_iartp'] = []

for t in np.linspace(time_step, time_horizon, int(time_horizon * n_steps)):

    iartp, artp = slp.compute_atp(
        pollutant=pollutant,
        rad_eff=rr_rad_eff,
        th=t
    )

    no_c_iartp, no_c_artp = slp.compute_atp(
        pollutant=pollutant,
        rad_eff=rr_rad_eff,
        th=t,
        c_scaling=False
    )

    no_erf_iartp, no_erf_artp = slp.compute_atp(
        pollutant=pollutant,
        rad_eff=rr_rad_eff,
        th=t,
        erf_scaling=False
    )

    no_c_no_erf_iartp, no_c_no_erf_artp = slp.compute_atp(
        pollutant=pollutant,
        rad_eff=rr_rad_eff,
        th=t,
        c_scaling=False,
        erf_scaling=False
    )

    artp_dict['artp'].append(artp[0])
    iartp_dict['iartp'].append(iartp[0])
    artp_dict['no_c_artp'].append(no_c_artp[0])
    iartp_dict['no_c_iartp'].append(no_c_iartp[0])
    artp_dict['no_erf_artp'].append(no_erf_artp[0])
    iartp_dict['no_erf_iartp'].append(no_erf_iartp[0])
    artp_dict['no_c_no_erf_artp'].append(no_c_no_erf_artp[0])
    iartp_dict['no_c_no_erf_iartp'].append(no_c_no_erf_iartp[0])

    print("\rt = {:5.2f}".format(t), flush=True, end=" ")

# Plot figure
sensitivity.plot_scalings(artp_dict, iartp_dict, time_horizon)

# Save figure
fig_name = '{}_scalings_{}_{}.pdf'.format(pollutant, emission_region, response_regions[0])
plt.savefig(os.path.join(FIGURE_PATH, fig_name))
