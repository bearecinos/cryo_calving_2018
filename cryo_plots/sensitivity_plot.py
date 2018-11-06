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
rcParams['legend.fontsize'] = 18
# Set figure width and height in cm
width_cm = 14
height_cm = 7


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
    glacier = glacier[['rgi_id','terminus_type', 'calving_flux']]#, 'mu_star']]
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

###################### Fiting data to linear model #######################################

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

################### reading Glen A exp ##########################################

EXPERIMENT_PATH_A = os.path.join(MAIN_PATH,
                'output_data/3_Sensitivity_studies_k_A_fs/3_2_glen_A_exp/')

#Glen a x factor directories
WORKING_DIR_zero_A = os.path.join(EXPERIMENT_PATH_A,
                                'glena_exp1/glacier_char*.csv')     #0
WORKING_DIR_one_A = os.path.join(EXPERIMENT_PATH_A,
                                'glena_exp2/glacier_char*.csv')    #1
WORKING_DIR_two_A = os.path.join(EXPERIMENT_PATH_A,
                                'glena_exp3/glacier_char*.csv')      #2
WORKING_DIR_three_A = os.path.join(EXPERIMENT_PATH_A,
                                'glena_exp4/glacier_char*.csv')      #3

filenames_A = []
filenames_A.append(sorted(glob.glob(WORKING_DIR_zero_A)))
filenames_A.append(sorted(glob.glob(WORKING_DIR_one_A)))
filenames_A.append(sorted(glob.glob(WORKING_DIR_two_A)))
filenames_A.append(sorted(glob.glob(WORKING_DIR_three_A)))

# Glen_a array or FS
factors = [0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
glen_a = np.asarray(factors)*2.4e-24

calvings_A = []

for elem in filenames_A:
    res = []
    for f in elem:
        res.append(read_experiment_file(f))
    calvings_A.append(res)

calving_fluxes_A = []

for cf in calvings_A:
    calving_fluxes_A.append(pd.concat([c for c in cf], axis=1))
    calving_fluxes_A[-1] = calving_fluxes_A[-1][(calving_fluxes_A[-1].T != 0).any()]
    calving_fluxes_A[-1] = calving_fluxes_A[-1].reset_index(drop=True)


cf0_A = calving_fluxes_A[0]
cf1_A = calving_fluxes_A[1]

cf2_A = calving_fluxes_A[2]
cf3_A = calving_fluxes_A[3]

cf0_A = cf0_A['calving_flux'].sum(axis=0)
cf1_A = cf1_A['calving_flux'].sum(axis=0)

cf2_A = cf2_A['calving_flux'].sum(axis=0)
cf3_A = cf3_A['calving_flux'].sum(axis=0)

data_frame0_A = cf0_A.T
data_frame1_A = cf1_A.T

data_frame2_A = cf2_A.T
data_frame3_A = cf3_A.T

my_labels_glena = {"x0": "fs = 0.0, $k_{1}$ = 0.61",
                   "x1": "fs = 0.0, $k_{2}$ = 0.70",
                   "x2": "fs = OGGM default, $k_{1}$ = 0.61",
                   "x3": "fs = OGGM default, $k_{2}$ = 0.70"}

####################### Reading fs experiments ##################################3
EXPERIMENT_PATH_fs = os.path.join(MAIN_PATH,
                'output_data/3_Sensitivity_studies_k_A_fs/3_3_fs_exp/')

WORKING_DIR_one_fs = os.path.join(EXPERIMENT_PATH_fs, 'fs_exp1/glacier_char*.csv') #1

WORKING_DIR_two_fs = os.path.join(EXPERIMENT_PATH_fs, 'fs_exp2/glacier_char*.csv')#2


filenames_fs = []
filenames_fs.append(sorted(glob.glob(WORKING_DIR_one_fs)))
filenames_fs.append(sorted(glob.glob(WORKING_DIR_two_fs)))

# Glen_a array or FS
fsfactors = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2]
fs = np.asarray(fsfactors)*5.7e-20

calvings_fs = []

for elem in filenames_fs:
    res = []
    for f in elem:
        res.append(read_experiment_file(f))
    calvings_fs.append(res)

calving_fluxes_fs = []

for cf in calvings_fs:
    calving_fluxes_fs.append(pd.concat([c for c in cf], axis=1))
    calving_fluxes_fs[-1] = calving_fluxes_fs[-1][(calving_fluxes_fs[-1].T != 0).any()]
    calving_fluxes_fs[-1] = calving_fluxes_fs[-1].reset_index(drop=True)

cf1_fs = calving_fluxes_fs[0]
cf2_fs = calving_fluxes_fs[1]

cf1_fs = cf1_fs['calving_flux'].sum(axis=0)
cf2_fs = cf2_fs['calving_flux'].sum(axis=0)

data_frame1_fs = cf1_fs.T
data_frame2_fs = cf2_fs.T

my_labels_fs = {"x1": "A = OGGM default, $k_{1}$ = 0.61",
                "x2": "A = OGGM default, $k_{2}$ = 0.70"}


######################################## plots ######################################

my_labels_k = {"x1": "A = OGGM default, fs = 0.0",
                "x2": "A = OGGM default, fs = OGGM default"}

