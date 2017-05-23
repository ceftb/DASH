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
        print 'hardness is', h
        if h >= 0:  # a negative value turns this off so we can test other things
            self.agents[0].sendAction('set_service_hardness',
                                      [['weak', 1 + h, h/6, 0.33], ['average', 5+h, h/4, 0.67], ['strong', 8+h, h/3, 1.0]])

    def agent_should_stop(self, agent):
        return False  # Stop when max_iterations reached, which is tested separately in should_stop

    def process_after_run(self):
        pa = self.agents[0]
        reuses = pa.sendAction('send_reuses')
        print 'reuses:', reuses
        resets = pa.call_measure('proportion_of_resets')
        print 'cog burden is', pass_sim.levenshtein_set_cost(pa.known_passwords), 'for', len(pa.known_passwords), \
              'passwords. Threshold is', pa.cognitive_threshold, \
              'proportion of resets is', resets
        self.results = len(pa.known_passwords), pass_sim.expected_number_of_sites(reuses), resets  #, reuses

    def output(self):
        return self.results


def run_one(arguments):
    #e = Experiment(PasswordTrial, num_trials=2, independent=['hardness', [0, 7]])  # Range(0, 2)])  # typically 0,14 but shortened for testing
    # Setting up one trial to test the Magi integration
    e = Experiment(PasswordTrial, num_trials=1, independent=['hardness', [0]])  # Range(0, 2)])  # typically 0,14 but shortened for testing
    run_results = e.run(run_data={'max_iterations': 100})  # typically max_iterations is 100, but lowered for testing
    print run_results
    print 'processing'
    processed_run_results = e.process_results()
    print 'processed:', processed_run_results
    print 'args were', arguments
    return e, run_results, processed_run_results


# can be called from the command line with e.g. the number of agents per trial.
if __name__ == "__main__":
    exp, results, processed_results = run_one(sys.argv)
