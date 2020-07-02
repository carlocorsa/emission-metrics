# Third party imports
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

# Local application imports
from plotting import plot_utils
from utils import constants

# Font size
FS = 13

# Line width
LW = 3

# y-axis limit factor
LF = 0.2

# Plot parameters
PARAMS = {
    0: {
        'color': sns.xkcd_rgb["pale red"]
    },
    1: {
        'color': sns.xkcd_rgb["denim blue"]
    },
    2: {
        'color': sns.xkcd_rgb["brown"]
    }
}


def plot_temp_mixed_scenario(temp_dict, time_horizons, time_step=0.01):

    # Compute total response and uncertainty
    tot_temp = sum(temp_dict[pol]['temp'] for pol in temp_dict.keys())
    tot_std = np.sqrt(sum(temp_dict[pol]['std']**2 for pol in temp_dict.keys()))

    # Get total number of points
    n_points = len(tot_temp)

    # Plot style
    sns.set_style("darkgrid")

    # Plot temperature change for each pollutant
    plt.figure(figsize=(12, 8))

    for i, pol in enumerate(temp_dict.keys()):
        plt.plot(temp_dict[pol]['temp'], PARAMS[i]['color'], linewidth=LW)
        plt.fill_between(
            range(n_points),
            temp_dict[pol]['temp'] + temp_dict[pol]['std'],
            temp_dict[pol]['temp'] - temp_dict[pol]['std'],
            facecolor=PARAMS[i]['color'],
            alpha=0.5
        )

    # Plot total temperature change
    plt.plot(tot_temp, sns.xkcd_rgb["jungle green"], linewidth=LW)
    plt.fill_between(
        range(n_points),
        tot_temp + tot_std,
        tot_temp - tot_std,
        facecolor=sns.xkcd_rgb["green"],
        alpha=0.5
    )

    # Get minimum and maximum temperature change
    min_temp = min(
        min(min(temp_dict[pol]['temp']) for pol in temp_dict.keys()),
        min(tot_temp)
    )

    max_temp = max(
        max(max(temp_dict[pol]['temp']) for pol in temp_dict.keys()),
        max(tot_temp)
    )

    y_limits = [np.round((min_temp-LF)*10) / 10, np.round((max_temp+LF)*10) / 10]

    # Plot lines for the time horizons
    plt.plot([0, n_points], [0, 0], 'k--', linewidth=0.8)
    for th in time_horizons:
        plt.plot([th / time_step, th / time_step], y_limits, 'k:', linewidth=0.8)

    # Get optimal x-axis ticks positions and labels
    xt, xtl = plot_utils.optimal_xticks(max(time_horizons), n_points)

    # Set axis ticks, labels and limits
    plt.xlim([0, n_points])
    plt.xlabel('Time (yr)', fontsize=FS)
    plt.xticks(xt, xtl, fontsize=FS)
    plt.ylim(y_limits)

#     plt.ylabel(p_label, fontsize=fs)
#
#     plt.ylim(-0.45,1.30)
# #    plt.legend(loc='best',fontsize=fs)
#     plt.text(200,1.20,'linear increase up to 120%',fontsize=fs-1)
#     plt.text(3100,1.20,'sustained emission at 120%',fontsize=fs-1)
#     plt.text(6600,1.20,'linear decrease down to 100%',fontsize=fs-1)
#     plt.text(1500,0.4, pol1, fontsize=25)
#     plt.text(200,-0.40,'linear increase up to 150%',fontsize=fs-1)
#     plt.text(3100,-0.40,'sustained emission at 150%',fontsize=fs-1)
#     plt.text(6600,-0.40,'linear decrease down to 100%',fontsize=fs-1)
#     plt.text(1500,-0.25, pol2, fontsize=25)
