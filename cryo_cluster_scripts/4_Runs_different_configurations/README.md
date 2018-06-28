# Configuration experiments 

These scripts will run the calving module for Alaska with different model
configurations.

The content of each experiment (each folder) is the following:

4.1 No calving experiments: 
*  In here we have separated Marine - terminating glaciers from Lake- and Land-
terminating glaciers. Because the following filters, affect marine-terminating glaciers
thickness distribution:  

**For Marine- terminating glaciers:**    
    `cfg.PARAMS['correct_for_neg_flux'] = False`   
`cfg.PARAMS['filter_for_neg_flux'] = False`   

**For Lake- and Land- terminating glaciers:**   
    `cfg.PARAMS['correct_for_neg_flux'] = True`  
`cfg.PARAMS['filter_for_neg_flux'] = True`   

* We include lake-terminating together with land-terminating because we can't model a calving flux for these glaciers.

* Configuration **1 or 2** corresponds to adding or not the sliding velocity.   
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
| 3              | f<sub>s</sub> = 0.0, Glen A = OGGM default, k<sub>1</sub> = 0.962             |
| 4              | f<sub>s</sub> = 0.0, Glen A = OGGM default, k<sub>2</sub> = 1.236             |
| 5              | f<sub>s</sub> = OGGM default, Glen A = OGGM default, k<sub>1</sub> = 0.962    |
| 6              | f<sub>s</sub> = OGGM default, Glen A = OGGM default, k<sub>2</sub> = 1.236    |
         
             
             
4.3 With calving experiments only MT (vbsl):   
These scripts are exactly the same as 4.2, with the following differences: 

* **vbsl** stands for volume below sea level and in here we replace the 
inversion output name with: `inversion_onput_with_calving.pkl`   

* If we do this inside the scripts of folder 4.2 we will get the wrong 
`glacier_characteristics_with_calving.csv`, and then the wrong volume. This 
 because the OGGM function: `utils.glacier_characteristics()` does not record 
  the volume after calving or after the `filesuffix='_with_calving_'` name has been 
  added to the `inversion_output.pkl` 

To execute the runs in the cluster type the commands below in experiment root 
folder: *cryo_cluster_scritps/4_Runs_different_configurations*:     

**And make sure you make this files executables by doing:** *e.g.* `chmod +x run_no_calving_exp.sh`    

`./run_no_calving_exp.sh`   
`./run_with_calving_exp.sh`   
`./run_with_calving_exp_vbsl.sh`   

4.4 Calculate_vbsl:   

* **This script is run from the PC, this needs to be run before calculating the 
Alaska volume with the script in: `/cryo_plots/alaska_volume.py`. If you want to 
run this from the cluster you will have to make a new .slurm script.** The run
takes a few seconds so it can be done in the PC after copying the output_data folder
to your `~/cryo_calving_2018/output_data` folder.  
 
4.5 Velocities run:    

* This script has the same configuration as the `run_calving_columbia.py` script. 
In this routine we calculate the calving flux for marine-terminating glaciers, keeping
OGGM's default parameters **(k, Glen A and fs = Default)**, there is **also no correction
to the terminus width and depth**.       

* In here we save the /per_glacier output of both experiments: 
No calving and after calving.     

* To run this script make sure this file is excetuable.     

* To execute the run in the cluster type the commands below in experiment root 
folder: *cryo_cluster_scritps/4_Runs_different_configurations*:       
`./run_velocities.sh`
  

