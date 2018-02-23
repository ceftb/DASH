#!/bin/bash

source deter.conf

NUMBER_OF_NODES=${#NODES[@]}
echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
for ID in `seq 1 $NUMBER_OF_NODES`;
        do
                echo 'Starting worker on node ' ${NODES[$ID-1]}
		ssh ${NODES[$ID-1]} "tmux new-session -d $WEBDASH_CLONE/Dash2/distributed_github/start_single_worker.sh $ID"
        done

echo 'workers are running'


