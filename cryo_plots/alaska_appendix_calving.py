# This script will plot the calving flux of alaska
# with depth and width correction


import numpy as np
import pandas as pd
import os
import seaborn as sns
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams


# Set figure width and height in cm
width_cm = 20
height_cm = 5


MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

lit_calving = os.path.join(MAIN_PATH,
                           'input_data/literature_calving_complete.csv')

run_output = os.path.join(MAIN_PATH,'output_data/5_Appendix_runs/')

glacier_char = os.path.join(run_output,
                    'glacier_characteristics_with_calving__cfgA_cfgFS2.4.csv')

glacier_char_norec = os.path.join(run_output,
        'glacier_characteristics_with_calving_no_recbed__cfgA_cfgFS2.4.csv')


Fa_lit = pd.read_csv(lit_calving, index_col=0).sort_index(ascending=[True])
Fa_oggm = pd.read_csv(glacier_char, index_col=0).sort_index(ascending=[True])
Fa_oggm_norec =  pd.read_csv(glacier_char_norec, index_col=0).sort_index(ascending=[True])

Fa_oggm_sel = Fa_oggm.loc[Fa_lit.index]
Fa_oggm_norec_sel = Fa_oggm_norec.loc[Fa_lit.index]

d = {'McNabb et al. (2015)': Fa_lit['calving_flux_Gtyr']*1.091,
     'OGGM rectangular': Fa_oggm_sel['calving_flux'], 'OGGM parabolic': Fa_oggm_norec_sel['calving_flux']}

df = pd.DataFrame(data=d)


diff = df['McNabb et al. (2015)'] - df['OGGM rectangular']
diff_norec = df['McNabb et al. (2015)'] - df['OGGM parabolic']

fig = plt.figure(figsize=(width_cm, height_cm))
sns.set()
sns.set_color_codes("colorblind")
#sns.set_style("white")
# Plot settings
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['legend.fontsize'] = 16

N = len(df)
ind = np.arange(N)
labels = df.index.values

p1 = plt.plot(ind, diff, '-')
p2 = plt.plot(ind, diff_norec, '-')

plt.ylabel('Calving flux differences (km³$yr^{-1}$)')
plt.xticks(ind, labels, rotation='vertical')
plt.legend((p1[0], p2[0]), ('Rectangular bed shape','Parabolic bed shape'))
plt.margins(0.05)
#plt.show()
plt.savefig(os.path.join(plot_path, 'appendixb.png'), dpi=150,
                 bbox_inches='tight')


#Create figure and axes instances
#
#
fig = plt.figure(figsize=(width_cm, height_cm))
sns.set()
# Plot settings
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 20
rcParams['ytick.labelsize'] = 20
rcParams['legend.fontsize'] = 16

N = len(df)
ind = np.arange(N)
graph_width = 0.35

std_oggm = df['OGGM rectangular'].values.std()
std_fix =  df['McNabb et al. (2015)'].values.std()

labels = df.index.values

p1 = plt.bar(ind, df['OGGM rectangular'].values, graph_width)#, yerr=std_oggm)
p2 = plt.bar(ind+graph_width, df['McNabb et al. (2015)'].values, graph_width)#, yerr=std_fix)

plt.ylabel('Calving flux (km³$yr^{-1}$)')
plt.xticks(ind + graph_width/2, labels, rotation='vertical')
plt.legend((p1[0], p2[0]), ('OGGM', 'McNabb et al. (2015)'))

#plt.show()

plt.savefig(os.path.join(plot_path, 'appendixa.png'), dpi=150,
                 bbox_inches='tight')
