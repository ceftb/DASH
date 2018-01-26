
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
import time
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

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]


    # Override the default (which runs each agent once) to decide whether to create a new agent
    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(port=6000, trace_client=False)
            a.trace_client = False  # cut chatter when connecting and disconnecting
            a.traceLoop = False  # cut chatter when agent runs steps
            a.trace_github = False  # cut chatter when acting in github world
            #print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
        # In the second take, disconnect and reconnect each time so we don't run out of socket resources
        #if not a.connected:
        #    a.register()
        #a.agentLoop(max_iterations=1)

    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])


# This is useful to run experiments of varying length and host distribution
def run_exp(max_iterations=20, hosts=None, dependent='num_agents', num_trials=1):
    e = Experiment(GitHubTrial,
                   hosts=hosts,
                   exp_data={'max_iterations': max_iterations},
                   num_trials=num_trials,
                   independent=['prob_create_new_agent', Range(0.5, 0.6, 0.1)],
                   dependent=dependent,
                   imports='import Dash2.github.github_experiment',
                   trial_class_str='Dash2.github.github_experiment.GitHubTrial')
    return e, e.run()

if __name__ == "__main__":
    print 'argv is', sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == "run":  # usage: python xx run host..; host list
        exp, trial_outputs = run_exp(hosts=sys.argv[2:])  # rest of the arguments are hosts to run on
    elif len(sys.argv) > 1 and sys.argv[1] == "find":  # usage: python xx run host..; host list
        ar = find_posterior(hosts=sys.argv[2:])

start = time.time()
exp, trial_outputs = run_exp(max_iterations=10000,
                             dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                             num_trials=1)
print 'run took', time.time() - start, 'seconds'

