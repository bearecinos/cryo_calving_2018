# Sensitivity experiments 

These scripts will calculate the frontal ablation flux of Alaska marine-terminating 
glaciers computed by varying OGGM default parameters.

The content of each experiment is the following:

**3.1 k experiment:**   
*  In here we vary the calving constant of proportionality *k* in a range of 
0.24 -  2.52 yr<sup>-1</sup>.    
* We repeat this for `fs = 0.0 (1_k_parameter.py)` and for `fs = OGGM default 
(2_k_parameter.py)`   

**3.2 glen a experiment:**   
*  After finding the intersects between the results in 3.1 and the frontal 
ablation observations, we pick the values of *k* to be (`k1 = 0.6124` and
 `k2 = 0.707`)   
* The intercepts were found using the plotting script: `~/cryo_calving_2018/cryo_plots/sensitivity_plot.py`.   
* We then take these values of *k* and vary the values of *Glen A* from a factor of 
0.6 - 1.7 x `Glen A = OGGM defalut`. Alternating sliding and no sliding for each *k* value. 

| File           | Configuration                                          |
| -------------: | :-----------------------------------------------------:|
| glena_exp1     | f<sub>s</sub> = 0.0, k<sub>1</sub> = 0.6124            |
| glena_exp2     | f<sub>s</sub> = 0.0, k<sub>2</sub> = 0.707             |
| glena_exp3     | f<sub>s</sub> = OGGM default, k<sub>1</sub> = 0.6124   |
| glena_exp4     | f<sub>s</sub> = OGGM default, k<sub>2</sub> = 0.707    |

**3.3 fs experiment:**
* We do the same analysis to the sliding parameter varying *fs* parameter
in a factor range of 0.0 - 1.2 x `fs = OGGM default`. And alternating the different values of *k*.

| File        | Configuration                                          |
| ----------: | :-----------------------------------------------------:|
| fs_exp1     | glen a = OGGM default, k<sub>1</sub> = 0.6124          |
| fs_exp2     | glen a = OGGM default, k<sub>2</sub> = 0.707           |

To execute the runs in the cluster type the commands below in experiment root folder:    
 *cryo_cluster_scritps/3_Sensitivity_studies_k_A_fs*:     

**And make sure you make this files executables by doing:** *e.g.* `chmod +x run_k_experiments.sh`    

**Then run using:**     

`./run_k_experiments.sh`   
`./run_glena_experiments.sh`   
`./run_fs_experiments.sh`   
 
 
