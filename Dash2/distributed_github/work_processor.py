import sys; sys.path.extend(['../../'])
from kazoo.client import KazooClient


# WorkProcessor class is responsible for running experiment trial on a node in cluster
class WorkProcessor:
    def __init__(self, host_id=1):
        self.host_id = host_id

    def process_task(self, zk, task_path):
        if zk is not  None and task_path is not  None:
            task_type, _ = zk.get(task_path + "/" + "task_type")
            prob_create_new_agent, _  = zk.get(task_path + "/" + "prob_create_new_agent")
            max_iterations, _  = zk.get(task_path + "/" + "max_iterations")
            print "Received: " + str(task_type) + ", " + str(prob_create_new_agent) + ", " + str(max_iterations)
        else:
            print "None received"


