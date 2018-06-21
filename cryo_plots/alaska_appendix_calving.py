# This script will plot the calving flux of alaska
# with depth and width correction


import numpy as np
import pandas as pd
import os
import seaborn as sns
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Plot settings
rcParams['axes.labelsize'] = 15
rcParams['xtick.labelsize'] = 15
rcParams['ytick.labelsize'] = 15
rcParams['legend.fontsize'] = 15
# Set figure width and height in cm
width_cm = 12
height_cm = 5


MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

lit_calving = os.path.join(MAIN_PATH,
                           'input_data/literature_calving_complete.csv')

run_output = os.path.join(MAIN_PATH,'output_data/5_Appendix_runs/')

glacier_char = os.path.join(run_output,
                    'glacier_characteristics_with_calving__cfgA_cfgFS2.4.csv')


Fa_lit = pd.read_csv(lit_calving, index_col=0).sort_index(ascending=[True])
Fa_oggm = pd.read_csv(glacier_char, index_col=0).sort_index(ascending=[True])


Fa_oggm_sel = Fa_oggm.loc[Fa_lit.index]

d = {'McNabb et al. (2015)': Fa_lit['calving_flux_Gtyr']*1.091,
     'OGGM': Fa_oggm_sel['calving_flux']}

df = pd.DataFrame(data=d)

# Create figure and axes instances
fig = plt.figure(figsize=(width_cm, height_cm))

N = len(df)
ind = np.arange(N)
graph_width = 0.35

std_oggm = df['OGGM'].values.std()
std_fix =  df['McNabb et al. (2015)'].values.std()

labels = df.index.values

p1 = plt.bar(ind, df['OGGM'].values, graph_width)#, yerr=std_oggm)
p2 = plt.bar(ind+graph_width, df['McNabb et al. (2015)'].values, graph_width)#, yerr=std_fix)

plt.ylabel('Calving flux (km³$yr^{-1}$)')
plt.xticks(ind + graph_width/2, labels, rotation='vertical')
plt.legend((p1[0], p2[0]), ('OGGM', 'McNabb et al. (2015)'))

plt.show()