# This script will plot the results of calving vs volume experiment


import numpy as np
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import OrderedDict
import seaborn as sns

# Plot settings
rcParams['axes.labelsize'] = 15
rcParams['xtick.labelsize'] = 15
rcParams['ytick.labelsize'] = 15
rcParams['legend.fontsize'] = 12
# Set figure width and height in cm
width_cm = 12
height_cm = 6

MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

WORKING_DIR = os.path.join(MAIN_PATH,
    'output_data/2_Calving_vs_Volume_exp/sensitivity_calvsvolRGI60-01.*.csv')

plot_path = os.path.join(MAIN_PATH, 'plots/')

filenames = sorted(glob.glob(WORKING_DIR))


def percentage(percent, whole):
    return (percent / whole)

# Create figure and axes instances
fig1 = plt.figure(1,figsize=(width_cm, height_cm))

percent = []
# "warm grey", "gunmetal", "dusky blue"
my_labels = {"x1": "volume > 500 km³", "x2": "500 km³ > volume > 100 km³",
             "x3": "100 km³ > volume > 10 km³", "x4": "10 km³ > volume > 0 km³"}

sns.set_style("white")
for j, f in enumerate(filenames):
    glacier = pd.read_csv(f)
    calving = glacier['calving_flux']
    volume = glacier['volume']
    if volume[0] > 500:
        percent = volume / volume[0]
        plt.plot(calving, percent, sns.xkcd_rgb["burnt orange"],
                 label=my_labels["x1"], linewidth=2.5)
    if 500 > volume[0] > 100:
        percent = volume / volume[0]
        see = np.diff(percent)
        indexes = [i for i, e in enumerate(see) if e!=0]
        plt.plot(calving[indexes], percent[indexes], sns.xkcd_rgb["teal green"],
                     label=my_labels["x2"], linewidth=2.5)
    if 100 > volume[0] > 10:
        percent = volume / volume[0]
        see = np.diff(percent)
        indexes = [i for i, e in enumerate(see) if e != 0]
        plt.plot(calving[indexes], percent[indexes], sns.xkcd_rgb["ocean blue"],
                 label=my_labels["x3"], linewidth=2.5)
    # if 10 > volume[0] > 0:
    #     percent = volume/volume[0]
    #     see = np.diff(percent)
    #     indexes = [i for i, e in enumerate(see) if e != 0]
    #     plt.plot(calving[indexes[0]], percent[indexes[0]], color='pink',
    #               label=my_labels["x4"], linewidth=2.5)
    else:
        pass

    plt.xlabel('Calving flux $km^{3}$$yr^{-1}$', size=20)
    plt.ylabel('Standardised glacier volume', size=20)
    plt.margins(0.05)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')
    letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='white'))
    plt.text(-0.7, 1.7, 'a', **letkm)
#plt.show()
plt.savefig(os.path.join(plot_path,'calving_volume.png'),
                              dpi=150, bbox_inches='tight')


fig2 = plt.figure(2, figsize=(width_cm, height_cm))
sns.set_style("white")
for j, f in enumerate(filenames):
    glacier = pd.read_csv(f)
    calving = glacier['calving_flux']
    mu_star = glacier['mu_star']
    volume = glacier['volume']
    if volume[0] > 500:
        plt.plot(calving, mu_star, sns.xkcd_rgb["burnt orange"],
                 label=my_labels["x1"], linewidth=2.5)
    if 500 > volume[0] > 100:
        plt.plot(calving, mu_star, sns.xkcd_rgb["teal green"],
                 label=my_labels["x2"], linewidth=2.5)
    if 100 > volume[0] > 10:
         plt.plot(calving, mu_star, sns.xkcd_rgb["ocean blue"],
                  label=my_labels["x3"], linewidth=2.5)
    # if  10 > volume[0] > 0:
    #     plt.plot(calving[0:150], mu_star[0:150], color='pink',
    #             label=my_labels["x4"],  linewidth=2.0)
    else:
        pass
        # plt.plot(calving[0:2], mu_star[0:2], color='r', linewidth=2.0)
    plt.xlabel('Calving flux $km^{3}$$yr^{-1}$', size=20)
    plt.ylabel('Temperature sensitivity ($\mu^{*}$)', size=20)
    plt.margins(0.05)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')
    letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='white'))
    plt.text(-0.7, 150, 'b', **letkm)
#plt.show()
plt.savefig(os.path.join(plot_path,'calving_mu_star.png'),
                             dpi=150, bbox_inches='tight')