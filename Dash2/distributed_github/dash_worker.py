import sys; sys.path.extend(['../../'])
import time
import json
from kazoo.client import KazooClient


# TBD: This class to be moved into core module when zookeeper version of DASH is stable
class DashWorker(object):
    def __init__(self, zk_hosts='127.0.0.1:2181', host_id=1):
        self.zk = KazooClient(zk_hosts)
        self.zk.start()
        self.zk_hosts = zk_hosts
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
            node_prefix = "/tasks/nodes/" + str(self.host_id)
            self.zk.ensure_path(node_prefix)

            @self.zk.ChildrenWatch(node_prefix)
            def watch_tasks(tasks):
                if tasks is not None:
                    for task_id in tasks:
                        @self.zk.DataWatch(node_prefix + "/" + task_id)
                        def watch_task_update(data, stat_):
                            if data is not None:
                                print "New task " + task_id + "\ntask data " + data
                                self.process_tasks(data, task_id)
                                self.zk.delete(node_prefix + "/" + task_id)
                                print "New task " + task_id + " deleted"
                                return False
                            return True
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

    def process_tasks(self, data, task_id):
        print "Received task " + task_id + " with data " + data
        args = json.loads(data)
        module_name = args["work_processor_module"]
        class_name = args["work_processor_class"]
        processor_class = self.retrieve_work_processor_class(module_name, class_name)
        processor = processor_class(zk=self.zk, host_id=self.host_id, task_id=task_id, data=args)
        processor.process_task()
        print "Task " + str(task_id) + " is complete."

    @staticmethod
    def retrieve_work_processor_class( module_name, class_name):
        mod = __import__(module_name, fromlist=[class_name])
        cls = getattr(mod, class_name)
        return cls


if __name__ == "__main__":
    print "running experiment ..."
    if len(sys.argv) == 1: # no parameters. 127.0.0.1:2181 is a default zookeeper server, 1 - default node id
        node = DashWorker()
        node.run()
    elif len(sys.argv) == 2:  # If one argument is given, it defines current host id. 127.0.0.1:2181 is a default zookeeper server here.
        curr_host_id = int(sys.argv[1])

        node = DashWorker(host_id=curr_host_id)
        node.run()
    elif len(sys.argv) == 3: # If two arguments were given, 1st argument is a comma separated list of hosts, 2nd argument is the current host's id (number between 1-255)
        hosts_list = sys.argv[1]
        curr_host_id = int(sys.argv[2])

        node = DashWorker(zk_hosts=hosts_list, host_id=curr_host_id)
        node.run()
    else:
        print 'incorrect arguments: ', sys.argv

