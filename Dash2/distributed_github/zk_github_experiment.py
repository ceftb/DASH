import sys;


sys.path.extend(['../../'])
import random
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Uniform
from Dash2.core.parameter import Parameter
from dash_trial import DashTrial
from Dash2.distributed_github.dash_work_processor import DashWorkProcessor
from Dash2.github.git_user_agent import GitUserAgent
from dash_experiment import DashExperiment
from dash_controller import DashController
from zk_repo_hub import ZkRepoHub

# This is an example of experiment script

class ZkGithubWorkProcessor(DashWorkProcessor):

    # this is path to current package
    # I cannot use reflection in super class here because, it would return path to superclass, therefore need to define it explicitly in subclasses
    module_name = "Dash2.distributed_github.zk_github_experiment"

    def __init__(self, zk, host_id, task_full_id, data):
        DashWorkProcessor.__init__(self, zk, host_id, task_full_id, data, ZkRepoHub(zk, task_full_id))

    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False  # cut chatter when connecting and disconnecting
            a.traceLoop = False  # cut chatter when agent runs steps
            a.trace_github = False  # cut chatter when acting in github world
            # print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again

    def dependent(self):
        return {"num_agents": self.num_agents(), "num_repos": self.num_repos(), "total_agent_activity": self.total_agent_activity()}

    # Measures #
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])


class ZkGithubTrial(DashTrial):
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5)]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def initialize(self):
        self.results = {"num_agents": 0, "num_repos": 0, "total_agent_activity": 0}

    # partial_dependent is a dictionary of dependent vars
    def append_partial_results(self, partial_dependent):
        for measure in self.measures:
            self.results[measure.name] += int(partial_dependent[measure.name])

    # Measures #
    def num_agents(self):
        return self.results["num_agents"]

    def num_repos(self):
        return self.results["num_repos"]

    def total_agent_activity(self):
        return self.results["total_agent_activity"]


if __name__ == "__main__":
    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        number_of_hosts = int(sys.argv[1])
    elif len(sys.argv) == 3:
        zk_hosts = sys.argv[1]
        number_of_hosts = int(sys.argv[2])
    else:
        print 'incorrect arguments: ', sys.argv

    max_iterations = 5000
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = DashExperiment(trial_class=ZkGithubTrial,
                         work_processor_class=ZkGithubWorkProcessor,
                         number_of_hosts=number_of_hosts,
                         independent=independent,
                         dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                         exp_data=exp_data,
                         num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=True)

