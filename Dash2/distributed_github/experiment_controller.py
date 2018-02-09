import sys; sys.path.extend(['../../'])

from kazoo.client import KazooClient


class ExperimentController:
    # zk_hosts - Comma-separated list of hosts of zookeeper to connect to
    # hosts - Comma-separated list of hosts avialable in experiment
    # Default value for host id is 1 which is a leader's id
    def __init__(self, zk_host_id=1, zk_hosts='127.0.0.1:2181', host_id=1, hosts='127.0.0.1:2181'):
        # zookeeper connection is a process level shared object, all threads use it
        self.zk = KazooClient(hosts)
        self.zk.start()

        self.zk_hosts = zk_hosts
        self.number_of_zk_hosts = len(zk_hosts.split(","))
        self.zk_host_id = zk_host_id

        self.hosts = hosts
        self.number_of_hosts = len(hosts.split(","))
        self.host_id = host_id

        self.list_of_hosts_ids = range(1, len(self.hosts.split(",")) + 1)  # assume that host ids are [1 ... total_number_of_hosts]

    def run(self, experiment, run_data={}):
        print "ExperimentController: setting up the experiment ..."
        experiment.run(self.zk, run_data=run_data)
        print "ExperimentController: experiment in progress"
        name = raw_input("Type q to exit\n")
        print("Experiment completed")
