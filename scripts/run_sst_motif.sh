#!/bin/bash

echo_usage () {
    echo
    echo "USAGE: $0 <cmd> [options]"
    echo "  cmd:"
    echo "    pairwise, mixed: pairwise or mixed workload study"
    echo "  options:"
    echo "      --target: fft3d, lu, lqcd, cosmoflow, stencil5d, lulesh, all(for mixed workload), default cosmoflow"
    echo "      --background: null, random, lu, fft3d, allreduce (for DL), halo3d, default null"
    echo "      --rting: ugal-3vc (for UGALg), ugal-4vc (for UGALn), par (for PAR), q-adaptive, default q-adaptive"  
    echo "      --np: number of MPI ranks for simulation, default \$(nproc)/2 "
    echo
}

TEMP=$(getopt -o h --long help,target:,background:,rting:,np: \
              -n $0 -- "$@")

if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi
eval set -- "$TEMP"

targetapp=cosmoflow
bgapp=null
mpi_ranks=$(($(nproc)/2))
rting_list=()

while true; do
    case "$1" in
        -h|--help ) echo_usage; exit ;;
        --np ) mpi_ranks="$2"; shift 2 ;;
        --target ) targetapp="$2"; shift 2 ;;
        --background ) bgapp="$2"; shift 2 ;;
        --rting ) rting_list+=("$2"); shift 2 ;;
        -- ) shift; break ;;
        * ) break ;;
    esac
done

if (( ${#rting_list[@]} == 0 )); then
    rting_list=(q-adaptive)
fi

# handle non-option arguments
if [[ $# -ne 1 ]]; then
    echo "Missing cmd: pairwise, mixed"
    echo_usage
    exit
fi

mode=$1

ROOT_DIR=$(dirname $(readlink -f $0))  

echo "********"
echo "  ${mode} workload analysis with ${mpi_ranks} processes"
echo "  routing algorithms: ${rting_list[*]}"

if [[ "${mode}" == "pairwise" ]]; then
    echo "   ${targetapp} v.s. ${bgapp}"
fi
echo "********"

run_script="${ROOT_DIR}/dragonfly-motif.sh"
io_thld=10000000 ## IO for every 10MB message

if [[ "${mode}" == "pairwise" ]]; then
    multidgridsize="[2,2,3,4,11]"  ## 5d stencil 528 nodes
    if [[ "${targetapp}" == "lulesh" ]]; then
        motif="${targetapp} null ${bgapp}"
        motif_nnum="512 16 528"
    else
        motif="${targetapp} ${bgapp}"
        motif_nnum="528 528"
    fi

else
    multidgridsize="[3,3,3,3,3]"  ## 243 nodes
    motif_nnum="140 138 140 139 256 243"

    if [[ "${targetapp}" == "all" ]]; then
        motif="fft3d cosmoflow lu random lqcd stencil5d"

    elif [[ "${targetapp}" == "fft3d" ]]; then
        motif="fft3d null null null null null"

    elif [[ "${targetapp}" == "cosmoflow" ]]; then
        motif="null cosmoflow null null null null"

    elif [[ "${targetapp}" == "lu" ]]; then
        motif="null null lu null null null"

    elif [[ "${targetapp}" == "random" ]]; then
        motif="null null null random null null"

    elif [[ "${targetapp}" == "lqcd" ]]; then
        motif="null null null null lqcd null"

    elif [[ "${targetapp}" == "stencil5d" ]]; then
        motif="null null null null null stencil5d"
    else
        echo "unknown app: ${targetapp}"
        exit
    fi
fi

for rtings in "${rting_list[@]}"; do 
    ${run_script} "${motif}" "${rtings}" "${motif_nnum}" ${io_thld} ${mpi_ranks} ${multidgridsize}
done
