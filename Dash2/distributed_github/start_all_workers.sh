#!/bin/bash

function start_single_worker {
	CURR_NODE_ID=$1
	ZK_NODE_ID=$2
	WEBDASH_CLONE=$3
	cd $WEBDASH_CLONE/Dash2/distributed_github/
	python dash_worker.py $ZK_NODE_ID $CURR_NODE_ID
}

function start_all {

	source ./deter.conf

	NUMBER_OF_NODES=${#DASH_NODES[@]}
    echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
	do
        echo 'Starting workers on node ' ${DASH_NODES[$ID-1]}
        let MAX_PROC_ID=$NUMBER_OF_WORKERS_PER_NODE-1
        for PROC_ID in `seq 0 $MAX_PROC_ID`;
        do
            let WORKER_ID=$ID+$PROC_ID*$NUMBER_OF_NODES
            echo 'Starting worker '  $WORKER_ID
            ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/start_all_workers.sh $WORKER_ID ${ZK_MAP[${DASH_NODES[$ID-1]}]}:2181 $WEBDASH_CLONE"
        done

	done
	echo 'workers are running'
}


if [ -z "$1" ]
then 
	start_all
else
	start_single_worker $1 $2 $3
fi




