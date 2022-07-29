## Reproduction of Fig 9 in the paper

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

## Where cosmoflow_null, cosmoflow_halo3d ... is stored
sim_data_dir='/home/ac.kang/q-adaptive_sst/wkdir'

plt.rcParams.update(
    {
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.labelsize": 8,
    'axes.titlesize': 8,
    }
)

# width_sc  = 3.337
width_sc  = 3.336
height_sc = width_sc / 1.618

# width_dc = 7.006
width_dc = 7.004
height_dc = width_dc / 1.618

script_root = os.path.dirname(os.path.realpath(__file__))
json_dir = Path('./json_res')

fig_root=Path('./fig')
fig_root.mkdir(parents=True, exist_ok=True)
json_dir.mkdir(parents=True, exist_ok=True)

motif_flds_cases = [
    [cosmoflow, null],
    [null, halo3d],
    [cosmoflow, halo3d],
    [cosmoflow, halo3d],
]

nodecnt_list = ['528','528']
target_motif_id_list = [0,1,0,1]

rting_list=[
    'par',
    'q-adaptive',
]

emberrandom_subite='1'

assert(len(motif_flds_cases) == len(target_motif_id_list))

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


label_name = [
    'cosmoflow_alone_par',
    'cosmoflow_alone_q',
    'halo3d_alone_par',
    'halo3d_alone_q',
    
    'cosmoflow_interfer_par',
    'cosmoflow_interfer_q',
    
    'halo3d_interfer_par',
    'halo3d_interfer_q',
]

## pad zero since Cosmoflow network activity starts from around 5500 us
cosmo_pos = [0,1,4,5]
for cos in cosmo_pos:
    idx_list[cos] = np.concatenate( [list(range(0,5500,100)) , idx_list[cos] ] )
    bw_list[cos] = np.concatenate( [ [0]*len(list(range(0,5500,100))) , bw_list[cos] ] )

smooth_factor = 10
lat_smooth = [ get_smooth_line(latline, smooth_factor) for latline in lat_list  ]
bw_smooth = [ get_smooth_line(bwline, smooth_factor) for bwline in bw_list  ]
idx_smooth = [ idx[::smooth_factor] for idx in idx_list  ]

## bwonly
figname = fig_root / 'Figure9'

figuresize = (width_dc, width_dc/3.3)
fig= plt.figure(figsize=figuresize)

subpltsarray=(1,2)
ax = [
    plt.subplot2grid(subpltsarray, (0, 0), colspan=1, rowspan=1), 
    plt.subplot2grid(subpltsarray, (0, 1), colspan=1, rowspan=1),
]

plot_datafile_idxs = [
    [0,2,4,6],
    [1,3,5,7]
]

linewidth=1
plt_params_alone={
    'linewidth': linewidth,
}

plt_params_interfer={
    'linewidth': linewidth,
    'linestyle': '--',
}

params_list = [plt_params_alone,plt_params_alone,plt_params_interfer,plt_params_interfer]

ax[0] = axpltvstime( ax[0], idx_smooth, bw_smooth, label_name, plot_datafile_idxs[0], 0, params_list) 
ax[1] = axpltvstime( ax[1], idx_smooth, bw_smooth, label_name, plot_datafile_idxs[1], 0, params_list) 


for axs in [ax[0], ax[1]]:
    axs.set_ylim((-0.5,5.5))

ax[0].set_xticks( [0,5000,10000,15000], ['0', '5', '10', '15'] )
ax[1].set_xticks( [0,5000,10000,15000], ['0', '5', '10', '15',] )

ax[0].set_xlabel('time (ms)\n(a)', labelpad=0)
ax[1].set_xlabel('time (ms)\n(b)', labelpad=0)

ax[0].set_title('PAR', pad=0)
ax[1].set_title('Q-adp', pad=0)

ax[0].set_ylabel('Throughput (GB/ms)', labelpad=0)

leghandles, leglabels = ax[0].get_legend_handles_labels()
leglabels_formal = ['CosmoFlow_alone', 'Halo3D_alone', 'CosmoFlow_interfered', 'Halo3D_interfered' ]
assert(len(leglabels_formal) == len(leghandles))
fig.legend(leghandles, leglabels_formal, 
           bbox_to_anchor=(0.05, 0.9, 0.935, .9), loc=3,
           borderaxespad=0.,
           ncol=len(leghandles),
           mode="expand",
           fontsize=8
          )


fig.subplots_adjust(left=0.05, right=0.985, bottom=0.21, top=0.84, wspace=0.15, hspace=0.38)
print(figname)
fig.savefig(figname)