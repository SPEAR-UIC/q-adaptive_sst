import os
import pandas as pd
import numpy as np
import math

## App definition
random={
    'name': 'random',
    'count': '384',
    'ite': '7200',
    'computet': '0' 
}

halo3d={
    'name': 'halo3d',
    'count': '72000',
    'ite':'30',
    'computet': '0'
}

naslu={
    'name': 'lu',
    'count': '1500',
    'ite': '3',
    'computet': '1'
}

lqcd={
    'name': 'lqcd',
    'count': '132',
    'ite': '1',
    'computet': '1'
}

fft3d={
    'name': 'fft3d',
    'count': '400',
    'ite': '8',
    'computet': 'x'
}

cosmoflow={
    'name': 'cosmoflow',
    'count': '140750',
    'ite': '2',
    'computet': '5160000'
}

## DL
allreduce={
    'name': 'allreduce',
    'count': '144000',
    'ite': '8',
    'computet': '0'
}

null={
    'name': 'null',
    'count': 'x',
    'ite': 'x',
    'computet': 'x'
}

stencil5d = {
    'name': 'stencil5d', 
    'count': '350000', 
    'ite': '1',
    'computet': '0'  
}

lulesh = {
    'name': 'lulesh', 
    'count': 'x',
    'ite': '12', 
    'computet': '0'
}


## plt tool
def ax_plt_bar_cluster(ax, data2plt, col2plt, bar_names, cluster_names, msg_count,
                       bar_label='', cluster_label='', bar_colors={}, 
                       scatter_max=False, param_dict={},
                       plt_bar_err=None,
                       err_bar_clr='#000000',
):
    bar_width=0.8
    cluster_space=0.8
    cluster_width=bar_width*len(bar_names)

    if not bar_label:
        bar_label = bar_names
    if not cluster_label:
        cluster_label = cluster_names

    ## Draw all the bars in each cluster
    for bar_id, bar_name in enumerate(bar_names):
        x_locs=[]
        plt_data=[]
        plt_err=[]
        plt_max = []
        plt_bar_errs = [ [], [] ]
        
        for cluster_id, cluster_name in enumerate(cluster_names):
            start_x = cluster_id * (cluster_width + cluster_space)
            x_locs.append( start_x + ( bar_id + 0.5 ) * bar_width)

            case_name =  f'{bar_name}_{cluster_name}'
            col_name = f'count{msg_count}_{col2plt}'
            datapoint2draw = data2plt.loc[data2plt['case'] == case_name][col_name].to_numpy()[0]
            plt_data.append( datapoint2draw )
            max_name = f'count{msg_count}_max'
            if scatter_max:
                plt_max.append( data2plt.loc[data2plt['case'] == case_name][max_name].to_numpy()[0])
            if plt_bar_err == 'max':
                anerr = data2plt.loc[data2plt['case'] == case_name][max_name].to_numpy()[0] - data2plt.loc[data2plt['case'] == case_name][col_name].to_numpy()[0]
                plt_bar_errs[0].append(0)
                plt_bar_errs[1].append(anerr)
            elif plt_bar_err == 'std':
                astd = data2plt.loc[data2plt['case'] == case_name][f'count{msg_count}_std'].to_numpy()[0]
                plt_bar_errs[0].append(astd/2)
                plt_bar_errs[1].append(astd/2) 
            elif plt_bar_err == None:
                plt_bar_errs = [ [0], [0] ]
            else:
                print('Unknown plt_bar_errs: ', plt_bar_err )
                
        this_bar_color = ''
        try:
            this_bar_color = bar_colors[bar_label[bar_id]]
        except:
            this_bar_color = ''
            
        if this_bar_color:
            ax.bar(x_locs, plt_data,  width=bar_width, label=f'{bar_label[bar_id]}', 
                   yerr=plt_bar_errs,
                   color=this_bar_color, ecolor=err_bar_clr)
        else:
            ax.bar(x_locs, plt_data,  width=bar_width, label=f'{bar_label[bar_id]}',
                  yerr=plt_bar_errs, ecolor=err_bar_clr)
        
        if scatter_max:
            ax.scatter(x_locs, plt_max, 
                           **param_dict,
                          )

    ax.set_xticks([0.5*cluster_width+cid*(cluster_space+cluster_width) for cid in range(0, len(cluster_label))])
    ax.set_xticklabels(cluster_label)
    return ax

