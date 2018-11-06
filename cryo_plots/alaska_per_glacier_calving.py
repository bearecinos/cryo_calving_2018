# This script will plot the calving flux of alaska
# with depth and width correction

import numpy as np
import pandas as pd
import os
import seaborn as sns
os.getcwd()
import matplotlib.pyplot as plt
from matplotlib import rcParams

MAIN_PATH = os.path.expanduser('~/cryo_calving_2018/')

plot_path = os.path.join(MAIN_PATH, 'plots/')

lit_calving = os.path.join(MAIN_PATH,
                           'input_data/literature_calving_complete.csv')

run_output = os.path.join(MAIN_PATH,'output_data/5_runs_width_depth_correction/')

glacier_char = os.path.join(run_output,
                    'glacier_characteristics_with_calving__cfgA_cfgFS2.4.csv')

glacier_char_corrected = os.path.join(run_output,
        'glacier_characteristics_with_calving_corrected__cfgA_cfgFS2.4.csv')


Fa_lit = pd.read_csv(lit_calving, index_col=0).sort_index(ascending=[True])

Fa_oggm = pd.read_csv(glacier_char, index_col=0).sort_index(ascending=[True])

Fa_oggm_corrected = pd.read_csv(glacier_char_corrected,
                                index_col=0).sort_index(ascending=[True])

Fa_oggm_sel = Fa_oggm.loc[Fa_lit.index]

Fa_oggm_sel_corrected = Fa_oggm_corrected.loc[Fa_lit.index]


d = {'McNabb et al. (2015)': Fa_lit['calving_flux_Gtyr']*1.091,
     'OGGM default': Fa_oggm_sel['calving_flux'],
     'OGGM width and depth corrected': Fa_oggm_sel_corrected['calving_flux']}

df = pd.DataFrame(data=d)

diff = df['OGGM default'] - df['McNabb et al. (2015)']
diff_corrected = df['OGGM width and depth corrected'] - df['McNabb et al. (2015)']

# Set figure width and height in cm
width_cm = 12
height_cm = 5

fig = plt.figure(figsize=(width_cm, height_cm))
sns.set()
sns.set_color_codes("colorblind")
sns.set(style="white", context="talk")
# Plot settings
rcParams['axes.labelsize'] = 20
rcParams['xtick.labelsize'] = 16
rcParams['ytick.labelsize'] = 16
rcParams['legend.fontsize'] = 16

letkm = dict(color='black', ha='left', va='top', fontsize=20,
             bbox=dict(facecolor='white', edgecolor='black'))

N = len(df)
ind = np.arange(N)
print(ind)
graph_width = 0.3
labels = df.index.values
print(labels)

ax = fig.add_subplot(111)
p1 = plt.bar(ind, df['OGGM default'].values, graph_width)
p2 = plt.bar(ind+graph_width, df['OGGM width and depth corrected'].values, graph_width)#, yerr=std_oggm)
p3 = plt.bar(ind+2*graph_width, df['McNabb et al. (2015)'].values, graph_width )#, yerr=std_fix)
ax.axhline(y=0, color='k', linewidth=1.1)
plt.ylabel('Frontal ablation \n [km³$yr^{-1}$]')
plt.xticks(ind + graph_width, labels, rotation='vertical')
plt.ylim(0,15)

ax.tick_params(axis=u'both', which=u'both', length=5)

plt.legend((p1[0], p2[0], p3[0]),
           ('OGGM default','OGGM width and depth corrected', 'McNabb et al. (2015)'),
           bbox_to_anchor=(0.5,1))

plt.margins(0.05)

plt.savefig(os.path.join(plot_path, 'calving_per_glacier.pdf'), dpi=150,
                 bbox_inches='tight')