import numbers
import numpy
from trial import Trial

# An experiment consists of a number of trials. trial.py shows how the trials can be
# customized, and phish_experiment.py gives an example of the experiment harness.


class Experiment(object):
    def __init__(self, trial_class=Trial, exp_data={}, num_trials=3):
        self.goal = ""  # The goal is a declarative representation of the aim of the experiment.
                        # It is used where possible to automate experiment setup and some amount of validation.
        self.trial_class = trial_class
        self.exp_data = exp_data
        self.num_trials = num_trials
        self.trial_outputs = []

    # Runs a set of trials, keeping all values constant, and returning the set of trial outputs
    def run(self, run_data={}):
        self.trial_outputs = []
        # Build up trial data from experiment data and run data
        trial_data = self.exp_data.copy()
        for key in run_data:
            trial_data[key] = run_data[key]
        for trial_number in range(self.num_trials):
            print "Trial", trial_number
            trial = self.trial_class(data=trial_data)
            trial.run()
            self.trial_outputs.append(trial.output())
        return self.trial_outputs

    def process_results(self):  # After calling run(), use to process and return the results
        # If each result is a list, zip them and attempt simple statistics on them
        if self.trial_outputs and all([isinstance(x, (list, tuple)) for x in self.trial_outputs]):
            print 'iterating simple statistics on', self.trial_outputs
            return [simple_statistics([trial[i] for trial in self.trial_outputs])
                    for i, in xrange(len(self.trial_outputs[0]))]
        elif self.trial_outputs and all([isinstance(x, numbers.Number) for x in self.trial_outputs]):
            return simple_statistics(self.trial_outputs)
        else:
            return self.trial_outputs


def simple_statistics(numlist):
    print 'running simple statistics on', numlist
    if all([isinstance(x, numbers.Number) for x in numlist]):
        return [numpy.mean(numlist), numpy.median(numlist), numpy.var(numlist)]