## read the aggregated linkcontrol file
def read_job_linkctrl(res_f, job_bw, pkt_latencies, window_size = 1000, index_column='', raw_bw=True):
    # res_f aggregated linkcontrol file of 1 job
    # job_bw B/ns
    # pkt_latencies  ## return pkt_latency for boxplot?
    # window_size in ns
    # index_column = False for comma ended files

    fstline = "linkcontrol: jobid, vn, pktid, src, dest, bits, hop num, lat, send time, recv time, adp, val pos, midgroup, route_path\n"

    cols_names = ['jobid', 'vn', 'msgid', 'src', 'dest', 'bits', 'hop num', 'lat',
       'send time', 'recv time', 'adp', 'val pos', 'midgroup', ' route_path'] 

    with open(res_f, 'r') as f:
        fst_line = f.readline()
        if fst_line != fstline:
            assert fst_line == fstline , print( f'Error: expecting \n {fstline}\n got \n {fst_line}' )
        
    if index_column == 'False':
        job_df = pd.read_csv(res_f, names=cols_names, header=0, usecols=range(len(cols_names)), index_col=False)
    else:
        assert(index_column == '')
        job_df = pd.read_csv(res_f, names=cols_names, header=0, usecols=range(len(cols_names)))
    
    print('PID {}: read {}\n\tmsgs:{}, jobbw{}, win size:{}, get rawbw {}'.format(os.getpid(), res_f, job_df.shape[0], job_bw, window_size, raw_bw))

    plt_lat_list=[]
    if pkt_latencies == 'true':
        plt_lat_list=job_df['lat'].to_list()
    
    job_df['win_index_recv'] = job_df[['recv time']] // (window_size)
    job_df['win_index_inject'] = job_df[['send time']] // (window_size)
    
    recv_df = job_df[['win_index_recv','bits']].groupby('win_index_recv').sum().sort_index().copy()
    win_recv = recv_df.index.to_numpy()
    recv_df['bw'] = (recv_df['bits']/8)/(window_size)
    if not raw_bw:
        recv_df['bw'] = (recv_df['bw'])/(job_bw)
    
    mean_df = job_df[['win_index_recv','lat', 'hop num', 'adp']].groupby('win_index_recv').mean().sort_index()
    recv_df['avg lat'] = mean_df['lat']
    recv_df['avg hop'] = mean_df['hop num']
    recv_df['avg adp'] = mean_df['adp']
    
    #input bw
    inject_df = job_df[['win_index_inject','bits']].groupby('win_index_inject').sum().sort_index().copy()
    win_inject = inject_df.index.to_numpy()

    inject_df['bw'] = (inject_df['bits']/8)/(window_size)
    if not raw_bw:
        inject_df['bw'] = (inject_df['bw'])/(job_bw)
    
    return [plt_lat_list, win_recv.tolist(), recv_df['bw'].to_list(), recv_df['avg lat'].to_list(), recv_df['avg hop'].to_list(), recv_df['avg adp'].to_list(), win_inject.tolist(), inject_df['bw'].to_list(), res_f]
    
    
def axpltvstime( ax, idxlist, datalist, linenames, pltidxs, smooth_factor, param_dictlist=''  ):
    if not param_dictlist:
        param_dictlist=[{}]*len(pltidxs)
    pltid=0
    for lineid, line_n in enumerate(linenames):
        if lineid in pltidxs:
            if smooth_factor > 1:
                idx_smooth = idxlist[lineid][::smooth_factor]
                data_smooth = get_smooth_line(datalist[lineid],smooth_factor)
            else:
                idx_smooth = idxlist[lineid]
                data_smooth = datalist[lineid]
            ax.plot(idx_smooth, data_smooth, label=line_n, **param_dictlist[pltid])
            pltid+=1
    ax.grid()
    return ax

def get_smooth_line(line_list, smooth_factor):
    line_array = np.array(line_list)
    smooth_line = []
    for i in range( math.ceil(len(line_list)/smooth_factor) ):
        smooth_line.append(line_array[smooth_factor*i: smooth_factor*(i+1)].mean())
    return smooth_line


def global_port_to_destG(rid, gpid, num_groups, rpg, igpr):
    #groupid, rtrid(within system), globalportid(index from port0)
    # rid, np list  
    
    gid = rid // rpg
    rid %= rpg
    assert(gid<num_groups)
    assert(rid<rpg)
    assert(gpid < (rpg-1) + rpg )
    
    gpid = gpid - (rpg-1) - rpg//2
    
    if(gpid<0):
        return -1
    
    raw_dest = rid * igpr + gpid;
    
    assert(gpid<igpr)
    assert(raw_dest < num_groups-1)

    # Turn raw_dest into dest_grp and link_num
    link_num = raw_dest // (num_groups-1);
    dest_grp = raw_dest - link_num * (num_groups-1)

    if dest_grp >= gid:
        dest_grp = dest_grp + 1
    
    return dest_grp