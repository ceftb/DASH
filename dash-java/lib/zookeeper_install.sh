#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python). 
# Tested on Ubuntu 16.04 LTS

# $REPO_CLONES_HOME is a local path where cloned repositories and installation archives are stored.
 
REPO_CLONES_HOME=~/projects 

# The following proejcts (reposiztory clones) are requred to be in $REPO_CLONES_HOME
# - kazoo
# - webdash

cd $REPO_CLONES_HOME/kazoo
# install kazoo 
echo "installing kazoo ..."
sudo apt-get install python-setuptools
sudo python setup.py install

# install zookeeper 
echo "installing zookeeper base ..."
sudo apt-get install zookeeper

# TBD: replace this part with standalone package of zookeeper
# install zookeeper server
echo "installing zookeeper server ..."
sudo apt-get install zookeeperd




