# Configuration experiments 

These scripts will calculate the total glacier volume of Alaska with different model
configurations.

| Configuration  | Description                                                                 |
| -------------: | :--------------------------------------------------------------------------:|
| 1              |  k<sub>1</sub> = 0.6124, Glen A = OGGM default, f<sub>s</sub> = 0.0         |
| 2              |  k<sub>2</sub> = 0.707, Glen A = OGGM default, f<sub>s</sub> = 0.0          |
| 3              |  k<sub>1</sub> = 0.6124, Glen A = OGGM default, f<sub>s</sub> = OGGM default|
| 4              |  k<sub>2</sub> = 0.707, Glen A = OGGM default, f<sub>s</sub> = OGGM default |
| 5              |  k<sub>1</sub> = 0.6124, Glen A = 2.34e10−24, f<sub>s</sub> = 0.0           |
| 6              |  k<sub>2</sub> = 0.707, Glen A = 3.33e10−24, f<sub>s</sub> = 0.0            |
| 7              |  k<sub>1</sub> = 0.6124, Glen A = 1.61e10−24 , f<sub>s</sub> = OGGM default |
| 8              |  k<sub>2</sub> = 0.707, Glen A = 2.33e10−24, f<sub>s</sub> = OGGM default   |

The content of each experiment (each folder) is the following:

4.1 No calving experiments:
 
*  In here we have separated Marine - terminating glaciers from Lake- and Land-
terminating glaciers (_rest). Because of the following filters:  

**For Marine- terminating glaciers:**    
    `cfg.PARAMS['correct_for_neg_flux'] = False`   
`cfg.PARAMS['filter_for_neg_flux'] = False`   

**For Lake- and Land- terminating glaciers:**   
    `cfg.PARAMS['correct_for_neg_flux'] = True`  
`cfg.PARAMS['filter_for_neg_flux'] = True`   

4.2 With calving experiments only MT:      

* In here we only run MT glaciers, the frontal ablation parametrisation is only 
apply to these type of glaciers, so there is no need to run again the Lake- and
Land- terminating ones. (Read section 3.3 of the paper to learn about the limitations of the 
parametrisation in lake-terminating glaciers.)

4.3 With calving experiments only MT (vbsl):   

These scripts are exactly the same as 4.2, with the following differences: 

* **vbsl** stands for volume below sea level and in here we replace the 
inversion output name with: `inversion_onput_with_calving.pkl`   

* If we do this inside the scripts of folder 4.2 we will get the wrong 
`glacier_characteristics_with_calving.csv`, and then the wrong volume 
after accounting for frontal ablation. This due to the fact that 
the OGGM function: `utils.glacier_characteristics()` does not record 
the volume after calving or after the `filesuffix='_with_calving_'` name has been 
added to the `inversion_output.pkl` 

4.4 Calculate_vbsl:   

* **This script is run from the PC ONLY, this needs to be run before calculating the 
Alaska volume plot with the script in: `/cryo_plots/alaska_volume.py`. If you want to 
run this from the cluster you will have to make a new .slurm script.** The run
takes a few seconds so it can be done in the PC after copying the output_data folder
to your PC `~/cryo_calving_2018` folder.  

4.5 Velocities: 
* This script will run MT glaciers before and after accounting for frontal ablation
with OGGM default parameters. This run is done to estimate changes in velocity
before accounting for frontal ablation and after accounting for frontal ablation.

To execute runs 4_1, 4_2, 4_3 and 4_5 in the cluster type these commands in experiment root 
folder: *4_Runs_different_configurations*:  

`./run_no_calving_exp.sh`   
`./run_with_calving_exp.sh`   
`./run_with_calving_exp_vbsl.sh`   
`./run_velocities.sh`