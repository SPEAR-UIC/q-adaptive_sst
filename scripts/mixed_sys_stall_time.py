## plot system level, link stall time, e.g. fig 11 in paper

import pandas as pd
import numpy as np
import os,sys,time
import matplotlib
import matplotlib.pyplot as plt
import math,os,sys
from pathlib import Path

HOME = os.path.expanduser("~")

from df_utils import *

# ------------- Consider to update ----------------------------
simroot_path = '/home/df_user/mnt/wkdir/fft3d_cosmoflow_lu_random_lqcd_stencil5d/'
rting_cases = [
    'q-adaptive_count_itesx1_node140_138_140_139_256_243_ct__',
    'par_count_itesx1_node140_138_140_139_256_243_ct__',
]

fig_root = Path('./fig')
# -------------------------------------------------------------

fig_root.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.labelsize": 8,
    'axes.titlesize': 8,
    }
)

width_sc  = 3.336
height_sc = width_sc / 1.618
width_dc = 7.004
height_dc = width_dc / 1.618

num_groups = 33
rpg = 8
igpr = 4
local_ports=[4,11]  #[a,b)
global_ports=[11,15]  #[a,b)


stats_dfs = [pd.read_csv(
    os.path.join(
        HOME, simroot_path,
        stats_p,
        'all_stats.csv'
        ) ) for stats_p in rting_cases]

metric_name = 'output_port_stalls'   ## ms

local_traffic = []
global_traffic = []

metric_dfs = []
for stats_df in stats_dfs:
    metric_df = stats_df.loc[
        (stats_df['ComponentName'].str.contains('rtr:G'))
        & (stats_df[' StatisticName'].str.contains(metric_name))
    ].copy()
    
    metric_df['gid'] = metric_df['ComponentName'].str.split('R').str[0].str.split('G').str[-1].astype(int)
    metric_df['rtrid'] = metric_df['ComponentName'].str.split('R').str[-1].astype(int)
    metric_df['rtrid'] += rpg*metric_df['gid']
       
    metric_df['port'] = metric_df[' StatisticSubId'].str.split('_').str[0].str.split('port').str[-1].astype(int)
    metric_df['job'] = metric_df[' StatisticSubId'].str.split('job').str[-1]
    
    metric_dfs.append(metric_df)
    
    localtraffic = {}
    globaltraffic = {}
    for gid in range(num_groups):
        grpdf = metric_df.loc[metric_df['gid']==gid]
        
        if metric_name == 'output_port_stalls' or metric_name == 'idle_time' :
            unitconvertor = 10**9  ## ps ==>  ms
        else:
            unitconvertor = 8 * 10**6  ## bit => MB 
        ## local traffic
        localtraffic[gid] = grpdf.loc[(grpdf['port']>=local_ports[0]) & (grpdf['port']<local_ports[1])][' Sum.u64'].sum()/(unitconvertor)
        ## global traffic
        for rtr in range(rpg):
            rtrid_g = rtr + gid * rpg 
            for gport in range(global_ports[0], global_ports[1]):
                destg = global_port_to_destG(rtrid_g, gport, num_groups, rpg, igpr) 
                globaltraffic[(gid, destg)] = grpdf.loc[(grpdf['rtrid']==rtrid_g) & (grpdf['port']==gport)][' Sum.u64'].sum()/(unitconvertor)

    local_traffic.append(localtraffic)
    global_traffic.append(globaltraffic)


### Draw stall time
assert(  metric_name == 'output_port_stalls'  )   ## ms
line_c_base = 1.5
normfun = matplotlib.colors.Normalize(vmin=line_c_base**0.08, vmax=line_c_base**2.80)
cmap = matplotlib.cm.get_cmap('Greys')

system_radius = 20
figsize = (width_sc, width_sc/2 )
fig, axs = plt.subplots(1,2, figsize=figsize)

group_locs = {}

norm = matplotlib.colors.Normalize(vmin=10.0, vmax=20.0)

for axid, ax in enumerate(axs): 
    if axid >= len(rting_cases):
        continue
    
    center = ( (axid*2+1) * figsize[0]//4, figsize[1]//2)
    
    cnormal = '#4F535C' 
    for gid in range(num_groups):
        gloc_x = center[0] + system_radius * math.cos( 2 * gid * math.pi/num_groups)
        gloc_y = center[1] + system_radius * math.sin( 2 * gid * math.pi/num_groups)
        group_locs[gid] = [gloc_x, gloc_y]
        
        plot_color = cnormal
        plot_color = '#FFA699' 

        ax.scatter(gloc_x, gloc_y, label = f'{gid}', marker='o', color=plot_color, 
                   s=2.3**(local_traffic[axid][gid]/14)
                   , zorder=2,
                   alpha = 0.6,
                  edgecolors='black', linewidths=0.5)
        
        if (gid %2 == 0):
            ax.annotate(f'G{gid}', xy =(gloc_x, gloc_y),
                    xytext =(center[0] - 2.2 + (1.1 * system_radius) * math.cos( 2 * gid * math.pi/num_groups),
                             center[1] - 0.5 + (1.1 * system_radius) * math.sin( 2 * gid * math.pi/num_groups)
                            )
                        ,
                        fontsize = 6
                       )
       
    for glink, v in sorted(global_traffic[axid].items(), key=lambda item: item[1]):
        if glink[0] == 0:
            sgid = glink[0]
            dgid = glink[1]
            plot_color = cmap(normfun(line_c_base**global_traffic[axid][glink]))
    
            ax.plot([group_locs[sgid][0], group_locs[dgid][0]],
                    [group_locs[sgid][1], group_locs[dgid][1]], 
                    color = plot_color,
                    zorder=1, 
                    lw = 2,
                    )
            
    ax.axis('off')
            
axs[0].set_title('Q-adp\n(a)', y=-0.24)
axs[1].set_title('PAR\n(b)', y=-0.24)

sm = plt.cm.ScalarMappable(cmap=cmap)
sm._A = []
axpos0 = axs[0].get_position()
axpos1 = axs[1].get_position()
cax = plt.axes([0.91, axpos1.y0, 0.02, 0.96-axpos1.y0])
cbar = plt.colorbar(sm,
                    cax=cax,  
                    ticks=[0., 0.333, 0.666, 1]
                   )

cbar.ax.set_yticklabels(['0.08', '1.35', '2.18', '2.80'], x=-0.005, fontsize=6)  # vertically oriented colorbar

fig.subplots_adjust(left=0.02, right=0.88, bottom=0.16, top=0.96, wspace=0.1, hspace=0.38)

figname = fig_root / 'mixed-workload-stalltime'

fig.savefig(figname)
print( f'fig saved to {figname}.png'  )