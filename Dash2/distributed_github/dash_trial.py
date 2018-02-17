import sys; sys.path.extend(['../../'])
import random
import json
from Dash2.core.trial import Trial
from Dash2.distributed_github.dash_work_processor import DashWorkProcessor

# TBD: This class to be merged with Trial class from core module, when zookeeper version of DASH is stable
# parameters and measures will be moved to domain specific subclass (for a specific experiment)
# DashTrial uses Zookeeper to distribute agents across hosts.
class DashTrial(Trial):
    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = []
    measures = []

    # Note for future refactoring: it is possible to merge this class with Trial.
    # zk and number_of_hosts  should be added to Trial constructor. trial_id can be passed via parameters[]
    def __init__(self, zk, number_of_hosts, exp_id, trial_id, data={}, work_processor_class=DashWorkProcessor, max_iterations=-1):
        Trial.__init__(self, data, max_iterations)
        self.zk = zk
        self.exp_id = exp_id
        self.trial_id = trial_id
        self.curr_trial_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id)
        self.zk.ensure_path(self.curr_trial_path)
        self.number_of_hosts = number_of_hosts
        self.received_tasks_counter = 0
        self.work_processor_class = work_processor_class

        self.zk.ensure_path(self.curr_trial_path + "/status")
        self.zk.set(self.curr_trial_path + "/status", json.dumps({"trial_id": self.trial_id, "status": "in progress", "dependent": ""}))

    def initialize(self):
        pass

    def run(self):
        self.initialize()
        # create a task for each node in experiment assemble
        task_number = 1 # task_number by default is the same as node id,
        # because by default each task in trial is assigned to exactly one node, but it might be different
        # in other implementations of Trial class
        for node_id in range(1, self.number_of_hosts + 1):
            task_full_id = str(self.exp_id) + "-" + str(self.trial_id) + "-" + str(task_number)
            task_path = "/tasks/nodes/" + str(node_id) + "/" + task_full_id
            dependent_vars_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(node_id) + "/dependent_variables"
            self.zk.ensure_path(dependent_vars_path)

            task_data = {"work_processor_module": self.work_processor_class.module_name,
                         "work_processor_class": self.work_processor_class.__name__,
                         "max_iterations": self.max_iterations,
                         "task_full_id": task_full_id,
                         "parameters": []}
            for par in self.__class__.parameters:
                task_data[par.name] = getattr(self, par.name)
                task_data["parameters"].append(par.name) # work processor needs to know list of parameters (names)
            self.zk.ensure_path(task_path)
            self.zk.set(task_path, json.dumps(task_data))

            @self.zk.DataWatch(dependent_vars_path)
            def watch_dependent_vars(data, stat_):
                if data is not None and data != "":
                    self.received_tasks_counter += 1
                    # append partial results/dependent vars
                    task_results = json.loads(data)
                    node_id = task_results["node_id"]
                    dependent_vars_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(node_id) + "/dependent_variables"
                    self.zk.set(dependent_vars_path, "")  # clearing data
                    partial_dependent = task_results["dependent"]
                    self.append_partial_results(partial_dependent)
                    if self.received_tasks_counter == self.number_of_hosts:
                        self.aggregate_results()
                        self.zk.set(self.curr_trial_path + "/status", json.dumps({"trial_id": self.trial_id, "status": "completed", "dependent": self.results}))
                        return False
                return True
            task_number += 1

    # partial_dependent is a dictionary of dependent vars
    def append_partial_results(self, partial_dependent):
       pass

    def aggregate_results(self):
        pass
