# Local application imports
from rem.simulations import loading, variables
from rem.metrics import slp

# Define input variables
time_horizon = 100
pollutant = 'SO2'
emission_region = 'Europe'
response_region = 'US'

# Load and compute climate variables average variations
grid_delta_temp, grid_delta_precip = loading.load_climate_variables(pollutant, emission_region)

rr_temp_avg, temp_avg, rr_precip_avg, precip_avg = variables.compute_climate_variables(
    response_region, grid_delta_temp, grid_delta_precip
)

# Compute radiative efficiencies
rr_rad_eff, rad_eff, rad_eff_a = variables.compute_radiative_efficiency(
    pollutant, emission_region, response_region
)

# Compute potentials
iARTP, ARTP = slp.compute_atp(rr_rad_eff, time_horizon)
iAGTP, AGTP = slp.compute_atp(rad_eff, time_horizon)

iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp = slp.compute_app(
    pollutant, rad_eff, rad_eff_a, time_horizon, rr_precip_avg, precip_avg
)
