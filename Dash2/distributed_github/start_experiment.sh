#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python) 
# and then starts the experiment. 
# 
# Tested on Ubuntu 16.04 LTS

# WEBDASH_CLONE is a local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  ).
WEBDASH_CLONE=~/projects/webdash 

bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh

python $WEBDASH_CLONE/Dash2/distributed_github/
