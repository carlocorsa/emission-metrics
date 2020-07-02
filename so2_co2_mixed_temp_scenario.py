# Third party imports
import numpy as np

# Local application imports
from rem.simulations import loading, variables
from rem.metrics import co2, slp
from rem.scenarios import temperature_scenarios

# Define input variables
pollutants = ['SO2', 'CO2']
emission_region = 'NHML'
response_regions = ['Europe']
scenarios = ['linear', 'sustained', 'linear']
magnitudes = [120, 120, 100]
time_horizons = [30, 60, 100]
time_step = 0.01
n_steps = 1 / time_step

# Create dictionaries to store results for
# different potentials and pollutants
pot_dict = dict()
std_dict = dict()

for pol in pollutants:

    pot_dict[pol] = dict()
    std_dict[pol] = dict()

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

# # Compute potentials
# iARTP, ARTP = co2.compute_atp(rr_rad_eff, time_horizon)
# iAGTP, AGTP = co2.compute_atp(rad_eff, time_horizon)
#
# iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp = co2.compute_app(
#     rad_eff, rad_eff_a, time_horizon, rr_precip_avg, precip_avg
# )

    # Compute temperature potentials at each time step
    iartp_list = []
    artp_list = []

    for t in np.linspace(time_step, time_horizons[-1], int(time_horizons[-1] * n_steps)):

        if pol == 'CO2':
            iartp, artp = co2.compute_atp(
                rad_eff=rr_rad_eff,
                th=t
            )
        else:
            iartp, artp = slp.compute_atp(
                pollutant=pol,
                rad_eff=rr_rad_eff,
                th=t
            )

        artp_list.append(artp)
        iartp_list.append(iartp)

    # Compute temperature in different scenarios
    temp_response = temperature_scenarios.compute_mixed_scenarios_temperature(
            pol, emission_region, magnitudes, scenarios, time_horizons, artp_list, time_step
    )

    # Store results in dictionaries
    pot_dict[pol] = temp_response
