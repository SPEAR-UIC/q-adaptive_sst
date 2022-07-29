#!/bin/bash

motifs=($1)
rtings=($2)
motif_nnum=$3
io_thld=${4}
mpi_ranks=${5}
## for emberStencilNd
multdgridsize=${6}
stats_startat=0us
start=$(date +%s)

#; openmpi
export OMPI_MCA_btl_vader_single_copy_mechanism=none

#; sst env
export SST_INSTALL=$HOME/sst/install
export PATH=$SST_INSTALL/sst-core/bin:$PATH
export PATH=$SST_INSTALL/sst-elements/bin:$PATH
export LD_LIBRARY_PATH=$SST_INSTALL/sst-elements/lib:$LD_LIBRARY_PATH

ROOT_DIR=$(dirname $(readlink -f $0))  

CONFIG_DIR=$ROOT_DIR/config

export PYTHONPATH=${CONFIG_DIR}
export PYTHONPATH=$HOME/sst/src/sst-elements/src/sst/elements/ember/test:${PYTHONPATH}
export PYTHONPATH=$ROOT_DIR/../sst-elements/src/sst/elements/ember/test:${PYTHONPATH}

cwd=$(pwd)
echo "curr dir is ${cwd}"



mkload=${ROOT_DIR}/mkload.sh
PLATFORM="platform_df1056"     ## __import__() this file
STATSMOD="statModule1056"      ## __import__() this file

motifs_str="${motifs[*]}"
motifs_str="${motifs_str// /_}"
motifs_node_str="${motif_nnum// /_}"

echo "Bash: rting is ${rtings[*]}"
echo "Bash: motif is ${motifs[*]} <-> ${motifs_str}"
echo "Bash: motif node number ${motif_nnum} <-> ${motifs_node_str}"

