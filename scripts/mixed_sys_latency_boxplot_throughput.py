## plot system wide packet latency distribution and throughput
## e.g. fig 13 in the paper

import pandas as pd
import numpy as np
import os,sys,time
import matplotlib.pyplot as plt
from pathlib import Path
import ujson as json
import math

from df_utils import *

# ------------- Consider to update ----------------------------
simroot_path = '/home/df_user/mnt/wkdir/fft3d_cosmoflow_lu_random_lqcd_stencil5d/'
rtings = [
    # 'ugal-3vc_count_itesx1_node140_138_140_139_256_243_ct__',
    # 'ugal-4vc_count_itesx1_node140_138_140_139_256_243_ct__'
    # 'par_count_itesx1_node140_138_140_139_256_243_ct__',
    'q-adaptive_count_itesx1_node140_138_140_139_256_243_ct__',
]

## corresponds to rting_cases
label_name = [
    # 'UGALg', 
    # 'UGALn', 
    # 'PAR', 
    'Q-adp'
    ]

fig_root = Path('./fig')
json_dir = Path('./json_res')
# -------------------------------------------------------------

fig_root.mkdir(parents=True, exist_ok=True)
json_dir.mkdir(parents=True, exist_ok=True)

script_root = os.path.dirname(os.path.realpath(__file__))

motifs='fft3d_cosmoflow_lu_random_lqcd_stencil5d'

data_files = [
    os.path.join(simroot_path, rting,
                 'link_control_data/aggregate.result')
    for rting in rtings
]

for apath in data_files:
    assert os.path.isfile(apath), print('Check file path, cannot find {apath}')

json_p = json_dir / 'tmp.json'
read_script=os.path.join(script_root, 'parallel_read_linkcontrol.py')

print(data_files)

print(' Reading and parsing data files ... ')

f2read = ''.join(str(data_files).strip('[]').split(','))

# os.system(f'python3 {read_script} {json_p} 1000 False true --datafs {f2read} --rawbw True') 

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
    
    indi_pkt_lat_list.append(np.array(res[0])/1000)  # ns => us
    idx_list.append(np.array(res[1]))
    bw_list.append(np.array(np.array(res[2]))/1000)  ## GB/ms
    lat_list.append(np.array(res[3])/1000)           # ns => us
    hop_list.append(np.array(res[4]))
    adp_list.append(np.array(res[5]))
    
    idx_inject_list.append(np.array(res[6]))
    bw_inject_list.append(np.array(res[7]))

percentiles=[95,99]
p99_list=[]

for alatlist in lat_list:
    p99_list.append(np.percentile( alatlist, percentiles, method='lower')) 

smooth_factor = 10
lat_smooth = [ get_smooth_line(latline, smooth_factor) for latline in lat_list  ]
bw_smooth = [ get_smooth_line(bwline, smooth_factor) for bwline in bw_list  ]
idx_smooth = [ idx[::smooth_factor] for idx in idx_list  ]



fig, axs = plt.subplots(1, 2)

bxdit = axs[0].boxplot(lat_list, 
            showfliers = False,
            showmeans = True,
            meanprops = {
                'markersize':4,
            }
           )
axs[0].set_xticklabels(label_name, rotation=-20)

for ppid, pnum in enumerate(percentiles):
    axs[0].scatter(range(1,len(rtings)+1), [ ptiles[ppid] for ptiles in p99_list ], label=f'p{pnum}', s=16)
axs[0].set_ylabel('Packet Latency (us)', labelpad=0)
axs[0].set_xlabel('(a)', labelpad=-1)

for idx in range(len(label_name)):
    axs[1].plot(idx_smooth[idx], bw_smooth[idx], label = label_name[idx], linewidth=1, alpha=0.8 )

axs[1].set_xticks( [0,10000,20000,30000, 40000], ['0', '10', '20', '30', '40'])
axs[1].set_xlabel('time (ms)\n(b)', labelpad=0)
axs[1].set_ylabel('Throughput (GB/ms)', labelpad=0)

leghandles, leglabels = axs[0].get_legend_handles_labels()
axs[0].legend( 
    [leghandles[1], leghandles[0], bxdit['means'][0]], 
    ['p99', 'p95', 'mean'],
    bbox_to_anchor=(0.0, 1.03, 1, .9), loc=3,
    ncol=len(leghandles)+1,
    mode="expand",
    fontsize=8,
    borderaxespad= 0.0,
    handletextpad=-0.6
          )

axs[1].legend( 
    bbox_to_anchor=(0.0, 1.03, 1, .3), loc=3,
    borderaxespad=0.,
    ncol=2,
    mode="expand",
    fontsize=8,
    handletextpad=0.08
          )

plt.tight_layout()

figname = fig_root / 'mixed_sys_pktlat_throughput'
fig.savefig(figname)

print(f'plot saved to {figname}.png')