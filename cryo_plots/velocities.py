import pandas as pd
import os
import geopandas as gpd
import numpy as np
from oggm import cfg, utils
from oggm import workflow

import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
rcParams['axes.labelsize'] = 10
rcParams['xtick.labelsize'] = 10
rcParams['ytick.labelsize'] = 10
rcParams['legend.fontsize'] = 10
# Set figure width and height in cm
width_cm = 14
height_cm = 8

cfg.initialize()
# Reading glacier directories per experiment

MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

no_calving = os.path.join(MAIN_PATH,
'output_data/4_Runs_different_configurations/4_5_Velocities/no_calving/')

with_calving = os.path.join(MAIN_PATH,
'output_data/4_Runs_different_configurations/4_5_Velocities/calving/')

# Reading RGI
RGI_FILE = os.path.join(MAIN_PATH,
                'input_data/01_rgi60_Alaska_modify/01_rgi60_Alaska.shp')

def calculate_velocity(gdir):
    map_dx = gdir.grid.dx

    fls = gdir.read_pickle('inversion_flowlines')
    cl = gdir.read_pickle('inversion_input')[-1]
    inv = gdir.read_pickle('inversion_output')[-1]

    section = inv['volume'] / inv['dx']

    x = np.arange(fls[-1].nx) * fls[-1].dx * map_dx * 1e-3

    flux = cl['flux_a0']

    velocity = flux / section

    return velocity, x

def normalize(vel):
    vel_min = min(vel)
    vel_max = max(vel)

    n_vel = (vel - vel_min) / (vel_max - vel_min)
    return n_vel

def standarize(vel):
    vel_mean = np.nanmean(vel)
    vel_std = np.nanstd(vel)
    n_vel = (vel - vel_mean)/vel_std
    return n_vel

cfg.PATHS['working_dir'] = no_calving
cfg.PARAMS['border'] = 20

# Read RGI file
rgidf = gpd.read_file(RGI_FILE)

# Run only for Marine terminating
glac_type = [0, 2]
keep_glactype = [(i not in glac_type) for i in rgidf.TermType]
rgidf = rgidf.iloc[keep_glactype]

gdirs = workflow.init_glacier_regions(rgidf)

for gdir in gdirs:
    velocity, x = calculate_velocity(gdir)
    vel_new = standarize(velocity)
    new_x = standarize(x)
    # ids = ['RGI60-01.09757','RGI60-01.09783','RGI60-01.09810','RGI60-01.10575',
    #         'RGI60-01.10607','RGI60-01.12683','RGI60-01.17843','RGI60-01.20734',
    #         'RGI60-01.20891','RGI60-01.10689','RGI60-01.26732']
    ids = ['RGI60-01.09757',
            'RGI60-01.09783',
            'RGI60-01.09810',
            'RGI60-01.10575',
            'RGI60-01.10607',
            'RGI60-01.12683',
            'RGI60-01.14391',
            'RGI60-01.17843',
            'RGI60-01.20734',
            'RGI60-01.20791',
            'RGI60-01.20891',
            'RGI60-01.10689',
            'RGI60-01.26732',
            'RGI60-01.14443']

    plt.figure(1)
    if gdir.rgi_id in ids:
    #     print(vel_new)
        #indexes = [i for i, e in enumerate(x) if e > 10.0]
        plt.plot(new_x, vel_new, '-', label=gdir.rgi_id)

    plt.xlabel('Standardised distance along the main flowline', size=14)
    plt.ylabel('Standardised velocity', size=14)
    #plt.legend(loc='center left',bbox_to_anchor=(1.0,0.5))
letkm = dict(color='black', ha='left', va='top', fontsize=20,
bbox=dict(facecolor='white', edgecolor='white'))

#plt.text(-2.5, max(velocity)+1, 'a', **letkm)
plt.margins(0.05)
#plt.show()
plt.savefig(os.path.join(plot_path,'velocity_nocalving.png'),
                            dpi=150, bbox_inches='tight')

cfg.PATHS['working_dir'] = with_calving
cfg.PARAMS['border'] = 20

# Read RGI file
rgidf = gpd.read_file(RGI_FILE)

# Run only for Marine terminating
glac_type = [0, 2]
keep_glactype = [(i not in glac_type) for i in rgidf.TermType]
rgidf = rgidf.iloc[keep_glactype]

gdirs = workflow.init_glacier_regions(rgidf)

for gdir in gdirs:
    velocity_c, x = calculate_velocity(gdir)

    vel_new_c = standarize(velocity_c)
    new_x = standarize(x)

    plt.figure(2)
    if velocity_c[-1]>0.0:
        print(gdir.rgi_id)
        #indexes = [i for i, e in enumerate(x) if e > 10.0]
        plt.plot(new_x, vel_new_c, '-', label=gdir.rgi_id)

    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.xlabel('Standardised distance along the main flowline', size=14)
    plt.ylabel('Standardised velocity', size=14)

letkm = dict(color='black', ha='left', va='top', fontsize=20,
             bbox=dict(facecolor='white', edgecolor='white'))

#plt.text(-2.5, max(velocity)+1, 'b', **letkm)
plt.margins(0.05)
#plt.show()
plt.savefig(os.path.join(plot_path,'velocity_calving.png'),
                            dpi=150, bbox_inches='tight')