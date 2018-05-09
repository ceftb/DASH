import sys; sys.path.extend(['../../'])
import os.path
from heapq import heappush, heappop
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Uniform
from Dash2.core.parameter import Parameter
from Dash2.core.trial import Trial
from Dash2.core.experiment import Experiment
from Dash2.core.dash_controller import DashController
from Dash2.core.work_processor import WorkProcessor
from Dash2.github.git_user_agent import GitUserAgent
from Dash2.github.initial_state_loader import GithubStateLoader
from Dash2.github.zk_repo_hub import ZkRepoHub

# This is an example of experiment script

# Work processor performs simulation as individual process (it is a DashWorker)
class ZkGithubStateWorkProcessor(WorkProcessor):

    # this is path to current package
    module_name = "Dash2.github.zk_github_state_experiment"

    def initialize(self):
        self.agents = {} # in this experiment agents are stored as a dictionary (fyi: by default it was a list)
        self.events_heap = []
        self.event_counter = 0
        self.hub = ZkRepoHub(self.zk, self.task_full_id, 0, log_file=self.log_file)
        self.log_file.close()

        if self.state_file is not None and self.state_file != "":
            meta_data = GithubStateLoader.read_state_file(self.state_file)
        if self.users_file is not None and self.users_file != "":
            # it is important to load users first, since this will instantiate list of repos used by agents in this dash worker
            GithubStateLoader.load_profiles_from_file(self.users_file, self.populate_agents_collection)
        if self.repos_file is not None and self.repos_file != "":
            pass
            #GithubStateLoader.load_profiles_from_file(self.repos_file, self.populate_repos_collection)

        self.log_file = open(self.task_full_id + '_event_log_file.txt', 'w')
        self.hub.log_file = self.log_file
        print "Agents instantiated: ", len(self.agents)

    # Function takes a user profile and creates an agent.
    def populate_agents_collection(self, profile):
        agent_id = profile.pop("id", None)
        a = GitUserAgent(useInternalHub=True, hub=self.hub, id=agent_id,
                         trace_client=False, traceLoop=False, trace_github=False)
        # frequency of use of associated repos:
        total_even_counter = 0
        for repo_id, freq in profile.iteritems():
            int_repo_id = int(repo_id)
            a.repo_id_to_freq[int_repo_id] = int(freq["f"])
            a.name_to_repo_id[int_repo_id] = int_repo_id
            total_even_counter += a.repo_id_to_freq[int_repo_id]
            is_node_shared = True if int(freq["c"]) > 1 else False
            self.hub.init_repo(repo_id=int_repo_id, user_id=a.id, curr_time=0, is_node_shared=is_node_shared)
        a.total_activity = total_even_counter
        heappush(self.events_heap, (a.next_event_time(self.start_time, self.max_time), a.id))
        self.agents[a.id] = a

    # Function takes a repo profile and populates repo object in self.hub
    def populate_repos_collection(self, profile):
        int_repo_id = int(profile.pop("id", None))
        if int_repo_id in self.hub.all_repos:
            # self.hub.init_repo(repo_id=int_repo_id, profile=profile)
            repo = self.hub.all_repos[int_repo_id]
            # update repo properties here

    def run_one_iteration(self):
        event_time, agent_id = heappop(self.events_heap)
        a = self.agents[int(agent_id)]
        self.hub.set_curr_time(event_time)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)
        heappush(self.events_heap, (a.next_event_time(event_time, self.max_time), agent_id))
        self.event_counter += 1

    def get_dependent_vars(self):
        return {"num_agents": len(self.agents),
                "num_repos": sum([len(a.name_to_repo_id) for a in self.agents.viewvalues()]),
                "total_agent_activity": sum([a.total_activity for a in self.agents.viewvalues()])}


