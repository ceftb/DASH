import sys; sys.path.extend(['../../'])

from Dash2.core.experiment import Experiment
from Dash2.core.trial import Trial
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from Dash2.core.measure import Measure
import random
import time
import numpy
import subprocess
from zk_trial import ZkTrial
from zk_experiment import ZkExperiment
from experiment_controller import ExperimentController

if __name__ == "__main__":
    # print 'argv is', sys.argv
    # TBD read parameters from argv
    max_iterations = 20
    num_trials = 1
    independent = ['prob_create_new_agent', Range(0.5, 0.6, 0.1)]
    dependent = 'num_agents'
    exp_data = {'max_iterations': max_iterations}

    controller = ExperimentController(zk_host_id=1, zk_hosts='127.0.0.1:2181', host_id=1, hosts='127.0.0.1:2181')
    exp = ZkExperiment(trial_class=ZkTrial,
                       independent=independent, dependent=dependent, exp_data=exp_data, num_trials=num_trials)
    controller.run(exp)

