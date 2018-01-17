# Runs a simple github experiment using the Experiment and Trial classes.

"""
1/11/18 - Created, following the description from the one-on-one call on 1/10/18: on each iteration, either an
existing agent is chosen or a new agent is created with some probability, then the agent either picks an
existing repo or creates a new one with some probability. If it picks an existing repo, it picks an event
and sends it to the hub, for a new repo the create event is sent.
"""
import sys; sys.path.extend(['../../'])

from Dash2.core.experiment import Experiment
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.core.measure import Measure
from git_user_agent import GitUserAgent
import random
import numpy
import subprocess
import sys


# One trial of an experiment
class GitHubTrial(Trial):

    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  ]

    measures = [Measure('num_agents'), Measure('num_repos')]


    # Override the default (which runs each agent once) to decide whether to create a new agent
    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(port=6000)
            print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
        # In the second take, disconnect and reconnect each time so we don't run out of socket resources
        #if not a.connected:
        #    a.register()
        #a.agentLoop(max_iterations=1)

    # This is defined above as a measure
    def num_agents(self):
        return len(self.agents)

    # This doesn't work yet - will probably query the hub (and init will reset the hub between trials)
    def num_repos(self):
        return len(self.repos)


# This is useful to run experiments of varying length and host distribution
def run_exp(max_iterations=20):
    e = Experiment(GitHubTrial,
                   exp_data={'max_iterations': max_iterations}, num_trials=1,
                   independent=['prob_create_new_agent', Range(0.5, 0.6, 0.1)], dependent='num_agents')
    e.run()

run_exp(max_iterations=100)
