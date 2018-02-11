import sys; sys.path.extend(['../../'])
import random
from zk_repo_hub import ZkRepoHub
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.github.git_user_agent import GitUserAgent
from Dash2.core.experiment import Experiment
from Dash2.core.parameter import Parameter
from Dash2.core.measure import Measure
from kazoo.client import KazooClient
from collections import defaultdict
from zk_repo_hub import ZkRepoHub


# Trial of an experiment. ZkTrial uses Zookeeper to distribute agents across hosts.
class ZkTrial(Trial):
    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  ]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def __init__(self, zk, hosts, exp_id, trial_id, data={}, max_iterations=-1):
        Trial.__init__(self, data, max_iterations)
        self.zk = zk
        self.exp_id = exp_id
        self.trial_id = trial_id
        self.curr_trial_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id)
        self.zk.ensure_path(self.curr_trial_path)
        self.hosts = hosts

    def initialize(self):
        self.agent_id_generator = self.zk.Counter(self.curr_trial_path + "/agent_id_counter", 0)
        self.hub = ZkRepoHub(repo_hub_id=1, zk=self.zk)
        self.zk.ensure_path(self.curr_trial_path + "/status")
        self.zk.set(self.curr_trial_path + "/status", "in progress")

    def run(self):
        self.initialize()

        @self.zk.DataWatch(self.curr_trial_path + "/status")
        def watch_assemble_status(data, stat_):
            print("New status is %s" % data)
            if data == "completed":
                print "Trial " + self.trial_id + " is complete"
                self.status = data
                return False
            return True

        number_of_hosts = len(self.hosts.split(","))
        task_id = 0
        # create a task for each node in experiment assemble
        for node_id in range(1, number_of_hosts + 1):
            task_path = "/tasks/nodes/" + str(node_id) + "/" + str(self.exp_id) + "/" + str(self.trial_id) + "/" + str(task_id)
            # By default use this implementation: "Dash2.distributed_github.work_processor", "WorkProcessor"
            # can be replaced with custom WorkProcessor
            self.zk.ensure_path(task_path + "/" + "work_processor_module")
            self.zk.ensure_path(task_path + "/" + "work_processor_class")
            self.zk.ensure_path(task_path + "/" + "prob_create_new_agent")
            self.zk.ensure_path(task_path + "/" + "max_iterations")
            self.zk.set(task_path + "/" + "work_processor_module", "Dash2.distributed_github.work_processor")
            self.zk.set(task_path + "/" + "work_processor_class", "WorkProcessor")
            self.zk.set(task_path + "/" + "prob_create_new_agent", str(self.prob_create_new_agent))
            self.zk.set(task_path + "/" + "max_iterations", str(self.max_iterations))
            task_id += 1

    # Measures #
    def num_agents(self):
        return -1 #len(self.zk.get_children("/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/agents"))

    def num_repos(self):
        # agents_ids = self.zk.get_children("/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/agents")
        # for agent_id in agents_ids:
        #    pass # TBD: count summ of repos
        return -1

    def total_agent_activity(self):
        # TBD need to define in KZ repository
        return -1

