#!/bin/bash
for script in 4_5_Velocities/*; do sbatch ./run_rgi_generic_all.slurm "$script"; done
