# This script will calculate the total alaska volume per experiment
# TODO MAKE THIS SCRIPT BETTER IS THE WORSE OF THE WORSE!
import oggm.cfg as cfg
import numpy as np
import pandas as pd
import os
import glob
import seaborn as sns
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
# Set figure width and height in cm
width_cm = 12
height_cm = 8

def calculate_sea_level_equivalent(value):
    rho_ice = 0.900  #Gt km-3
    area_ocean = 3.618e8 # km^2
    height_ocean = 1e-6 # km (1 mm)
    # Volume of water required to raise global sea levels by 1 mm
    vol_water = area_ocean*height_ocean # km^3 of water
    mass_ice = value * rho_ice # Gt
    return np.around(mass_ice*(1 / vol_water),1)

def calculate_sea_level_percentage(voltotal, vbsl):
    return np.around((vbsl*100)/voltotal,2)

def calculate_total_percentage(vol_no_calving,vol_calving):
    percentage = (vol_calving/vol_no_calving)*100
    return np.around(percentage-100,2)

def read_experiment_file(filename):
    glacier_run = pd.read_csv(filename, index_col='rgi_id')
    tail = os.path.basename(filename)
    basedir = os.path.dirname(filename)
    total_volume = glacier_run['inv_volume_km3'].sum()
    return total_volume, tail, basedir

def read_experiment_file_vbsl(filename):
    glacier_run = pd.read_csv(filename)
    tail = os.path.basename(filename)
    total_volume = glacier_run['volume bsl'].sum()
    total_volume_c = glacier_run['volume bsl with calving'].sum()
    return total_volume, total_volume_c, tail


# Reading the data
MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

output_dir_path = os.path.join(MAIN_PATH,
                        'output_data/4_Runs_different_configurations/')

exclude = set(['4_3_With_calving_exp_onlyMT_vbsl','4_5_Velocities'])


# Just paths for Land and lake glacier_char.csv experiment file
full_exp_name_land_lake = []

for path, subdirs, files in os.walk(output_dir_path, topdown=True):
    subdirs[:] = [d for d in subdirs if d not in exclude]
    subdirs[:] = [d for d in subdirs if "onlyMT" not in d]
    subdirs[:] = sorted(subdirs)

    for name in files:
        full_exp_name_land_lake.append(os.path.join(path,name))

#print(full_exp_name_land_lake)

# Just paths for marine glacier_char.csv experiment file
full_exp_name = []

for path, subdirs, files in os.walk(output_dir_path, topdown=True):
    subdirs[:] = [d for d in subdirs if d not in exclude]
    subdirs[:] = [d for d in subdirs if "rest" not in d]
    subdirs[:] = sorted(subdirs)

    for name in files:
        full_exp_name.append(os.path.join(path,name))

#print(full_exp_name[0:8])

# Volumes for No calving experiments
# Reading no calving experiments

#print(full_exp_name[0:6])
volume_per_exp_no_calving = []
exp_name = []
exp_number = [1, 2, 3, 4, 5, 6, 7, 8]

for f in full_exp_name[0:8]:
    total_vol, tails, basedir = read_experiment_file(f)
    volume_per_exp_no_calving += [np.around(total_vol,2)]
    exp_name += [basedir]

print('Experiment name', exp_number)
print('Volume before calving', volume_per_exp_no_calving)

volume_per_exp_no_calving_sle = []
for value in volume_per_exp_no_calving:
    volume_per_exp_no_calving_sle.append(calculate_sea_level_equivalent(value))
print('Volume before calving SLE', volume_per_exp_no_calving_sle)

# Volumes for calving experiments
# Reading calving experiments

#print(full_exp_name[8:len(full_exp_name)])
volume_per_exp_calving = []
exp_name = []
exp_number_c = [10, 3, 4, 5, 6, 7, 8, 9]

for f in full_exp_name[8:len(full_exp_name)]:
    total_vol, tails, basedir= read_experiment_file(f)
    volume_per_exp_calving += [np.around(total_vol,2)]
    exp_name += [basedir]

print('Experiment name', exp_number_c)
print('Volume after calving', volume_per_exp_calving)

volume_per_exp_calving_sle = []

for value in volume_per_exp_calving:
    volume_per_exp_calving_sle.append(calculate_sea_level_equivalent(value))
print('Volume after calving SLE', volume_per_exp_calving_sle)

#Volumes for land and lake terminating before calving
volume_land_lake = []
exp_name_land_lake = []

for f in full_exp_name_land_lake:
    total_vol, tails, basedir=read_experiment_file(f)
    volume_land_lake += [np.around(total_vol,2)]
    exp_name_land_lake += [basedir]

print('Experiment name', exp_name_land_lake)
print('Land and lake volume', volume_land_lake)


volume_land_lake_sle = []
for value in volume_land_lake:
    volume_land_lake_sle.append(calculate_sea_level_equivalent(value))
print('Land and lake volume SLE', volume_land_lake_sle)



gather_volume_bsl = True

