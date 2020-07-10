# Third party imports
import seaborn as sns
from matplotlib import pyplot as plt

# Local application imports
from plotting import plot_utils


# Font size
FS = 12

# Line width
LW = 2

# Labels
LABELS = [
    'full scaling',
    'ERF scaling',
    'c scaling',
    'no scaling'
]

# Line styles
LINESTYLE = {
    LABELS[0]: '-',
    LABELS[1]: ':',
    LABELS[2]: '--',
    LABELS[3]: '-.'
}

# Colors
COLORS = {
    LABELS[0]: 'k',
    LABELS[1]: 'C2',
    LABELS[2]: 'C0',
    LABELS[3]: 'C1'
}


def plot_scalings(
        artp_potentials, iartp_potentials, time_horizon, pollutant=None, emission_region=None, response_region=None
):

    # Get total number of points
    n_points = len(artp_potentials['artp'])

    # Get optimal x-axis ticks positions and labels
    xt, xtl = plot_utils.optimal_xticks(time_horizon, n_points)

    # Plot style
    sns.set_style("darkgrid")

    # Plot potentials with and without scalings
    plt.figure(figsize=(12, 5))
    # plt.suptitle("{} temperature potentials due to a change in {} emissions from {}".format(
    #     response_region, pollutant, emission_region
    # ), fontsize=FS)

    # Plot ARTP
    plt.subplot(1, 2, 1)

    for i, key in enumerate(artp_potentials.keys()):
        plt.plot(
            artp_potentials[key],
            linewidth=LW,
            label=LABELS[i],
            linestyle=LINESTYLE[LABELS[i]],
            color=COLORS[LABELS[i]]
        )

    plt.legend(loc='lower right', fontsize=FS)
    plt.title("Pulse ARTP", fontsize=FS+2)

    # Set axis ticks, labels and limits
    plt.xlim([0, n_points])
    plt.xlabel('Time (yr)', fontsize=FS)
    plt.xticks(xt, xtl, fontsize=FS)
    plt.ylabel('ARTP (K Tg$^{{-1}}$)', fontsize=FS)
    plt.yticks(fontsize=FS)
    plt.gca().get_yaxis().get_major_formatter().set_powerlimits((0, 0))

    # Plot iARTP
    plt.subplot(1, 2, 2)

    for i, key in enumerate(iartp_potentials.keys()):
        plt.plot(
            iartp_potentials[key],
            linewidth=LW,
            label=LABELS[i],
            linestyle=LINESTYLE[LABELS[i]],
            color=COLORS[LABELS[i]]
        )

    plt.legend(loc='upper right', fontsize=FS)
    plt.title("Sustained ARTP", fontsize=FS+2)

    # Set axis ticks, labels and limits
    plt.xlim([0, n_points])
    plt.xlabel('Time (yr)', fontsize=FS)
    plt.xticks(xt, xtl, fontsize=FS)
    plt.ylabel('iARTP (K Tg$^{{-1}}$)', fontsize=FS)
    plt.yticks(fontsize=FS)
    plt.gca().get_yaxis().get_major_formatter().set_powerlimits((0, 0))

    # Adjust subplots position
    plt.subplots_adjust(top=0.90, bottom=0.10, left=0.10, right=0.95, hspace=0.25, wspace=0.28)
