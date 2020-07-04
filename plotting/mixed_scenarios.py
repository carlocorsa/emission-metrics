# Third party imports
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

# Local application imports
from plotting import plot_utils
from utils import constants

# Font size
FS = 14

# Line width
LW = 3

# y-axis limit factor
LF = 0.3

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


def plot_temp_mixed_scenario(
        temp_dict, time_horizons, scenarios, magnitudes, emission_region, response_region, time_step=0.01
):

    # Get name of pollutants
    pollutants = list(temp_dict.keys())

    # Compute total response and uncertainty
    tot_temp = sum(temp_dict[pol]['temp'] for pol in pollutants)
    tot_std = np.sqrt(sum(temp_dict[pol]['std']**2 for pol in pollutants))

    # Get minimum and maximum temperature change
    min_temp = min(
        min(min(temp_dict[pol]['temp']) for pol in pollutants),
        min(tot_temp)
    )

    max_temp = max(
        max(max(temp_dict[pol]['temp']) for pol in pollutants),
        max(tot_temp)
    )

    # Get total number of points
    n_points = len(tot_temp)

    # Plot style
    sns.set_style("darkgrid")

    # Plot temperature change for each pollutant
    plt.figure(figsize=(12, 8))

    for i, pol in enumerate(pollutants):
        plt.plot(temp_dict[pol]['temp'], PARAMS[i]['color'], linewidth=LW, label=constants.NOTATIONS[pol])
        plt.fill_between(
            range(n_points),
            temp_dict[pol]['temp'] + temp_dict[pol]['std'],
            temp_dict[pol]['temp'] - temp_dict[pol]['std'],
            facecolor=PARAMS[i]['color'],
            alpha=0.5
        )

        # Get strings to use for the plot description
        change_strings = plot_utils.get_change_strings(magnitudes[pol])

        # Add scenarios information
        if pol == "SO2":
            y_padding = min_temp - LF + 0.14
        else:
            y_padding = max_temp + LF - 0.14

        plt.text(1 / time_step, y_padding, '{} {} {}%'.format(
            scenarios[0], change_strings[0], magnitudes[pol][0]
        ), fontsize=FS-1, color=PARAMS[i]['color'], fontweight='bold')
        for j, scenario in enumerate(scenarios[1:]):
            plt.text((time_horizons[j] + 1) / time_step, y_padding, '{} {} {}%'.format(
                scenario, change_strings[j+1], magnitudes[pol][j+1]
            ), fontsize=FS-1, color=PARAMS[i]['color'], fontweight='bold')

    # Plot total temperature change
    plt.plot(
        tot_temp, sns.xkcd_rgb["jungle green"], linewidth=LW,
        label=' + '.join([constants.NOTATIONS[pol] for pol in pollutants])
    )
    plt.fill_between(
        range(n_points),
        tot_temp + tot_std,
        tot_temp - tot_std,
        facecolor=sns.xkcd_rgb["green"],
        alpha=0.5
    )

    # Define y-axis limits based on minimum and maximum values of temperature change
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
    plt.ylabel(r'$\Delta$T (K)', fontsize=FS)
    plt.yticks(fontsize=FS)

    # Plot legend and title
    plt.legend(loc='center right', fontsize=FS, facecolor='white')
    title = "{} T change due to changes in {} emissions from {}".format(
        response_region, " and ".join(pollutants), emission_region
    )
    plt.title(title, fontsize=FS + 2)

    plt.show()
