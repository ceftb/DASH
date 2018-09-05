import sys; sys.path.extend(['../../'])
import os.path
import time
from datetime import datetime
from heapq import heappush, heappop
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Parameter
from Dash2.core.trial import Trial
from Dash2.core.experiment import Experiment
from Dash2.core.dash_controller import DashController
from Dash2.core.work_processor import WorkProcessor
from Dash2.github.initial_state_loader import build_state_from_event_log, read_state_file, load_profiles, \
    populate_embedding_probabilities, populate_event_rate, GraphUpdater
from Dash2.github.zk_repo_hub import ZkRepoHub
from Dash2.github.distributed_event_log_utils import merge_log_file, trnaslate_user_and_repo_ids_in_event_log, event_types

# Work processor performs simulation as individual process (it is a DashWorker)
class ZkGithubStateWorkProcessor(WorkProcessor):

    # this is path to current package
    module_name = "Dash2.github.zk_github_state_experiment"

    def initialize(self):


        self.agents_decision_data = {}
        self.events_heap = []
        self.event_counter = 0
        self.hub = ZkRepoHub(self.zk, self.task_full_id, 0, log_file=self.log_file)

        mod = __import__(self.agent_module_name, fromlist=[self.agent_class_name])
        cls = getattr(mod, self.agent_class_name)

        self.agent =cls(useInternalHub=True, hub=self.hub, skipS12=True, trace_client=False, traceLoop=False, trace_github=False)
        # close and remove event log file, which was create by __init__(), we need a different name and we need to open after state is loaded.
        self.log_file.close()
        os.remove(self.task_full_id + '_event_log_file.txt')

        self.hub.graph_file_path = self.UR_graph_path
        if self.users_file is not None and self.users_file != "":
            load_profiles(self.users_file, self.populate_agents_collection)

        # load embeddings probabilities, if such are specified in the initial state file
        populate_embedding_probabilities(self.agents_decision_data, self.embedding_path, truncation_coef=self.truncation_coef)

        # closing and reopening log file due to delays in loading the state (netwok fils system sometimes interrupts the file otherwise)
        self.log_file = open(self.output_file_name + self.task_full_id + '_event_log_file.txt', 'w')
        self.hub.log_file = self.log_file
        self.hub.agents_decision_data = self.agents_decision_data # will not work for distributed version
        self.hub.finalize_statistics()
        print "Agents instantiated: ", len(self.agents_decision_data)

    # Function takes a user profile and creates an agent decision data object.
    def populate_agents_collection(self, profile):
        decision_data = self.agent.create_new_decision_object(profile)
        self.agent.decision_data = decision_data
        first_event_time = self.agent.first_event_time(self.start_time)
        if first_event_time is not None:
            heappush(self.events_heap, (self.agent.next_event_time(self.start_time), decision_data.id))
        self.agents_decision_data[decision_data.id] = decision_data

    def run_one_iteration(self):
        event_time, agent_id = heappop(self.events_heap)
        decision_data = self.agents_decision_data[int(agent_id)]
        self.hub.set_curr_time(event_time)
        self.agent.decision_data = decision_data
        self.agent.agentLoop(max_iterations=1, disconnect_at_end=False)
        next_event_time = self.agent.next_event_time(event_time)
        if next_event_time < self.max_time:
            heappush(self.events_heap, (next_event_time, agent_id))
        self.event_counter += 1

    def should_stop(self):
        if self.max_iterations > 0 and self.iteration >= self.max_iterations:
            print 'reached end of iterations for trial'
            return True
        if len(self.events_heap) == 0:
            print 'reached end of event queue, no more events'
            return True
        return False

    def get_dependent_vars(self):
        return {"num_agents": len(self.agents),
                "num_repos": sum([len(a.name_to_repo_id) for a in self.agents_decision_data.viewvalues()]),
                "total_agent_activity": sum([a.total_activity for a in self.agents_decision_data.viewvalues()]),
                "number_of_cross_process_communications": self.hub.sync_event_counter
                }


