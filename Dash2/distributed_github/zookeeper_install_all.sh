#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python) on all nodes
# Tested on Ubuntu 16.04 LTS

source ./deter.conf

NUMBER_OF_NODES=${#NODES[@]}
echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
for ID in `seq 1 $NUMBER_OF_NODES`;
        do
                echo 'Installing Zookeeper on node ' ${NODES[$ID-1]}
                ssh ${NODES[$ID-1]} "tmux new-session -d $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh $ID"
        done

echo "Zookeeper installation completed on all nodes"



