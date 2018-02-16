import sys; sys.path.extend(['../../'])
import random
import json
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

# TBD: This class to be merged with Trial class from core module, when zookeeper version of DASH is stable
# parameters and measures will be moved to domain specific subclass (for a specific experiment)
# ZkTrial uses Zookeeper to distribute agents across hosts.
class ZkTrial(Trial):
    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  ]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    # Note for future refactoring: it is possible to merge this class with Trial.
    # zk and number_of_hosts  should be added to Trial constructor. trial_id can be passed via parameters[]
    def __init__(self, zk, number_of_hosts, exp_id, trial_id, data={}, max_iterations=-1):
        Trial.__init__(self, data, max_iterations)
        self.zk = zk
        self.exp_id = exp_id
        self.trial_id = trial_id
        self.curr_trial_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id)
        self.zk.ensure_path(self.curr_trial_path)
        self.number_of_hosts = number_of_hosts
        self.results = {"num_agents": 0, "num_repos": 0, "total_agent_activity": 0}
        self.received_tasks_counter = 0

    def initialize(self):
        self.agent_id_generator = self.zk.Counter(self.curr_trial_path + "/agent_id_counter", 0)
        self.hub = ZkRepoHub(repo_hub_id=1, zk=self.zk)
        self.zk.ensure_path(self.curr_trial_path + "/status")
        self.zk.set(self.curr_trial_path + "/status", json.dumps({"trial_id": self.trial_id, "status": "in progress", "dependent": ""}))

    def run(self):
        self.initialize()

        # create a task for each node in experiment assemble
        task_counter = 1
        for node_id in range(1, self.number_of_hosts + 1):
            task_id = str(self.exp_id) + "-" + str(self.trial_id) + "-" + str(task_counter)
            task_path = "/tasks/nodes/" + str(node_id) + "/" + task_id
            dependent_vars_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(node_id) + "/dependent_variables"
            self.zk.ensure_path(dependent_vars_path)

            # By default use this implementation: "Dash2.distributed_github.dash_work_processor", "DashWorkProcessor"
            # can be replaced with a custom WorkProcessor
            js_data = {}
            js_data["work_processor_module"] = "Dash2.distributed_github.dash_work_processor"
            js_data["work_processor_class"] = "DashWorkProcessor"
            self.init_parameters(js_data)
            self.zk.ensure_path(task_path)
            self.zk.set(task_path, json.dumps(js_data))

            @self.zk.DataWatch(dependent_vars_path)
            def watch_dependent_vars(data, stat_):
                if data is not None and data != "":
                    self.received_tasks_counter += 1
                    self.append_partial_results(data)
                    if self.received_tasks_counter == self.number_of_hosts:
                        self.aggregate_results()
                        self.zk.set(self.curr_trial_path + "/status", json.dumps({"trial_id": self.trial_id, "status": "completed", "dependent": self.results}))
                        return False
                return True
            task_counter += 1

    def init_parameters(self, js_data):
        js_data["prob_create_new_agent"] = str(self.prob_create_new_agent)
        js_data["max_iterations"] = str(self.max_iterations)

    def append_partial_results(self, data):
        task_results = json.loads(data)
        node_id = task_results["node_id"]
        dependent_vars_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(node_id) + "/dependent_variables"
        self.zk.set(dependent_vars_path, "") # clearing data
        partial_measures = task_results["dependent"]
        for measure in self.measures:
            self.results[measure.name] += int(partial_measures[measure.name])

    def aggregate_results(self):
        pass

    # Measures #
    def num_agents(self):
        return self.results["num_agents"]

    def num_repos(self):
        return self.results["num_repos"]

    def total_agent_activity(self):
        return self.results["total_agent_activity"]

