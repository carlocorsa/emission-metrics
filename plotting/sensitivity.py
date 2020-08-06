# Third party imports
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

# Local application imports
from plotting import plot_utils


# Font size
FS = 12

# Line width
LW = 2


def plot_scalings(artp_potentials, iartp_potentials, time_horizon):

    # Labels
    labels = [
        'full scaling',
        'ERF scaling',
        'c scaling',
        'no scaling'
    ]

    # Line styles
    linestyle = {
        labels[0]: '-',
        labels[1]: ':',
        labels[2]: '--',
        labels[3]: '-.'
    }

    # Colors
    colors = {
        labels[0]: 'k',
        labels[1]: 'C2',
        labels[2]: 'C0',
        labels[3]: 'C1'
    }

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
            linestyle=linestyle[labels[i]],
            color=colors[labels[i]]
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
            label=labels[i],
            linestyle=linestyle[labels[i]],
            color=colors[labels[i]]
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


def plot_lifetime_range(artp_potentials, iartp_potentials, time_horizon):

    # Get total number of points
    n_points = len(artp_potentials['avg'])

    # Get optimal x-axis ticks positions and labels
    xt, xtl = plot_utils.optimal_xticks(time_horizon, n_points)

    # Plot style
    sns.set_style("white")

    # Plot potentials using different lifetime values
    plt.figure(figsize=(12, 5))

    # Plot ARTP
    ax1 = plt.subplot(1, 2, 1)
    ax1.plot(artp_potentials['avg'], linewidth=LW, color='C0')
    ax1.fill_between(range(n_points), artp_potentials['min'], artp_potentials['max'], facecolor='C0', alpha=0.5)
    ax1.set_title("Pulse ARTP", fontsize=FS+2)
    # ax1.plot([0, n_points], [0, 0], color='k', linestyle='--', linewidth=1)

    # Set axis ticks, labels and limits
    ax1.set_xlim([0, n_points])
    ax1.set_xlabel('Time (yr)', fontsize=FS)
    plt.xticks(xt, xtl, fontsize=FS)
    if max(artp_potentials['avg']) < 0:
        ax1.set_ylim([ax1.get_ylim()[0], 0])
    else:
        ax1.set_ylim([0, ax1.get_ylim()[1]])
    ax1.set_ylabel('ARTP (K Tg$^{{-1}}$)', fontsize=FS)
    ax1.tick_params(labelsize=FS)
    ax1.get_yaxis().get_major_formatter().set_powerlimits((0, 0))

    # Add second axis with ratio of potentials
    ax2 = ax1.twinx()
    ax2.plot(np.array(artp_potentials['avg']) / np.array(artp_potentials['min']), color='C1', linestyle='--')
    ax2.set_ylim([1, 1.4])
    ax2.yaxis.label.set_color('C1')
    ax2.spines["right"].set_edgecolor('C1')
    ax2.tick_params(axis='y', colors='C1')

    # Plot iARTP
    ax3 = plt.subplot(1, 2, 2)
    ax3.plot(iartp_potentials['avg'], linewidth=LW, color='C0')
    ax3.fill_between(range(n_points), iartp_potentials['min'], iartp_potentials['max'], facecolor='C0', alpha=0.5)
    ax3.set_title("Sustained ARTP", fontsize=FS+2)
    # ax3.plot([0, n_points], [0, 0], color='k', linestyle='--', linewidth=1)

    # Set axis ticks, labels and limits
    ax3.set_xlim([0, n_points])
    ax3.set_xlabel('Time (yr)', fontsize=FS)
    plt.xticks(xt, xtl, fontsize=FS)
    if max(artp_potentials['avg']) < 0:
        ax3.set_ylim([ax3.get_ylim()[0], 0])
    else:
        ax3.set_ylim([0, ax3.get_ylim()[1]])
    ax3.set_ylabel('iARTP (K Tg$^{{-1}}$)', fontsize=FS)
    ax3.tick_params(labelsize=FS)
    ax3.get_yaxis().get_major_formatter().set_powerlimits((0, 0))

    # Add second axis with ratio of potentials
    ax4 = ax3.twinx()
    ax4.plot(np.array(iartp_potentials['avg']) / np.array(iartp_potentials['min']), color='C1', linestyle='--')
    ax4.set_ylim([1, 1.4])
    ax4.yaxis.label.set_color('C1')
    ax4.spines["right"].set_edgecolor('C1')
    ax4.tick_params(axis='y', colors='C1')

    # Adjust subplots position
    plt.subplots_adjust(top=0.90, bottom=0.10, left=0.10, right=0.95, hspace=0.25, wspace=0.28)
