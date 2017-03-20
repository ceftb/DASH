"""
3/15/17 - created, based on phish_experiment_class. Allows iterating on, e.g. password constraints and measuring
aggregate security for the pass_sim.py agent. pass_sim_hub.py should be running.
"""

import experiment
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
    results = []
    for i in range(0, 14):
        hardnesses = [['weak', 1 + i, i/6, 0.33], ['average', 5+i, i/4, 0.67], ['strong', 8+i, i/3, 1.0]]
        print hardnesses
        e = experiment.Experiment(PasswordTrial, num_trials=30)
        e.run(run_data={'max_iterations': 100})
        print e.process_results()  # Prints mean, median and variance of each item in a result list


# can be called from the command line with the number of agents per trial.
if __name__ == "__main__":
    run_one(sys.argv)