# Dash Trial decomposes trial into tasks and allocates them to DashWorkers
class ZkGithubStateTrial(Trial):
    parameters = [Parameter('prob_create_new_agent', distribution=Uniform(0,1), default=0.5),
                  Parameter('prob_agent_creates_new_repo', distribution=Uniform(0,1), default=0.5),
                  Parameter('max_time', distribution=Uniform(1528648881, 1528648882), default=1528648881),
                  Parameter('start_time', distribution=Uniform(1523464880, 1523464881), default=1523464880)]

    # all measures are considered depended vars, values are aggregated in self.results
    measures = [Measure('num_agents'), Measure('num_repos'), Measure('total_agent_activity')]

    # input event log and output event log files names
    #input_event_log = "./data_jan_2017/data_jan_2017.csv"
    input_event_log = "./data_sample/data_sample.csv"

    output_event_log = input_event_log + "_output"

    def initialize(self):
        if os.path.isfile(ZkGithubStateTrial.input_event_log + "_state.json"):
            intial_state_meta_data = GithubStateLoader.read_state_file(ZkGithubStateTrial.input_event_log + "_state.json")
        else:
            intial_state_meta_data = GithubStateLoader.build_state_from_event_log(input_event_log=ZkGithubStateTrial.input_event_log,
                                                                     number_of_hosts=self.number_of_hosts)
        print intial_state_meta_data
        self.state_file = ZkGithubStateTrial.input_event_log + "_state.json"
        self.users_file = intial_state_meta_data["users_file"]
        self.repos_file = intial_state_meta_data["repos_file"]
        self.users_ids = intial_state_meta_data["users_ids"]
        self.repos_ids = intial_state_meta_data["repos_ids"]
        is_partitioning_needed = intial_state_meta_data["is_partitioning_needed"]
        # generate task files for individual dash workers
        if is_partitioning_needed == "True":  # partitioning breaks input simulation state file into series of task files for DashWokers.
            # Generated task file can be reused across experiments with the same number of dash workers, which speeds up overall time.
            GithubStateLoader.partition_profiles_file(self.users_file, self.number_of_hosts, int(intial_state_meta_data["number_of_users"]))
        # set up max ids
        #self.zk.restart()
        self.set_max_repo_id(int(intial_state_meta_data["number_of_repos"]))
        self.set_max_user_id(int(intial_state_meta_data["number_of_users"]))
        self.is_loaded = True


    # this method defines parameters of individual tasks (as a json data object - 'data') that will be sent to dash workers
    def init_task_params(self, task_full_id, data):
        _, _, task_num = task_full_id.split("-")
        self.init_task_param("state_file", self.state_file, data)
        self.init_task_param("users_file", self.users_file + "_" + str(int(task_num) - 1), data)
        self.init_task_param("repos_file", self.repos_file + "_" + str(int(task_num) - 1), data)

    # partial_dependent is a dictionary of dependent vars
    def append_partial_results(self, partial_dependent):
        for measure in self.measures:
            if not (measure.name in self.results):
                self.results[measure.name] = 0
            self.results[measure.name] += int(partial_dependent[measure.name])

    def process_after_run(self):  # merge log files from all workers
        file_names = []
        number_of_files = self.number_of_hosts
        for task_index in range(0, number_of_files, 1):
            log_file_name = str(self.exp_id) + "-" + str(self.trial_id) + "-" + str(task_index + 1) + "_event_log_file.txt"
            file_names.append(log_file_name)
        GithubStateLoader.merge_log_file(file_names , "tmp_output.csv", "timestamp,event,user_id,repo_id")
        for log_file_name in file_names:
            os.remove(log_file_name)
        output_file_name = ZkGithubStateTrial.output_event_log + "_trial_" + str(self.trial_id) + ".csv"
        GithubStateLoader.trnaslate_user_and_repo_ids_in_event_log(even_log_file="tmp_output.csv",
                                                                   output_file_name=output_file_name,
                                                                   users_ids_file=self.users_ids,
                                                                   repos_ids_file=self.repos_ids)
        os.remove("tmp_output.csv")


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

    # if state file is not present, then create it.
    if not os.path.isfile(ZkGithubStateTrial.input_event_log + "_state.json"):
        print str(ZkGithubStateTrial.input_event_log) + "_state.json file is not present, creating one. May take a while, please wait ..."
        intial_state_meta_data = GithubStateLoader.build_state_from_event_log(ZkGithubStateTrial.input_event_log, number_of_hosts)
        print str(ZkGithubStateTrial.input_event_log) + "_state.json file created."

    number_of_events = 10000 # total number of actions in experiments
    max_iterations_per_worker = number_of_events / number_of_hosts
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.0, 0.1, 0.1)]
    exp_data = {'max_iterations': max_iterations_per_worker}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = Experiment(trial_class=ZkGithubStateTrial,
                         work_processor_class=ZkGithubStateWorkProcessor,
                         number_of_hosts=number_of_hosts,
                         independent=independent,
                         exp_data=exp_data,
                         num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)

