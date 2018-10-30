# This will run OGGM on the Alaska Region with calving

from __future__ import division
import oggm

# Module logger
import logging
log = logging.getLogger(__name__)

# Python imports
import os
import geopandas as gpd
import numpy as np
import pandas as pd
import shutil

# Locals
import oggm.cfg as cfg
from oggm import workflow
from oggm import tasks
from oggm.workflow import execute_entity_task
from oggm import utils

# Time
import time
start = time.time()

# Regions:
# Alaska
rgi_region = '01'

# Initialize OGGM and set up the run parameters
# ---------------------------------------------

cfg.initialize()
rgi_version = '6'

SLURM_WORKDIR = os.environ["WORKDIR"]
# Local paths (where to write output and where to download input)
WORKING_DIR = SLURM_WORKDIR

MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

RGI_FILE = os.path.join(MAIN_PATH,
                        'input_data/01_rgi60_Alaska_modify/01_rgi60_Alaska.shp')

Columbia_prepro = os.path.join(MAIN_PATH,
          'output_data/1_Columbia_Glacier_runs/1_preprocessing/per_glacier/')

Columbia_dir = os.path.join(Columbia_prepro,
                            'RGI60-01/RGI60-01.10/RGI60-01.10689')

cfg.PATHS['working_dir'] = WORKING_DIR
# Use multiprocessing
cfg.PARAMS['use_multiprocessing'] = True
# We make the border 80 so we can use the Columbia itmix DEM
cfg.PARAMS['border'] = 20
# Set to True for operational runs
cfg.PARAMS['continue_on_error'] = True
#For tidewater we set this to False
cfg.PARAMS['correct_for_neg_flux'] = False
cfg.PARAMS['filter_for_neg_flux'] = False
# We will needs this set to true for the calving loop
cfg.PARAMS['allow_negative_mustar'] = True
cfg.PARAMS['inversion_glen_a'] = 2.3346e-24

# We use intersects
path = utils.get_rgi_intersects_region_file(rgi_region, version=rgi_version)
cfg.set_intersects_db(path)

# RGI file, 4 Marine-terminating glaciers were merged with their respective
# branches, this is why we use our own version of RGI v6
rgidf = gpd.read_file(RGI_FILE)

# Pre-download other files which will be needed later
_ = utils.get_cru_file(var='tmp')
p = utils.get_cru_file(var='pre')
print('CRU file: ' + p)

# Some controllers maybe this is not necessary
RUN_GIS_mask = True
RUN_GIS_PREPRO = True # run GIS pre-processing tasks (before climate)
RUN_CLIMATE_PREPRO = True # run climate pre-processing tasks
RUN_INVERSION = True  # run bed inversion
With_calving = True

# Run only for Marine terminating
glac_type = [0, 2]
keep_glactype = [(i not in glac_type) for i in rgidf.TermType]
rgidf = rgidf.iloc[keep_glactype]

# Sort for more efficient parallel computing
rgidf = rgidf.sort_values('Area', ascending=False)

log.info('Starting run for RGI reg: ' + rgi_region)
log.info('Number of glaciers: {}'.format(len(rgidf)))

# Go - initialize working directories
# -----------------------------------
gdirs = workflow.init_glacier_regions(rgidf)

k = 0.707

# Defining a calving function
def calving_from_depth(gdir, k):
    """ Finds a calving flux based on the approaches proposed by
        Huss and Hock, (2015) and Oerlemans and Nick (2005).
        We take the initial output of the model and surface elevation data
        to calculate the water depth of the calving front.
    """
    # Read inversion output
    cl = gdir.read_pickle('inversion_output')[-1]
    fl = gdir.read_pickle('inversion_flowlines')[-1]

    width = fl.widths[-1] * gdir.grid.dx

    t_altitude = cl['hgt'][-1]  # this gives us the altitude at the terminus
    if t_altitude < 0:
        t_altitude = 0

    thick = cl['thick'][-1]

    w_depth = thick - t_altitude

    # print('t_altitude_fromfun', t_altitude)
    # print('depth_fromfun', w_depth)
    # print('thick_fromfun', thick)
    # print('width', width)
    out = k * thick * w_depth * width / 1e9
    if out < 0:
        out = 0
    return out, w_depth, thick, width

if RUN_GIS_mask:
    execute_entity_task(tasks.glacier_masks, gdirs)

#We copy Columbia glacier dir with the itmix dem
shutil.rmtree(os.path.join(WORKING_DIR,
                           'per_glacier/RGI60-01/RGI60-01.10/RGI60-01.10689'))
shutil.copytree(Columbia_dir, os.path.join(WORKING_DIR,
                            'per_glacier/RGI60-01/RGI60-01.10/RGI60-01.10689'))

# Pre-processing tasks
task_list = [
    tasks.compute_centerlines,
    tasks.initialize_flowlines,
    tasks.catchment_area,
    tasks.catchment_intersections,
    tasks.catchment_width_geom,
    tasks.catchment_width_correction,
]

if RUN_GIS_PREPRO:
    for task in task_list:
        execute_entity_task(task, gdirs)

if RUN_CLIMATE_PREPRO:
    for gdir in gdirs:
        gdir.inversion_calving_rate = 0
    cfg.PARAMS['correct_for_neg_flux'] = False
    cfg.PARAMS['filter_for_neg_flux'] = False
    execute_entity_task(tasks.process_cru_data, gdirs)
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)

suf = 'glen_a'+str(2.3346e-24)+'_cfgFS'+str(k)

