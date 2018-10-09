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
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['legend.fontsize'] = 16
# Set figure width and height in cm
width_cm = 14
height_cm = 8


# Reading the data
MAIN_PATH = os.path.expanduser('~/Documents/cryo_calving_2018_version2/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

EXPERIMENT_PATH = os.path.join(MAIN_PATH,
                'output_data/3_Sensitivity_studies_k_A_fs/3_3_fs_exp/')

WORKING_DIR_one = os.path.join(EXPERIMENT_PATH, 'fs_exp1/glacier_char*.csv') #1

WORKING_DIR_two = os.path.join(EXPERIMENT_PATH, 'fs_exp2/glacier_char*.csv')#2


filenames = []
filenames.append(sorted(glob.glob(WORKING_DIR_one)))
filenames.append(sorted(glob.glob(WORKING_DIR_two)))

# Glen_a array or FS
fsfactors = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2]
fs = np.asarray(fsfactors)*5.7e-20

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

cf1 = calving_fluxes[0]
cf2 = calving_fluxes[1]

cf1 = cf1['calving_flux'].sum(axis=0)
cf2 = cf2['calving_flux'].sum(axis=0)

data_frame1 = cf1.T
data_frame2 = cf2.T

my_labels_fs = {"x1": "A = OGGM default, $k_{1}$ = 0.6124 +/- 0.0023",
                "x2": "A = OGGM default, $k_{2}$ = 0.707 +/- 0.004"}

# Create figure and axes instances
fig2 = plt.figure(2, figsize=(width_cm, height_cm))

#sns.set_color_codes("dark")
sns.set_color_codes("colorblind")
sns.set_style("white")

plt.plot(fs, data_frame1,
         label=my_labels_fs["x1"], linewidth=2.5)

plt.plot(fs, data_frame2,
         label=my_labels_fs["x2"], linewidth=2.5)

plt.plot(fs, np.repeat(15.11 * 1.091, len(fs)), '--', color='black',
         label='Regional calving flux. (McNabb et al., 2015)', linewidth=3.0)
plt.xticks(fs)
#plt.yticks(np.arange(0, max(data_frame2), 5.0))
plt.ylabel('Alaska calving flux $km³.yr^{-1}$')
plt.xlabel('Sliding parameter $f_{s}$ ($\mathregular{s^{−1}} \mathregular{Pa^{−3}}$)')
plt.legend(loc='upper right')#, bbox_to_anchor=(1, 0.1))
letkm = dict(color='black', ha='left', va='top', fontsize=20,
             bbox=dict(facecolor='white', edgecolor='white'))
#plt.text(-9e-21, 20, 'c', **letkm)
plt.margins(0.05)
#plt.show()
plt.savefig(os.path.join(plot_path, 'fs_factors.png'), dpi=150,
                 bbox_inches='tight')
