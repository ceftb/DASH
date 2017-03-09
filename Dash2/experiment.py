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
        if self.trial_outputs:
            return [numpy.mean(self.trial_outputs), numpy.median(self.trial_outputs),
                    numpy.var(self.trial_outputs)]
        else:
            return None
