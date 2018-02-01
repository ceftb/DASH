#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

sudo su

# $KAZOO_CLONE is a local path where kazoo is cloned (git clone https://github.com/2600hz/kazoo.git  ).
sudo apt-get install mc --yes
 
KAZOO_CLONE=~/projects/kazoo 
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
sudo echo 1 > $ZK_ID
sudo cat ./zoo.conf > $ZK_CONF

echo "restarting zookeeper server ..."
sudo service zookeeper stop
sudo service zookeeper start



