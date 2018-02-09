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

    def __init__(self, zk, data={}, max_iterations=-1):
        super(ZkTrial, self).__init__(data, max_iterations)
        self.zk = zk
        self.hub = ZkRepoHub(repo_hub_id=1, zk=self.zk)

    # Override the default (which runs each agent once) to decide whether to create a new agent
    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False  # cut chatter when connecting and disconnecting
            a.traceLoop = False  # cut chatter when agent runs steps
            a.trace_github = False  # cut chatter when acting in github world
            print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again

    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])

    def create_agents(self, host_ids, number_of_agents):
        agents_map = defaultdict(list)
        for i in range(number_of_agents):
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False
            a.traceLoop = False
            a.trace_github = False
            self.agents.append(a)  # legacy
            batch = (number_of_agents + number_of_agents % len(host_ids)) / len(host_ids)
            host_index = i / batch + 1
            agents_map[host_index].append(a)
        return agents_map

    def load_agents(self, host_ids, number_of_agents):
        self.agents_map = defaultdict(list)

    def save_agents_to_zk(self, agents_map):
        pass