if RUN_INVERSION:
    # Inversion tasks
    execute_entity_task(tasks.prepare_for_inversion, gdirs, add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=2.3346e-24,
                        fs=cfg.FS)
    execute_entity_task(tasks.filter_inversion_output, gdirs)

    # Log
    m, s = divmod(time.time() - start, 60)
    h, m = divmod(m, 60)
    log.info(
        "OGGM no_calving is done! Time needed: %02d:%02d:%02d" % (h, m, s))

# Calving loop
# -----------------------------------
if With_calving:
    # Re-initializing climate tasks and inversion without calving to be sure
    for gdir in gdirs:
        gdir.inversion_calving_rate = 0

    cfg.PARAMS['correct_for_neg_flux'] = False
    cfg.PARAMS['filter_for_neg_flux'] = False
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)
    execute_entity_task(tasks.prepare_for_inversion, gdirs,
                        add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=2.3346e-24,
                        fs=cfg.FS)

    for gdir in gdirs:
        cl = gdir.read_pickle('inversion_output')[-1]
        if gdir.is_tidewater:
            assert cl['volume'][-1] == 0.

    # Selecting the tidewater glaciers on the region
    for gdir in gdirs:
        if gdir.terminus_type == 'Marine-terminating':
            # Starting the calving loop, with a maximum of 50 cycles
            i = 0
            data_calving = []
            w_depth = []
            thick = []
            t_width = []
            mu_star_calving = []
            forwrite = []

            # Our first guess of calving is that of a water depth of 1m

            # We read the model output, of the last pixel of the inversion
            cl = gdir.read_pickle('inversion_output')[-1]

            # We assume a thickness of alt + 1
            t_altitude = cl['hgt'][-1]

            thick = t_altitude + 1
            w_depth = thick - t_altitude

            # print('t_altitude', t_altitude)
            # print('depth', w_depth)
            # print('thick', thick)
            fl = gdir.read_pickle('inversion_flowlines')[-1]
            width = fl.widths[-1] * gdir.grid.dx

            # Lets compute the theoretical calving out of it
            pre_calving = k * thick * w_depth * width / 1e9
            gdir.inversion_calving_rate = pre_calving
            print('pre_calving', pre_calving)

            # Recompute all with calving
            tasks.distribute_t_stars([gdir], minimum_mustar=0.)
            tasks.apparent_mb(gdir)
            tasks.prepare_for_inversion(gdir, add_debug_var=True)
            tasks.volume_inversion(gdir, glen_a=2.3346e-24, fs=cfg.FS)
            df = pd.read_csv(gdir.get_filepath('local_mustar')).iloc[0]
            mu_star = df['mu_star']

            while i < 50:
                # First calculates a calving flux from model output

                F_calving, new_depth, new_thick, t_width = calving_from_depth(
                    gdir, k)

                # Stores the data, and we see it
                data_calving += [F_calving]
                w_depth = np.append(w_depth, new_depth)
                thick = np.append(thick, new_thick)
                t_width = t_width
                # print('Calving rate calculated', F_calving)

                # We put the calving function output into the Model
                gdir.inversion_calving_rate = F_calving

                # Recompute mu with calving
                tasks.distribute_t_stars([gdir], minimum_mustar=0.)
                tasks.apparent_mb(gdir)

                # Inversion with calving, inv optimization is not iterative
                tasks.prepare_for_inversion(gdir, add_debug_var=True)
                tasks.volume_inversion(gdir, glen_a=2.3346e-24, fs=cfg.FS)

                df = pd.read_csv(gdir.get_filepath('local_mustar')).iloc[0]
                mu_star = df['mu_star']
                mu_star_calving = np.append(mu_star_calving, mu_star)

                i += 1
                avg_one = np.average(data_calving[-4:])
                avg_two = np.average(data_calving[-5:-1])
                difference = abs(avg_two - avg_one)

                if difference < 0.05 * avg_two or data_calving[-1] == 0:
                    break

            # Making a dictionary for calving
            cal_dic = dict(calving_fluxes=data_calving,
                           water_depth=w_depth,
                           H_ice=thick, t_width=t_width,
                           mu_star_calving=mu_star_calving)
            forwrite.append(cal_dic)
            # We write out everything
            gdir.write_pickle(forwrite, 'calving_output')

        gdir.inversion_calving_rate = 0

    # Reinitialize everything
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)
    execute_entity_task(tasks.prepare_for_inversion, gdirs,
                        add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=2.3346e-24,
                        fs=cfg.FS)

    # Assigning to each tidewater glacier its own last_calving flux calculated
    for gdir in gdirs:
        if gdir.terminus_type == 'Marine-terminating':
            calving_output = gdir.read_pickle('calving_output')
            for objt in calving_output:
                all_calving_data = objt['calving_fluxes']
                all_data_depth = objt['water_depth']
                all_data_H_i = objt['H_ice']
                all_data_width = objt['t_width']
            # we see the final calculated calving flux
            last_calving = all_calving_data[-1]
            last_width = all_data_width

            print('For the glacier', gdir.rgi_id)
            print('last calving value is:', last_calving)

            gdir.inversion_calving_rate = last_calving

    # Calculating everything again with a calving flux assigned and filtering
    # and correcting for negative flux
    cfg.PARAMS['correct_for_neg_flux'] = False
    cfg.PARAMS['filter_for_neg_flux'] = False
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)
    execute_entity_task(tasks.prepare_for_inversion, gdirs,
                        add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs,
                        glen_a=2.3346e-24, fs=cfg.FS, filesuffix='_with_calving_')

    m, s = divmod(time.time() - start, 60)
    h, m = divmod(m, 60)
    log.info("OGGM with calving is done! Time needed: %02d:%02d:%02d" % (
        h, m, s))