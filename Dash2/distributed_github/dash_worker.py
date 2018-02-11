import sys; sys.path.extend(['../../'])
import time
from kazoo.client import KazooClient

class DashWorker(object):
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

        self.status = "active"

    def run(self):
        # allowed values for "/experiment_assemble_status" are "active" and "terminated"
        self.zk.ensure_path("/experiment_assemble_status")
        self.status, stat = self.zk.get("/experiment_assemble_status")

        if self.status is None or self.status == '':
            self.zk.set("/experiment_assemble_status", "active")
            status = "active"

        if self.status == "terminated":
            self.zk.stop()
            return
        elif self.status == "active":
            task_path = "/tasks/nodes/" + str(self.host_id)
            self.zk.ensure_path(task_path)

            @self.zk.ChildrenWatch(task_path)
            def watch_tasks(tasks):
                if tasks is not None:
                    self.process_tasks(tasks, task_path)
                    print "ts"
                return True

            @self.zk.DataWatch("/experiment_assemble_status")
            def watch_assemble_status(data, stat_):
                print("New status is %s" % data)
                if data == "terminated":
                    print "Node was terminated by experiment assemble status change"
                    self.status = data
                    return False
                return True

            while self.status == "active":
                print "Waiting for tasks ... \nTo terminate dash nodes change /experiment_assemble_status to 'terminated' via ExperimentController\n"
                time.sleep(5)
            self.zk.stop()
            return
        else:
            raise ValueError('/experiment_assemble_status contains incorrect value')

    def process_tasks(self, experiments, node_prefix):
        # while node has assigned tasks handle each task
        for exp in experiments:
            trials = self.zk.get_children(node_prefix + "/" + exp)
            for trial in trials:
                tasks = self.zk.get_children(node_prefix + "/" + exp + "/" + trial)
                for task in tasks:
                    task_path = node_prefix + "/" + exp + "/" + trial + "/" + task
                    module_name = str(self.zk.get(task_path + "/" + "work_processor_module")[0])
                    class_name = str(self.zk.get(task_path + "/" + "work_processor_class")[0])

                    #processor_class = self.retrieve_work_processor_class("Dash2.distributed_github.work_processor", "WorkProcessor")
                    processor_class = self.retrieve_work_processor_class(module_name, class_name)
                    processor = processor_class(zk=self.zk, host_id=self.host_id, exp_id=exp, trial_id=trial, task_id=task)
                    processor.process_task()
                    print "Task " + str(task_path) + " is complete. Removing task from queue ..."
                    self.zk.delete(task_path, recursive=True)
                    print "Task " + str(task_path) + " deleted."

    @staticmethod
    def retrieve_work_processor_class(self, module_name, class_name):
        mod = __import__(module_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        return cls



# 1st argument is a comma separated list of hosts.
# The first host in the list should be a local machine for better performance
# 2nd argument is the current host's id (number between 1-255)
# 3d argument is a comma separated list of hosts zookeeper hosts
# 4th argument is the current zookeeper host's id (number between 1-255)
# if third and forth arguments are omitted then it is assumed that zookeeper nodes are the same as experiment nodes.
if __name__ == "__main__":
    print "running experiment ..."
    if len(sys.argv) == 1:
        node = DashWorker()
        node.run()
    elif len(sys.argv) == 3:
        hosts_list = sys.argv[1]
        curr_host_id = int(sys.argv[2])

        node = DashWorker(zk_host_id=curr_host_id, zk_hosts=hosts_list, host_id=curr_host_id, hosts=hosts_list)
        node.run()
    elif len(sys.argv) == 5:
        hosts_list = sys.argv[1]
        curr_host_id = int(sys.argv[2])
        zk_hosts_list = sys.argv[3]
        zk_curr_host_id = int(sys.argv[4])

        node = DashWorker(zk_host_id=zk_curr_host_id, zk_hosts=zk_hosts_list, host_id=curr_host_id, hosts=hosts_list)
        node.run()
    else:
        print 'incorrect arguments: ', sys.argv

