#!/bin/bash
#
#SBATCH --job-name=calving_vs_volume
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=14
#SBATCH --time=24:00:00
#SBATCH --mail-user=recinos@uni-bremen.de
#SBATCH --mail-type=ALL

# Abort whenever a single step fails. Without this, bash will just continue on errors.
set -e

# Load the required environment modules for OGGM
module load python/3.6.1 oggm-binary-deps/1

# Activate our local OGGM virtualenv
source ~/oggm_venv/bin/activate

# On every node, when slurm starts a job, it will make sure the directory
# /work/username exists and is writable by the jobs user.
# We create a sub-directory there for this job to store its runtime data at.
WORKDIR="/work/$SLURM_JOB_USER/$SLURM_JOB_ID/"
mkdir -p "$WORKDIR"
echo "Workdir for this run: $WORKDIR"

# Export the WORKDIR as environment variable so our script can use it to find its working directory.
export WORKDIR

# Use the local data download cache
export OGGM_DOWNLOAD_CACHE=/home/data/download
export OGGM_DOWNLOAD_CACHE_RO=1
export OGGM_EXTRACT_DIR="/work/$SLURM_JOB_USER/$SLURM_JOB_ID/oggm_tmp"

# Run the actual job. The srun invocation starts it as individual step for slurm.
srun -n 1 -c "${SLURM_JOB_CPUS_PER_NODE}" python3 ./run_calving_vs_vol_exp.py

echo "Start copying..."

# Once a slurm job is done, slurm will clean up the /work directory on that node from any leftovers from that user.
# So copy any result data you need from there back to your home dir!
# $SLURM_SUBMIT_DIR points to the directory from where the job was initially commited.
OUTDIR="$HOME/cryo_calving_2018/output_data/2_Calving_vs_Volume_exp/"
mkdir -p "$OUTDIR"

# Copy any neccesary result data.
cp -R "${WORKDIR}/sensitivity_calvsvol"*.csv "${OUTDIR}/"
# cp -R "${WORKDIR}"/* "${OUTDIR}/"

# Print a final message so you can actually see it being done in the output log.
echo "SLURM DONE"

