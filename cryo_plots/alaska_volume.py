# This script will calculate the total alaska volume per experiment


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
width_cm = 7
height_cm = 5

def read_experiment_file(filename):
    glacier_run = pd.read_csv(filename, index_col='rgi_id')
    tail = os.path.basename(filename)
    total_volume = glacier_run['inv_volume_km3'].sum()
    return total_volume, tail

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

full_exp_name = []

exclude = set(['4_3_With_calving_exp_onlyMT_vbsl','4_5_Velocities'])

for path, subdirs, files in os.walk(output_dir_path, topdown=True):
    subdirs[:] = [d for d in subdirs if d not in exclude]
    for name in files:
        full_exp_name.append(os.path.join(path,name))

full_exp_name = sorted(full_exp_name)

#print(full_exp_name)

# Reading no calving experiments
volume_per_exp_no_calving = []
exp_name = []

for f in full_exp_name[0:4]:
    total_vol, tails = read_experiment_file(f)
    volume_per_exp_no_calving += [total_vol]
    exp_name += [tails]

# We have to add Marine + Lake + Land terminating
vol_no_calving = [volume_per_exp_no_calving[0] + volume_per_exp_no_calving[1],
                  volume_per_exp_no_calving[2] + volume_per_exp_no_calving[3]]

exp_name_no_calving = [exp_name[0], exp_name[2]]
#print(exp_name_no_calving)
#print(vol_no_calving)


# Reading calving experiments
volume_per_exp_calving = []
exp_name = []

for f in full_exp_name[4:9]:
    total_vol, tails = read_experiment_file(f)
    volume_per_exp_calving += [total_vol]
    exp_name += [tails]

# We have to add Marine + Lake + Land terminating
volume_with_calving = [volume_per_exp_calving[0] + vol_no_calving[0],
                       volume_per_exp_calving[1] + vol_no_calving[0],
                       volume_per_exp_calving[2] + vol_no_calving[1],
                       volume_per_exp_calving[3] + vol_no_calving[1]]

#print(exp_name)
#print(volume_with_calving)


# Making a data frame
all_vol  = [vol_no_calving + volume_with_calving][0]
all_names = [exp_name_no_calving + exp_name][0]

exp_name_number = ['1', '2', '3',
                   '4', '5', '6']

d = {'Experiment No': exp_name_number, 'Alaska volume ($km^{3}$)': all_vol,
     'Original glacier_char name': all_names}

df = pd.DataFrame(data=d)

print(df)

## TODO a nicer way to plot this
# fig1 = plt.figure(1, figsize=(width_cm, height_cm))
#
# g = sns.pointplot(np.arange(1,7,1),'Alaska volume ($km^{3}$)', data=df,
#                   hue='Experiment No', markers='x', scale=1.5)
# g.legend_.remove()
# plt.ylabel('Volume ($km^{3}$)')
# plt.xlabel('Experiment Nº')
# plt.show()

gather_volume_bsl = True

if gather_volume_bsl:
    exp_dir_path = os.path.join(output_dir_path,'4_3_With_calving_exp_onlyMT_vbsl')
    dir_name = os.listdir(exp_dir_path)
    full_dir_name = []

    for d in dir_name:
        full_dir_name.append(os.path.join(exp_dir_path,
                                          d +'/volume_below_sea_level.csv'))

    full_dir_name = sorted(full_dir_name)
    print(full_dir_name)

    # Reading no calving experiments
    vbsl_per_exp = []
    vbsl_per_exp_c = []
    exp_name = []

    for f in full_dir_name:
        total_vol, total_vol_c,  tails = read_experiment_file_vbsl(f)
        vbsl_per_exp += [total_vol]
        vbsl_per_exp_c += [total_vol_c]
        exp_name += [tails]

    exp_name_number = ['1', '2', '3',
                       '4']

    print(exp_name, vbsl_per_exp, vbsl_per_exp_c)

    d = {'Experiment No': exp_name_number, 'Vbsl': vbsl_per_exp,
         'Vbsl with calving': vbsl_per_exp_c,
         'Original glacier_char name': exp_name}

    ds = pd.DataFrame(data=d)

    print(ds)
