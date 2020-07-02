# Third party imports
import numpy as np

# Local application imports
from simulations import loading, variables
from metrics import co2, slp
from scenarios import temperature_scenarios
from uncertainties import propagation

# Define input variables
pollutants = ['SO2', 'CO2']
emission_region = 'NHML'
response_regions = ['Europe']
scenarios = ['linear', 'sustained', 'linear']
magnitudes = {
    'SO2': [150, 150, 100],
    'CO2': [120, 120, 100]
}
time_horizons = [30, 60, 100]
time_step = 0.01
n_steps = 1 / time_step

# Create dictionaries to store results for
# different potentials and pollutants
temp_dict = dict()

for pol in pollutants:

    temp_dict[pol] = dict()

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

    # Compute temperature potentials at each time step
    artp_list = []
    slow_arpp_list = []
    fast_arpp_list = []

    for t in np.linspace(time_step, time_horizons[-1], int(time_horizons[-1] * n_steps)):

        if pol == 'CO2':
            _, artp = co2.compute_atp(
                rad_eff=rr_rad_eff,
                th=t
            )

            _, _, _, arpp, slow_arpp, fast_arpp = co2.compute_app(
                rad_eff=rad_eff,
                rad_eff_a=rad_eff_a,
                th=t,
                rr_precip_avg=rr_precip_avg,
                precip_avg=precip_avg
            )

        else:
            _, artp = slp.compute_atp(
                pollutant=pol,
                rad_eff=rr_rad_eff,
                th=t
            )

            _, _, _, _, slow_arpp, fast_arpp = slp.compute_app(
                pollutant=pol,
                rad_eff=rad_eff,
                rad_eff_a=rad_eff_a,
                th=t,
                rr_precip_avg=rr_precip_avg,
                precip_avg=precip_avg
            )

        artp_list.append(artp[0])
        slow_arpp_list.append(slow_arpp[0])
        fast_arpp_list.append(fast_arpp[0])

    # Convert list to arrays
    artp_array = np.array(artp_list).ravel()
    slow_arpp_array = np.array(slow_arpp_list).ravel()
    fast_arpp_array = np.array(fast_arpp_list).ravel()

    # Compute temperature in different scenarios
    temp_response = temperature_scenarios.compute_mixed_scenarios_temperature(
            pol, emission_region, magnitudes[pol], scenarios, time_horizons, artp_array, time_step
    )

    # Compute uncertainties
    temp_std, _ = propagation.get_potential_uncertainties(
        pollutant=pol,
        emission_region=emission_region,
        response_regions=response_regions,
        artp=np.array(temp_response).ravel(),
        slow_arpp=slow_arpp_array,
        fast_arpp=fast_arpp_array
    )

    # Store results in dictionaries
    temp_dict[pol]['temp'] = np.array(temp_response)
    temp_dict[pol]['std'] = np.array(temp_std)

    print("Temperature for {:3s} computed.".format(pol))
