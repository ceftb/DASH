#!/bin/bash
# This scrip installs Kazoo python library (zookeeper client API for Python) and other software
# Tested on Ubuntu 16.04 LTS

function install_on_all_nodes {
	source deter.conf

	NUMBER_OF_NODES=${#DASH_NODES[@]}
	echo 'Total ' $NUMBER_OF_NODES ' workers in assemble'
	for ID in `seq 1 $NUMBER_OF_NODES`;
		do
			echo 'Installing software packages on node ' ${DASH_NODES[$ID-1]}
			ssh ${DASH_NODES[$ID-1]} "tmux new-session -d bash $WEBDASH_CLONE/Dash2/github/software_install.sh $ID $KAZOO_CLONE $TMP_DIR $IJSON_CLONE $NETWORKX_CLONE $METIS_CLONE $NUMPY_CLONE $PSUTILS_CLONE"
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

    # install psutils from $NETWORKX_CLONE ( https://github.com/networkx/networkx.git )
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

