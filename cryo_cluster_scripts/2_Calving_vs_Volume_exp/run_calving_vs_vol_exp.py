# TODO: read this message carefully before the run!
# This script runs the Calving vs Volume experiment in Alaska with sliding
# for smoother results
# This script requires the pre-processing folder of the Columbia Glacier
# named: 1_preprocessing/per_glacier/
# This folder can be found in
# ~/home/users/your_user_name/cryo_calving_2018/output_data/1_Columbia_Glacier_runs
# This run takes approximately 2 hrs because the calving array length is 25

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

#DATA_INPUT = '/home/users/bea/cryo_calving_2018/'
MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

RGI_FILE = os.path.join(MAIN_PATH,
                     'input_data/01_rgi60_Alaska_modify/01_rgi60_Alaska.shp')

#This path needs to be change
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

# Run only for Lake Terminating and Marine Terminating
glac_type = [0]
keep_glactype = [(i not in glac_type) for i in rgidf.TermType]
rgidf = rgidf.iloc[keep_glactype]

# Sort for more efficient parallel computing
rgidf = rgidf.sort_values('Area', ascending=False)

log.info('Starting run for RGI reg: ' + rgi_region)
log.info('Number of glaciers: {}'.format(len(rgidf)))

# Go - initialize working directories
# -----------------------------------
gdirs = workflow.init_glacier_regions(rgidf)

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

    execute_entity_task(tasks.process_cru_data, gdirs)
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)

if RUN_INVERSION:
    # Inversion tasks
    execute_entity_task(tasks.prepare_for_inversion, gdirs, add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=cfg.FS)

if With_calving:
    # Re-initializing climate tasks and inversion without calving to be sure
    for gdir in gdirs:
        gdir.inversion_calving_rate = 0
    cfg.PARAMS['correct_for_neg_flux'] = False
    cfg.PARAMS['filter_for_neg_flux'] = False
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)
    execute_entity_task(tasks.prepare_for_inversion, gdirs, add_debug_var=True)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=cfg.FS)

    for gdir in gdirs:
        if gdir.is_tidewater:
            cl = gdir.read_pickle('inversion_output')[-1]
            assert cl['volume'][-1] == 0.

            volumes = []
            all_mus = []

            data_calving = np.arange(0, 5, 0.2)

            for j, c in enumerate(data_calving):
                gdir.inversion_calving_rate = c
                # Recompute mu with calving
                cfg.PARAMS['correct_for_neg_flux'] = False
                cfg.PARAMS['filter_for_neg_flux'] = False
                tasks.distribute_t_stars([gdir])
                execute_entity_task(tasks.apparent_mb, gdirs)
                tasks.prepare_for_inversion(gdir, add_debug_var=True)
                tasks.volume_inversion(gdir, glen_a=cfg.A, fs=cfg.FS)

                df = pd.read_csv(gdir.get_filepath('local_mustar')).iloc[0]
                mu_star = df['mu_star']

                vol = []
                cl = gdir.read_pickle('inversion_output')
                for c in cl:
                    vol.extend(c['volume'])
                vol = np.nansum(vol) * 1e-9

                volumes.append(vol)
                all_mus = np.append(all_mus, mu_star)

            print(volumes, data_calving)
            print(len(volumes), len(data_calving))

            d = {'calving_flux': data_calving, 'volume': volumes,
                 'mu_star': all_mus}
            df = pd.DataFrame(data=d)
            df.to_csv(os.path.join(cfg.PATHS['working_dir'],
                              'sensitivity_calvsvol' + gdir.rgi_id + '.csv'))