launched_sims=0
for rting in "${rtings[@]}"; do 
    qtable_path=''
    if [[ "${rting}" == "q-adaptive" ]]; then
        rting_realname="q-adaptive"
        qlr1="0.2"
        qlr2="0.04"
        explore="0.001"
        qthld1="0.2"
        qthld2="0.35"

    elif [[ "${rting}" == "ugal-3vc" || "${rting}" == "ugal-4vc" || "${rting}" == "par" ]]; then
        rting_realname=${rting}
        qlr1="-1"
        qlr2="-1"
        explore="-1"
        qthld1="-1"
        qthld2="-1"

    else
        echo "Unknown routing: ${rting}"
        exit 1
    fi 

    motif_id=0
        ember_motif=()
        motif_node_list=(${motif_nnum})

        list_idx=0
        for motif in "${motifs[@]}"; do
            computetime=${motif_compute_time_list[${list_idx}]}
            node_num=${motif_node_list[${list_idx}]}
            if (( node_num == 528 )); then ##1/2 system
                shape_2d=(22 24)
            elif (( node_num == 512 )); then
                shape_2d=(16 32)
                shape_3d=(8 8 8)
            elif (( node_num == 140 )); then
                shape_2d=(10 14)
            elif (( node_num == 16 || node_num == 138 || node_num == 139 || node_num == 243 || node_num == 256 )); then
                shape_2d=(x x) ## let it pass
            else
                echo "Error unknown jobsize : ${node_num} for motif ${motif}"
                exit 1
            fi

            if [[ "${motif}" == "halo3d" ]]; then
                ember_motif+=("Halo3D nx=1 ny=1 nz=1 pex=0 pey=0 pez=0 fields_per_cell=72000 datatype_width=8 doreduce=0 computetime=0 copytime=0 iterations=30 wait2start=350000")

            elif [[ "${motif}" == "stencil5d" ]]; then
                ember_motif+=("StencilNd gridsize=${multdgridsize} fields_per_cell=350000 datatype_width=8 computetime=0 iterations=1 wait2start=350000 doreduce=0")

            elif [[ "${motif}" == "allreduce" ]]; then
                ember_motif+=("Allreduce iterations=8 compute=0 count=$((1*144000)) wait2start=350000 dobarrier=false")

            elif [[ "${motif}" == "lu" ]]; then
                ember_motif+=("NASLU nx=1500 ny=1500 nz=1500 nzblock=10 pex=${shape_2d[0]} pey=${shape_2d[1]} iterations=3 computetime=1 wait2start=350000")
            
            elif [[ "${motif}" == "fft3d" ]]; then
                ember_motif+=("FFT3D nx=400 ny=400 nz=400 npRow=${shape_2d[0]} iterations=8 wait2start=350000")

            elif [[ "${motif}" == "lqcd" ]]; then
                ember_motif+=("LQCD nx=132 ny=132 nz=132 nt=132 iterations=1 computetime=1 wait2start=350000")

            elif [[ "${motif}" == "cosmoflow" ]]; then
                ember_motif+=("Allreduce iterations=2 compute=5160000 count=$((1*140750)) wait2start=350000 dobarrier=false")

            elif [[ "${motif}" == "random" ]]; then
                ember_motif+=("Random iterations=7200 subiterations=1 compute=0 messagesize=$((1*384)) waitunblock=1 report_step=1000 wait2start=350000")

            elif [[ "${motif}" == "lulesh" ]]; then
                ember_motif+=(
                    "Lulesh iterations=12 dobcast=1 doreduce=1 do3dnn26=1 do3dsweep=1 pex=${shape_3d[0]} pey=${shape_3d[1]} pez=${shape_3d[2]} pep=${shape_2d[0]} peq=${shape_2d[1]} kba=100 msgscale=1 compute=0 wait2start=350000"
                )

            elif [[ "${motif}" == "bg"* || "${motif}" == "null" ]]; then
                ember_motif+=(${motif})

            else
                echo "qos-dragonfly-motif.sh: unknown motif: ${motif} "
                exit 1
            fi

            ((list_idx++))
        done 

            echo "motifstr is ${motifs_str}"
            if [[ "${motifs_str}" == *"random"* ]]; then
                work_dir=${cwd}/${motifs_str}/${rting}_count${msg_count}_ites${motif_ites}x1_node${motifs_node_str}_ct${computetimes}__
            
            elif [[ "${motifs_str}" == *"allreduce"* || "${motifs_str}" == *"cosmoflow"* ]]; then
                work_dir=${cwd}/${motifs_str}/${rting}_count${msg_count}_ites${motif_ites}_node${motifs_node_str}_ct${computetimes}_barrierfalse__
            
            elif [[ "${motifs_str}" == *"lulesh"* ]]; then
                luleshflagstr=${luleshflags[@]}
                luleshflagstr=${luleshflagstr// /_}
                work_dir=${cwd}/${motifs_str}/${rting}_ites${motif_ites}_node${motifs_node_str}_ct${computetimes}_flgs${luleshflagstr}__
            else
                work_dir=${cwd}/${motifs_str}/${rting}_count${msg_count}_ites${motif_ites}_node${motifs_node_str}_ct${computetimes}__
            fi
            
            if [[ -d ${work_dir} ]]; then
                echo "working dir: ${work_dir} already exist, skipping"
            else 
                mkdir -p ${work_dir}

                LOADFILE=${work_dir}/df_1056_auto.load

                echo "Motifs passed to mkload: ${ember_motif[@]}"
            
                if (${mkload} ${ROOT_DIR} ${LOADFILE} "${ember_motif[@]}" "${motif_nnum}"); then
                    echo
                    echo "start job in ${work_dir}"
                    date
                    echo
                    ## run in subshell, background, parallel

                    sst_opts=(
                        --model-options=" \
--loadFile=$LOADFILE \
--platform=$PLATFORM \
--topo=dragonfly \
--algoRting=${rting_realname} \
--stats_startat=${stats_startat} \
--numVNs=1 \
--smallCollectiveVN=-1 \
--smallCollectiveSize=-1 \
--qlr1=${qlr1} \
--qlr2=${qlr2} \
--explore=${explore} \
--qthld1=${qthld1} \
--qthld2=${qthld2} \
--qtable_path=${qtable_path} \
--io_level=2 \
--io_thld=${io_thld} \
"
                        ${CONFIG_DIR}/emberLoad_df1056.py
                        --heartbeat-period=6ms
                        --stop-at=100ms \
                    )

                    echo "-----------------SST CMD----------------------"
                    echo mpirun -np ${mpi_ranks} sst \""${sst_opts[@]}"\" ">sim_output 2>&1"
                    echo "----------------------------------------------"

                    dirroot=$(pwd)
                    cd ${work_dir} && touch ${COBALT_JOBID}.jid && time mpirun -np ${mpi_ranks} sst "${sst_opts[@]}" |& tee output
                    cd ${dirroot}

                else
                    echo "Err making load file ${LOADFILE}"
                fi
            fi
            echo

done

wait
echo "Script finish"
echo
