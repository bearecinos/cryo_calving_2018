# This script will plot the results of kxfactors experiment

import numpy as np
import uncertainties as unc
from scipy import stats
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
MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

EXPERIMENT_PATH = os.path.join(MAIN_PATH,
                        'output_data/3_Sensitivity_studies_k_A_fs/3_1_k_exp/')

#K x factors directories
WORKING_DIR_one= os.path.join(EXPERIMENT_PATH,
         '1_k_parameter_exp/glacier_char*.csv') #1
WORKING_DIR_two = os.path.join(EXPERIMENT_PATH,
        '2_k_parameter_exp/glacier_char*.csv')  #2

filenames = []
filenames.append(sorted(glob.glob(WORKING_DIR_one)))
filenames.append(sorted(glob.glob(WORKING_DIR_two)))

kfactors = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35,
           0.4, 0.45, 0.5, 0.55, 0.6, 0.65,
           0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
           1.0, 1.05]

k = np.asarray(kfactors)*2.4
print(k)

def read_experiment_file(filename):
    glacier = pd.read_csv(filename)
    glacier = glacier[['rgi_id','terminus_type', 'calving_flux', 'mu_star']]
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

#Observations
obs = np.repeat(15.11 * 1.091, len(k))

#Fitting the data to a linear model
A = np.column_stack([k**0, k])

slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(k,
                                                         data_frame1)
# print('k1',slope1, intercept1, r_value1, p_value1, std_err1)
slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(k,
                                                         data_frame2)
# print('k2',slope2, intercept2, r_value2, p_value2, std_err2)

slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(k,
                                                         obs)
# print('k3', slope3, intercept3, r_value3, p_value3, std_err3)

# Calculating uncertainties on slope and intercepts
mx = k.mean()
sx2 = ((k-mx)**2).sum()

sd_intercept1 = std_err1 * np.sqrt(1. / len(k) + mx * mx / sx2)
sd_slope1 = std_err1 * np.sqrt(1. / sx2)

sd_intercept2 = std_err2 * np.sqrt(1. / len(k) + mx * mx / sx2)
sd_slope2 = std_err2 * np.sqrt(1. / sx2)

sd_intercept3 = std_err3 * np.sqrt(1. / len(k) + mx * mx / sx2)
sd_slope3 = std_err3 * np.sqrt(1. / sx2)

b1=unc.ufloat(intercept1, sd_intercept1)
b2=unc.ufloat(intercept2, sd_intercept2)
b3 = unc.ufloat(intercept3, sd_intercept3)
m1 = unc.ufloat(slope1, sd_slope1)
m2 = unc.ufloat(slope2, sd_slope2)
m3 = unc.ufloat(slope3, sd_slope3)

print('intercepts',b1,b2,b3)
print('slopes',m1,m2,m3)

k_intersection_one = (b3 - b1) / (m1 - m3)
k_intersection_two = (b3 - b2) / (m2 - m3)

print(k_intersection_one)
print(k_intersection_two)


my_labels_fs = {"x1": "A = OGGM default, fs = 0.0",
                "x2": "A = OGGM default, fs = OGGM default"}

# Create figure and axes instances
fig1 = plt.figure(1, figsize=(width_cm, height_cm))

#sns.set_color_codes("colorblind")
sns.set_style("white")

plt.plot(k, data_frame1, "o", color=sns.xkcd_rgb["ocean blue"],
             linewidth=2.5, markersize=12,
             label=my_labels_fs["x1"])

plt.plot(k, intercept1 + slope1 * k, color=sns.xkcd_rgb["ocean blue"],
             linewidth=2.5, label='fitted line 1')

plt.plot(k, data_frame2, "o", color=sns.xkcd_rgb["teal green"],
             linewidth=2.5, markersize=12,
             label=my_labels_fs["x2"])

plt.plot(k, intercept2 + slope2 * k, color=sns.xkcd_rgb["teal green"],
             linewidth=2.5, label='fitted line 2')

plt.plot(k, intercept3 + slope3 * k, '--', color='black', linewidth=3.0,
             label='Regional calving flux. (McNabb et al., 2015)')

#plt.xticks(k)
plt.yticks(np.arange(0, 90, 20.0))
plt.ylabel('Alaska calving flux $km³.yr^{-1}$')
plt.xlabel('Calving constant k ($\mathregular{yr^{-1}}$) ')
plt.legend(bbox_to_anchor=(0.6, 1))
plt.text(0.4, 57.0, 'Intercepts to observations', fontsize=16)
plt.text(0.4,52,'$k_{1}$ = 0.6124 +/- 0.0023', fontsize=16)
plt.text(0.4, 47, '$k_{2}$ = 0.707 +/- 0.004', fontsize=16)
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='white'))

#plt.text(-0.1, 90, 'a', **letkm)
plt.margins(0.05)
#plt.show()
plt.savefig(os.path.join(plot_path, 'k_factors.png'), dpi=150,
                   bbox_inches='tight')