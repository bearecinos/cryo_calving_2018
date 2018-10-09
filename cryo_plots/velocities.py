import pandas as pd
import os
import geopandas as gpd
import numpy as np
from oggm import cfg, utils
from oggm import workflow

import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
rcParams['axes.labelsize'] = 16
rcParams['xtick.labelsize'] = 16
rcParams['ytick.labelsize'] = 16
rcParams['legend.fontsize'] = 14
# Set figure width and height in cm
width_cm = 14
height_cm = 8


# Reading glacier directories per experiment
MAIN_PATH = os.path.expanduser('~/Documents/cryo_calving_2018_version2/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

no_calving = os.path.join(MAIN_PATH,
'output_data/4_Runs_different_configurations/4_5_Velocities/no_calving/')

with_calving = os.path.join(MAIN_PATH,
'output_data/4_Runs_different_configurations/4_5_Velocities/calving/')

# Reading RGI
RGI_FILE = os.path.join(MAIN_PATH,
                'input_data/01_rgi60_Alaska_modify/01_rgi60_Alaska.shp')

def normalize(vel):
    vel_min = min(vel)
    vel_max = max(vel)

    n_vel = (vel - vel_min) / (vel_max - vel_min)
    return n_vel

def init_velocity(workdir):
    cfg.initialize()
    cfg.PARAMS['use_multiprocessing'] = False
    cfg.PATHS['working_dir'] = workdir
    cfg.PARAMS['border'] = 20

    # Read RGI file
    rgidf = gpd.read_file(RGI_FILE)

    # Run only for Marine terminating
    glac_type = [0, 2]
    keep_glactype = [(i not in glac_type) for i in rgidf.TermType]
    rgidf = rgidf.iloc[keep_glactype]

    return workflow.init_glacier_regions(rgidf)

def calculate_velocity(gdir):
    map_dx = gdir.grid.dx
    fls = gdir.read_pickle('inversion_flowlines')
    cl = gdir.read_pickle('inversion_input')[-1]
    inv = gdir.read_pickle('inversion_output')[-1]

    # vol in m3 and dx in m
    section = (inv['volume'] / inv['dx'])*1e-6

    x = np.arange(fls[-1].nx) * fls[-1].dx * map_dx * 1e-3

    # this flux is in km3
    flux = cl['flux_a0']

    angle = cl['slope_angle']

    velocity = flux / section

    return velocity, normalize(x), angle

gdirs_one = init_velocity(no_calving)

gdirs_two = init_velocity(with_calving)

for gdir, gdir_c in zip(gdirs_one,gdirs_two):
    vel, x, angle = calculate_velocity(gdir)
    vel_c, x_c, angle_c= calculate_velocity(gdir_c)
    diff_angle_c = np.diff(np.arctan(angle_c))
    diff_angle = np.diff(np.arctan(angle))

    plt.figure(1)
    if vel_c[-1] > 0.0:
        plt.plot(x_c, vel_c-vel, '-', label=gdir.rgi_id)
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.xlabel('Normalised distance along the main flowline', size=16)
        plt.ylabel('Velocity difference [$km.yr^{-1}$]', size=16)

    # plt.figure(2)
    # if np.abs(diff_angle[-1]) < 0.025:
    #     plt.plot(x_c[-11:len(angle_c)-1],diff_angle_c[-10:], '-o')
    #     plt.xlabel('Normalised distance along the main flowline', size=14)
    #     plt.ylabel('Slope angle differences', size=14)


plt.margins(0.05)
#plt.show()


plt.savefig(os.path.join(plot_path,'velocity_differences.pdf'),
                              dpi=150, bbox_inches='tight')
