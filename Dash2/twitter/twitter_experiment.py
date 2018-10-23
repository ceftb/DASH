import sys; sys.path.extend(['../../'])
import os
import time
from datetime import datetime
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Parameter
from Dash2.core.experiment import Experiment
from Dash2.core.dash_controller import DashController
from Dash2.reddit.reddit_state_creator import RedditGraphBuilder
from Dash2.socsim.network_utils import create_initial_state_files
from Dash2.socsim.event_types import reddit_events_list, reddit_events
from Dash2.socsim.socsim_trial import SocsimTrial
from Dash2.socsim.socsim_work_processor import SocsimWorkProcessor


if __name__ == "__main__":
    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1
    input_event_log = sys.argv[1]
    embedding_directory = sys.argv[2] if sys.argv[2] != "None" else "" # None if embedding is not used. # must have '/' in the end
    agent_class_name = sys.argv[3] # "TwitterAgent"
    agent_module_name = sys.argv[4] # "Dash2.teitter.twitter_agent"
    start_date = sys.argv[5]
    end_date = sys.argv[6]
    number_of_days_in_simulation = 1.0 + float((time.mktime(datetime.strptime(str(end_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())
                                        - time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())) / (3600.0 * 24.0))
    output_file_name = sys.argv[7]

    # if state file is not present, then create it. State file is created from input event log.
    # Users in the initial state are partitioned (number of hosts is the number of partitions)
    initial_state_file_name = input_event_log + "_state.json"
    if not os.path.isfile(initial_state_file_name):
        print initial_state_file_name + " file is not present, creating one. May take a while, please wait ..."
        create_initial_state_files(input_event_log , RedditGraphBuilder, reddit_events, reddit_events_list)
        print str(initial_state_file_name) + " file created."

    # length of the simulation is determined by two parameters: max_iterations_per_worker and end max_time
    # max_iterations_per_worker - defines maximum number of events each dash worker can do
    # max_time - defines end time of the simulaition (event with time later than max_time will not be scheduled in the event queue)
    max_iterations_per_worker = number_of_days_in_simulation * 1110000 / number_of_hosts # assuming <1.11M events per day

    # experiment setup
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.0, 0.1, 0.1)]
    experiment_data = {
        'max_iterations': max_iterations_per_worker,
        'initial_state_file': initial_state_file_name}

    # Trial parameters and measures
    class TwitterTrial(SocsimTrial):
        parameters = [
                    Parameter('prob_create_new_agent', default=0.5),
                    Parameter('prob_agent_creates_new_repo', default=0.5),
                    Parameter('start_time', default=time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())),
                    Parameter('max_time', default=time.mktime(datetime.strptime(str(end_date) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timetuple())),
                    Parameter('hub_class_name', default="TwitterHub"),
                    Parameter('hub_module_name', default="Dash2.twitter.twitter_hub"),
                    Parameter('agent_class_name', default=agent_class_name),
                    Parameter('agent_module_name', default=agent_module_name),
                    Parameter('embedding_path', default=embedding_directory),
                    Parameter('output_file_name', default=output_file_name)
                ]
        measures = [
                    Measure('num_agents'),
                    Measure('num_resources'),
                    Measure('number_of_cross_process_communications'),
                    Measure('memory_usage'),
                    Measure('runtime')
                ]

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = Experiment(trial_class=TwitterTrial,
                     work_processor_class=SocsimWorkProcessor,
                     number_of_hosts=number_of_hosts,
                     exp_data=experiment_data,
                     num_trials=num_trials)
    results = controller.run(experiment=exp, run_data={}, start_right_away=False)
