# Third party imports
import numpy as np

# Local application imports
from rem.utils import constants
from rem.simulations import loading

# Load constants
A0 = constants.SPECS['CO2']['a0']
Ai = constants.SPECS['CO2']['ai']


def compute_time_step_temperature(t, emiss_scenario, artp, time_step=0.01):
    if t == 0:
        return emiss_scenario[t] * (time_step * artp[t] / 2)
    else:
        return sum([emiss_scenario[i] * (time_step * (artp[t - i] + artp[t - i - 1]) / 2) for i in range(0, t)])


def compute_mixed_scenarios_temperature(
        pollutant, emiss_region, magnitudes, emiss_scenarios, time_horizons, artp, time_step=0.01
):

    assert len(emiss_scenarios) == len(time_horizons), \
        "The number of scenarios ({}) does not correspond to the number of time horizons ({}).".format(
            len(emiss_scenarios), len(time_horizons)
        )

    # Compute number of steps per year
    n_steps = int(1 / time_step)

    if isinstance(time_horizons, float) or isinstance(time_horizons, int):
        time_horizons = [time_horizons]

    # Get final time horizon
    max_th = max(time_horizons)

    assert max_th * n_steps == len(artp), \
        "The total number of steps ({}) does not correspond to the length of the ARTP ({})".format(
            max_th * n_steps, len(artp)
        )

    # Load pollutant emissions
    delta_emiss_mass = loading.load_emissions(pollutant, emiss_region)

    # Instantiate an empty array for the full length of the emission scenarios
    mixed_scen_emiss = np.zeros(max_th * n_steps)

    for i, scenario in enumerate(emiss_scenarios):

        curr_th = time_horizons[i] * n_steps

        if pollutant == 'SO2':
            sign = -1
        else:
            sign = 1

        # Scale CO2 emissions
        if pollutant == 'CO2':
            aai = np.array([A0] + Ai)
            atau = np.array(
                [time_horizons[0]] +
                [ti if ti < time_horizons[0] else time_horizons[0] for ti in constants.SPECS['CO2']['tau']])
            delta_emiss_mass = delta_emiss_mass / sum(aai * atau)

        if i == 0:
            prev_th = 0
            prev_scen_emiss = 0
            scen_emiss = sign * delta_emiss_mass * (magnitudes[i] - 100) / 100
        else:
            prev_th = time_horizons[i - 1] * n_steps
            prev_scen_emiss = sign * delta_emiss_mass * (magnitudes[i - 1] - 100) / 100
            scen_emiss = sign * delta_emiss_mass * (magnitudes[i] - magnitudes[i - 1]) / 100

        if emiss_scenarios[i] == 'linear':
            for t in range(prev_th, curr_th):
                mixed_scen_emiss[t] = prev_scen_emiss + scen_emiss * ((t - prev_th + 1.) / (curr_th - prev_th))

        if emiss_scenarios[i] == 'sustained':
            for t in range(prev_th, curr_th):
                mixed_scen_emiss[t] = prev_scen_emiss + scen_emiss

        if emiss_scenarios[i] == 'quadratic':
            for t in range(prev_th, curr_th):
                mixed_scen_emiss[t] = prev_scen_emiss + scen_emiss * ((t - prev_th + 1.) / (curr_th - prev_th)) ** 2

    mixed_scenario_temperature = []
    for t in range(0, max_th * n_steps):
        mixed_scenario_temperature.append(compute_time_step_temperature(t, mixed_scen_emiss, artp, time_step))

    return mixed_scenario_temperature


def compute_scenarios_temperature(pollutant, emiss_region, magnitude, time_horizon, artp, time_step=0.01):

    # Compute number of steps per year
    n_steps = int(1 / time_step)

    assert time_horizon * n_steps == len(artp), \
        "The total number of steps ({}) does not correspond to the length of the ARTP ({})".format(
            time_horizon * n_steps, len(artp)
        )

    # Load pollutant emissions
    delta_emiss_mass = loading.load_emissions(pollutant, emiss_region)

    # Get scaled emission mass variation
    if pollutant == 'SO2':
        scaled_delta_emiss_mass = delta_emiss_mass * (100 - magnitude) / 100
    else:
        scaled_delta_emiss_mass = delta_emiss_mass * (magnitude - 100) / 100

    linear_scen_emiss = []
    quadratic_scen_emiss = []
    sin_scen_emiss = []
    sustained_scen_emiss = []
    for t in np.linspace(time_step, time_horizon, time_horizon * n_steps):
        linear_scen_emiss.append(scaled_delta_emiss_mass * ((t + 1) / time_horizon))
        quadratic_scen_emiss.append(scaled_delta_emiss_mass * ((t + 1) / time_horizon) ** 2)
        sin_scen_emiss.append(scaled_delta_emiss_mass * np.sin(np.pi * ((t + 1) / time_horizon)))
        sustained_scen_emiss.append(scaled_delta_emiss_mass)

    temperature = dict()
    temperature['linear'] = np.zeros(time_horizon * n_steps)
    temperature['quadratic'] = np.zeros(time_horizon * n_steps)
    temperature['sin'] = np.zeros(time_horizon * n_steps)
    temperature['sustained'] = np.zeros(time_horizon * n_steps)
    temperature['mixed'] = np.zeros(time_horizon * n_steps)
    for t in range(0, time_horizon * n_steps):
        temperature['linear'][t] = compute_time_step_temperature(t, linear_scen_emiss, artp, time_step)
        temperature['quadratic'][t] = compute_time_step_temperature(t, quadratic_scen_emiss, artp, time_step)
        temperature['sin'][t] = compute_time_step_temperature(t, sin_scen_emiss, artp, time_step)
        temperature['sustained'][t] = compute_time_step_temperature(t, sustained_scen_emiss, artp, time_step)

    return temperature
