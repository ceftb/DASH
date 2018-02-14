import sys; sys.path.extend(['../../'])

from Dash2.core.parameter import Range
from zk_trial import ZkTrial
from zk_experiment import ZkExperiment
from dash_controller import DashController

# This is an example of experiment script

if __name__ == "__main__":
    zk_host_id = 1
    zk_hosts = '127.0.0.1:2181'
    host_id = 1
    hosts = '127.0.0.1:2181'

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 3:
        zk_host_id = sys.argv[2]
        zk_hosts = sys.argv[1]
        host_id = sys.argv[2]
        hosts = sys.argv[1]

    elif len(sys.argv) == 5:
        zk_host_id = sys.argv[2]
        zk_hosts = sys.argv[1]
        host_id = sys.argv[4]
        hosts = sys.argv[3]
    else:
        print 'incorrect arguments: ', sys.argv

    max_iterations = 20
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    exp_data = {'max_iterations': max_iterations}

    # ExperimentController is a until class that provides command line interface to run the experiment on clusters
    controller = DashController(zk_host_id=zk_host_id, zk_hosts=zk_hosts, host_id=host_id, hosts=hosts)
    exp = ZkExperiment(trial_class=ZkTrial,
                       exp_id=101,
                       hosts=hosts,
                       independent=independent,
                       dependent=lambda t: [t.num_agents(), t.num_repos(), t.total_agent_activity()],
                       exp_data=exp_data,
                       num_trials=num_trials)
    results = controller.run(exp)

