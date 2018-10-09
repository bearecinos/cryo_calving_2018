# This script will plot the results of glenaxfactors experiment

import numpy as np
import pandas as pd
import os
import glob
import seaborn as sns
import uncertainties as unc
from scipy import stats
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['legend.fontsize'] = 14
# Set figure width and height in cm
width_cm = 14
height_cm = 8


# Reading the data
MAIN_PATH = os.path.expanduser('~/Documents/cryo_calving_2018_version2/')

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

def selec_data(data):
    index = np.where((data > 15.0) & (data < 18.0))
    data = data[(data > 15.0) & (data < 18.0)]
    return data, index

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

# get calving fluxes indexes close to observations

data_frame0_sel, index0 = selec_data(data_frame0)
print(data_frame0_sel)
data_frame1_sel, index1 = selec_data(data_frame1)
print(data_frame1_sel)
data_frame2_sel, index2 = selec_data(data_frame2)
print(data_frame2_sel)
data_frame3_sel, index3 = selec_data(data_frame3)
print(data_frame3_sel)

print(glen_a[index0])

#Observations
obs = np.repeat(15.11 * 1.091, len(glen_a))

###################### Fiting data to linear model #######################################

#Fitting the data to a linear model
#A = np.column_stack([glen_a**0, glen_a])

slope0, intercept0, r_value0, p_value0, std_err0 = stats.linregress(glen_a[index0],
                                                         data_frame0_sel)

slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(glen_a[index1],
                                                         data_frame1_sel)
# print('k1',slope1, intercept1, r_value1, p_value1, std_err1)
slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(glen_a[index2],
                                                         data_frame2_sel)
# print('k2',slope2, intercept2, r_value2, p_value2, std_err2)

slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(glen_a[index3],
                                                         data_frame3_sel)

slope4, intercept4, r_value4, p_value4, std_err4 = stats.linregress(glen_a,
                                                         obs)

# print('k3', slope3, intercept3, r_value3, p_value3, std_err3)

# Calculating uncertainties on slope and intercepts
mx = glen_a.mean()
sx2 = ((glen_a-mx)**2).sum()

sd_intercept0 = std_err0 * np.sqrt(1. / len(glen_a) + mx * mx / sx2)
sd_slope0 = std_err0 * np.sqrt(1. / sx2)

sd_intercept1 = std_err1 * np.sqrt(1. / len(glen_a) + mx * mx / sx2)
sd_slope1 = std_err1 * np.sqrt(1. / sx2)

sd_intercept2 = std_err2 * np.sqrt(1. / len(glen_a) + mx * mx / sx2)
sd_slope2 = std_err2 * np.sqrt(1. / sx2)

sd_intercept3 = std_err3 * np.sqrt(1. / len(glen_a) + mx * mx / sx2)
sd_slope3 = std_err3 * np.sqrt(1. / sx2)

sd_intercept4 = std_err4 * np.sqrt(1. / len(glen_a) + mx * mx / sx2)
sd_slope4 = std_err4 * np.sqrt(1. / sx2)

b0=unc.ufloat(intercept0, sd_intercept0)
b1=unc.ufloat(intercept1, sd_intercept1)
b2=unc.ufloat(intercept2, sd_intercept2)
b3 = unc.ufloat(intercept3, sd_intercept3)
b4 = unc.ufloat(intercept4, sd_intercept4)

m0 = unc.ufloat(slope0, sd_slope0)
m1 = unc.ufloat(slope1, sd_slope1)
m2 = unc.ufloat(slope2, sd_slope2)
m3 = unc.ufloat(slope3, sd_slope3)
m4 = unc.ufloat(slope4, sd_slope4)

print('intercepts',b0,b1,b2,b3,b4)
print('slopes',m0, m1,m2,m3,m4)

glena_intersection_zero = (intercept4 - intercept0) / (slope0 - slope4)
glena_intersection_one = (intercept4 - intercept1) / (slope1 - slope4)
glena_intersection_two = (intercept4 - intercept2) / (slope2 - slope4)
glena_intersection_three = (intercept4 - intercept3) / (slope3 - slope4)

print(glena_intersection_zero)
print(glena_intersection_one)
print(glena_intersection_two)
print(glena_intersection_three)


#################### plotting ###################################

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
plt.plot(glen_a[index0], intercept0 + slope0 * glen_a[index0],"-o", color=sns.xkcd_rgb["dark blue"],
             linewidth=2.5, label='fitted line 0')

plt.plot(glen_a, data_frame1, linestyle="--", #color=sns.xkcd_rgb["green"],
             label=my_labels_glena["x1"], linewidth=2.5)
plt.plot(glen_a[index1], intercept1 + slope1 * glen_a[index1],"-o", color=sns.xkcd_rgb["dark orange"],
             linewidth=2.5, label='fitted line 1')

plt.plot(glen_a, data_frame2, #color=sns.xkcd_rgb["teal"],
             label=my_labels_glena["x2"], linewidth=2.5)
plt.plot(glen_a[index2], intercept2 + slope2 * glen_a[index2],"-o", color=sns.xkcd_rgb["dark green"],
             linewidth=2.5, label='fitted line 2')

plt.plot(glen_a, data_frame3, #color=sns.xkcd_rgb["turquoise"],
             label=my_labels_glena["x3"], linewidth=2.5)
plt.plot(glen_a[index3], intercept3 + slope3 * glen_a[index3],"-o", color=sns.xkcd_rgb["dark red"],
             linewidth=2.5, label='fitted line 3')

plt.plot(glen_a, np.repeat(15.11*1.091, len(glen_a)), '--', color='black',
             label='Regional calving flux. (McNabb et al., 2015)', linewidth=3.0)
plt.xticks(glen_a)
plt.yticks(np.arange(0, 35, 5.0))#max(data_frame2)
plt.ylabel('Alaska calving flux $km³.yr^{-1}$')
plt.xlabel('Glen A ($\mathregular{s^{−1}} \mathregular{Pa^{−3}}$)')
plt.legend()
letkm = dict(color='black', ha='left', va='top', fontsize=20,
                 bbox=dict(facecolor='white', edgecolor='white'))
#plt.text(glen_a[0]-(glen_a[1]/5), 25, 'b', **letkm)
plt.margins(0.05)

plt.show()
#plt.savefig(os.path.join(plot_path, 'glena_factors.png'), dpi=150,
#                 bbox_inches='tight')