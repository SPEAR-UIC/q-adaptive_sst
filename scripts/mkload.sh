#!/bin/bash

load_path=$1; shift

if [[ -f ${load_path} ]]; then
    echo "${load_path} already exist, skipping"
    exit 1
else
    touch "${load_path}"
fi

motifs=("$@")
## motif node numbers
last_idx=$(( ${#motifs[@]} - 1 ))
motifs_nnum=(${motifs[$last_idx]})  # array of motif node numbers
unset motifs[$last_idx]

num_motifjob=${#motifs[@]}

echo "Num jobs ${num_motifjob}. Motifs are: "
for motif in "${motifs[@]}"; do
    echo ${motif}
done

if (( num_motifjob > 10 )); then
    echo "mkload.sh: Merlin::Portcontrol only support up to 5 jobs so far ...."
    exit 1
fi

if (( ${num_motifjob} != ${#motifs_nnum[@]} )); then
    echo "mkload.sh Error: motif job (${num_motifjob}): ${motifs[@]}"
    echo "motif node number (${#motifs_nnum[@]}): ${motifs_nnum[*]}  "
    exit 1
fi 

read -a nidlist_1056 < $HOME/scripts/df1056_random.list

syssize=${#nidlist_1056[@]}
if (( syssize != 1056 )); then
    echo "Not running on a 1056 node system, size is ${syssize}"
    exit 1
fi

total_motif_node=0
for node_num in "${motifs_nnum[@]}"; do
    total_motif_node=$((total_motif_node + node_num))
done
if (( total_motif_node != syssize )); then
    echo "Error, motif nodes: ${motifs_nnum[*]}, total motif nodes ${total_motif_node} != sys size ${syssize}"
    exit 1
fi 

# location of emberNull and backgd job is explicitly passed in 
rest_nnum=$((syssize-total_motif_node))
echo "random nid list had ${#nidlist_1056[@]} nodes"
echo "   first 5 elements are ${nidlist_1056[*]:0:5}"
echo "   last 5 elements are ${nidlist_1056[@]:1051}"
echo "   ${num_motifjob} motif jobs: ${motifs[@]}"
echo "   motif job size: ${motifs_nnum[*]}, rest ${rest_nnum}"

node_start_id=0
for (( jobid=0; jobid<num_motifjob; jobid++ )); do
    motif_str=${motifs[${jobid}]}
    nids="${nidlist_1056[@]:${node_start_id}:${motifs_nnum[${jobid}]}}"
    node_start_id=$((node_start_id+${motifs_nnum[${jobid}]}))
    nids="${nids// /,}"

    echo "[JOB_ID] ${jobid}" >> ${load_path}
    echo "[NID_LIST] ${nids}" >> ${load_path}

    if [[ "${motif_str}" == "null" ]]; then
        echo "[MOTIF] Null" >> ${load_path}

    else
        echo "[MOTIF] Init" >> ${load_path}
        echo "[MOTIF] ${motifs[${jobid}]}" >> ${load_path}
        echo "[MOTIF] Fini" >> ${load_path}
    fi

    echo "[NUM_CORES] 1" >> ${load_path}
    echo >> ${load_path}

done
