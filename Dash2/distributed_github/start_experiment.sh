#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python) 
# and then starts the experiment. 
# 
# Tested on Ubuntu 16.04 LTS

# WEBDASH_CLONE is a local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  ).
WEBDASH_CLONE=~/projects/webdash 

bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh

# bash ./zookeeper_install.sh # ususally I copy zookeeper_install.sh to zoo_install.sh where I modify names of hosts
# bash ./zoo_install.sh # Alexey's local version for 7 DETER nodes

ssh node1 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 1 & disown " & disown
ssh node2 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 2 & disown " & disown
ssh node3 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 3 & disown " & disown
ssh node4 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 4 & disown " & disown
ssh node5 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 5 & disown " & disown
ssh node6 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 6 & disown " & disown
ssh node7 "cd ~/projects/webdash/Dash2/distributed_github/ ; bash ./zoo_install.sh ; python dash_worker.py 7 & disown " & disown

echo 'workers are running'

echo 'installing python-scipy'
sudo apt-get install python-scipy

cd ~/projects/webdash/Dash2/distributed_github/
echo 'To star controller run'
echo 'python zk_github_experiment.py 7'

