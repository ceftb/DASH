#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	source ./deter.conf

	NUMBER_OF_NODES=${#ZK_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing Zookeeper on node ' ${ZK_NODES[$ID-1]}
			ssh ${ZK_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh $ID $WEBDASH_CLONE $KAZOO_CLONE"
		done
	
	echo "Zookeeper installation completed on all nodes"
}

function install_single_zookeeper_instance {
	CURR_NODE_ID=$1
	WEBDASH_CLONE=$2
	source $WEBDASH_CLONE/Dash2/distributed_github/deter.conf # defines $ZK_NODES , redifines $WEBDASH_CLONE and $KAZOO_CLONE
	KAZOO_CLONE=$3
	WEBDASH_CLONE=$2

	ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
	ZK_ID=/etc/zookeeper/conf/myid

	# install zookeeper 
	echo "installing zookeeper base ..."
	sudo apt-get install zookeeper --yes

	# install zookeeper server
	echo "installing zookeeper server ..."
	sudo apt-get install zookeeperd --yes

	# set up conf file and node id
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
	sudo service zookeeper stop
	sudo service zookeeper start

	echo "Zookeeper installation completed"

	echo "installing mc ..."
	sudo apt-get install mc --yes
	echo "installing pip ..."
	sudo apt-get install python-pip --yes
	echo "installing python-numpy python-scipy ..."
	sudo apt-get install python-numpy python-scipy --yes
}

if [ -z "$1" ]
then 
	install_on_all_nodes
else
	install_single_zookeeper_instance  $1 $2 $3
fi








