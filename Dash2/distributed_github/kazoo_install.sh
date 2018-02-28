#!/bin/bash
# This scrip installs Kazoo python library (zookeeper client API for Python)..
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	source ./deter.conf

	NUMBER_OF_NODES=${#DASH_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing Zookeeper on node ' ${DASH_NODES[$ID-1]}
			ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/distributed_github/kazoo_install.sh $ID $WEBDASH_CLONE $KAZOO_CLONE"
		done
	
	echo "Kazoo installation completed on all DASH nodes"
}

function install_zookeeper {
	CURR_NODE_ID=$1
	WEBDASH_CLONE=$2
	source $WEBDASH_CLONE/Dash2/distributed_github/deter.conf.
	KAZOO_CLONE=$3
	WEBDASH_CLONE=$2

	cp -R $KAZOO_CLONE $WEBDASH_CLONE/../kazoo_clone_$CURR_NODE_ID
	cd $WEBDASH_CLONE/../kazoo_clone_$CURR_NODE_ID
	# install kazoo.
	echo "installing kazoo ..."
	sudo apt-get install python-setuptools --yes
	sudo python setup.py install  >> ~/projects/kazoo_report_$CURR_NODE_ID.txt
	rm -Rf $WEBDASH_CLONE/../kazoo_clone_$CURR_NODE_ID

	# install zookeeper.
	echo "installing zookeeper base ..."
	sudo apt-get install zookeeper --yes

	echo "installing mc ..."
	sudo apt-get install mc --yes
	echo "installing pip ..."
	sudo apt-get install python-pip --yes
	echo "installing python-numpy python-scipy ..."
	sudo apt-get install python-numpy python-scipy --yes

	pip freeze | grep kazoo >> ~/projects/kazoo_report_$CURR_NODE_ID.txt
}

if [ -z "$1" ]; then
	install_on_all_nodes
else
	install_zookeeper $1 $2 $3
fi

