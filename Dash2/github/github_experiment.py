
# Runs a simple github experiment using the Experiment and Trial classes.

"""
1/11/18 - Created, following the description from the one-on-one call on 1/10/18: on each iteration, either an
existing agent is chosen or a new agent is created with some probability, then the agent either picks an
existing repo or creates a new one with some probability. If it picks an existing repo, it picks an event
and sends it to the hub, for a new repo the create event is sent.
"""
import sys; sys.path.extend(['../../'])

from Dash2.core.dash import DASHAgent
from Dash2.core.experiment import Experiment
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.core.measure import Measure
from git_user_agent import GitUserDecisionData, GitUserAgent, GitUserMixin
from git_repo_hub import GitRepoHub
from zk_repo import ZkRepo
import random
import time
import numpy
import subprocess
import sys
from heapq import heappush, heappop


# One trial of an experiment
class GitHubTrial(Trial):

    # Class-level information about parameter ranges and distributions. Note that the second probability
    # is passed to each agent but defined here on the population
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  ]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def initialize(self):
        self.events_heap = []
        # Create a hub object that will reside in the experiment with the agents
        self.hub = GitRepoHub(1)
        self.freqs = {101: 10, 102: 20, 103: 30}
        # The experiment now has one actual DASH agent and many copies of the agent-specific data.
        # On each iteration that an agent takes a step, the agent-specific data is copied into the agent
        a = GitUserAgent(useInternalHub=True, hub=self.hub, port=6000, trace_client=False)
        self.agents = [a]
        a.trace_client = False  # cut chatter when connecting and disconnecting
        a.traceLoop = False  # cut chatter when agent runs steps
        a.trace_github = False  # cut chatter when acting in github world
        self.agent_objects = []  # Use a different list for agent data

    # Override the default (which runs each agent once) to decide whether to create a new agent
    def run_one_iteration(self):
        a = self.agents[0]
        if not self.agent_objects or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            d = GitUserDecisionData(freqs=self.freqs)
            #print 'created agent', a
            self.agent_objects.append(d)
            agent_object_index = len(self.agent_objects) - 1
            a.decision_data = d
            heappush(self.events_heap, (a.next_event_time(0, 1528648881), agent_object_index))
            event_time = 0
        else:
            #d = random.choice(self.agent_objects)
            event_time, agent_object_index = heappop(self.events_heap)
            d = self.agent_objects[agent_object_index]
        # Not quite right since doesn't use an event from the heap for a new agent
        a.decision_data = d
        a.knownDict = d.knownDict  # keep track of dynamic system 2 data for agents
        a.knownFalseDict = d.knowFalseDict
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
        # In the second take, disconnect and reconnect each time so we don't run out of socket resources
        # (Not necessary now that the hub is in the same image as the agent and/or now that there is only one agent.)
        #if not a.connected:
        #    a.register()
        #a.agentLoop(max_iterations=1)
        heappush(self.events_heap, (a.next_event_time(event_time, 1528648881), agent_object_index))
        if self.iteration % 100 == 0:
            print 'iteration', self.iteration

    # These are defined above as measures
    def num_agents(self):
        return len(self.agent_objects)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agent_objects])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agent_objects])


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
#exp, trial_outputs = run_exp(max_iterations=1000,
#                             dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
#                             num_trials=1)

# Create a class that can perform all the actions but does not have a full DASHAgent. This seems to be a red herring,
# instead I'll try to reduce the information stored with each GitUserMixin.
class SmallAgent(GitUserMixin):
    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def readAgent(self, goal_def):
        pass

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True, skipS12=False):
        GitUserMixin.agentLoop(self, max_iterations, disconnect_at_end, True)  # Don't allow using the DASH loop

    def register(self, args):
        pass

    def primitiveActions(self, list):
        pass

    def use_system2(self, a):
        pass


# Test time and space to create a lot of agents
agents = []
hub = GitRepoHub(1)
# Create a system2 for the first agent and copy it for all the rest
#sys2_agent = None
#for i in xrange(0, 100000):
    # Try runing the mixin instead of the full DASH agent. We can always create a DASH agent later if needed.
    # 10k SmallAgents took 85mb on my laptop, 10k DASHAgents took 106mb, so the difference is not huge.
    #agents.append(GitUserAgent(useInternalHub=True, hub=hub, port=6000, trace_client=False, system2_proxy=sys2_agent))
    #agents.append(SmallAgent(useInternalHub=True, hub=hub, port=6000, trace_client=False, system2_proxy=sys2_agent))
    #agents.append(GitUserDecisionData())  # Takes the same space as SmallAgent
    #sys2_agent = agents[0]  # The first call above, sys2_agent will be None and system2 data will be created
#    agents.append(DASHAgent())
exp, trial_outputs = run_exp(max_iterations=1000,
                             dependent=lambda t: {'trial': t, 'agents': t.num_agents(), 'repos': t.num_repos(),
                                                  'actions': sum([a.total_activity for a in t.agent_objects])})
print 'running took', time.time() - start, 'seconds, with'
# getsizeof returns the same for GitUserAgents as for SmallAgents, but the python process sits in less than half
# the memory for the latter, so pursuing this idea.
#print 'total size for', len(agents), 'agents:', sum([sys.getsizeof(a) for a in agents])

