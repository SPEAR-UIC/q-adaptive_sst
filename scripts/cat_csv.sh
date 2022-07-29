#!/bin/bash

catmode=$1  # stats | linkcontrol     | emberlog
jobId=$2    #  ""   | jobid: 0,1,2... |  app name
exclude_pattern=$3

declare -A emberlog_maps
emberlog_maps["fft3d"]="emberFFT3D"
emberlog_maps["lu"]="emberNASLU"
emberlog_maps["lqcd"]="emberLQCD"
emberlog_maps["cosmoflow"]="emberAllreduce_2_140750_5160000"
emberlog_maps["stencil5d"]="emberStencil5d"
emberlog_maps["lulesh"]="emberLulesh"
emberlog_maps["random"]="emberRandom"

start=(date +%s)

catcsvs() {
    if [[ ! -d ./link_control_data ]]; then
        echo "Not a simulation root dir: $(pwd)"
        echo "Execute cmd under the sim root dir"
        exit 1
    fi

    if [[ "$catmode" == "stats" ]]; then
        RES_DIR="."
        RES_FILE="all_stats.csv"

        head -1 ${RES_DIR}/stats_0.csv > ${RES_DIR}/${RES_FILE} 
        tail -n +2 -q ${RES_DIR}/stats_*.csv >> ${RES_DIR}/${RES_FILE}
        echo "     stats_*.csv >> ${RES_DIR}/${RES_FILE}"

    elif [[ "$catmode" == "linkall" ]]; then
        RES_DIR="./link_control_data"
        RES_FILE="aggregate.result"
        head -1 ${RES_DIR}/job0.result > ${RES_DIR}/${RES_FILE} 
        tail -n +2 -q ${RES_DIR}/job*.result >> ${RES_DIR}/${RES_FILE}
        echo "     $(pwd)/job*.result >> ${RES_DIR}/${RES_FILE}"

    elif [[ "$catmode" == "linkcontrol" ]]; then
        # concat linkcontrol data file
        RES_DIR="./link_control_data"
        if [[ ${#jobId} -eq 1 ]]; then
            RES_FILE="job${jobId}.result"

            if [[ -f "${RES_DIR}/${RES_FILE}" ]]; then
                echo "     $(pwd)/ already done, skipping ...."
            else
                head -1 ${RES_DIR}/linkcontrol_job${jobId}_*_0 > ${RES_DIR}/${RES_FILE} 
                tail -n +2 -q ${RES_DIR}/linkcontrol_job${jobId}* >> ${RES_DIR}/${RES_FILE}
                echo "     $(pwd)/linkcontrol_job${jobId}* >> ${RES_DIR}/${RES_FILE}"	
            fi
        else 
            echo "cat_job1.sh <jobid: 1, 2, 12>"
        fi

    elif [[ "$catmode" == "rmlink" ]]; then
        # rm individual linkcontrol data file
        RES_DIR="./link_control_data"
        if [[ ${#jobId} -eq 1 ]]; then
            RES_FILE="job${jobId}.result"
            if [[ -f "${RES_DIR}/${RES_FILE}" ]]; then
                echo "Found ${RES_DIR}/${RES_FILE} ..."
                rm ${RES_DIR}/linkcontrol_job${jobId}*
                echo "DONE: rm ${RES_DIR}/linkcontrol_job${jobId}*"
            else
                echo "!!! Cannot found aggregate file: ${RES_DIR}/${RES_FILE}"
                echo "Double check to avoid unwanted delete"
            fi
        else 
            echo "cat_job1.sh rmlink <jobid: 1, 2, 12>"
        fi

    elif [[ "$catmode" == "emberlog" ]]; then
        # concat stats file
        RES_DIR="./ember_stats"
        embername=${emberlog_maps[${jobId}]}   
        RES_FILE="motif_${embername}.csv"

        if compgen -G "${RES_DIR}/${embername}_rank0_*" > /dev/null; then

            head -1 ${RES_DIR}/${embername}_rank0_* > ${RES_DIR}/${RES_FILE} 
            tail -n +2 -q ${RES_DIR}/${embername}_rank* >> ${RES_DIR}/${RES_FILE}
            echo "     $(pwd)/${RES_DIR}/${embername}_rank* >> ${RES_DIR}/${RES_FILE}"
        else 
            echo "No ${RES_DIR}/${embername}_rank0_*, skipping..."
        fi

    else
        echo "cat_job.sh <mode:stats,linkcontrol,emberlog> <jobid/appname>"
        echo "----check executed from root of sim folder"
        exit
    fi
}

if [[ -d ./link_control_data ]]; then
    (time catcsvs)
else
    echo "checking sub dirs:"

    for subdir in ./*; do
        if [[ "${subdir}" != *"${exclude_pattern}"* || "${exclude_pattern}" == "" ]]; then
            if [[ -d ${subdir}/link_control_data ]]; then
                # echo "go down 1 level: ${subdir}..."
                (cd ${subdir} && time catcsvs) &
            else
                for subsubdir in ${subdir}/*; do
                    # echo "go down 2 level: ${subsubdir}..."
                    if [[ "${subdir}" != *"${exclude_pattern}"* || "${exclude_pattern}" == "" ]]; then
                        (cd ${subsubdir} && time catcsvs) &
                    else
                        echo "skipping pattern: ${exclude_pattern} // ${subdir}"
                    fi   
                done
            fi
        else
            echo "skipping pattern: ${exclude_pattern} // ${subdir}"
        fi
    done
fi

wait 

end=(date +%s)
runtime=$((end-start))
runtime=$(echo "${runtime}/60" | bc)
echo "all done: ${runtime} mins"