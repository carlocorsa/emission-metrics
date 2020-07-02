# Third party imports
import numpy as np


def optimal_xticks(x_max, n_points):
    """Get optimal x ticks position and label.

    Parameters
    ----------
    x_max: int
        x-axis max value

    n_points: int
        Number of x points.

    Returns
    -------
    xt: list
        List with position of x-axis ticks.

    xtl: list
        List with labels of x-axis ticks.
    """

    if x_max % 10 == 0:
        xt = np.linspace(n_points / 10, n_points, 10)
        xtl = range(x_max // 10, x_max + 1, x_max // 10)
    elif x_max % 5 == 0:
        xt = np.linspace(n_points / 5, n_points, 5)
        xtl = range(x_max // 5, x_max + 1, x_max // 5)
    else:
        x_ceil = np.ceil(x_max / 10.) * 10
        n_ceil = x_ceil * 5
        xt = np.linspace(n_ceil / 10, n_ceil, 10)
        xtl = np.linspace(x_ceil / 10, x_ceil, 10).astype(int)

    return xt, xtl
