#####################
#### INSTALLATION ###
#####################

The package distributed_github contains Zookeeper installation scripts.

To install Zookeeper on DETER nodes simply call zookeeper_install.sh
Make sure that the following variables are properly specified in zookeeper_install.sh
NUMBER_OF_NODES=7
KAZOO_CLONE=~/projects/kazoo 
WEBDASH_CLONE=~/projects/webdash 

To run the the experiment on DETER execute start_experiment.sh or python zk_experiment.py

To install kazoo and Zookeeper locally do this (tested on Ubuntu):
# install kazoo 
pip install kazoo

# Ubuntu
# install zookeeper base
sudo apt-get install zookeeper
# install zookeeper server
sudo apt-get install zookeeperd

# Mac OS
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null

brew install zookeeper


############################
#### EXPERIMENT START UP ###
############################

Run dash_worker.py on every host. This a server that listens for tasks.
Tasks are distributed by experiment controller process (lead node), which is run separately.



