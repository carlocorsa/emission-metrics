# Third party imports
import numpy as np

# Local application imports
from rem.utils import constants
from rem.simulations import variables

# Load constants
D = constants.D
Cf = constants.CF


def compute_atp(pollutant, rad_eff, th):
    """Compute integrated and pulse Absolute Temperature Potential (ATP).
    Depending on the radiative efficiency `rad_eff` the returned potentials
    can be either regional or global.

    Parameters
    ----------
    pollutant: str
        One of the following single lifetime pollutants:
        - SO2
        - BC
        - CH4

    rad_eff: float
        Radiative efficiency for CO2 experiments.

    th: int
        Time horizon - must not be smaller than 5.

    Returns
    -------
    iatp: float
        Integrated absolute (either regional or global) temperature potential.

    atp: float
        Pulse absolute (either regional or global) temperature potential.

    """

    assert th >= 5, "The chosen time horizon is smaller than 5."
    assert pollutant in constants.SLP, "{} is not an accepted pollutant".format(pollutant)

    # Load constants
    tau = constants.SPECS[pollutant]['tau']
    fp = constants.SPECS[pollutant]['fp']
    k = constants.SPECS[pollutant]['k']

    # Get scaled climate sensitivity
    c_scaled = variables.get_scaled_climate_sensitivity(pollutant)

    # Compute the integrated absolute temperature potential
    iatp = sum((rad_eff * tau * c_scaled[j] / (tau - D[j])) *
               (tau * (1 - np.exp(-th / tau)) - D[j] * (1 - np.exp(-th / D[j])))
               for j in range(2))

    # Compute the pulse absolute temperature potential
    atp = sum(((rad_eff * tau * c_scaled[j]) / (tau - D[j])) *
              (np.exp(-th / tau) - np.exp(-th / D[j]))
              for j in range(2))

    return iatp, atp


def compute_app(pollutant, rad_eff, rad_eff_a, th, rr_precip_avg, precip_avg):
    """Compute integrated and pulse Absolute Regional Precipitation
    Potential (ARPP) for single lifetime pollutants.

    Parameters
    ----------
    Parameters
    ----------
    pollutant: str
        One of the following single lifetime pollutants:
        - SO2
        - BC
        - CH4

    rad_eff: float
        Global radiative efficiency for CO2 experiments.

    rad_eff_a: float
        Atmospheric component of the radiative efficiency for CO2 experiments.

    th: int
        Time horizon - must not be smaller than 5.

    rr_precip_avg: float
        Average regional precipitation difference.

    precip_avg: float
        Global regional precipitation difference.

    Returns
    -------
    iarpp: float
        Integrated Absolute Regional Precipitation Potential (iARPP).

    slow_iarpp: float
        Slow response component of the iARPP.

    fast_iarpp: float
        Fast response component of the iARPP.

    arpp: float
        Pulse Absolute Regional Precipitation Potential (ARPP).

    slow_arpp: float
        Slow response component of the ARPP.

    fast_arpp: float
        Fast response component of the ARPP.
    """

    assert th >= 5, "The chosen time horizon is smaller than 5."
    assert pollutant in constants.SLP, "{} is not an accepted pollutant".format(pollutant)

    # Load constants
    tau = constants.SPECS[pollutant]['tau']
    fp = constants.SPECS[pollutant]['fp']
    k = constants.SPECS[pollutant]['k']

    # Compute the absolute global temperature potentials
    iagtp, agtp = compute_atp(pollutant, rad_eff, th)

    # Compute the integrated absolute regional precipitation potential (iARPP)
    iarpp = Cf * (k * iagtp - fp * rad_eff_a * tau * (1 - np.exp(-th / tau))) * (rr_precip_avg / precip_avg)

    # Compute the slow response component of the iARPP
    slow_iarpp = Cf * k * iagtp * (rr_precip_avg / precip_avg)

    # Compute the fast response component of the iARPP
    fast_iarpp = Cf * -fp * rad_eff_a * tau * (1 - np.exp(-th / tau)) * (rr_precip_avg / precip_avg)

    # Compute the pulse absolute regional precipitation potential (ARPP)
    arpp = Cf * (k * agtp - fp * rad_eff_a * np.exp(-th / tau)) * (rr_precip_avg / precip_avg)

    # Compute the slow response component of the ARPP
    slow_arpp = Cf * k * agtp * (rr_precip_avg / precip_avg)

    # Compute the fast response component of the ARPP
    fast_arpp = Cf * -fp * rad_eff_a * np.exp(-th / tau) * (rr_precip_avg / precip_avg)

    return iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp
