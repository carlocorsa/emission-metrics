# Third party imports
import numpy as np

# Local application imports
from utils import constants
from simulations import loading

# Load constants
A0 = constants.SPECS['CO2']['a0']
Ai = constants.SPECS['CO2']['ai']


def compute_time_step_temperature(index, emissions, artp, time_step=0.01):
    """"Compute temperature change by numerical integration.

    Parameters
    ----------
    index: int
        Index at which to compute the temperature change.

    emissions: list of floats
        List of emission values.

    artp: array-like
        Array of ARTP values.

    time_step: float (default=0.01)
        Length in years of the time step used
        for numerical integration.

    Returns
    -------
    Temperature change at `index`.
    """
    if index == 0:
        return emissions[index] * (time_step * artp[index] / 2)
    else:
        return sum([emissions[i] * (time_step * (artp[index-i] + artp[index-i-1]) / 2) for i in range(0, index)])


def compute_mixed_scenarios_temperature(
        pollutant, emiss_region, magnitudes, emiss_scenarios, time_horizons, artp, time_step=0.01
):
    """Compute the temperature change due to variations of `pollutant' emissions.
    There can be any number of emission scenarios and each of them needs to have magnitude,
    scenario type and time horizon specified.

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    emiss_region: str
        The name of the pollutant emission region.
        For SO2, CO2 and CH4, one of the following options:
        - NHML
        - US
        - China
        - EastAsia
        - India
        - Europe

        For BC, one of the following options:
        - Global
        - Asia

    magnitudes: list of integers
        A list of magnitudes, one for each scenario.
           0 = total reduction (zero emission)
         100 = no change (100% of current emission)
        1000 = 10 times current emissions

    emiss_scenarios: list of str
        A list of emission scenario types.
        Must be one of the following:
        - linear
        - sustained
        - quadratic

    time_horizons: list of integers
        A list of time horizons, one for each scenario.
        Each time horizon must be larger than the
        previous one, eg, [30, 60, 100].

    artp: array-like
        Array of ARTP values covering the maximum
        time horizon considered.
        Must have a length equal to:
        max(time_horizons) * (1 / time_step)

    time_step: float (default=0.01)
        Length in years of the time step used
        for numerical integration.
        Should be smaller than the lifetime of the
        used pollutant.

    Returns
    -------
    mixed_scenario_temperature: list of floats
        List of temperature changes for each point in
        the period considered.
        Length = max(time_horizons) * (1 / time_step)
    """

    assert len(emiss_scenarios) == len(time_horizons), \
        "The number of scenarios ({}) does not correspond to the number of time horizons ({}).".format(
            len(emiss_scenarios), len(time_horizons)
        )

    for scenario in emiss_scenarios:
        assert scenario in constants.SCENARIOS, "{} is not a valid scenario type".format(scenario)

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
            dth_i = time_horizons[i] - time_horizons[i-1] if i > 0 else time_horizons[i]
            aai = np.array([A0] + Ai)
            atau = np.array(
                [time_horizons[0]] +
                [ti if ti < dth_i else dth_i for ti in constants.SPECS['CO2']['tau']]
            )
            tot_delta_emiss_mass = delta_emiss_mass / sum(aai * atau)
        else:
            tot_delta_emiss_mass = delta_emiss_mass

        if i == 0:
            prev_th = 0
            prev_scen_emiss = 0
            scen_emiss = sign * tot_delta_emiss_mass * (magnitudes[i] - 100) / 100
        else:
            prev_th = time_horizons[i - 1] * n_steps
            prev_scen_emiss = sign * tot_delta_emiss_mass * (magnitudes[i-1] - 100) / 100
            scen_emiss = sign * tot_delta_emiss_mass * (magnitudes[i] - magnitudes[i-1]) / 100

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
