#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	source ./deter.conf

	NUMBER_OF_NODES=${#NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing Zookeeper on node ' ${NODES[$ID-1]}
			ssh ${NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh $ID $WEBDASH_CLONE $WEBDASH_CLONE"
		done
	
	echo "Zookeeper installation completed on all nodes"
}

function install_zookeeper {
	CURR_NODE_ID=$1
	WEBDASH_CLONE=$2
	KAZOO_CLONE=$3
	source $WEBDASH_CLONE/Dash2/distributed_github/deter.conf # defines $NODES

	ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
	ZK_ID=/etc/zookeeper/conf/myid

	cd $KAZOO_CLONE
	cp -R $KAZOO_CLONE $KAZOO_CLONE/../kazoo_clone_$CURR_NODE_ID
	# install kazoo 
	echo "installing kazoo ..."
	sudo apt-get install python-setuptools --yes
	sudo python setup.py install  >> ~/projects/kazoo_report_$CURR_NODE_ID.txt
	rm -Rf $KAZOO_CLONE/../kazoo_clone_$CURR_NODE_ID

	# install zookeeper 
	echo "installing zookeeper base ..."
	sudo apt-get install zookeeper --yes

	# TBD: replace this part with standalone package of zookeeper
	# install zookeeper server
	echo "installing zookeeper server ..."
	sudo apt-get install zookeeperd --yes

	# set up conf file and node id
	# need root access to write in /etc
	cd $WEBDASH_CLONE
	sudo chmod go+rw $ZK_ID
	sudo uname -n | sed 's/[^0-9]*//g' > $ZK_ID
	sudo chmod go+rw $ZK_CONF
	sudo cat $WEBDASH_CLONE/Dash2/distributed_github/zoo.conf > $ZK_CONF

	# appending other nodes to zookeeper config file
	NUMBER_OF_NODES=${#NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' hosts in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
		        echo 'Zookeeper node ' $ID ' -> ' ${NODES[$ID-1]}
			echo server.$ID=${NODES[$ID-1]}:2888:3888 >> $ZK_CONF
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

	pip freeze | grep kazoo >> ~/projects/kazoo_report_$CURR_NODE_ID.txt
}

if [ -z "$1" ]
then 
	install_on_all_nodes
else
	install_zookeeper $1 $2 $3
fi








