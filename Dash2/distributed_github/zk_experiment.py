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
from kazoo.client import KazooClient
from collections import defaultdict


# One trial of an experiment
class ZkTrial(Trial):
    # class level information to configure zookeeper connection
    # zookeeper connection is a process lelev shared object, all threads use it

    zk = None
    # Comma-separated list of hosts of zookeeper to connect to
    zk_hosts = '127.0.0.1:2181'
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

    def __init__(self, data={}, max_iterations=-1):
        super(ZkTrial, self).__init__(data, max_iterations)
        self.agents_map = {}

    # The initialize function sets up the agent list
    def initialize(self):

        if ZkTrial.zk is None:
            self.init_zookeeper(ZkTrial.zk_hosts)
        self.hub = ZkRepoHub(ZkTrial.host_id, ZkTrial.zk)

        if (ZkTrial.zk_host_id == 1): # host is a leader
            self.create_agents([1,2,3,4,5], 1000)

    def init_zookeeper(self, hosts):
        ZkTrial.zk = KazooClient(hosts)
        ZkTrial.zk.start()

    def create_agents(self, host_ids, number_of_agents):
        self.agents_map = defaultdict(list)
        for i in range(number_of_agents):
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False
            a.traceLoop = False
            a.trace_github = False
            self.agents.append(a)
            batch = (number_of_agents + number_of_agents % len(host_ids)) / len(host_ids)
            host_index = i / batch
            self.agents_map[host_index].append(a)

    def run_one_iteration(self):
        for a in self.agents_map[self.host_id]: # only iterate over agents of the current host
            a.agentLoop(max_iterations=1, disconnect_at_end=False)

    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])


# hosts - comma separated list of hosts
# number of hosts in hosts list must be odd for zookeeper
# by default hosts in zookeeper assemble are the same as experiment hosts
def run_exp(max_iterations=20, host_id=1, hosts='127.0.0.1:2181', dependent='num_agents', num_trials=2):
    # Zookeeper hosts in assemble
    ZkTrial.zk_host_id = host_id
    ZkTrial.zk_hosts = hosts
    ZkTrial.number_of_zk_hosts = count_hosts(hosts)
    # Hosts in experiment
    ZkTrial.host_id = host_id
    ZkTrial.hosts = hosts
    ZkTrial.number_of_hosts = count_hosts(hosts)

    e = Experiment(trial_class=ZkTrial,
                     exp_data={'max_iterations': max_iterations},
                     num_trials=num_trials,
                     independent=['prob_create_new_agent', Range(0.5, 0.6, 0.1)],
                     dependent=dependent
                     );
    return e, e.run()

def count_hosts(hosts):
    return 1 # TBD fixt it

# TBD: need to read hosts from CLI arguments
if __name__ == "__main__":
    print 'argv is', sys.argv
    print "running experiment ..."
    run_exp()
