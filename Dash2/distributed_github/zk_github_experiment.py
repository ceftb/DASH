import sys; sys.path.extend(['../../'])

from Dash2.core.parameter import Range
from zk_trial import ZkTrial
from zk_experiment import ZkExperiment
from experiment_controller import ExperimentController

# This is an example of experiment script

if __name__ == "__main__":
    # TBD read parameters from argv if it is needed
    max_iterations = 20
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = ExperimentController(zk_host_id=1, zk_hosts='127.0.0.1:2181', host_id=1, hosts='127.0.0.1:2181')
    exp = ZkExperiment(trial_class=ZkTrial,
                       independent=independent,
                       dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                       exp_data=exp_data,
                       num_trials=num_trials)
    results = controller.run(exp)

