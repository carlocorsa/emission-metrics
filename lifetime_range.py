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
pollutant = 'CH4'
emission_region = 'NHML'
response_regions = ['US']
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

# Compute temperature potentials using the following lifetime values:
# min = lifetime - lifetime standard deviation
# avg = lifetime
# max = lifetime + lifetime standard deviation

artp_dict = dict()
iartp_dict = dict()

artp_dict['min'] = []
artp_dict['avg'] = []
artp_dict['max'] = []
iartp_dict['min'] = []
iartp_dict['avg'] = []
iartp_dict['max'] = []

for t in np.linspace(time_step, time_horizon, int(time_horizon * n_steps)):

    iartp, artp = slp.compute_atp(
        pollutant=pollutant,
        rad_eff=rr_rad_eff,
        th=t,
        lifetime_range=True
    )

    artp_dict['min'].append(artp[0])
    artp_dict['avg'].append(artp[1])
    artp_dict['max'].append(artp[2])
    iartp_dict['min'].append(iartp[0])
    iartp_dict['avg'].append(iartp[1])
    iartp_dict['max'].append(iartp[2])

    print("\rt = {:5.2f}".format(t), flush=True, end=" ")

# Plot figure
sensitivity.plot_lifetime_range(artp_dict, iartp_dict, time_horizon)

# Save figure
fig_name = '{}_lifetime_range_{}_{}.pdf'.format(pollutant, emission_region, response_regions[0])
plt.savefig(os.path.join(FIGURE_PATH, fig_name))
