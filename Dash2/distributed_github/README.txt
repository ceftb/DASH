####################################################################################
#### CLUSTER INSTALLATION (via zookeeper_service.sh and dash_workers_service.sh) ###
####################################################################################

To prepare a cluster for experimentation ZooKeeper and Dash workers have to be deployed on cluster nodes.
zookeeper_service.sh and dash_workers_service.sh are responsible for the deployment and managements of these services.
Syntax:
zookeeper_service.sh install | clean | reconfigure | start | stop
dash_workers_service.sh start | stop
List of zookeeper nodes and dash worker nodes and other configuration parameters (e.g. # of workers per node) is defined in deter.conf
If zookeeper_service.sh is called without parameters, it performs installation; if dash_worker_service.sh is called without parameters, it starts dash workers.
All actions, performed by scripts, are only applied to nodes defined in deter.conf (ZK_NONDES and DASH_NODES)

To install Zookeeper call zookeeper_service.sh on any node in the cluster.
Make sure that ZK_NODES, DASH_NODES and ZK_MAP are properly specified in deter.sh

To run the the experiment on DETER
1. start workers on nodes by executing dash_workers_service.sh on any node in the cluster.
2. python zk_experiment.py <total_number_of_dash_workers>
3. <total_number_of_dash_workers>=NUMBER_OF_WORKERS_PER_NODE x DASH_NODES

Other important variables and their default values in deter.conf:
KAZOO_CLONE=/users/tregubov/projects/kazoo
WEBDASH_CLONE=/users/tregubov/projects/webdash
NUMBER_OF_WORKERS_PER_NODE=6
TMP_DIR=/users/tregubov/projects


TMP_DIR is needed for Kazoo installation. It must be accessible for read and write.

Kazoo must be installed before dash_workers. To install Kazoo, call kazoo_install.sh
It does not require reinstallation if Deter experiment is not swapped out.
IMPORTANT:
After Deter experiment was swapped out kazoo must be reinstalled by calling kazoo_install.sh

##############################################
#### MANUAL INSTALLATION  (SINGLE MACHINE) ###
##############################################

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
- If 2 arguments are given, these are current host id and comma-separate list of hosts. For example:
controller.py 1 127.0.0.1:2181,server1:2181,node5:2233
controller and worker will use provided list of hosts and current host id to connect to zookeeper assemble. Controller assumes that all given hosts have dash_workers running on them; therefore, it distributes work accordingly. Use port 2181 by default.



