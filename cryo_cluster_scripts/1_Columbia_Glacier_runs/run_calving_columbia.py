# This will run the calving parametrization for the Columbia Glacier
# This script is needed for the plot scripts: Columbia workflow
# To run the rest of the folders experiments (2,3,4)
# you don't need to run this script

from __future__ import division
import oggm

# Module logger
import logging
log = logging.getLogger(__name__)

# Python imports
import os
import geopandas as gpd
import pandas as pd
import numpy as np

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

# exclude the Columbia glacier and other errors for the moment
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
    cfg.PARAMS['correct_for_neg_flux'] = False
    cfg.PARAMS['filter_for_neg_flux'] = False
    execute_entity_task(tasks.process_cru_data, gdirs)
    tasks.distribute_t_stars(gdirs)
    execute_entity_task(tasks.apparent_mb, gdirs)

# Inversion tasks
execute_entity_task(tasks.prepare_for_inversion, gdirs, add_debug_var=True)
execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=cfg.FS)
execute_entity_task(tasks.filter_inversion_output, gdirs)

# Compile output
# utils.glacier_characteristics(gdirs, filesuffix='_Columbia_no_calving_with_sliding_')

# Log
m, s = divmod(time.time() - start, 60)
h, m = divmod(m, 60)
log.info("OGGM is done! Time needed: %02d:%02d:%02d" % (h, m, s))

With_calving = True
k = 2.4

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
    # tasks.optimize_inversion_params(gdirs)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A, fs=cfg.FS)

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
            tasks.volume_inversion(gdir, glen_a=cfg.A, fs=cfg.FS)
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
                tasks.volume_inversion(gdir, glen_a=cfg.A, fs=cfg.FS)
                # tasks.distribute_thickness(gdir, how='per_altitude')
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
    # tasks.optimize_inversion_params(gdirs)
    execute_entity_task(tasks.volume_inversion, gdirs, glen_a=cfg.A,
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
                        glen_a=cfg.A,
                        fs=cfg.FS,
                        filesuffix='_with_calving'+str(k))

    # Write out glacier statistics
    #utils.glacier_characteristics(gdirs,
    #                    filesuffix='_Columbia_with_calving_with_sliding_' + str(k),
    #                               inversion_only=True)