import sys; sys.path.extend(['../../'])
from zk_repo_hub import ZkRepoHub
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.github.git_user_agent import GitUserAgent
from Dash2.core.experiment import Experiment
from Dash2.core.parameter import Parameter
from Dash2.core.measure import Measure
from kazoo.client import KazooClient
from collections import defaultdict

# Trial of an experiment. ZkTrial uses Zookeeper to distribute agents across hosts.
class ZkTrial(Trial):
    # class level information to configure zookeeper connection
    # zookeeper connection is a process lelev shared object, all threads use it

    zk = None
    # Comma-separated list of hosts of zookeeper to connect to
    zk_hosts = '127.0.0.1:2181'  # default value is current machine (for local installation of Zookeeper)
    number_of_zk_hosts = 1
    zk_host_id = 1  # default value is 1 which is a leader's id

    # Comma-separated list of hosts avialable for each trial
    # By default it is assumed that it is the same set of hosts as in zookeeper assemble
    hosts = zk_hosts
    number_of_hosts = number_of_zk_hosts
    host_id = 1  # default value is 1 which is a leader's id

    # Class-level information about parameter ranges and distributions.
    # Note that the second probability is passed to each agent but defined here on the population
    parameters = [Parameter('prob_agent_creates_new_repo', distribution=Uniform(0, 1), default=0.5)]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def __init__(self, data={}, max_iterations=-1):
        super(ZkTrial, self).__init__(data, max_iterations)
        self.agents_map = {}
        self.hub = None

    # The initialize function sets up the agent list
    def initialize(self):
        if ZkTrial.zk is None:
            self.init_zookeeper(ZkTrial.zk_hosts)
        if self.hub is None:
            self.hub = ZkRepoHub(ZkTrial.host_id, ZkTrial.zk)

        list_of_hosts_ids = range(1, len(ZkTrial.hosts.split(",")) + 1)  # assume that host ids are 1 ... total_number_of_hosts
        if ZkTrial.host_id == 1:  # host is a leader
            self.create_agents(list_of_hosts_ids, 1000)

    # Connects to zookeeper server
    @classmethod
    def init_zookeeper(cls, hosts):
        ZkTrial.zk = KazooClient(hosts)
        ZkTrial.zk.start()

    # Gracefully stop zookeeper session and release resources.
    @classmethod
    def stop_zookeeper(cls, hosts):
        ZkTrial.zk.stop()

    def create_agents(self, host_ids, number_of_agents):
        self.agents_map = defaultdict(list)
        for i in range(number_of_agents):
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False
            a.traceLoop = False
            a.trace_github = False
            self.agents.append(a)
            batch = (number_of_agents + number_of_agents % len(host_ids)) / len(host_ids)
            host_index = i / batch + 1
            self.agents_map[host_index].append(a)

    def run_one_iteration(self):
        for a in self.agents_map[self.host_id]: # only iterate over agents of the current host
            a.agentLoop(max_iterations=1, disconnect_at_end=False)

    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])


# hosts - comma separated list of hosts
# number of hosts in hosts list must be odd for zookeeper
# by default hosts in zookeeper assemble are the same as experiment hosts
def run_exp(max_iterations=20, host_id=1, hosts='127.0.0.1:2181', dependent='num_agents', num_trials=1):
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
                     dependent=dependent)
    return e, e.run()


def count_hosts(hosts):
    addresses = hosts.split(",")
    return len(addresses)


# First argument is a comma separated list of hosts.
# The first host in the list should be a local machine for better performance
# Second argument is the current host's id (number between 1-255)
if __name__ == "__main__":
    print "running experiment ..."
    if len(sys.argv) == 3:
        print 'argv is', sys.argv
        hosts_list = sys.argv[1]
        curr_host_id = int(sys.argv[2])
        run_exp(host_id=curr_host_id, hosts=hosts_list)
    else:
        run_exp()
