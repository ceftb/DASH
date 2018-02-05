import sys;

sys.path.extend(['../../'])
import numbers
import math
import numpy
import time
import random
from zk_repo_hub import ZkRepoHub
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.github.git_user_agent import GitUserAgent
from Dash2.core.experiment import Experiment
from Dash2.core.parameter import Parameter
from Dash2.core.measure import Measure


# One trial of an experiment
class ZkTrial(Trial):
    # class level information to configure zookeeper connection
    # zookeeper connection is a process lelev shared object, all threads use it

    # Comma-separated list of hosts of zookeeper to connect to
    zk_hosts = ['127.0.0.1:2181']
    number_of_zk_hosts = 1
    zk_host_id = None

    # Comma-separated list of hosts avialable for each trial
    # By default it is assumed that it is the same set of hosts as in zookeeper assemble
    zk_hosts = zk_hosts
    number_of_hosts = number_of_zk_hosts
    host_id = None

    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0, 1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0, 1), default=0.5),
                  ]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    # The initialize function sets up the agent list
    def initialize(self):
        self.hub = ZkRepoHub(ZkTrial.host_id)
        pass

    # Override the default. In each iteration agent decides whether to create a new agent
    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False
            a.traceLoop = False
            a.trace_github = False
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)

    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])


# number of hosts must be odd for zookeeper
def run_exp(max_iterations=20, num_hosts=5, dependent='num_agents', num_trials=2):
    e = Experiment(trial_class=ZkTrial,
                     exp_data={'max_iterations': max_iterations},
                     num_trials=num_trials,
                     independent=['prob_create_new_agent', Range(0.5, 0.6, 0.1)],
                     dependent=dependent
                     );
    return e, e.run()


# TBD: need to read hosts from CLI arguments
if __name__ == "__main__":
    print 'argv is', sys.argv
    print "running experiment ..."
    run_exp()
