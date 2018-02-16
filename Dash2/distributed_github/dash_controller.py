import sys; sys.path.extend(['../../'])

from kazoo.client import KazooClient


# TBD: This class to be moved into core module when zookeeper version of DASH is stable

# ExperimentController is a until class that provides command line interface to run the experiment on clusters
# It allows to stop the experiment, check status of the experiment, check status of the nodes (dash workers)
class DashController:
    # zk_hosts - Comma-separated list of hosts of zookeeper to connect to
    # hosts - Comma-separated list of hosts available in experiment
    # Default value for host id is 1 which is a leader's id
    def __init__(self, zk_hosts='127.0.0.1:2181', number_of_hosts=1):
        # zookeeper connection is a process level shared object, all threads use it
        self.zk = KazooClient(zk_hosts)
        self.zk.start()

        self.zk_hosts = zk_hosts
        self.number_of_zk_hosts = len(zk_hosts.split(","))

        self.number_of_hosts = number_of_hosts

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
            cmd = raw_input("Press \n\tq to exit experiment controller, \n\tt to terminate all worker nodes (/experiment_assemble_status->terminated),"
                            "\n\ta to change assemble status to active (/experiment_assemble_status->active),\n\ts to see experiment status, "
                            "\n\tc to remove all data from zookeeper (clean up storage for new experiments)"
                            "\n\tr to run experiment again.\n")
            if cmd == "q":
                print("Exiting experiment controller")
                self.zk.stop()
                return
            elif cmd == "t":
                self.zk.ensure_path("/experiment_assemble_status")
                self.zk.set("/experiment_assemble_status", "terminated")
            elif cmd == "a":
                self.zk.ensure_path("/experiment_assemble_status")
                self.zk.set("/experiment_assemble_status", "active")
            elif cmd == "s":
                if self.zk.exists("/experiments/" + str(experiment.exp_id) + "/status"):
                    status, stat = self.zk.get("/experiments/" + str(experiment.exp_id) + "/status")
                else:
                    status = "no experiments found"
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
            elif cmd == "r":
                print "Running experiment again ..."
                self.zk.ensure_path("/experiments/" + str(experiment.exp_id) + "/status")
                self.zk.set("/experiments/" + str(experiment.exp_id) + "/status", "queued")
                experiment.run(self.zk, run_data=run_data)
            else:
                print "Unrecognized command " + cmd + "\n"