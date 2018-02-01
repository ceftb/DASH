#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

# $REPO_CLONES_HOME is a local path where cloned repositories and installation archives are stored.
sudo apt-get install mc --yes
 
REPO_CLONES_HOME=~/projects 
ZK_CONF=/etc/zookeeper/conf/zoo.cfg 
ZK_ID=/etc/zookeeper/conf/myid
USR=$USER

# The following proejcts (reposiztory clones) are requred to be in $REPO_CLONES_HOME
# - kazoo
# - webdash

cd $REPO_CLONES_HOME/kazoo
# install kazoo 
echo "installing kazoo ..."
sudo apt-get install python-setuptools --yes
sudo python setup.py install

# install zookeeper 
echo "installing zookeeper base ..."
sudo apt-get install zookeeper --yes

# TBD: replace this part with standalone package of zookeeper
# install zookeeper server
echo "installing zookeeper server ..."
sudo apt-get install zookeeperd --yes

# set up conf file and node id
# need root access to write in /etc
sudo su 
echo 1 > $ZK_ID
cat ./zoo.conf > $ZK_CONF
sudo $USR

sudo service zookeeper stop
sudo service zookeeper start



