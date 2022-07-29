## plot system level, congestion index, e.g. fig 12 in paper

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

metric_name = 'send_bit_count'     ## MB

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


link_bw = 25 ## 25MB/ms
local_link_cnt = rpg * (rpg-1)   ## within a group
global_link_cnt = 1              ## between group pairs 

sim_time = [0,0]
local_max = [0,0]
global_max = [0,0]
congest_idex_list = [
    np.empty((num_groups,num_groups)),
    np.empty((num_groups,num_groups)),
]  ## heatmaps 

assert  metric_name == 'send_bit_count' ,  print(metric_name) # ## MB
for caseid in range(len( rting_cases )):
    sim_time[caseid] = stats_dfs[caseid][' SimTime'].iloc[0] / (10**9) # ps => ms
    local_max[caseid] = sim_time[caseid] * local_link_cnt * link_bw
    global_max[caseid] = sim_time[caseid] * global_link_cnt * link_bw

    for srcg in range(num_groups):
        for destg in range(num_groups):
            if srcg == destg:
                congest_idex_list[caseid][num_groups-destg-1][srcg] = (
                    local_traffic[caseid][srcg]/local_max[caseid]
                ) 
            else:
                congest_idex_list[caseid][num_groups-destg-1][srcg] = (
                    global_traffic[caseid][(srcg, destg)]/global_max[caseid] 
                )  

for cidx in range(2):
    amax = 0
    amin = 100
    
    for ridx in range(33):
        if max(congest_idex_list[cidx][ridx]) > amax:
            amax = max(congest_idex_list[cidx][ridx])
        if min(congest_idex_list[cidx][ridx]) < amin:
            amin = min(congest_idex_list[cidx][ridx])
    
figsize = (width_sc, width_sc/2 )
fig = plt.figure(figsize=figsize)

ax = plt.subplot(121)
im = plt.imshow(congest_idex_list[0] * (-1), interpolation=None, vmin = -0.1, vmax = 0)
ax.set_title('Q-adp', pad = 0)
ax.set_xticks( [0, 10, 20 ,30], ['0', '10', '20', '30'])
ax.set_xlabel('Src. group\n(a)', labelpad=0)
ax.set_yticks( [32,22,12,2], ['0', '10', '20', '30'])
ax.set_ylabel('Dest. group', labelpad=0)

if len(rting_cases) > 1:

    ax = plt.subplot(122)
    plt.imshow(congest_idex_list[1] * (-1), interpolation=None, vmin = -0.1, vmax = 0)
    ax.set_title('PAR', pad = 0)
    ax.set_xticks( [0, 10, 20 ,30], ['0', '10', '20', '30'])
    ax.set_xlabel('Src. group\n(b)', labelpad=0)


fig.subplots_adjust(left=0.11, right=0.86, bottom=0.04, top=1.12, wspace=0.3, hspace=0.38)

axpos = ax.get_position()
cax = plt.axes([0.87, axpos.y0, 0.02, axpos.height])
cbar = plt.colorbar(cax=cax,  
                    ticks=[0, -0.05, -0.1]
                   )

cbar.ax.invert_yaxis()
cbar.ax.set_yticklabels(['0.00', '0.05', '0.10'])  # vertically oriented colorbar

figname = fig_root / 'mixed-workload-congestion-index'

fig.savefig(figname)
print(f'figure saved to {figname}.png' )