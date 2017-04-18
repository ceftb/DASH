"""
3/15/17 - created, based on phish_experiment_class. Allows iterating on, e.g. password constraints and measuring
aggregate security for the pass_sim.py agent. pass_sim_hub.py should be running.
"""

from experiment import Experiment
from parameter import Range
import trial
import sys
import pass_sim


class PasswordTrial(trial.Trial):
    def __init__(self, data={}, max_iterations=None):
        self.results = None  # process_after_run() stores the results here, picked up by output()
        trial.Trial.__init__(self, data=data, max_iterations=max_iterations)

    # need to set up the self.agents list for iteration.
    # Just run one at a time, or there may appear to be more password sharing than is warranted.
    def initialize(self):
        self.agents = [pass_sim.PasswordAgent()]
        # Set up hardnesses for the current run
        h = self.hardness
        if h >= 0:  # a negative value turns this off so we can test other things
            self.hardnesses = [['weak', 1 + h, h/6, 0.33], ['average', 5+h, h/4, 0.67], ['strong', 8+h, h/3, 1.0]]
            print 'hardnesses are', self.hardnesses
            self.agents[0].sendAction('set_service_hardness', self.hardnesses)

    def agent_should_stop(self, agent):
        return False  # Stop when max_iterations reached, which is tested separately in should_stop

    def process_after_run(self):
        pa = self.agents[0]
        reuses = pa.sendAction('send_reuses')
        print 'reuses:', reuses
        print 'cog burden is', pass_sim.levenshtein_set_cost(pa.known_passwords), 'for', len(pa.known_passwords), \
              'passwords. Threshold is', pa.cognitiveThreshold
        self.results = len(pa.known_passwords), pass_sim.expected_number_of_sites(reuses)  #, reuses

    def output(self):
        return self.results


def run_one(arguments):
    e = Experiment(PasswordTrial, independent=['hardness', Range(0, 2)])  # typically 0,14 but shortened for testing
    results = e.run(run_data={'max_iterations': 10})  # typically max_iterations is 100, but lowered for testing
    #for i in range(0, 14):
    #    hardnesses = [['weak', 1 + i, i/6, 0.33], ['average', 5+i, i/4, 0.67], ['strong', 8+i, i/3, 1.0]]
    #    print hardnesses
    #    #e = experiment.Experiment(PasswordTrial, num_trials=100)
    #    #e.run(run_data={'max_iterations': 100, 'hardnesses': hardnesses})
    #    results.append([i] + e.process_results())  # mean, median and variance of each item in a result list
    print results
    return results


# can be called from the command line with the number of agents per trial.
if __name__ == "__main__":
    run_one(sys.argv)
