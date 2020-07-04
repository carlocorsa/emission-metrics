# Third party imports
import numpy as np

# Local application imports
from simulations import input_selection, scaling
from uncertainties import erf, climate_variables
from utils import constants


def get_potential_uncertainties(pollutant, emission_region, response_regions, artp, slow_arpp, fast_arpp):
    """Get propagated uncertainties for the ARTP and the ARPP.

    Parameters
    ----------
    pollutant: str
        One of the following four options:
        - SO2
        - BC
        - CO2
        - CH4

    emission_region: str
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

    response_regions: list of str
        Names of the response regions.

    artp: array of floats
        Pulse or integrated ARTP.

    slow_arpp: array of floats
        Slow component of either the pulse or integrated ARPP.

    fast_arpp: array of floats
        Fast component of either the pulse or integrated ARPP.

    Returns
    -------
    artp_std: array of floats
        Propagated uncertainty for the ARTP for all `response_regions`.

    arpp_std: array of floats
        Propagated uncertainty for the ARPP for all `response_regions`.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    if pollutant == 'BC':
        assert emission_region in constants.BC_EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)
    else:
        assert emission_region in constants.EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)

    # Load constants
    fp = constants.SPECS[pollutant]['fp']
    k = constants.SPECS[pollutant]['k']
    k_std = constants.SPECS[pollutant]['k_std']

    # Get region names
    if 'All regions' in response_regions:
        region_names = input_selection.get_response_regions()
    else:
        region_names = response_regions

    n_regions = len(region_names)

    # Get temperature and precipitation stats
    reg_temp_avg, glo_temp_avg, temp_ratio_std_err, \
        reg_precip_avg, glo_precip_avg, precip_ratio_std_err = climate_variables.get_climate_stats(region_names)

    # Get ERF regional uncertainties
    if pollutant == 'SO2':
        reg_erf_avg, reg_erf_std_err = erf.get_so2_regional_uncertainty(emission_region)
        reg_erfa_avg = fp * reg_erf_avg
        reg_erfa_std_err = np.abs(fp) * reg_erf_std_err

    else:
        reg_erf_avg, reg_erf_std_err, reg_erfa_avg, reg_erfa_std_err = erf.get_regional_uncertainty(
            pollutant, emission_region
        )

    # Get ERF global uncertainties
    glo_erf_avg, glo_erf_std_err, glo_erfa_avg, glo_erfa_std_err = erf.get_global_uncertainty(pollutant)

    # Get uncertainty in scaling factor of climate sensitivity
    c_scaling_avg, c_scaling_std_err = scaling.get_mm_scaling(pollutant, 'temperature')[2:4]

    # Compute uncertainties for all response regions
    artp_std = []
    slow_arpp_std = []
    fast_arpp_std = []

    for i in range(n_regions):

        artp_std.append(
            np.sqrt(
                (reg_erf_std_err / reg_erf_avg) ** 2 +
                (glo_erf_std_err / glo_erf_avg) ** 2 +
                (temp_ratio_std_err[i] / (reg_temp_avg[i] / glo_temp_avg)) ** 2 +
                (c_scaling_std_err / c_scaling_avg) ** 2
            )
        )

        slow_arpp_std.append(
            np.sqrt(
                (reg_erf_std_err / reg_erf_avg) ** 2 +
                (glo_erf_std_err / glo_erf_avg) ** 2 +
                (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2 +
                (c_scaling_std_err / c_scaling_avg) ** 2 +
                (k_std / k) ** 2
            )
        )

        fast_arpp_std.append(
            np.sqrt(
                (reg_erfa_std_err / reg_erfa_avg) ** 2 +
                (glo_erfa_std_err / glo_erfa_avg) ** 2 +
                (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2
            )
        )

    # Compute artp propagated standard deviation
    artp_std = abs(artp) * np.array(artp_std)

    # Compute arpp propagated standard deviation
    slow_arpp_std = abs(slow_arpp) * np.array(slow_arpp_std)
    fast_arpp_std = abs(fast_arpp) * np.array(fast_arpp_std)
    arpp_std = np.sqrt(slow_arpp_std ** 2 + fast_arpp_std ** 2)

    return artp_std, arpp_std
