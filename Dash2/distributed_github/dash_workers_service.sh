#!/bin/bash

CONFIG_FILE_PATH=./deter.conf # path is relative to $WEBDASH_CLONE/Dash2/distributed_github/

function perfom_action_on_single_node {
	CURR_NODE_ID=$1
	ZK_NODE_ID=$2
	WEBDASH_CLONE=$3
	ACTION=$4

	cd $WEBDASH_CLONE/Dash2/distributed_github/

	if [ $ACTION == 'stop' ]
	then
		echo 'Stopping Dash worker ...'
        kill $(ps x | grep  "dash_worker.py $CURR_NODE_ID" | grep -v grep | awk '{print $1}')
	elif [ $ACTION == 'start' ]
	then
		echo 'Starting Dash worker ...'
	    python dash_worker.py $ZK_NODE_ID $CURR_NODE_ID
	else
		echo 'Unrecognized action ' $ACTION
		exit
	fi
}

function perform_action_on_all_nodes {
	source $CONFIG_FILE_PATH
	SCRIPT_NAME=$0
	ACTION=$1

    echo 'script name' $SCRIPT_NAME
	NUMBER_OF_NODES=${#DASH_NODES[@]}
    echo 'Total ' $NUMBER_OF_NODES ' nodes in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
	do
        echo 'Starting workers on node ' ${DASH_NODES[$ID-1]}
        let MAX_PROC_ID=$NUMBER_OF_WORKERS_PER_NODE-1
        for PROC_ID in `seq 0 $MAX_PROC_ID`;
        do
            let WORKER_ID=$ID+$PROC_ID*$NUMBER_OF_NODES
            echo 'Starting worker '  $WORKER_ID
            ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/$SCRIPT_NAME $WORKER_ID ${ZK_MAP[${DASH_NODES[$ID-1]}]}:2181 $WEBDASH_CLONE $ACTION"
        done

	done
	echo "Action ( $ACTION ) performed on all workers."
}

if [ -z "$1" ]
then
	echo 'Starting Dash workers on all nodes (nodes are definded in' $CONFIG_FILE_PATH') ...'
	perform_action_on_all_nodes 'start'
elif [ $# -eq 1 ]
then
	if [ $1 == 'stop' ]
	then
		echo 'Stopping Dash workers ...'
	elif [ $1 == 'start' ]
	then
		echo 'Starting Dash workers ...'
	else
		echo 'Unrecognized action ' $1
		exit
	fi
	perform_action_on_all_nodes $1
else
	perfom_action_on_single_node  $1 $2 $3 $4
fi





