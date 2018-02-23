#!/bin/bash


function start_single_worker {
	CURR_NODE_ID=$1
	WEBDASH_CLONE=$2
	cd $WEBDASH_CLONE/Dash2/distributed_github/
	python dash_worker.py 127.0.0.1:2181 $CURR_NODE_ID
	# ps x | grep 'python dash_worker.py' > ~/projects/node_$CURR_NODE_ID.txt
	# echo node $1 started
}

function start_all {

	source ./deter.conf

	NUMBER_OF_NODES=${#NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
	do
		echo 'Starting worker on node ' ${NODES[$ID-1]}
		ssh ${NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/start_all_workers.sh $ID $WEBDASH_CLONE"
	done
	echo 'workers are running'
}


if [ -z "$1" ]
then 
	start_all
else
	start_single_worker $1 $2
fi




