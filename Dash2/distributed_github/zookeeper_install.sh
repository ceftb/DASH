#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

source ./deter.conf

ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
ZK_ID=/etc/zookeeper/conf/myid

cd $KAZOO_CLONE
# install kazoo 
echo "installing kazoo ..."
sudo apt-get install python-setuptools --yes
yes | sudo python setup.py install

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


echo $1 >> ~/projects/kazoo_report.txt
pip freez | grep kazoo >> ~/projects/kazoo_report.txt