from matplotlib import gridspec
from matplotlib.ticker import ScalarFormatter

# Create figure and axes instances
fig1 = plt.figure(1, figsize=(width_cm, height_cm*3))

gs = gridspec.GridSpec(3, 1, hspace=0.2)

#sns.set_color_codes("colorblind")
plt.subplot(gs[0])
sns.set_style("white")

plt.plot(k, data_frame1, "o", color=sns.xkcd_rgb["ocean blue"],
             linewidth=2.5, markersize=12,
             label=my_labels_k["x1"])

plt.plot(k, intercept1 + slope1 * k, color=sns.xkcd_rgb["ocean blue"],
             linewidth=2.5, label='fitted line 1')

plt.plot(k, data_frame2, "o", color=sns.xkcd_rgb["teal green"],
             linewidth=2.5, markersize=12,
             label=my_labels_k["x2"])

plt.plot(k, intercept2 + slope2 * k, color=sns.xkcd_rgb["teal green"],
             linewidth=2.5, label='fitted line 2')

plt.plot(k, intercept3 + slope3 * k, '--', color='black', linewidth=3.0,
             label='Frontal ablation (McNabb et al., 2015)')

plt.fill_between(k,(intercept3 + slope3 * k)-3.96, (intercept3 + slope3 * k)+3.96,
                 color=sns.xkcd_rgb["grey"], alpha=0.3)

plt.yticks(np.arange(0, 90, 20.0))

plt.ylabel('Alaska frontal ablation \n [$km³.yr^{-1}$]')
plt.xlabel('Calving constant k [$\mathregular{yr^{-1}}$] ')
plt.legend(bbox_to_anchor=(0.02, 0.8), loc='center left', borderaxespad=0.)

plt.text(0.4, 47.0, 'Intercepts to observations', fontsize=18)
plt.text(0.4,41,'$k_{1}$ = 0.61', fontsize=18)
plt.text(0.4, 35, '$k_{2}$ = 0.70', fontsize=18)
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='black'))
plt.text(0.14, 84.5, 'a', **letkm)
plt.margins(0.05)

plt.subplot(gs[1])
sns.set_color_codes("colorblind")
sns.set_style("white")

plt.plot(glen_a, data_frame0_A, linestyle="--", #color=sns.xkcd_rgb["forest green"],
             label=my_labels_glena["x0"], linewidth=2.5)

plt.plot(glen_a, data_frame1_A, linestyle="--", #color=sns.xkcd_rgb["green"],
             label=my_labels_glena["x1"], linewidth=2.5)

plt.plot(glen_a, data_frame2_A, #color=sns.xkcd_rgb["teal"],
             label=my_labels_glena["x2"], linewidth=2.5)

plt.plot(glen_a, data_frame3_A, #color=sns.xkcd_rgb["turquoise"],
             label=my_labels_glena["x3"], linewidth=2.5)

plt.plot(glen_a, np.repeat(15.11*1.091, len(glen_a)), '--', color='black',
             label='Frontal ablation (McNabb et al., 2015)', linewidth=3.0)

plt.fill_between(glen_a,np.repeat(15.11*1.091-3.96, len(glen_a)),
                 np.repeat(15.11*1.091+3.96, len(glen_a)),
                 color=sns.xkcd_rgb["grey"], alpha=0.3)

plt.xticks(glen_a)
plt.yticks(np.arange(0, 35, 3.0))

plt.ylabel('Alaska frontal ablation \n [$km³.yr^{-1}$]')
plt.xlabel('Glen A [$\mathregular{s^{−1}} \mathregular{Pa^{−3}}$]')
plt.legend(bbox_to_anchor=(0.4, 0.8), loc='center left', borderaxespad=0.)
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='black'))
plt.text(glen_a[0]-1.15e-25, 27.25, 'b', **letkm)
plt.margins(0.05)


ax = plt.subplot(gs[2])
#sns.set_color_codes("dark")
sns.set_color_codes("colorblind")
sns.set_style("white")

plt.plot(fs, data_frame1_fs,
         label=my_labels_fs["x1"], linewidth=2.5)

plt.plot(fs, data_frame2_fs,
         label=my_labels_fs["x2"], linewidth=2.5)

plt.plot(fs, np.repeat(15.11 * 1.091, len(fs)), '--', color='black',
         label='Frontal ablation (McNabb et al., 2015)', linewidth=3.0)

plt.fill_between(fs,np.repeat(15.11*1.091-3.96, len(fs)),
                 np.repeat(15.11*1.091+3.96, len(fs)),
                 color=sns.xkcd_rgb["grey"], alpha=0.3)

plt.xticks(fs)

plt.yticks(np.arange(0, 25, 1))
plt.ylabel('Alaska frontal ablation \n [$km³.yr^{-1}$]')
plt.xlabel('Sliding parameter $f_{s}$ [$\mathregular{s^{−1}} \mathregular{Pa^{−3}}$]')
plt.legend()
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='black'))
plt.text(-3e-21, 20.73, 'c', **letkm)
plt.margins(0.05)
plt.subplots_adjust(hspace=0.2)

plt.savefig(os.path.join(plot_path, 'sensitivity.pdf'), dpi=150,
                   bbox_inches='tight')