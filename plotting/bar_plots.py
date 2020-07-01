# Standard library imports
import string

# Third party imports
from matplotlib import pyplot as plt

# Font size
FS = 13

# Bar width
BW = 0.35

# y-axis limits
Y_LIMITS = {
    'iARTP': {
        'SO2': [-0.026, 0.008],
        'BC': [0, 0.11]
    },
    'iARPP': {
        'SO2': [-0.01, 0.0025],
        'BC': [-0.07, 0.04]
    }
}

# Bar colors
COLORS = {
    'SO2': {
        'A': 'C0',
        'B': 'orange'
    },
    'BC': {
        'A': 'C2',
        'B': 'C5'
    }
}

# Subplots order
ORDER = {
    'SO2': [
        'NHML',
        'US',
        'Europe',
        'EastAsia',
        'India'
    ],
    'BC': [
        'Global',
        'Asia'
    ]
}


def plot_so2_bc_subplot(
        pollutant, emission_region, response_regions, potential_a, potential_b,
        std_a, std_b, potential_name, y_label, subplot_idx, th_a=20, th_b=100
):

    n_regions = len(response_regions)

    assert len(potential_a) == n_regions, \
        "Potential A has {} elements but instead should have {} elements.".format(len(potential_a), n_regions)

    assert len(potential_b) == n_regions, \
        "Potential B has {} elements but instead should have {} elements.".format(len(potential_b), n_regions)

    # Use capital letters to identify the different regions
    region_ids = list(string.ascii_uppercase)[0:n_regions]

    # Define bar positions
    bar_a = [i + 0.08 for i in range(1, n_regions + 1)]
    bar_b = [i + 0.48 for i in range(1, n_regions + 1)]

    # Define X ticks position
    x_ticks = [i + 0.43 for i in range(1, n_regions + 1)]

    # Identify the subplot to use
    ax = plt.subplot(3, 3, subplot_idx)

    # Plot bars
    plt.bar(
        bar_a, potential_a, align='edge', width=BW, label='H = {} yr'.format(th_a),
        yerr=std_a, color=COLORS[pollutant]['A']
    )
    plt.bar(
        bar_b, potential_b, align='edge', width=BW, label='H = {} yr'.format(th_b),
        yerr=std_b, color=COLORS[pollutant]['B']
    )

    # Plot dashed line at y=0
    plt.plot([0, n_regions + 2], [0, 0], 'k', linestyle='--', linewidth=1)
    plt.xlim([0, n_regions + 2])

    # Define plot limits based on plotted potentials
    plt.ylim(Y_LIMITS[potential_name][pollutant])

    # Add x-axis ticks and labels
    plt.xticks(x_ticks, region_ids, ha='center', rotation=0, fontsize=FS-3)

    # Add y-axis ticks and label
    plt.yticks(fontsize=FS-2)
    if subplot_idx == 1 or subplot_idx == 4 or subplot_idx == 7:
        plt.ylabel(y_label, fontsize=FS-1)
    plt.gca().get_yaxis().get_major_formatter().set_powerlimits((0, 0))

    # Add title
    tit = emission_region
    if emission_region == 'EastAsia':
        tit = 'East Asia'
    plt.title(tit, fontsize=FS+2)

    # Add legend for SO2
    if subplot_idx == 5:

        ax.legend(bbox_to_anchor=(2, 0.7), fontsize=FS)
        ax.text(1.6, 0.7, 'SO2', fontsize=FS+7, transform=plt.gca().transAxes)

        text1 = [[region_ids[i] + ': ' + response_regions[i]] for i in range(0, n_regions // 2)]
        text2 = [[region_ids[i] + ': ' + response_regions[i]] for i in range(n_regions // 2, n_regions)]

        t1 = ax.table(cellText=text1, bbox=(1.3, -0.5, 1, 0.8), edges='open', cellLoc='left')
        t2 = ax.table(cellText=text2, bbox=(1.7, -0.5, 1, 0.8), edges='open', cellLoc='left')
        t1.auto_set_font_size(False)
        t1.set_fontsize(FS)
        t2.auto_set_font_size(False)
        t2.set_fontsize(FS)

    # Add legend for BC
    if subplot_idx == 8:

        ax.legend(bbox_to_anchor=(2, 0.4), fontsize=FS)
        ax.text(1.6, 0.4, 'BC', fontsize=FS+7, transform=plt.gca().transAxes)


def plot_so2_bc_double_bars(potential_dict, std_dict, response_regions, potential_name, th_a=20, th_b=100):

    assert potential_name in ['iARTP', 'iARPP'], \
        "{} is not an accepted potential name. Accepted potential names are "

    if potential_name == 'iARTP':
        y_label = 'iARTP (K Tg$^{-1}$)'

    else:
        y_label = 'iARPP (mm day$^{-1}$ Tg$^{-1}$)'

    plt.figure(figsize=(12, 12))

    subplot_idx = 1
    for pol in ['SO2', 'BC']:

        for reg in ORDER[pol]:

            plot_so2_bc_subplot(
                pollutant=pol,
                emission_region=reg,
                response_regions=response_regions,
                potential_a=potential_dict[pol][reg][th_a],
                potential_b=potential_dict[pol][reg][th_b],
                std_a=std_dict[pol][reg][th_a],
                std_b=std_dict[pol][reg][th_b],
                potential_name=potential_name,
                y_label=y_label,
                subplot_idx=subplot_idx,
                th_a=th_a,
                th_b=th_b
            )

            if subplot_idx == 5:
                subplot_idx += 2
            else:
                subplot_idx += 1

    plt.subplots_adjust(top=0.95, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.28)
