import sys; sys.path.extend(['../../'])

from kazoo.client import KazooClient


# TBD: This class to be moved into core module when zookeeper version of DASH is stable

# ExperimentController is a until class that provides command line interface to run the experiment on clusters
# It allows to stop the experiment, check status of the experiment, check status of the nodes (dash workers)
class DashController:
    # zk_hosts - Comma-separated list of hosts of zookeeper to connect to
    # hosts - Comma-separated list of hosts available in experiment
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

        # assume that host ids are [1 ... total_number_of_hosts]
        self.list_of_hosts_ids = range(1, len(self.hosts.split(",")) + 1)

    def run(self, experiment, run_data={}):
        print "ExperimentController: setting up the experiment ..."
        self.zk.ensure_path("/experiments/" + str(experiment.exp_id) + "/status")
        self.zk.set("/experiments/" + str(experiment.exp_id) + "/status", "queued")

        @self.zk.DataWatch("/experiments/" + str(experiment.exp_id) + "/status")
        def watch_status_change(data, _):
            if data == "completed":
                print "Experiment " + str(experiment.exp_id) + " is complete"
                return False
            else:
                print "Experiment " + str(experiment.exp_id) + " status: " + data
                return True

        experiment.run(self.zk, run_data=run_data)
        print "ExperimentController: experiment in progress"
        while True:
            cmd = raw_input("Type \n\tq to exit experiment controller, \n\tt to terminate all worker nodes,"
                            "\n\ts to see experiment status, \n\tc to remove all data from zookeeper (clean up storage for new experiments)\n")
            if cmd == "q":
                print("Exiting experiment controller")
                self.zk.stop()
                return
            elif cmd == "t":
                self.zk.ensure_path("/experiment_assemble_status")
                self.zk.set("/experiment_assemble_status", "terminated")
            elif cmd == "s":
                status, stat = self.zk.get("/experiments/" + str(experiment.exp_id) + "/status")
                print status
            elif cmd == "c":
                print "Cleaning up zookeeper storage ..."
                self.zk.delete("/experiments", recursive=True)
                for node_id in range(1, self.number_of_hosts + 1):
                    tasks = self.zk.get_children("/tasks/nodes/" + str(node_id))
                    for task in tasks:
                        self.zk.delete("/tasks/nodes/" + str(node_id) + "/" + str(task), recursive=True)
                self.zk.ensure_path("/experiment_assemble_status")
                self.zk.set("/experiment_assemble_status", "active")
                print "Previous experiments removed"
            elif cmd == "r": # TBD: make sure old watchers are removed
                print "Running experiment again ..."
                self.zk.ensure_path("/experiments/" + str(experiment.exp_id) + "/status")
                self.zk.set("/experiments/" + str(experiment.exp_id) + "/status", "queued")
                experiment.run(self.zk, run_data=run_data)
            else:
                print "Unrecognized command " + cmd + "\n"