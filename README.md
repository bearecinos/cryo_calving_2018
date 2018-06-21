# OGGM cryo calving paper 2018

This repository **cryo_calving_2018** contains the scripts used to implement a
calving parameterisation into [OGGM](www.oggm.org) and produce the results of
the paper that will be submitted to: https://www.the-cryosphere.net/ or other journal that the co-authors suggest.    

This repository uses a OGGM version V1.0.1 pinned here: https://github.com/OGGM/oggm/releases/tag/v1.0.1    

The content of the repository is the following: 

**I. cryo_cluster_scripts** (the running scripts)

* Contains the following sub-folders:

1. Columbia Glacier scripts
2. Calving vs Volume experiment
3. Sensitivity experiments with OGGM default parameters:
    **k**, **Glen A** and **fs** 
4. Alaska volume and volume below sea level calculated with 
different model configurations.

5. Appendix run: Marine-terminating glaciers calving fluxes calculated 
correcting the depth width of the terminus 

* **IMPORTANT:**
* To run the scripts make sure you have this repository on your home directory.
* To run the scripts you **must follow the order of the folders.** 
* All scripts require a modified version of **RGI v.6.0**, where four 
*Marine-terminating glaciers* have been merged with their respective branches. 
**This file is already located in the input_data folder of the repository.**  

* RGI id's of the glacier merged:    

RGI60-01.21008 with RGI60-01.26732         
RGI60-01.10689 with RGI60-01.23635         
RGI60-01.26736 with RGI60-01.14443    
RGI60-01.03890 with RGI60-01.23664     

* The merge was necessary in order to use McNabb *et al.* 2012 data base.

* Scripts in folders **2, 3 and 4** require the output of the Columbia Glacier
pre-processing run. **You can't run these folders without having ran the scripts 
in folder # 1.** 
* All the data need it for the runs can be found in the input data file.   


**II. cryo_plots** (the plotting scripts)

* You will be able to run the plotting scripts after you have completed the runs
in cryo_cluster_scripts and copied to your PC home directory the output_data folder generated from the runs. The right place to copy this folder is in  `~/cryo_calving_2018/output_data/`

**III. Input data** 

* Contains all data necessary for the cluster running and plotting scripts.

**IV. Output data**
* Thi folder will be generated once you have ran the cryo_cluster_scripts.
* Contains the output files for each folder in cryo_cluster_scripts.

**V. plots** 

* Where all the plots get save


#### Please read the top of the scripts to know more about the ouput of each run.

### External libraries that are not in OGGM env:    

Some of the cryo_plots scripts requiere additional libraries outside OGGM libraries such as:    
`collections` , `cartopy`, `cartopy.mpl.gridliner` , `cartopy.feature`, `cartopy.io.shapereader` and `cartopy.crs`   

Also make sure to install the `uncertainties` python library from:   
   
https://pythonhosted.org/uncertainties/  

Or via   
`conda install -c conda-forge uncertainties`

This library is use only in the `k_factors_plot.py` to find *k* values that 
intercept the frontal ablation observations.    
 
 


