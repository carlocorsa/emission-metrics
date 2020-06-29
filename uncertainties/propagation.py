import numpy as np
import pandas as pd

# Local application imports
from rem.simulations import input_selection, scaling
from rem.uncertainties import erf, climate_variables
from rem.utils import constants


def get_potential_uncertainties(pollutant, emission_region, response_region):
    """Get propagated uncertainties for the ARTP and the ARPP.
    N.B. To get the full uncertainties the returned values will need to be
    multiplied by the absolute value of the corresponding potential.

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

    response_region: str
        Name of the response region.

    Returns
    -------
    artp_total_std: float or list of floats
        Propagated uncertainty for the ARTP.
        Can be either a single float for a single response region or
        a list of floats if response_region='All regions'.

    slow_arpp_total_std: float or list of floats
        Propagated uncertainty for the slow component of the ARPP.
        Can be either a single float for a single response region or
        a list of floats if response_region='All regions'.

    fast_arpp_total_std: float or list of floats
        Propagated uncertainty for the fast component of the ARPP.
        Can be either a single float for a single response region or
        a list of floats if response_region='All regions'.
    """

    assert pollutant in constants.POLLUTANTS, "{} is not an accepted pollutant".format(pollutant)

    if pollutant == 'BC':
        assert emission_region in constants.BC_EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)
    else:
        assert emission_region in constants.EMISS_REGIONS, \
            "{} is not an accepted emission region for {}".format(emission_region, pollutant)

    fp = constants.SPECS[pollutant]['fp']
    k = constants.SPECS[pollutant]['k']
    k_std = constants.SPECS[pollutant]['k_std']

    # Get temperature and precipitation stats
    reg_temp_avg, glo_temp_avg, temp_ratio_std_err, \
        reg_precip_avg, glo_precip_avg, precip_ratio_std_err = climate_variables.get_climate_stats(response_region)

    # Get ERF regional uncertainties
    if pollutant == 'BC':
        reg_erf_avg, reg_erf_std_err, reg_erfa_avg, reg_erfa_std_err = erf.get_bc_regional_uncertainty(emission_region)

    elif pollutant == 'SO2':
        reg_erf_avg, reg_erf_std_err = erf.get_so2_regional_uncertainty(emission_region)
        reg_erfa_avg = fp * reg_erf_avg
        reg_erfa_std_err = np.abs(fp) * reg_erf_std_err

    else:
        reg_erf_avg = 1
        reg_erf_std_err = 0
        reg_erfa_avg = 1
        reg_erfa_std_err = 0

    # Get ERF global uncertainties
    glo_erf_avg, glo_erf_std_err, glo_erfa_avg, glo_erfa_std_err = erf.get_global_uncertainty(pollutant)

    # Get uncertainty in scaling factor of climate sensitivity
    c_scaling_avg, c_scaling_std_err = scaling.get_mm_scaling(pollutant, 'temperature')[2:4]

    if response_region == 'All regions':

        region_names = input_selection.get_response_regions()
        n_regions = len(region_names)

        artp_total_std = []
        slow_arpp_total_std = []
        fast_arpp_total_std = []

        for i in range(n_regions):

            # The following needs to be multiplied by the total function to obtain the final uncertainty
            artp_total_std.append(
                np.sqrt(
                    (reg_erf_std_err / reg_erf_avg) ** 2 +
                    (glo_erf_std_err / glo_erf_avg) ** 2 +
                    (temp_ratio_std_err[i] / (reg_temp_avg[i] / glo_temp_avg)) ** 2 +
                    (c_scaling_std_err / c_scaling_avg) ** 2
                )
            )

            slow_arpp_total_std.append(
                np.sqrt(
                    (reg_erf_std_err / reg_erf_avg) ** 2 +
                    (glo_erf_std_err / glo_erf_avg) ** 2 +
                    (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2 +
                    (c_scaling_std_err / c_scaling_avg) ** 2 +
                    (k_std / k) ** 2
                )
            )

            fast_arpp_total_std.append(
                np.sqrt(
                    (reg_erfa_std_err / reg_erfa_avg) ** 2 +
                    (glo_erfa_std_err / glo_erfa_avg) ** 2 +
                    (precip_ratio_std_err[i] / (reg_precip_avg[i] / glo_precip_avg)) ** 2
                )
            )

    else:

        # The following needs to be multiplied by the total function to obtain the final uncertainty
        artp_total_std = np.sqrt(
            (reg_erf_std_err / reg_erf_avg) ** 2 +
            (glo_erf_std_err / glo_erf_avg) ** 2 +
            (temp_ratio_std_err / (reg_temp_avg / glo_temp_avg)) ** 2 +
            (c_scaling_std_err / c_scaling_avg) ** 2
        )

        slow_arpp_total_std = np.sqrt(
            (reg_erf_std_err / reg_erf_avg) ** 2 +
            (glo_erf_std_err / glo_erf_avg) ** 2 +
            (precip_ratio_std_err / (reg_precip_avg / glo_precip_avg)) ** 2 +
            (c_scaling_std_err / c_scaling_avg) ** 2 +
            (k_std / k) ** 2
        )

        fast_arpp_total_std = np.sqrt(
            (reg_erfa_std_err / reg_erfa_avg) ** 2 +
            (glo_erfa_std_err / glo_erfa_avg) ** 2 +
            (precip_ratio_std_err / (reg_precip_avg / glo_precip_avg)) ** 2
        )

    if isinstance(artp_total_std, pd.Series):
        artp_total_std = artp_total_std.tolist()
    if isinstance(slow_arpp_total_std, pd.Series):
        slow_arpp_total_std = slow_arpp_total_std.tolist()
    if isinstance(fast_arpp_total_std, pd.Series):
        fast_arpp_total_std = fast_arpp_total_std.tolist()

    return artp_total_std, slow_arpp_total_std, fast_arpp_total_std

