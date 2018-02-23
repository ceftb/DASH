###############################################
#### INSTALLATION WITH zookeeper_install.sh ###
###############################################

To install Zookeeper call zookeeper_install.sh on master node in cluster.
Make sure that the following variables are properly specified in deter.sh
NODES=(server1 host2 node10) # default value NODES=(localhost) 
KAZOO_CLONE=~/projects/kazoo 
WEBDASH_CLONE=~/projects/webdash 

To run the the experiment on DETER
1. start workers on each node by executing start_all_workers.sh on master node in cluster.
2. python zk_experiment.py <total_number_of_nodes>

#############################
#### MANUAL INSTALLATION  ###
#############################

# To install kazoo run:
pip install kazoo

# Ubuntu
# To install zookeeper base run
sudo apt-get install zookeeper
# To install zookeeper server run
sudo apt-get install zookeeperd

# Mac OS run:
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null
brew install zookeeper


############################
#### EXPERIMENT START UP ###
############################
Step 1. Run dash_worker.py on every host (provide arguments, see below). 
Step 2. Run zk_github_experiment.py on any host that you want to be a controller (provide arguments, see below).

Explanation:
dash_worker.py is a server that listens for tasks. 
dash_controller.py or any descendant of this class (e.g. zk_github_experiment.py) run are used to create and run experiment object. Tasks are distributed by dash_controller.py process. Currently you should only run zk_github_experiment.py 

Arguments:
Both dash_worker.py and dash controller.py accept the following command line arguments:
- If no arguments are given, controller and worker are run locally. Controller assumes that there is only one worker node in assemble and allocates all work to it. Both controller and worker assume that Zookeeper also runs locally on default port.
- If 2 arguments are given, these are comma-separate list of hosts and current host id. For example
controller.py 127.0.0.1:2181,server1:2181,node5:2233 1
controller and worker will use provided list of hosts and current host id to connect to zookeeper assemble. Controller assumes that all given hosts have dash_workers running on them; therefore, it distributes work accordingly. Use port 2181 by default.



