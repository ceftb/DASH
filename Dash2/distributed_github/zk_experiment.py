import sys; sys.path.extend(['../../'])
import numpy
from Dash2.core.parameter import Range, Parameter, Uniform, TruncNorm
from zk_trial import ZkTrial


class ZkExperiment(object):
    def __init__(self, trial_class=ZkTrial, exp_id=None, hosts='127.0.0.1:2181',
                 independent=None, dependent=None, exp_data={}, num_trials=3):
        self.trial_class = trial_class
        self.independent = independent
        self.dependent = dependent
        self.exp_data = exp_data
        self.num_trials = num_trials
        self.exp_id = exp_id
        self.hosts = hosts

    # this method is taken from Experiment
    def run(self, zk, run_data={}):
        if self.exp_id is None:
            # TBD register new experiment in Zookeeper and update experiment id
            self.exp_id = 0

        zk.ensure_path("/experiments/" + str(self.exp_id) + "/status")
        zk.set("/experiments/" + str(self.exp_id) + "/status", "in progress")

        self.trial_outputs = {}
        # Build up trial data from experiment data and run data
        trial_data_for_all_values = self.exp_data.copy()
        for key in run_data:
            trial_data_for_all_values[key] = run_data[key]
        # Append different data for the independent variable in each iteration
        independent_vals = self.compute_independent_vals()
        # Dependent might be a method or a string representing a function or a member variable
        # If it's a string representing a function it's changed to the function. We don't pass this to another host.
        if isinstance(self.dependent, str):
            if hasattr(self.trial_class, self.dependent) and callable(getattr(self.trial_class, self.dependent)):
                print "Dependent is callable on the trial, so switching to the method"
                self.dependent = getattr(self.trial_class, self.dependent)
            elif not hasattr(self.trial_class, self.dependent):
                print "Dependent is not a callable method, but is a variable on the trial"
            else:
                print "Dependent is a string"
        else:
            print "dependent is not a string:", self.dependent

        for independent_val in independent_vals:
            trial_data = trial_data_for_all_values.copy()
            if self.independent is not None:
                trial_data[self.independent[0]] = independent_val
            self.trial_outputs[independent_val] = []
            for trial_number in range(self.num_trials):
                print "Trial", trial_number, "with", None if self.independent is None else self.independent[0], "=", \
                    independent_val
                trial = self.trial_class(zk=zk, hosts=self.hosts, exp_id=self.exp_id, trial_id=trial_number, data=trial_data)
                trial.run()
                trial_dependent = self.dependent(trial) if callable(self.dependent) else getattr(trial, self.dependent)
                print "Dependent", self.dependent, "evaluated to", trial_dependent
                self.trial_outputs[independent_val].append(trial_dependent)

        return self.trial_outputs

    def compute_independent_vals(self):
        independent_vals = [None]
        # The representation for independent variables isn't fixed yet. For now, a two-element list with
        # the name of the variable and a range object.
        if self.independent is not None and isinstance(self.independent[1], Range):
            #independent_vals = range(self.independent[1].min, self.independent[1].max, self.independent[1].step)
            # Need something that handles floats. Leaving the old code above in case this causes trouble
            independent_vals = numpy.arange(self.independent[1].min, self.independent[1].max, self.independent[1].step)
            print 'expanded range to', independent_vals
        elif self.independent is not None and isinstance(self.independent[1], (list, tuple)):  # allow a direct list
            independent_vals = self.independent[1]
        return independent_vals
