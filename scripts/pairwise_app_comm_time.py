# Plot target application communication time
# similar to Fig 4,8 in the paper

import os,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict
from pathlib import Path

from df_utils import *

## ------------ consider to update ----------------------
target_app = cosmoflow     
background_apps = [null, random]
rting_list = ['q-adaptive']

sim_data_dir = '~/mnt/wkdir'
fig_root = Path('./fig')
## ------------------------------------------------------


fig_root.mkdir(parents=True, exist_ok=True)
motif_flds = [ [target_app, null, bgapp] if target_app == lulesh else [target_app, bgapp] 
               for bgapp in background_apps  ]
nodecnt_list = ['512', '16', '528'] if target_app == lulesh else ['528', '528']
emberrandom_subite='1'

csv_fname={
    "allreduce": "emberAllreduce_8_144000_0",
    'halo3d': 'emberHalo3D',
    "fft3d": "emberFFT3D",
    "naslu": "emberNASLU",
    "lqcd": "emberLQCD",
    "cosmoflow": "emberAllreduce_2_140750_5160000",
    'all2allv': "emberA2Av",    
    'random': "emberRandom",
    'stencil5d': 'emberStencil5d',
    'lulesh': 'emberLulesh',
}

rank_comm_time = {}
app_run_time = {}
rank_comm_df = {}
app_run_time_df = {}
motif_flds_strlist = {}
motif_msgcount={}
bgapps={}

motif_study_id = 0
motif_target_id = 0

# simfolder??
assert(motif_target_id<2)
motif_target_name = ''
num_iterations = ''
msgcount = ''
bgapps_amotif=[]

for motif_fld in motif_flds:
    
    if (len(motif_fld)>2):
        print(' WARNING !!!! this is for pairwise analysis, \
    assumming target and bck app takes first and last postion')

    bgapps_amotif.append(motif_fld[len(motif_fld)-1-motif_target_id]['name'])
    
    if motif_target_name:
        if(motif_target_name != motif_fld[motif_target_id]['name']):
            print(motif_target_name , motif_fld[motif_target_id]['name'])
        assert(motif_target_name == motif_fld[motif_target_id]['name'])
        assert(num_iterations == motif_fld[motif_target_id]['ite'])
        assert(msgcount == motif_fld[motif_target_id]['count'])
    else:
        motif_target_name = motif_fld[motif_target_id]['name']
        num_iterations = motif_fld[motif_target_id]['ite']
        msgcount = motif_fld[motif_target_id]['count']

num_iterations = int(num_iterations)

print(f'Plotting for {motif_target_name}, under background:{bgapps_amotif}')

motif_flds_strlist[motif_target_name] = [
    '_'.join( motifcase['name'] for motifcase in motifs ) for motifs in motif_flds
]
motif_msgcount[motif_target_name] = msgcount
bgapps[motif_target_name] = bgapps_amotif
rank_comm_time[motif_target_name] = []
app_run_time[motif_target_name] = []

print(f'Parsing simulation data...')
## Read emberlog file
for motiffldid, motif_fld in enumerate(motif_flds):
    for rtingid, rting in enumerate(rting_list):
        motifs_str = '_'.join( motif['name'] for motif in motif_fld  )
        msgstrs = '_'.join( motif['count'] for motif in motif_fld  )
        ite_str = '_'.join( motif['ite'] for motif in motif_fld  )
        cp_str = '_'.join( motif['computet'] for motif in motif_fld  )
        nodecnt_str = '_'.join(nodecnt_list)

        case_name= motifs_str+f'_{rting}'
        case_entry_commtme = [case_name]
        case_entry_runtme = [case_name]

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
                                'ember_stats',
                                "motif_"+csv_fname[motif_target_name]+".csv"
                                )

        df = pd.read_csv(df_path)
        df_focus_ites = df.loc[(df['ite'] >= 1) & (df['ite'] <= num_iterations)] 

        total_time = (df_focus_ites['stop(ns)'].max() - df_focus_ites['start(ns)'].min()) /1000000
        case_entry_runtme.append(total_time)

        comm_time = df_focus_ites.groupby('rank').sum()['comm(ns)'].to_numpy() / 1000000 ##ms
        case_entry_commtme += [comm_time.mean(), comm_time.max(), comm_time.std()]

        rank_comm_time[motif_target_name].append(case_entry_commtme)
        app_run_time[motif_target_name].append(case_entry_runtme)