# Dash Trial decomposes trial into tasks and allocates them to DashWorkers
class ZkGithubStateTrial(Trial):
    parameters = []
    # all measures are considered depended vars, values are aggregated in self.results
    measures = []

    def initialize(self):
        # self.initial_state_file is defined via experiment_data
        if not os.path.isfile(self.initial_state_file):
            raise Exception("Initial state file was not found")
        initial_state_meta_data = read_state_file(self.initial_state_file)
        print initial_state_meta_data
        self.users_file = initial_state_meta_data["users_file"]
        self.users_ids = initial_state_meta_data["users_ids"]
        self.repos_ids = initial_state_meta_data["repos_ids"]
        # set up max ids
        self.set_max_repo_id(int(initial_state_meta_data["number_of_repos"]))
        self.set_max_user_id(int(initial_state_meta_data["number_of_users"]))
        self.is_loaded = True


    # this method defines parameters of individual tasks (as a json data object - 'data') that will be sent to dash workers
    def init_task_params(self, task_full_id, data):
        _, _, task_num = task_full_id.split("-")
        self.init_task_param("initial_state_file", self.initial_state_file, data)
        self.init_task_param("users_file", self.users_file + "_" + str(int(task_num) - 1), data)
        self.init_task_param("UR_graph_path", read_state_file(self.initial_state_file)["UR_graph_path"], data)

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
            log_file_name = self.output_file_name + str(self.exp_id) + "-" + str(self.trial_id) + "-" + str(task_index + 1) + "_event_log_file.txt"
            file_names.append(log_file_name)
        tmp_file_name = self.output_file_name + "tmp_output.csv"

        if number_of_files == 1:
            os.rename(file_names[0], tmp_file_name)
            print "renamed ", file_names[0], " -> ", tmp_file_name
        else:
            merge_log_file(file_names, tmp_file_name, sort_chronologically=True)
            for log_file_name in file_names:
                os.remove(log_file_name)

        output_file_name = self.output_file_name + "_trial_" + str(self.trial_id) + ".csv"
        trnaslate_user_and_repo_ids_in_event_log(even_log_file=tmp_file_name,
                                                 output_file_name=output_file_name,
                                                 users_ids_file=self.users_ids,
                                                 repos_ids_file=self.repos_ids)
        os.remove(tmp_file_name)


if __name__ == "__main__":
    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1
    input_event_log = sys.argv[1] #"./dryrun2/dryrun_events_20170501-20170630.csv"
    number_of_month_in_event_log = float(sys.argv[2])
    number_of_days_in_simulation = int(sys.argv[3])
    embedding_directory = sys.argv[4] if sys.argv[4] != "None" else "" # None if embedding is not used. # must have '/' in the end
    agent_class_name = sys.argv[5] # "GitUserAgent"
    agent_module_name = sys.argv[6] # "Dash2.github.git_user_agent"
    start_date = sys.argv[7]
    end_date = sys.argv[8]
    output_file_name = sys.argv[9]
    training_data_weight = 1.0
    initial_condition_data_weight = 1.0
    truncation_coef = 1.0

    if embedding_directory != "":
        truncation_coef = sys.argv[10]
        if len(sys.argv) == 13:
            training_data_weight = float(sys.argv[11])
            initial_condition_data_weight = float(sys.argv[12])
    else:
        if len(sys.argv) == 12:
            training_data_weight = float(sys.argv[10])
            initial_condition_data_weight = float(sys.argv[11])


    # if state file is not present, then create it. State file is created from input event log.
    # Users in the initial state are partitioned (number of hosts is the number of partitions)
    initial_state_file_name = input_event_log + "_state.json"
    graph_updater = GraphUpdater(max_depth=100, max_number_of_user_nodes=100000, number_of_neighborhoods=10)
    if not os.path.isfile(initial_state_file_name):
        print initial_state_file_name + " file is not present, creating one. May take a while, please wait ..."
        build_state_from_event_log(input_event_log, number_of_hosts, initial_state_file_name,
                                   number_of_months=number_of_month_in_event_log,
                                   training_data_weight=training_data_weight,
                                   initial_condition_data_weight=initial_condition_data_weight,
                                   graph_updater=graph_updater)
        print str(initial_state_file_name) + " file created."

    # length of the simulation is determined by two parameters: max_iterations_per_worker and end max_time
    # max_iterations_per_worker - defines maximum number of events each dash worker can do
    # max_time - defines end time of the simulaition (event with time later than max_time will not be scheduled in the event queue)
    number_of_days =  number_of_days_in_simulation #62
    max_iterations_per_worker = number_of_days * 1110000 / number_of_hosts # assuming ~1.11M events per day

    # experiment setup
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.0, 0.1, 0.1)]
    experiment_data = {
        'max_iterations': max_iterations_per_worker,
        'initial_state_file': initial_state_file_name}

    # Trial parameters and measures
    ZkGithubStateTrial.parameters = [
        Parameter('prob_create_new_agent', default=0.5),
        Parameter('prob_agent_creates_new_repo', default=0.5),
        Parameter('start_time', default=time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())),
        Parameter('max_time', default=time.mktime(datetime.strptime(str(end_date) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timetuple())),
        Parameter('agent_class_name', default=agent_class_name),
        Parameter('agent_module_name', default=agent_module_name),
        Parameter('embedding_path', default=embedding_directory),
        Parameter('output_file_name', default=output_file_name),
        Parameter('truncation_coef', default=truncation_coef)
    ]
    ZkGithubStateTrial.measures = [
        Measure('num_agents'),
        Measure('num_repos'),
        Measure('total_agent_activity'),
        Measure('number_of_cross_process_communications')]

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = Experiment(trial_class=ZkGithubStateTrial,
                     work_processor_class=ZkGithubStateWorkProcessor,
                     number_of_hosts=number_of_hosts,
                     independent=independent,
                     exp_data=experiment_data,
                     num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)

