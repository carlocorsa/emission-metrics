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


def get_change_strings(magnitudes):
    """Get the correct strings for plotting mixed emission scenarios.

    Parameters
    ----------
    magnitudes: list
        Magnitudes for each emission scenario.

    Returns
    -------
    change_strings: list
        Strings for each emission scenario.
        Each element can be either of "increase up to"
        or "decrease down to".
    """

    change_strings = []
    if magnitudes[0] > 100:
        change_strings.append("increase up to")
    elif magnitudes[0] == 100:
        change_strings.append("emissions at")
    else:
        change_strings.append("decrease down to")

    for i, mag in enumerate(magnitudes[1:]):
        if mag > magnitudes[i]:
            change_strings.append("increase up to")
        elif mag == magnitudes[i]:
            change_strings.append("emissions at")
        else:
            change_strings.append("decrease down to")

    return change_strings