print(f'Parsing simulation data... DONE')  

col_names_commtme = ['case']
col_names_commtme += [f'count{msgcount}_mean', f'count{msgcount}_max', f'count{msgcount}_std']
rank_comm_df[motif_target_name] = pd.DataFrame(rank_comm_time[motif_target_name], columns=col_names_commtme)

col_names_runtme = ['case']
col_names_runtme += ['total time(us)']  

app_run_time_df[motif_target_name] = pd.DataFrame(app_run_time[motif_target_name], columns = col_names_runtme)

app_name={
    'null': 'None',
    'random': 'UR',
    'naslu': 'LU',
    'fft3d': 'FFT3D',
    'allreduce': 'DL',
    'halo3d': 'Halo3D', 
    'lqcd': 'LQCD',
    'cosmoflow': 'CosmoFlow',
    'stencil5d': 'Stencil5D',
    'lulesh': 'LULESH',
}

app_color={   
    'null': (0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0),
    'random': (1.0, 0.4980392156862745, 0.054901960784313725, 1.0),
    'naslu': (0.17254901960784313, 0.6274509803921569, 0.17254901960784313, 1.0),
    'fft3d': (0.8392156862745098, 0.15294117647058825, 0.1568627450980392, 1.0),
    'allreduce': (0.5803921568627451, 0.403921568627451, 0.7411764705882353, 1.0),
    'halo3d': (0.5490196078431373, 0.33725490196078434, 0.29411764705882354, 1.0),
    'lqcd': (0.8901960784313725, 0.4666666666666667, 0.7607843137254902, 1.0),
    'cosmoflow': (0.4980392156862745, 0.4980392156862745, 0.4980392156862745, 1.0),
    'stencil5d': '#bcbd22', 
    'lulesh': '#17becf',
}

fig, ax_to_plt = plt.subplots()

motif_id = 0
target_motif = target_app['name']
figname =  fig_root / (f'comm_time_{target_motif}')

ax_to_plt = ax_plt_bar_cluster(ax_to_plt, 
        rank_comm_df[target_motif], f'mean', motif_flds_strlist[target_motif], 
        rting_list, motif_msgcount[target_motif], 
        bar_label=bgapps[target_motif], cluster_label=rting_list,
        bar_colors=app_color,
        scatter_max=False,
        param_dict = {
        'color':  '#7f7f7f',
        'marker': '*',
        's': 10,
        },
        plt_bar_err='std',            
        err_bar_clr='#5E5E5E'                       
    )

ax_to_plt.grid()
ax_to_plt.set_title(app_name[target_motif], pad=0)
ax_to_plt.set_axisbelow(True)
ax_to_plt.tick_params(axis='x', which='major', pad=2)
ax_to_plt.tick_params(axis='y', which='major', pad=0)
ax_to_plt.set_ylabel('Comm. Time (ms)', labelpad=0)

leghandles, leglabels = ax_to_plt.get_legend_handles_labels()

leglabels_formalname = [ app_name[motifname] for motifname in leglabels ]
assert(len(leglabels_formalname) == len(leghandles))

leghandles_wtitle = [plt.plot([],marker="", ls="")[0]] + leghandles
leglabels_wtitle = ["Background:"] + leglabels_formalname  # Merging labels

figlengd = fig.legend(leghandles_wtitle, leglabels_wtitle, 
           bbox_to_anchor=(0.05, 0.96, 0.94, .9), loc=3,
           borderaxespad=0.,
           ncol=len(leghandles_wtitle),
           mode="expand",
           fontsize=8,
           handletextpad=0.2
          )

for vpack in figlengd._legend_handle_box.get_children()[:1]:
    for hpack in vpack.get_children():
        hpack.get_children()[0].set_width(0)

fig.savefig(figname)
print(f'Plot saved to : {figname}.png')