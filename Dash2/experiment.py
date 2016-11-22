import numpy
from trial import Trial

# An experiment consists of a number of trials. trial.py shows how the trials can be
# customized, and phish_experiment.py gives an example of the experiment harness.


class Experiment(object):
    def __init__(self, trial_class=Trial, num_trials=3):
        self.trial_class = trial_class
        self.num_trials = num_trials
        self.trial_outputs = []

    def run(self):
        #def run_trials(num_trials, objective, num_workers=100, num_recipients=4,
        #      num_phishers=1, phish_targets=20, max_rounds=20):
        self.trial_outputs = []
        for trial_number in range(self.num_trials):
            print "Trial", trial_number
            trial = self.trial_class()
            trial.run()
            self.trial_outputs.append(trial.output())

    def process_results(self):  # After calling run(), use to process and return the results
        if self.trial_outputs:
            return [numpy.mean(self.trial_outputs), numpy.median(self.trial_outputs),
                    numpy.var(self.trial_outputs)]
        else:
            return None
