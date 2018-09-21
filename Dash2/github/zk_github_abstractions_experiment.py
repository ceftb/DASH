import sys; sys.path.extend(['../../'])
import os.path
import time
from datetime import datetime
from Dash2.core.parameter import Range
from Dash2.core.measure import Measure
from Dash2.core.parameter import Parameter
from Dash2.core.experiment import Experiment
from Dash2.core.dash_controller import DashController
from Dash2.github.initial_state_loader import build_state_from_event_log, read_state_file, load_profiles, \
    populate_embedding_probabilities, populate_event_rate, InitialStateSampleGenerator

from zk_github_state_experiment import ZkGithubStateTrial, ZkGithubStateWorkProcessor


if __name__ == "__main__":
    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1
    input_event_log = sys.argv[1]
    embedding_directory = sys.argv[2] if sys.argv[2] != "None" else "" # None if embedding is not used. # must have '/' in the end
    agent_class_name = sys.argv[3] # "GitUserAgent"
    agent_module_name = sys.argv[4] # "Dash2.github.git_user_agent"
    start_date = sys.argv[5]
    end_date = sys.argv[6]
    number_of_days_in_simulation = 1.0 + float((time.mktime(datetime.strptime(str(end_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())
                                        - time.mktime(datetime.strptime(str(start_date) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timetuple())) / (3600.0 * 24.0))
    output_file_name = sys.argv[7]
    training_data_weight = 1.0
    initial_condition_data_weight = 1.0
    truncation_coef = 1.0

    if embedding_directory != "":
        truncation_coef = sys.argv[8]
        if len(sys.argv) == 11:
            training_data_weight = float(sys.argv[9])
            initial_condition_data_weight = float(sys.argv[10])
    else:
        if len(sys.argv) == 10:
            training_data_weight = float(sys.argv[8])
            initial_condition_data_weight = float(sys.argv[9])

    # if state file is not present, then create it. State file is created from input event log.
    # Users in the initial state are partitioned (number of hosts is the number of partitions)
    graph_updaters = [InitialStateSampleGenerator(max_depth=50, max_number_of_user_nodes=1000, number_of_neighborhoods=200,
                                                  number_of_graph_samples=2),
                      InitialStateSampleGenerator(max_depth=10, max_number_of_user_nodes=1000, number_of_neighborhoods=100,
                                                  number_of_graph_samples=3)
                      ]
    print "Creating initial state files. May take a while, please wait ..."
    build_state_from_event_log(input_event_log, number_of_hosts, None,
                               training_data_weight=training_data_weight,
                               initial_condition_data_weight=initial_condition_data_weight,
                               initial_state_generators=graph_updaters)
    print "Initial state files created."

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
        'initial_state_file': input_event_log + "_state.json"
    }

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
        Measure('number_of_cross_process_communications'),
        Measure('memory_usage'),
        Measure('runtime')
    ]

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)

    run_number = 0
    for index, graph_updater in enumerate(graph_updaters):
        for sample in range(0, graph_updater.number_of_graph_samples):
            experiment_data["initial_state_file"] = input_event_log + str(run_number) + "_state.json"
            ZkGithubStateTrial.parameters[7] = Parameter('output_file_name', default=output_file_name + str(run_number))
            run_number += 1
            exp = Experiment(trial_class=ZkGithubStateTrial,
                             work_processor_class=ZkGithubStateWorkProcessor,
                             number_of_hosts=number_of_hosts,
                             independent=independent,
                             exp_data=experiment_data,
                             num_trials=num_trials)
            if (sample == graph_updater.number_of_graph_samples - 1) and (index == len(graph_updaters) - 1):
                results = controller.run(experiment=exp, run_data={}, start_right_away=True, continue_right_away=False)
            else:
                results = controller.run(experiment=exp, run_data={}, start_right_away=True, continue_right_away=True)