if gather_volume_bsl:
    exp_dir_path = os.path.join(output_dir_path,'4_3_With_calving_exp_onlyMT_vbsl')
    dir_name = os.listdir(exp_dir_path)
    full_dir_name = []

    for d in dir_name:
        full_dir_name.append(os.path.join(exp_dir_path,
                                          d +'/volume_below_sea_level.csv'))

    full_dir_name = sorted(full_dir_name)
    #print(full_dir_name)

    # Reading no calving experiments
    vbsl_per_exp = []
    vbsl_per_exp_c = []
    exp_name = []

    for f in full_dir_name:
        total_vol, total_vol_c,  tails = read_experiment_file_vbsl(f)
        vbsl_per_exp += [np.around(total_vol,2)]
        vbsl_per_exp_c += [np.around(total_vol_c,2)]
        exp_name += [tails]


    print('Experiment', exp_number)
    print('no calving vbsl', vbsl_per_exp)
    print('with calving vbsl', vbsl_per_exp_c)


    # sea level equivalent
    vbsl_per_exp_sle = []
    vbsl_per_exp_c_sle = []
    for i, j in zip(vbsl_per_exp, vbsl_per_exp_c):
        vbsl_per_exp_sle.append(calculate_sea_level_equivalent(i))
        vbsl_per_exp_c_sle.append(calculate_sea_level_equivalent(j))

    print('sea level equivalent vbsl no calving', vbsl_per_exp_sle)
    print('sea level equivalent vbsl calving', vbsl_per_exp_c_sle)

    # Calculate percentage of volume below sea level
    vbsl_percentage = []
    vbsl_percentage_c = []

    for i, j in zip(volume_per_exp_no_calving, vbsl_per_exp):
        vbsl_percentage.append(calculate_sea_level_percentage(i,j))

    for i, j in zip(volume_per_exp_calving, vbsl_per_exp_c):
        vbsl_percentage_c.append(calculate_sea_level_percentage(i,j))

    #print('vol percentage bsl no calving',vbsl_percentage)
    #print('vol percantage bsl calving', vbsl_percentage_c)

    percentage_vol_changed = []
    for i, j in zip(volume_per_exp_no_calving, volume_per_exp_calving):
        percentage_vol_changed.append(calculate_total_percentage(i,j))

    print(percentage_vol_changed)

    d = {'Experiment No': exp_number,
         'Volume no calving': volume_per_exp_no_calving,
         'no calving vbsl': vbsl_per_exp,
         'no calving % below sea level': vbsl_percentage,
         'Volume with calving': volume_per_exp_calving,
         'with calving % below sea level': vbsl_percentage_c,
         'with calving vbsl': vbsl_per_exp_c,
         'Volume %':percentage_vol_changed}

    ds = pd.DataFrame(data=d)
    ds = ds.sort_values(by=['Experiment No'])

    print('-----------------------------------')
    print('TABLE',ds)

    # Volume differences
    vol_diff = []
    vol_diff_bsl = []

    for i, j in zip(volume_per_exp_calving, volume_per_exp_no_calving):
        vol_diff.append(i-j)

    for i, j in zip(vbsl_per_exp_c, vbsl_per_exp):
        vol_diff_bsl.append(i-j)

    print('total vol calving - no calving', np.round(vol_diff,2))
    print('total vol bsl calving - no calving', np.round(vol_diff_bsl,2))

import matplotlib.ticker as mtick

# exit()
fig = plt.figure(figsize=(width_cm, height_cm))
sns.set(style="white", context="talk")

ax1=fig.add_subplot(111)
ax2= ax1.twiny()

# Plot settings
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['legend.fontsize'] = 14

N = len(ds)
ind = np.arange(N)
graph_width = 0.35
labels = ds['Experiment No'].values

bars1 = ds['no calving vbsl'].values
bars2 = ds['Volume no calving'].values
#print(bars2)

bars3 = ds['with calving vbsl'].values
bars4 = ds['Volume with calving'].values

sns.set_color_codes()
sns.set_color_codes("colorblind")

p1 = ax1.barh(ind, bars1*-1, color="indianred", edgecolor="white", height=graph_width)
p2 = ax1.barh(ind, bars2, height=graph_width, edgecolor="white")

p3 = ax1.barh(ind - graph_width, bars3*-1, color="indianred",edgecolor="white", height=graph_width)
p4 = ax1.barh(ind - graph_width, bars4, edgecolor="white",
              height=graph_width)


ax1.set_xticks([-1000, 0, 1000, 2000, 3000, 4000, 5000])
ax1.set_xticklabels(abs(ax1.get_xticks()), fontsize=20)
ax2.set_xlim(ax1.get_xlim())
ax2.tick_params('Volume [mm SLE]', fontsize=20)
ax2.set_xticks(ax1.get_xticks())
array = ax1.get_xticks()
#print(array)

sle = []
for value in array:
    sle.append(abs(calculate_sea_level_equivalent(value)))
#print(sle)

ax2.set_xticklabels(sle,fontsize=20)
ax2.set_xlabel('Volume [mm SLE]', fontsize=18)

plt.yticks(ind - graph_width/2, labels)

ax1.set_yticklabels(labels, fontsize=20)
ax1.set_ylabel('Model configurations', fontsize=18)
ax1.set_xlabel('Volume [km³]',fontsize=18)
plt.legend((p2[0], p4[0], p1[0]),
           ('Volume without frontal ablation', 'Volume with frontal ablation', 'Volume below sea level'),
            frameon=True,
            bbox_to_anchor=(1.1, -0.1), ncol=3, fontsize=15)
plt.margins(0.05)

#plt.show()
plt.savefig(os.path.join(plot_path, 'marine_volume.pdf'), dpi=150,
                  bbox_inches='tight')
