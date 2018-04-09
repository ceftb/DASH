#!/bin/bash
# This scrip installs Kazoo python library (zookeeper client API for Python)..
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	source deter.conf

	NUMBER_OF_NODES=${#DASH_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing Zookeeper on node ' ${DASH_NODES[$ID-1]}
			ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/github/kazoo_install.sh $ID $KAZOO_CLONE $TMP_DIR"
		done
	
	echo "Kazoo installation completed on all DASH nodes"
}

function install_single_kazoo_instance {
	CURR_NODE_ID=$1
	KAZOO_CLONE=$2
	TMP_DIR=$3

	cp -R $KAZOO_CLONE $TMP_DIR/kazoo_clone_$CURR_NODE_ID
	cd $TMP_DIR/kazoo_clone_$CURR_NODE_ID
	# install kazoo
	echo "installing kazoo ..."
	sudo apt-get install python-setuptools --yes
	sudo python setup.py install >> $TMP_DIR/kazoo_report_$CURR_NODE_ID.txt
	rm -Rf $TMP_DIR/kazoo_clone_$CURR_NODE_ID

	echo "installing mc ..."
	sudo apt-get install mc --yes
	echo "installing pip ..."
	sudo apt-get install python-pip --yes
	echo "installing python-numpy python-scipy ..."
	sudo apt-get install python-numpy python-scipy --yes

	pip freeze | grep kazoo >> $TMP_DIR/kazoo_report_$CURR_NODE_ID.txt
}

if [ -z "$1" ]; then
	install_on_all_nodes
else
	install_single_kazoo_instance $1 $2 $3
fi

