#!/bin/bash
# This scrip installs Apache Zookeeper and Kazoo python library (zookeeper client API for Python) 
# and then starts the experiment. 
# 
# Tested on Ubuntu 16.04 LTS

# WEBDASH_CLONE is a local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  ).
WEBDASH_CLONE=~/projects/webdash 

# bash $WEBDASH_CLONE/Dash2/distributed_github/zookeeper_install.sh

# python $WEBDASH_CLONE/Dash2/distributed_github/


ssh node1 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 1 & disown " &
ssh node2 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 2 & disown " &
ssh node3 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 3 & disown " &
ssh node4 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 4 & disown " &
ssh node5 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 5 & disown " &
ssh node6 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 6 & disown " &
ssh node7 "cd ~/projects/webdash/Dash2/distributed_github/ ; python dash_worker.py 127.0.0.1:2181 7 & disown " &

echo 'workers are running'
cd ~/projects/webdash/Dash2/distributed_github/
echo 'To star controller run zh_github_experiment.py'

