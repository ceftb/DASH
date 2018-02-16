import sys; sys.path.extend(['../../'])

from Dash2.core.parameter import Range
from zk_trial import ZkTrial
from zk_experiment import ZkExperiment
from dash_controller import DashController

# This is an example of experiment script

if __name__ == "__main__":
    zk_hosts = '127.0.0.1:2181'
    number_of_hosts = 1

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 1:
        number_of_hosts = sys.argv[1]
    elif len(sys.argv) == 3:
        zk_hosts = sys.argv[1]
        number_of_hosts = sys.argv[2]
    else:
        print 'incorrect arguments: ', sys.argv

    max_iterations = 2000
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_hosts=zk_hosts, number_of_hosts=number_of_hosts)
    exp = ZkExperiment(trial_class=ZkTrial,
                       exp_id=101,
                       number_of_hosts=number_of_hosts,
                       independent=independent,
                       dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                       exp_data=exp_data,
                       num_trials=num_trials)
    results = controller.run(exp)

