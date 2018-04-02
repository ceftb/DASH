import sys; sys.path.extend(['../../'])
import random
from heapq import heappush, heappop
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
from github_intial_state_generator import GithubStateLoader

# This is an example of experiment script

class ZkGithubStateWorkProcessor(DashWorkProcessor):

    # this is path to current package
    # I cannot use reflection in super class here because, it would return path to superclass, therefore need to define it explicitly in subclasses
    module_name = "Dash2.distributed_github.zk_github_state_experiment"

    def __init__(self, zk, host_id, task_full_id, data):
        self.log_file = open('event_log_file.txt', 'w')
        DashWorkProcessor.__init__(self, zk, host_id, task_full_id, data, ZkRepoHub(zk=zk, task_full_id=task_full_id, start_time=0, log_file=self.log_file))
        self.agent_id_to_total_events = {}
        self.events_heap = []
        self.agents = {}
        GithubStateLoader.load_profiles_from_file(self.users_file, self.populate_agents_collection)
        print "Agents instantiated: ", len(self.agents)

    # function takes user profile and creates an agent, new agent is added to the pool of agents.
    def populate_agents_collection(self, profile):
        a = GitUserAgent(useInternalHub=True, hub=self.hub, id=profile["id"],
                         trace_client=False, traceLoop=False, trace_github=False)
        # frequency of use of associated repos:
        total_even_counter = 0
        for repo_id, freq in profile.iteritems():
            if repo_id != "id":
                int_repo_id = int(repo_id)
                a.repo_id_to_freq[int_repo_id ] = int(freq["f"])
                total_even_counter += a.repo_id_to_freq[int_repo_id]
                if int(freq["c"]) > 1:
                    self.hub.init_repo(repo_id=int_repo_id, user_id=a.id, curr_time=0, is_node_shared=True)
                else:
                    self.hub.init_repo(repo_id=int_repo_id, user_id=a.id, curr_time=0, is_node_shared=False)
        self.agent_id_to_total_events[a.id] = total_even_counter
        heappush(self.events_heap, (a.next_event_time(0, self.max_time), a.id))
        self.agents[a.id] = a

    def populate_repo_collection(self, profile):
        pass

    def run_one_iteration(self):
        event_time, agent_id = heappop(self.events_heap)
        a = self.agents[int(agent_id)]
        self.hub.set_curr_time(event_time)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)
        heappush(self.events_heap, (a.next_event_time(event_time, self.max_time), agent_id))

    def dependent(self):
        return {"num_agents": self.num_agents(), "num_repos": self.num_repos(), "total_agent_activity": self.total_agent_activity()}

    # Measures #
    def num_agents(self):
        return len(self.agents)

    def num_repos(self):
        return len(self.hub.all_repos)

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents.itervalues()])


class ZkGithubStateTrial(DashTrial):
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  Parameter('max_time', distribution=Uniform(5184000, 5184001), default=5184000)]

    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    def initialize(self):
        self.results = {"num_agents": 0, "num_repos": 0, "total_agent_activity": 0}
        self.users_file_name = "./data/data.csv_users.json"
        # prepare task files for individual dash workers
        #GithubStateLoader.partitionProfilesFile(self.users_file_name, self.number_of_hosts)

    # method defines parameters for individual tasks (as a json data object ) that will be sent to dash workers
    def init_task_params(self, task_full_id, data):
        self.exp_id, self.trial_id, self.task_num = task_full_id.split("-") # self.task_num by default is the same as node id
        # users_file
        data["users_file"] = self.users_file_name + "_" + str(int(self.task_num) - 1)
        data["parameters"].append("users_file")

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

    max_iterations = 3000
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.0, 0.1, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = DashExperiment(trial_class=ZkGithubStateTrial,
                         work_processor_class=ZkGithubStateWorkProcessor,
                         number_of_hosts=number_of_hosts,
                         independent=independent,
                         dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                         exp_data=exp_data,
                         num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)

