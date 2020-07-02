# Third party imports
import numpy as np

# Local application imports
from rem.utils import constants
from rem.simulations import variables

# Load constants
D = constants.D
Cf = constants.CF
A0 = constants.SPECS['CO2']['a0']
Ai = constants.SPECS['CO2']['ai']
TAU = constants.SPECS['CO2']['tau']
Fp = constants.SPECS['CO2']['fp']
K = constants.SPECS['CO2']['k']

# Get scaled climate sensitivity
C_SCALED = variables.get_scaled_climate_sensitivity('CO2')


def compute_atp(rad_eff, th):
    """Compute integrated and pulse Absolute Temperature Potential (ATP).
    Depending on the radiative efficiency `rad_eff` the returned potentials
    can be either regional or global.

    Parameters
    ----------
    rad_eff: float
        Radiative efficiency for CO2 experiments.

    th: int
        Time horizon.

    Returns
    -------
    iatp: float
        Integrated absolute (either regional or global) temperature potential.

    atp: float
        Pulse absolute (either regional or global) temperature potential.

    """

    # Compute the integrated absolute temperature potential
    iatp = rad_eff * (
            sum(
                A0 * C_SCALED[j] * (th - D[j] * (1 - np.exp(-th / D[j]))) +
                sum(
                    ((Ai[i] * TAU[i] * C_SCALED[j]) / (TAU[i] - D[j])) *
                    (TAU[i] * (1 - np.exp(-th / TAU[i])) - D[j] * (1 - np.exp(-th / D[j])))
                    for i in range(3)
                ) for j in range(2)
            )
    )

    # Compute the pulse absolute temperature potential
    atp = rad_eff * (
        sum(
            A0 * C_SCALED[j] * (1 - np.exp(-th / D[j])) +
            sum(
                ((Ai[i] * TAU[i] * C_SCALED[j]) / (TAU[i] - D[j])) *
                (np.exp(-th / TAU[i]) - np.exp(-th / D[j]))
                for i in range(3)
            ) for j in range(2)
        )
    )

    return iatp, atp


def compute_app(rad_eff, rad_eff_a, th, rr_precip_avg, precip_avg):
    """Compute integrated and pulse Absolute Regional
    Precipitation Potential (ARPP) for CO2.

    Parameters
    ----------
    rad_eff: float
        Global radiative efficiency for CO2 experiments.

    rad_eff_a: float
        Atmospheric component of the global
        radiative efficiency for CO2 experiments.

    th: int
        Time horizon.

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

    # Compute the absolute global temperature potentials
    iagtp, agtp = compute_atp(rad_eff, th)

    # Compute the integrated absolute regional precipitation potential (iARPP)
    iarpp = Cf * (K * iagtp - Fp * rad_eff_a * (
            A0 * th + sum(Ai[i] * TAU[i] * (1 - np.exp(-th / TAU[i])) for i in range(3))
    )) * (rr_precip_avg / precip_avg)

    # Compute the slow response component of the iARPP
    slow_iarpp = Cf * K * iagtp * (rr_precip_avg / precip_avg)

    # Compute the fast response component of the iARPP
    fast_iarpp = Cf * (-Fp * rad_eff_a * (
            A0 * th + sum(Ai[i] * TAU[i] * (1 - np.exp(-th / TAU[i])) for i in range(3))
    )) * (rr_precip_avg / precip_avg)

    # Compute the pulse absolute regional precipitation potential (iARPP)
    arpp = Cf * (K * agtp - Fp * rad_eff_a * (
            A0 + sum(Ai[i] * np.exp(-th / TAU[i]) for i in range(3))
    )) * (rr_precip_avg / precip_avg)

    # Compute the slow response component of the iARPP
    slow_arpp = Cf * K * agtp * (rr_precip_avg / precip_avg)

    # Compute the fast response component of the iARPP
    fast_arpp = Cf * (-Fp * rad_eff_a * (
            A0 + sum(Ai[i] * np.exp(-th / TAU[i]) for i in range(3))
    )) * (rr_precip_avg / precip_avg)

    return iarpp, slow_iarpp, fast_iarpp, arpp, slow_arpp, fast_arpp
