#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

CONFIG_FILE_PATH=./deter.conf # path is relative to $WEBDASH_CLONE/Dash2/distributed_github/

function perform_action_on_all_nodes {
	ACTION=$1
	source $CONFIG_FILE_PATH

	NUMBER_OF_NODES=${#ZK_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing Zookeeper on node ' ${ZK_NODES[$ID-1]}
			ssh ${ZK_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh $ID $WEBDASH_CLONE $ACTION"
		done
	
	echo "Zookeeper action ($ACTION) completed on all nodes"
}

function perfom_action_on_single_node {
	CURR_NODE_ID=$1
	WEBDASH_CLONE=$2
	ACTION=$3
	source $CONFIG_FILE_PATH # defines $ZK_NODES

	ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
	ZK_ID=/etc/zookeeper/conf/myid
	
	echo $ACTION
	if [ $ACTION == 'install' ]  
	then 
		# install zookeeper 
		echo "installing zookeeper base ..."
		sudo apt-get install zookeeper --yes
		# install zookeeper server
		echo "installing zookeeper server ..."
		sudo apt-get install zookeeperd --yes
	fi
	
	if [ $ACTION == 'install' ] || [ $ACTION == 'reconfigure' ]   
	then 
		# set up conf file and node id
		sudo service zookeeper stop

		# need root access to write in /etc
		cd $WEBDASH_CLONE
		sudo chmod go+rw $ZK_ID
		sudo echo $CURR_NODE_ID > $ZK_ID
		sudo chmod go+rw $ZK_CONF
		sudo cat $WEBDASH_CLONE/Dash2/distributed_github/zoo.conf > $ZK_CONF

		# appending other nodes to zookeeper config file
		NUMBER_OF_NODES=${#ZK_NODES[@]}
		echo 'Total ' $NUMBER_OF_NODES ' hosts in assemble'
		for ID in `seq 1 $NUMBER_OF_NODES`;
			do
				echo 'Zookeeper node ' $ID ' -> ' ${ZK_NODES[$ID-1]}
				echo server.$ID=${ZK_NODES[$ID-1]}:2888:3888 >> $ZK_CONF
			done 
		echo " " >> $ZK_CONF

		echo "restarting zookeeper server ..."
		sudo service zookeeper start
		echo "Zookeeper installation/recongfiguration completed"
	elif [ $ACTION == 'stop' ]
	then
		sudo service zookeeper stop
	elif [ $ACTION == 'start' ]
	then
		sudo service zookeeper start
	fi
}

if [ -z "$1" ]
then 
	echo 'Installing Zookeeper on all nodes (nodes are definded in' $CONFIG_FILE_PATH') ...'
	perform_action_on_all_nodes 'install'
elif [ $# -eq 1 ]
then 
	if [ $1 == 'install' ]  
	then 
		echo 'Installing Zookeeper (Zookeeper nodes are definded in' $CONFIG_FILE_PATH') ...'
	elif [ $1 == 'reconfigure' ]
	then 
		echo 'Uninstalling Zookeeper (Zookeeper nodes are definded in' $CONFIG_FILE_PATH') ...'
	elif [ $1 == 'stop' ]
	then 
		echo 'Stopping Zookeeper (Zookeeper nodes are definded in' $CONFIG_FILE_PATH') ...'
	elif [ $1 == 'start' ]
	then 
		echo 'Starting Zookeeper (Zookeeper nodes are definded in' $CONFIG_FILE_PATH') ...'
	else 
		echo 'Unrecognized action ' $1
		exit
	fi
	perform_action_on_all_nodes $1
else
	perfom_action_on_single_node  $1 $2 $3
fi








