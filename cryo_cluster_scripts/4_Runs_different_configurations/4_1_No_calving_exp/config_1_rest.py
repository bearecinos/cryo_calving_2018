# This will run OGGM preprocessing on the Alaska Region without calving

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

cfg.PATHS['working_dir'] = WORKING_DIR
# Use multiprocessing
cfg.PARAMS['use_multiprocessing'] = True
# We make the border 80 so we can use the Columbia itmix DEM
cfg.PARAMS['border'] = 20
# Set to True for operational runs
cfg.PARAMS['continue_on_error'] = True
#For tidewater we set this to False but here we run only lake and land
cfg.PARAMS['correct_for_neg_flux'] = True
cfg.PARAMS['filter_for_neg_flux'] = True
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

# Excluding Marine terminating
glac_type = [0, 2]
keep_glactype = [(i in glac_type) for i in rgidf.TermType]
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
    execute_entity_task(tasks.prepare_for_inversion, gdirs)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=0.0)

# Compile output
utils.glacier_characteristics(gdirs, filesuffix='_Lake_land_no_calving_fs_zero_')

# Log
m, s = divmod(time.time() - start, 60)
h, m = divmod(m, 60)
log.info("OGGM is done! Time needed: %02d:%02d:%02d" % (h, m, s))
