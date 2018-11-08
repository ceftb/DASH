#!/bin/bash
# This scrip installs Kazoo python library (zookeeper client API for Python) and other software
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	#source deter.conf
	################################################
    # A list of physical nodes where dash workeres will be instantiated.
    DASH_NODES=( localhost )

    # A list of physical nodes where zookeeper will be installed.
    # Number of nodes must always be odd !!!
    ZK_NODES=( localhost )

    # number of workers per each physical node
    NUMBER_OF_WORKERS_PER_NODE=1

    # Manual routing of Dash nodes to ZooKeeper nodes
    declare -A ZK_MAP
    ZK_MAP[localhost]=localhost

    ########## installation configuration ##########
    ################################################
    # A local path where kazoo is cloned (git clone https://github.com/python-zk/kazoo.git  )
    KAZOO_CLONE=/users/tregubov/projects/kazoo

    # A local path where ijson is cloned (git clone https://github.com/isagalaev/ijson.git  )
    IJSON_CLONE=/users/tregubov/projects/ijson

    # A local path where ijson is cloned (git clone https://github.com/networkx/networkx.git  )
    NETWORKX_CLONE=/users/tregubov/projects/networkx

    # A local path where METIS for python wrapper is cloned ( sudo apt install mercurial ; hg clone https://bitbucket.org/kw/metis-python/src )
    METIS_CLONE=/users/tregubov/projects/metis/src

    # A local path where numpy is cloned
    NUMPY_CLONE=/users/tregubov/projects/numpy

    # A local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  )
    PSUTILS_CLONE=/users/tregubov/projects/psutil

    # A local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  )
    WEBDASH_CLONE=/users/tregubov/projects/webdash

    # Place for temporary files. Must have write access.
    TMP_DIR=.


	NUMBER_OF_NODES=${#DASH_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing software packages on node ' ${DASH_NODES[$ID-1]}
			#ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/core/software_install.sh $ID $KAZOO_CLONE $TMP_DIR $IJSON_CLONE $NETWORKX_CLONE $METIS_CLONE $NUMPY_CLONE $PSUTILS_CLONE"
			install_on_single_instance $ID $KAZOO_CLONE $TMP_DIR $IJSON_CLONE $NETWORKX_CLONE $METIS_CLONE $NUMPY_CLONE $PSUTILS_CLONE
		done
	
	echo "Software installation started on all nodes"
}

