## plot application's packet latency distribution & througput v.s. time
## similar to figure 5,6,7,9 in the paper

import pathlib
import pandas as pd
import numpy as np
import os,sys,time
import matplotlib.pyplot as plt
import multiprocessing
import ujson as json
import math
from pathlib import Path

from df_utils import *

## ------------ consider to update ----------------------

# which sim case to plot
motif_flds_cases = [
    [cosmoflow, null],
    # [cosmoflow, random],
]

## which app to plot defined in motif_flds_cases, e,g the first app w/ idx==0
target_motif_id_list = [0,0] 
## which routing algorithm to plot
rting_list = ['q-adaptive']
## where is the simulation folder, expcted format: e.g. sim_data_dir/cosmoflow_null
sim_data_dir = '/home/df_user/mnt/wkdir'
## where to save the figures
fig_root = Path('./fig')
## tmp dir to store parsed data
json_dir = Path('./json_res')
## ------------------------------------------------------


script_root = os.path.dirname(os.path.realpath(__file__))

fig_root.mkdir(parents=True, exist_ok=True)
json_dir.mkdir(parents=True, exist_ok=True)
emberrandom_subite='1'
nodecnt_list = ['528', '528']

data_files = []
study_cases = []

cases_names = []

print(' Plotting for : ')

for target_jid, motif_flds in zip(target_motif_id_list, motif_flds_cases):
    assert(len(motif_flds)==2)
    case_str_base = ''
    for amotifid, amotif in enumerate(motif_flds):
        amotifname = amotif['name']
        if amotifid == target_jid:
            case_str_base+=f'**{amotifname}_'
        else:
            case_str_base+=f'{amotifname}_'
       
    for rtingid, rting in enumerate(rting_list):
        case_str = case_str_base + rting
        motifs_str = '_'.join([motif_fld['name'] for motif_fld in motif_flds])
        nodecnt_str = '_'.join(nodecnt_list)

        tmpstr=''
        if 'random' in motifs_str:
            tmpstr = f'{rting}_count_itesx{emberrandom_subite}_node{nodecnt_str}_ct__'
        elif 'allreduce' in motifs_str or 'cosmoflow' in motifs_str:
            tmpstr = f'{rting}_count_ites_node{nodecnt_str}_ct_barrierfalse__'
        elif 'lulesh' in motifs_str:
            tmpstr = f'{rting}_ites_node{nodecnt_str}_ct_flgs1_1_1_1_100__'
        else:
            tmpstr = f'{rting}_count_ites_node{nodecnt_str}_ct__'

        df_path = os.path.join(sim_data_dir, 
                               motifs_str, tmpstr,
                               'link_control_data',
                               f'job{target_jid}.result'
                              )   
        cases_names.append(case_str)
        print(case_str)
        if os.path.isfile(df_path):
            study_cases.append(case_str)
            data_files.append(df_path)
        else:
            assert(0), print('File not found: ', df_path)
            
json_p = json_dir / 'tmp.json'
read_script=os.path.join(script_root, 'parallel_read_linkcontrol.py')

print(data_files)

print(' Reading and parsing data files ... ')

f2read = ''.join(str(data_files).strip('[]').split(','))

os.system(f'python3 {read_script} {json_p} 1000 False true --datafs {f2read} --rawbw True') 

print(' loading parsed json result ... ')
json_res = {}

with json_p.open() as read_file:
    json_res = json.load(read_file) 

res_list = json_res['res_list']

for res_id, res in enumerate(res_list):
    if(data_files[res_id]!=res[-1]):
        print(  data_files[res_id], res[-1]  )


indi_pkt_lat_list = []
idx_list = []
bw_list = []
lat_list = []
hop_list = []
adp_list = []

idx_inject_list = []
bw_inject_list = []

for res_id, res in enumerate(res_list):
    assert(len(res) == 9)
    assert(data_files[res_id]==res[-1])
    
    indi_pkt_lat_list.append(np.array(res[0])/1000) # ns => us
    idx_list.append(np.array(res[1]))
    bw_list.append(np.array(np.array(res[2]))/1000) ## GB/ms
    lat_list.append(np.array(res[3])/1000) # ns => us
    hop_list.append(np.array(res[4]))
    adp_list.append(np.array(res[5]))
    
    idx_inject_list.append(np.array(res[6]))
    bw_inject_list.append(np.array(res[7]))

percentiles=[95,99]
p99_list=[]

for label_id, _ in enumerate(res_list):
    p99_list.append(np.percentile( indi_pkt_lat_list[label_id], percentiles, interpolation='lower')) 

print( 'plotting latency distribution boxplot')

fig=plt.figure()
xtickpos = range(1, len(cases_names)+1)
xticklabel = cases_names
bxpltsdit = plt.boxplot(
    indi_pkt_lat_list, 
    labels=cases_names,
    positions=xtickpos,
    showfliers = False,
    showmeans = True,
    widths = 0.5,
    )

for ppid, pnum in enumerate(percentiles):
    plt.scatter(xtickpos, [ ptiles[ppid] for ptiles in p99_list ], label=f'p{pnum}')

leghandles, leglabels = plt.gca().get_legend_handles_labels()
plt.legend([leghandles[1], leghandles[0], bxpltsdit['means'][0]], 
           ['p99', 'p95', 'mean'],
           loc='lower left',
           fontsize=8
          )
plt.grid()
plt.ylabel('Packet latency (us)')
plt.xticks(rotation = -20)

plt.yscale('log', base=10)
figname = fig_root / 'lat_boxplot'

plt.tight_layout()
fig.savefig(figname)

print(f'Latency boxplot saved to {figname}.png' )


print( 'plotting application throughput vs time plot')

smooth_factor = 10
lat_smooth = [ get_smooth_line(latline, smooth_factor) for latline in lat_list  ]
bw_smooth = [ get_smooth_line(bwline, smooth_factor) for bwline in bw_list  ]
idx_smooth = [ idx[::smooth_factor] for idx in idx_list  ]

fig, ax_to_plt = plt.subplots()

ax_to_plt = axpltvstime( ax_to_plt, idx_smooth, bw_smooth, cases_names, list(range(len(cases_names))), 0) 
ax_to_plt.set_ylabel('Throughput (GB/ms)', labelpad=0)
## convert us to ms x-axis
us_ticks = ax_to_plt.get_xticks()[::2] 
ax_to_plt.set_xticks( us_ticks )
ax_to_plt.set_xticklabels( [ str(us//1000) for us in us_ticks  ]  )
ax_to_plt.set_xlabel('time (ms)', labelpad=0)

fig.legend( )
plt.tight_layout()
figname = fig_root / 'app_bw_vs_time'
fig.savefig(figname)
print( f'figure saved as {figname}.png ')

print( 'plotting application packet latency vs time plot')
fig, ax_to_plt = plt.subplots()

ax_to_plt = axpltvstime( ax_to_plt, idx_smooth, lat_smooth, cases_names, list(range(len(cases_names))), 0) 
ax_to_plt.set_ylabel('packet latency (us)', labelpad=0)
ax_to_plt.set_xlabel('time (ms)', labelpad=0)
## convert us to ms x-axis
us_ticks = ax_to_plt.get_xticks()[::2] 
ax_to_plt.set_xticks( us_ticks )
ax_to_plt.set_xticklabels( [ str(us//1000) for us in us_ticks  ]  )
ax_to_plt.set_xlabel('time (ms)', labelpad=0)

fig.legend( )
plt.tight_layout()
figname = fig_root / 'app_latency_vs_time'
fig.savefig(figname)
print( f'figure saved as {figname}.png ')

