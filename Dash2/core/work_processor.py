import sys; sys.path.extend(['../../'])
import json
import time

# WorkProcessor class is responsible for running experiment trial on a node in cluster (distributed/parallel trial)
class WorkProcessor:
    def __init__(self, zk, host_id, task_full_id, data):
        self.agents = []
        self.zk = zk
        self.host_id = host_id
        self.exp_id, self.trial_id, self.task_num = task_full_id.split("-") # self.task_num by default is the same as node id
        self.task_full_id = task_full_id
        self.max_iterations = int(data["max_iterations"])
        for param in data["parameters"] :
            if is_number(data[param]):
                setattr(self, param, float(data[param]))
            else:
                setattr(self, param, str(data[param]))

        #self.log_file = open(task_full_id + '_event_log_file.txt', 'w')
        self.iteration = 0
        # init agents and their relationships with repos

    def initialize(self):
        # subclasses must initialize their own communication hub
        # self.hub = ZkRepoHub(zk, task_full_id, 0, log_file=self.log_file)
        pass

    def process_task(self):
        self.initialize()
        if self.zk is not None and self.task_full_id is not None:
            while not self.should_stop():
                self.run_one_iteration()
                self.process_after_iteration()
                self.iteration += 1
                if self.iteration % 100000 == 0 :
                    node_path = "/tasks/nodes/" + str(self.host_id) + "/" + self.task_full_id
                    self.zk.ensure_path(node_path + "/status")
                    self.zk.set(node_path + "/status", json.dumps({"status": "in progress", "iteration": self.iteration, "update time": time.time()}))
                    print "Iteration " + str(self.iteration) + " " \
                          + str({"status": "in progress", "iteration": self.iteration, "update time": time.strftime("%H:%M:%S", time.gmtime(time.time()))})

            self.process_after_run()

            result_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(self.host_id) + "/dependent_variables/"
            dep_vars = self.get_dependent_vars()
            task_result = {"node_id":self.host_id, "dependent":dep_vars}
            data = json.dumps(task_result)
            self.zk.set(result_path, data)
        else:
            raise Exception("Zookeeper is not initialized.")

    def should_stop(self):
        if self.max_iterations > 0 and self.iteration >= self.max_iterations:
            print 'reached end of iterations for trial'
            return True
        if self.max_iterations > 0 and self.iteration < self.max_iterations:
            return False  # Follow the number of iterations by default
        else:
            return True

    def run_one_iteration(self):
        # dummy implementation, override in subclass
        for agent in self.agents:
            if not self.agent_should_stop(agent):
                next_action = agent.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                self.process_after_agent_action(agent, next_action)

    def get_dependent_vars(self):
        pass # override this method to populate values of dependent variables
        return {}

    # Default method for whether an agent should stop. By default, true, so if neither
    # this method nor should_stop are overridden, nothing will happen.
    def agent_should_stop(self, agent):
        return True

    def process_after_agent_action(self, agent, action):  # do any book-keeping needed after each step by an agent
        pass

    def process_after_iteration(self):  # do any book-keeping needed after each iteration completes
        pass

    def process_after_run(self):  # do any book-keeping needed after the trial ends and before agents are disconnected
        pass # self.log_file.close()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False