function install_on_single_instance {
	CURR_NODE_ID=$1
	KAZOO_CLONE=$2
	TMP_DIR=$3
	IJSON_CLONE=$4
	NETWORKX_CLONE=$5
	METIS_CLONE=$6
	NUMPY_CLONE=$7
	PSUTILS_CLONE=$8

	echo "installing python-numpy python-scipy ..."
	sudo apt-get install python-numpy python-scipy --yes
	
	cp -R $KAZOO_CLONE $TMP_DIR/kazoo_clone_$CURR_NODE_ID
	cd $TMP_DIR/kazoo_clone_$CURR_NODE_ID
	# install kazoo
	echo "installing kazoo ..."

	sudo apt-get install python-setuptools --yes
	sudo python setup.py install >> $TMP_DIR/kazoo_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/kazoo_clone_$CURR_NODE_ID

	echo "installing mc ..."
	sudo apt-get install mc --yes
	echo "installing pip ..."
	sudo apt-get install python-pip --yes

	pip freeze | grep kazoo >> $TMP_DIR/kazoo_report_$CURR_NODE_ID.txt
	
	cp -R $IJSON_CLONE $TMP_DIR/ijson_clone_$CURR_NODE_ID
	cd $TMP_DIR/ijson_clone_$CURR_NODE_ID
	sudo python setup.py install  2>> $TMP_DIR/ijson_report_$CURR_NODE_ID.txt 1>> $TMP_DIR/ijson_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/ijson_clone_$CURR_NODE_ID

    # install networkX from $NETWORKX_CLONE ( https://github.com/networkx/networkx.git )
    cp -R $NETWORKX_CLONE $TMP_DIR/networkx_clone_$CURR_NODE_ID
	cd $TMP_DIR/networkx_clone_$CURR_NODE_ID
	sudo python setup.py install  2>> $TMP_DIR/networkx_report_$CURR_NODE_ID.txt 1>> $TMP_DIR/networkx_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/networkx_clone_$CURR_NODE_ID

	# install psutil from $PSUTILS_CLONE ( https://github.com/networkx/networkx.git )
    cp -R $PSUTILS_CLONE $TMP_DIR/psutils_clone_$CURR_NODE_ID
	cd $TMP_DIR/psutils_clone_$CURR_NODE_ID
	sudo python setup.py install  2>> $TMP_DIR/psutils_report_$CURR_NODE_ID.txt 1>> $TMP_DIR/psutils_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/psutils_clone_$CURR_NODE_ID

    # install METIS
	sudo apt-get install graphviz graphviz-dev pkg-config metis --yes


    # install METIS for Python wrapper
    cp -R $METIS_CLONE $TMP_DIR/metis_clone_$CURR_NODE_ID
	cd $TMP_DIR/metis_clone_$CURR_NODE_ID
	sudo python setup.py install  2>> $TMP_DIR/metis_report_$CURR_NODE_ID.txt 1>> $TMP_DIR/metis_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/metis_clone_$CURR_NODE_ID

	# install pandas
	sudo apt-get install python-pandas --yes

	# Numpy and OpenBLAS installation:
    sudo apt-get install libopenblas-base --yes
    sudo apt-get install cython  --yes
    # requires precompilied BLAS - do it manually
    cd ~/projects/OpenBLAS
    sudo make install
    sudo update-alternatives --install /usr/lib/libblas.so.3 libblas.so.3 /opt/OpenBLAS/lib/libopenblas.so 50
    #
    #cd ~/projects/numpy/
    #sudo python setup.py install
    # install numpy from $NUMPY_CLONE ( https://github.com/numpy/numpy.git )
	sudo cp -R $NUMPY_CLONE $TMP_DIR/numpy_clone_$CURR_NODE_ID
	cd $TMP_DIR/numpy_clone_$CURR_NODE_ID
	sudo python setup.py install  2>> $TMP_DIR/numpy_report_$CURR_NODE_ID.txt 1>> $TMP_DIR/numpy_report_$CURR_NODE_ID.txt
	sudo rm -Rf $TMP_DIR/numpy_clone_$CURR_NODE_ID

    install_zookeeper $WEBDASH_CLONE 'install'
}


function install_zookeeper {
	CURR_NODE_ID=1
	WEBDASH_CLONE=$1
	ACTION=$2

	cd $WEBDASH_CLONE/Dash2/core/
	#source $CONFIG_FILE_PATH # defines $ZK_NODES
    # A list of physical nodes where dash workeres will be instantiated.
    DASH_NODES=( localhost )

    # A list of physical nodes where zookeeper will be installed.
    # Number of nodes must always be odd !!!
    ZK_NODES=( localhost )

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
		sudo cat $WEBDASH_CLONE/Dash2/core/zoo.conf > $ZK_CONF

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
	elif [ $ACTION == 'clean' ]
	then
	    sudo service zookeeper stop
		sudo rm -f /var/lib/zookeeper/version-2/log.*
		sudo rm -f /var/lib/zookeeper/version-2/snapshot.*
		sudo service zookeeper start
	else
	    echo 'unrecognized action' $ACTION
	fi
}

function run_external_script_on_all_nodes {
	source deter.conf
	FULL_SCRIPT_PATH=$1

	NUMBER_OF_NODES=${#DASH_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Running script on node ' ${DASH_NODES[$ID-1]}
			ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $FULL_SCRIPT_PATH $ID"
		done

	echo "Script executed on all DASH nodes"
}

if [ -z "$1" ]; then
	install_on_all_nodes
else
    if [ "$#" -eq 1 ]; then
        run_external_script_on_all_nodes $1
    else
        install_on_single_instance $1 $2 $3 $4 $5 $6 $7 $8
    fi
fi

