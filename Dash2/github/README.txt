#########################################################
#### STANDALONE INSTALLATION  (with single dash worker)##
#########################################################
To install Zookeeper and other external dependencies on Ubuntu, you need to clone some repos first and update the
following variables in webdash/Dash2/github/standalone_install.sh :

    ########## installation configuration ##########
    ################################################
    # A local path where kazoo is cloned (git clone https://github.com/python-zk/kazoo.git  )
    KAZOO_CLONE=/users/tregubov/projects/kazoo

    # A local path where ijson is cloned (git clone https://github.com/isagalaev/ijson.git  )
    IJSON_CLONE=/users/tregubov/projects/ijson

    # A local path where ijson is cloned (git clone https://github.com/networkx/networkx.git  )
    NETWORKX_CLONE=/users/tregubov/projects/networkx

    # A local path where METIS for python wrapper is cloned ( sudo apt install mercurial ; hg clone https://bitbucket.org/kw/metis-python/src )
    METIS_CLONE=/users/tregubov/projects/metis/src

    # A local path where numpy is cloned
    NUMPY_CLONE=/users/tregubov/projects/numpy

    # A local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  )
    PSUTILS_CLONE=/users/tregubov/projects/psutils

    # A local path where webdash is cloned (git clone https://github.com/cuts/webdash.git  )
    WEBDASH_CLONE=/users/tregubov/projects/webdash

    # Place for temporary files. Must have write access.
    TMP_DIR=.

Then install software by calling (do it only once). It will require sudo
bash webdash/Dash2/github/standalone_install.sh

To run an experiment to go webdash/Dash2/github/ directory and then:
1. start worker in separate terminal by calling
python ../core/dash_worker.py
2. start the experiment by calling
python zk_github_state_experiment.py <input_initial_condition_events.csv> None <Agent_class_name> <Path_to_agent_class> <Start_date> <End_date> <name_of_output_events.csv>
For example:
python zk_github_state_experiment.py ./data_sample/data_sample.csv None ISI2GitUserAgent Dash2.github.git_isi_agent2 2017-08-01 2017-08-11 ./data_sample/simulation_output

'None' here is reserved for embedding files.


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
2. python zk_github_experiment.py <total_number_of_dash_workers>
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

# ZooKeeper installation
# Ubuntu
sudo apt-get install zookeeper
sudo apt-get install zookeeperd
# Mac OS
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null
brew install zookeeper

#############################################
#### RUNNING EXPERIMENTS ON LOCAL MACHINE ###
#############################################
Step 0 - check if zookeeper and kazoo are installed. All following commands called from webdash/Dash2/github

Step 1 - start a worker process by calling
python ../core/dash_worker.py

Step 2. in another terminal start an experiment:
python zk_github_state_experiment.py

#######################################
#### RUNNING EXPERIMENTS ON CLUSTER ###
#######################################
Step 0 - check if zookeeper and kazoo are installed and install them if need by calling:
kazoo_install.sh
zookeeper_service.sh install
You may need to reinstall them if experiment on Deter was swapped out.

Step 1 - preparation of the cluster nodes
1.1 Terminate all dash and zookeeper nodes left from previous experiments by calling from any node:
zookeeper_service.sh stop
dash_workers_service.sh stop
These scripts only act on zookeeper nodes and dash nodes are defined in deter.conf.
1.2 If necessary update deter.conf to change dash and zookeeper nodes configuration and routing, then start zookeeper and then dash nodes by calling from any node:
zookeeper_service.sh reconfigure
dash_workers_service.sh start

Step 2. starting an experiment
2.1 Update desirable experiment parameters in the experiment file (e.g. in zk_github_experiment.py you can change probabilities and max number of iterations)
2.2 Start the dash controller by calling from any node:
python zk_github_experiment.py <total_number_of_dash_workers>
where <total_number_of_dash_workers> - is the maximum number of dash workers experiment can use, it should be <= NUMBER_OF_WORKERS_PER_NODE x len(DASH_NODES)
NOTE: if experiment is run with flag start_right_away=False, then you have to type 'r' to start the experiment.
TIP: to make the interactive command line interface of the dash controller independent from current ssh session, it is recommended to use tmux:
tmux new-session -d 'python zk_github_experiment.py 126'

Quick tmux guide:
tmux list-session -shows list of all running tmux session
tmux attach -t <session_id> -switched to the selected session
<ctrl>+b  +  d -detaches opened tmux session


######################################
#### EXPERIMENT START UP (GENERAL) ###
######################################
Step 1. Run dash_worker.py on every host (provide arguments, see below).
Step 2. Run zk_github_experiment.py on any host that you want to be a controller (provide arguments, see below).

Explanation:
../core/dash_worker.py is a server that listens for tasks.
dash_controller.py or any descendant of this class (e.g. zk_github_experiment.py) run are used to create and run experiment object. Tasks are distributed by dash_controller.py process. Currently you should only run zk_github_experiment.py

Arguments:
Both dash_worker.py and dash controller.py accept the following command line arguments:
- If no arguments are given, controller and worker are run locally. Controller assumes that there is only one worker node in assemble and allocates all work to it. Both controller and worker assume that Zookeeper also runs locally on default port.
- If 2 arguments are given, these are current host id and comma-separate list of hosts. For example:
controller.py 1 127.0.0.1:2181,server1:2181,node5:2233
controller and worker will use provided list of hosts and current host id to connect to zookeeper assemble. Controller assumes that all given hosts have dash_workers running on them; therefore, it distributes work accordingly. Use port 2181 by default.
