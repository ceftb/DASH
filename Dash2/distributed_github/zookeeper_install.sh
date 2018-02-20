#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

# NODES is a list of nodes name or IP adresses of hosts in cluster.
# For example
# NODES=(server1 server22 host34 node3)

NODES=(localhost)

# KAZOO_CLONE is a local path where kazoo is cloned (git clone https://github.com/2600hz/kazoo.git  ).
KAZOO_CLONE=~/projects/kazoo 

# WEBDASH_CLONE is a local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  ).
WEBDASH_CLONE=~/projects/webdash 

ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
ZK_ID=/etc/zookeeper/conf/myid

cd $KAZOO_CLONE
# install kazoo 
echo "installing kazoo ..."
sudo apt-get install python-setuptools --yes
yes | sudo python setup.py install
yes | sudo apt-get install python-numpy python-scipy

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

# echo "installing mc .."
# sudo apt-get install mc --yes


