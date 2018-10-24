import sys; sys.path.extend(['../../'])
import os
import time
from datetime import datetime
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Parameter
from Dash2.core.experiment import Experiment
from Dash2.core.dash_controller import DashController
from Dash2.github.github_state_creator import GithubGraphBuilder, IdDictionaryInMemoryStream
from Dash2.socsim.network_utils import create_initial_state_files
from Dash2.socsim.event_types import github_events_list, github_events
from Dash2.socsim.socsim_trial import SocsimTrial
from Dash2.socsim.socsim_work_processor import SocsimWorkProcessor


if __name__ == "__main__":
    input_event_log = sys.argv[1]
    domain = sys.argv[2]
    scenario = sys.argv[3]
    agent_class_name = sys.argv[4] # "GithubAgent"
    agent_module_name = sys.argv[5] # "Dash2.github.github_agent"
    start_date = sys.argv[6]
    end_date = sys.argv[7]
    output_file_name = sys.argv[8]

    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1
    number_of_days_in_simulation = 1.0 + float((time.mktime(datetime.strptime(str(end_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())
                                        - time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())) / (3600.0 * 24.0))

    # Trial parameters and measures
    class GithubTrial(SocsimTrial):
        parameters = [
                    Parameter('prob_create_new_agent', default=0.5),
                    Parameter('prob_agent_creates_new_repo', default=0.5),
                    Parameter('start_time', default=time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())),
                    Parameter('max_time', default=time.mktime(datetime.strptime(str(end_date) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timetuple())),
                    Parameter('hub_class_name', default="GithubHub"),
                    Parameter('hub_module_name', default="Dash2.github.github_hub"),
                    Parameter('agent_class_name', default=agent_class_name),
                    Parameter('agent_module_name', default=agent_module_name),
                    Parameter('embedding_path', default=""),
                    Parameter('team_name', default="usc"),
                    Parameter('scenario', default=scenario),
                    Parameter('domain', default=domain),
                    Parameter('platform', default="github"),
                    Parameter('output_file_name', default=output_file_name)
                ]
        measures = [
                    Measure('num_agents'),
                    Measure('num_resources'),
                    Measure('number_of_cross_process_communications'),
                    Measure('memory_usage'),
                    Measure('runtime')
                ]

    # if state file is not present, then create it. State file is created from input event log.
    # Users in the initial state are partitioned (number of hosts is the number of partitions)
    initial_state_file_name = str(input_event_log).split(".json")[0] + "_state.json"
    if not os.path.isfile(initial_state_file_name):
        print initial_state_file_name + " file is not present, creating one. May take a while, please wait ..."
        create_initial_state_files(input_event_log , GithubGraphBuilder, github_events, github_events_list,
                                   dictionary_stream_cls=IdDictionaryInMemoryStream,
                                   initial_state_generators=None)
        print str(initial_state_file_name) + " file created."

    # experiment setup
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.0, 0.1, 0.1)]
    experiment_data = {
        'max_iterations': number_of_days_in_simulation * 1110000 / number_of_hosts, # max_iterations_per_worker
        'initial_state_file': initial_state_file_name}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = Experiment(trial_class=GithubTrial,
                     work_processor_class=SocsimWorkProcessor,
                     number_of_hosts=number_of_hosts,
                     exp_data=experiment_data,
                     num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)
