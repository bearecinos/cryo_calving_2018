# Configuration experiments 

These scripts will calculate the total glacier volume of Alaska with different model
configurations.

4.1 No calving experiments: 
*  In here we have separated Marine- terminating glaciers from Lake- and Land-
terminating glaciers, because of the following filters that affect the calving flux calculation:  

**For Marine- terminating glaciers:**    
    `cfg.PARAMS['correct_for_neg_flux'] = False`   
`cfg.PARAMS['filter_for_neg_flux'] = False`   

**For Lake- and Land- terminating glaciers:**   
    `cfg.PARAMS['correct_for_neg_flux'] = True`  
`cfg.PARAMS['filter_for_neg_flux'] = True`   

* Configuration 1 or 2 corresponds to adding or not the sliding velocity.   
**config_1** -> `fs=0.0`   
**config_2** -> `fs = OGGM default` 

4.2 With calving experiments only MT:   
* In here we only run MT glaciers, the frontal ablation parametrisation is only 
apply to these type of glaciers, so there is no need to run again the Lake- and
Land- terminating ones.    
(Read section 3.3 of the paper to learn about the limitations of the 
parametrisation.)

* The different configurations are:    

| Configuration  | Description                                               |
| -------------: | :--------------------------------------------------------:|
| 3              | f<sub>s</sub> = 0.0, Glen A = OGGM default, k<sub>1</sub> = 0.6124            |
| 4              | f<sub>s</sub> = 0.0, Glen A = OGGM default, k<sub>2</sub> = 0.707             |
| 5              | f<sub>s</sub> = OGGM default, Glen A = OGGM default, k<sub>1</sub> = 0.6124   |
| 6              | f<sub>s</sub> = OGGM default, Glen A = OGGM default, k<sub>2</sub> = 0.707    |

4.3 With calving experiments only MT (vbsl):   
These scripts are exactly the same as 4.2, with the following differences: 

* The **vbsl** name in the folder stands for volume below sea level. The only difference between this
 scripts and 4.2 is that in here we replace the inversion output name with a suffix:    
 `inversion_onput_with_calving.pkl`   

* If we do this inside the scripts of folder 4.2 we will get the wrong volume at the 
`glacier_characteristics.csv` file. Because the OGGM function: `utils.glacier_characteristics()`
 does not record the volume after calving or after the `filesuffix='_with_calving_'` name has been 
 added to the `inversion_output.pkl` 

To execute the runs in the cluster type these commands in experiment root 
folder: *4_Runs_different_configurations*:  

`./run_no_calving_exp.sh`   
`./run_with_calving_exp.sh`   
`./run_with_calving_exp_vbsl.sh`   

4.4 Calculate_vbsl:   

* **This script is run from the PC, this needs to be run before calculating the 
Alaska volume with the script in: `/cryo_plots/alaska_volume.py`. If you want to 
run this from the cluster you will have to make a new .slurm script.** The run
takes a few seconds so it can be done in the PC after copying the output_data folder
to your `~/cryo_calving_2018/ouput_data` folder.  
 