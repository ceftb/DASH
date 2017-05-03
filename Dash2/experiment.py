import numbers
import numpy
from trial import Trial
from parameter import Range

# An experiment consists of a varying condition and for each condition a number of trials.
# trial.py shows how the trials can be customized, and phish_experiment.py gives an example of the experiment harness.


class Experiment(object):
    def __init__(self, trial_class=Trial, independent=None, dependent=None, exp_data={}, num_trials=3):
        self.goal = ""  # The goal is a declarative representation of the aim of the experiment.
                        # It is used where possible to automate experiment setup and some amount of validation.
        self.trial_class = trial_class
        self.exp_data = exp_data
        self.num_trials = num_trials
        self.trial_outputs = {}  # A dict with the independent variable as key
        self.independent = independent
        self.dependent = dependent

    # Runs a set of trials for each value of the independent variable, keeping all other values constant,
    # and returning the set of trial outputs.
    # run_data may be a function of the independent variable or a constant.
    def run(self, run_data={}):
        self.trial_outputs = {}
        # Build up trial data from experiment data and run data
        trial_data_for_all_values = self.exp_data.copy()
        for key in run_data:
            trial_data_for_all_values[key] = run_data[key]
        # Append different data for the independent variable in each iteration
        independent_vals = [None]
        # The representation for independent variables isn't fixed yet. For now, a two-element list with
        # the name of the variable and a range object.
        if self.independent is not None and isinstance(self.independent[1], Range):
            independent_vals = range(self.independent[1].min, self.independent[1].max, self.independent[1].step)
            print 'expanded range to', independent_vals
        for independent_val in independent_vals:
            trial_data = trial_data_for_all_values.copy()
            if self.independent is not None:
                trial_data[self.independent[0]] = independent_val
            self.trial_outputs[independent_val] = []
            for trial_number in range(self.num_trials):
                print "Trial", trial_number, "with", None if self.independent is None else self.independent[0], "=", \
                    independent_val
                trial = self.trial_class(data=trial_data)
                trial.run()
                self.trial_outputs[independent_val].append(trial.output())
        return self.trial_outputs

    def process_results(self):  # After calling run(), use to process and return the results
        # If the results are a dictionary, assume the key is the independent variable and process the outcomes
        # for each one
        if self.trial_outputs and isinstance(self.trial_outputs, dict):
            result = dict()
            for key in self.trial_outputs:
                result[key] = process_list_results(self.trial_outputs[key])
            return result
        return process_list_results(self.trial_outputs)


def process_list_results(list_results):
    # If each result is a list, zip them and attempt simple statistics on them
    if list_results and all([isinstance(x, (list, tuple)) for x in list_results]):
        print 'iterating simple statistics on', list_results
        return [simple_statistics([trial[i] for trial in list_results])
                for i in xrange(len(list_results[0]))]
    elif list_results and all([isinstance(x, numbers.Number) for x in list_results]):
        return simple_statistics(list_results)
    else:
        return list_results


def simple_statistics(numlist):
    print 'running simple statistics on', numlist
    if all([isinstance(x, numbers.Number) for x in numlist]):
        return [numpy.mean(numlist), numpy.median(numlist), numpy.var(numlist)]

