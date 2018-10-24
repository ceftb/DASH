import sys; sys.path.extend(['../../'])
import random
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Uniform
from Dash2.core.parameter import Parameter
from Dash2.core.trial import Trial
from Dash2.core.experiment import Experiment
from Dash2.core.work_processor import WorkProcessor
from Dash2.core.dash_controller import DashController
from Dash2.github_baseline.git_user_agent import GitUserAgent
from Dash2.github_baseline.zk_repo_hub import ZkRepoHub

# This is an example of experiment script

class ZkGithubWorkProcessor(WorkProcessor):

    # this is path to current package
    # I cannot use reflection in super class here because, it would return path to superclass, therefore need to define it explicitly in subclasses
    module_name = "Dash2.github.zk_github_experiment"

    def initialize(self):
        self.hub = ZkRepoHub(self.zk, self.task_full_id, 0, log_file=self.log_file)

    def run_one_iteration(self):
        sys2_proxy = None
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False, system2_proxy=sys2_proxy)
            if sys2_proxy is None:
                sys2_proxy = a
            a.trace_client = False  # cut chatter when connecting and disconnecting
            a.traceLoop = False  # cut chatter when agent runs steps
            a.trace_github = False  # cut chatter when acting in github world
            # print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again

    def get_dependent_vars(self):
        return {"num_agents": len(self.agents), "num_repos": sum([len(a.name_to_repo_id) for a in self.agents]), "total_agent_activity": sum([a.total_activity for a in self.agents])}


class ZkGithubTrial(Trial):
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5)]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def initialize(self):
        # init agents
        self.agents = []

    # partial_dependent is a dictionary of dependent vars values from dash worker
    def append_partial_results(self, partial_dependent):
        for measure in self.measures:
            if not (measure.name in self.results):
                self.results[measure.name] = 0
            self.results[measure.name] += int(partial_dependent[measure.name])


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

    max_iterations = 3000
    num_trials = 3
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = Experiment(trial_class=ZkGithubTrial,
                         work_processor_class=ZkGithubWorkProcessor,
                         number_of_hosts=number_of_hosts,
                         independent=independent,
                         exp_data=exp_data,
                         num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)

