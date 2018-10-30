# This will run OGGM preprocessing task and first inversion without calving
# For the Columbia Glacier
# ITMIX DEM is needed for this run

from __future__ import division
import oggm

# Module logger
import logging
log = logging.getLogger(__name__)

# Python imports
import os
import geopandas as gpd

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

#DATA_INPUT = '/home/users/bea/cryo_calving_2018/input_data/'
DATA_INPUT = os.path.expanduser('~/cryo_calving_2018/input_data')

RGI_FILE = os.path.join(DATA_INPUT,
                        '01_rgi60_Alaska_modify/01_rgi60_Alaska.shp')

Columbia_itmix_dem = os.path.join(DATA_INPUT,
                                  'RGI50-01.10689_itmixrun_new/dem.tif')

cfg.PATHS['working_dir'] = WORKING_DIR

# Use multiprocessing
cfg.PARAMS['use_multiprocessing'] = True

# We make the border 20 so we can use the Columbia itmix DEM
cfg.PARAMS['border'] = 20

# Set to True for operational runs
cfg.PARAMS['continue_on_error'] = True

#For land and lake terminating we set this to True
cfg.PARAMS['correct_for_neg_flux'] = False
cfg.PARAMS['filter_for_neg_flux'] = False
cfg.PATHS['dem_file'] = Columbia_itmix_dem
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

# Run only the Columbia Glacier
columbia = ['RGI60-01.10689']
keep_indexes = [(i in columbia) for i in rgidf.RGIId]
rgidf = rgidf.iloc[keep_indexes]

# Sort for more efficient parallel computing
rgidf = rgidf.sort_values('Area', ascending=False)

log.info('Starting run for RGI reg: ' + rgi_region)
log.info('Number of glaciers: {}'.format(len(rgidf)))

# Go - initialize working directories
# -----------------------------------
gdirs = workflow.init_glacier_regions(rgidf)

# Prepro task, after this task we will replace Columbia OGGM's DEM for the ITMIX
execute_entity_task(tasks.glacier_masks, gdirs)

# Prepro tasks
task_list = [
    tasks.compute_centerlines,
    tasks.initialize_flowlines,
    tasks.catchment_area,
    tasks.catchment_intersections,
    tasks.catchment_width_geom,
    tasks.catchment_width_correction,
]
for task in task_list:
    execute_entity_task(task, gdirs)

# Climate tasks -- we make sure that calving is = 0 for all tidewater
for gdir in gdirs:
    gdir.inversion_calving_rate = 0

execute_entity_task(tasks.process_cru_data, gdirs)
tasks.distribute_t_stars(gdirs)
execute_entity_task(tasks.apparent_mb, gdirs)

# Inversion tasks
execute_entity_task(tasks.prepare_for_inversion, gdirs, add_debug_var=True)
execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=cfg.FS)

# Compile output
utils.glacier_characteristics(gdirs, filesuffix='_Columbia_no_calving_with_sliding_')

# Log
m, s = divmod(time.time() - start, 60)
h, m = divmod(m, 60)
log.info("OGGM is done! Time needed: %02d:%02d:%02d" % (h, m, s))
