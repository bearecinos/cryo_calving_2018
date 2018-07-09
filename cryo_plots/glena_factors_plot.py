# This script will plot the results of glenaxfactors experiment

import numpy as np
import pandas as pd
import os
import glob
import seaborn as sns
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
rcParams['axes.labelsize'] = 15
rcParams['xtick.labelsize'] = 15
rcParams['ytick.labelsize'] = 15
rcParams['legend.fontsize'] = 15
# Set figure width and height in cm
width_cm = 14
height_cm = 8


# Reading the data
MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

EXPERIMENT_PATH = os.path.join(MAIN_PATH,
                'output_data/3_Sensitivity_studies_k_A_fs/3_2_glen_A_exp/')

#Glen a x factor directories
WORKING_DIR_zero = os.path.join(EXPERIMENT_PATH,
                                'glena_exp1/glacier_char*.csv')     #0
WORKING_DIR_one = os.path.join(EXPERIMENT_PATH,
                                'glena_exp2/glacier_char*.csv')    #1
WORKING_DIR_two = os.path.join(EXPERIMENT_PATH,
                                'glena_exp3/glacier_char*.csv')      #2
WORKING_DIR_three = os.path.join(EXPERIMENT_PATH,
                                'glena_exp4/glacier_char*.csv')      #3

filenames = []
filenames.append(sorted(glob.glob(WORKING_DIR_zero)))
filenames.append(sorted(glob.glob(WORKING_DIR_one)))
filenames.append(sorted(glob.glob(WORKING_DIR_two)))
filenames.append(sorted(glob.glob(WORKING_DIR_three)))

# Glen_a array or FS
factors = [0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
glen_a = np.asarray(factors)*2.4e-24

def read_experiment_file(filename):
    glacier = pd.read_csv(filename)
    glacier = glacier[['rgi_id','terminus_type', 'calving_flux']]
    calving = glacier['calving_flux']
    return calving

calvings = []

for elem in filenames:
    res = []
    for f in elem:
        res.append(read_experiment_file(f))
    calvings.append(res)

calving_fluxes = []

for cf in calvings:
    calving_fluxes.append(pd.concat([c for c in cf], axis=1))
    calving_fluxes[-1] = calving_fluxes[-1][(calving_fluxes[-1].T != 0).any()]
    calving_fluxes[-1] = calving_fluxes[-1].reset_index(drop=True)


cf0 = calving_fluxes[0]
cf1 = calving_fluxes[1]

cf2 = calving_fluxes[2]
cf3 = calving_fluxes[3]

cf0 = cf0['calving_flux'].sum(axis=0)
cf1 = cf1['calving_flux'].sum(axis=0)

cf2 = cf2['calving_flux'].sum(axis=0)
cf3 = cf3['calving_flux'].sum(axis=0)

data_frame0 = cf0.T
data_frame1 = cf1.T

data_frame2 = cf2.T
data_frame3 = cf3.T

my_labels_glena = {"x0": "fs = 0.0, $k_{1}$ = 0.6124 +/- 0.0023",
                   "x1": "fs = 0.0, $k_{2}$ = 0.707 +/- 0.004",
                   "x2": "fs = OGGM default, $k_{1}$ = 0.6124 +/- 0.0023",
                   "x3": "fs = OGGM default, $k_{2}$ = 0.707 +/- 0.004"}
#Create figure and axes instances

fig1 = plt.figure(1, figsize=(width_cm, height_cm))

sns.set_color_codes("colorblind")
sns.set_style("white")

plt.plot(glen_a, data_frame0, linestyle="--", #color=sns.xkcd_rgb["forest green"],
             label=my_labels_glena["x0"], linewidth=2.5)

plt.plot(glen_a, data_frame1, linestyle="--", #color=sns.xkcd_rgb["green"],
             label=my_labels_glena["x1"], linewidth=2.5)

plt.plot(glen_a, data_frame2, #color=sns.xkcd_rgb["teal"],
             label=my_labels_glena["x2"], linewidth=2.5)

plt.plot(glen_a, data_frame3, #color=sns.xkcd_rgb["turquoise"],
             label=my_labels_glena["x3"], linewidth=2.5)

plt.plot(glen_a, np.repeat(15.11*1.091, len(glen_a)), '--', color='black',
             label='Regional calving flux. (McNabb et al., 2015)', linewidth=3.0)
plt.xticks(glen_a)
plt.yticks(np.arange(0, 35, 5.0))#max(data_frame2)
plt.ylabel('Alaska calving flux $km³.yr^{-1}$')
plt.xlabel('Glen A ($\mathregular{s^{−1}} \mathregular{Pa^{−3}}$)')
plt.legend()
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='white'))
plt.text(glen_a[0]-(glen_a[1]/5), 25, 'b', **letkm)
plt.margins(0.05)

#plt.show()
plt.savefig(os.path.join(plot_path, 'glena_factors.png'), dpi=150,
                 bbox_inches='tight')