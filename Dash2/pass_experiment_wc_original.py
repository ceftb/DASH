"""
3/15/17 - created, based on phish_experiment_class. Allows iterating on, e.g. password constraints and measuring
aggregate security for the pass_sim.py agent. pass_sim_hub.py should be running.
"""

from experiment import Experiment
from parameter import Range
import trial
import sys
import pass_sim_wc_original


class PasswordTrial(trial.Trial):
    def __init__(self, data={}, max_iterations=None):
        self.results = None  # process_after_run() stores the results here, picked up by output()
        trial.Trial.__init__(self, data=data, max_iterations=max_iterations)

    # need to set up the self.agents list for iteration.
    # Just run one at a time, or there may appear to be more password sharing than is warranted.
    def initialize(self):
        self.agents = [pass_sim_wc_original.PasswordAgent()]
        # Set up hardnesses for the current run
        h = self.hardness
        print 'hardness is', h
        if h >= 0:  # a negative value turns this off so we can test other things
            self.agents[0].sendAction('set_service_hardness',
                                      [['weak', 1 + h, 0, 0.33], ['average', 5+h, 0, 0.67], ['strong', 8+h, 0, 1.0]])

    def agent_should_stop(self, agent):
        return False  # Stop when max_iterations reached, which is tested separately in should_stop

    def process_after_run(self):
        pa = self.agents[0]
        #reuses = pa.sendAction('send_reuses')
        #print 'reuses:', reuses
        #resets = pa.call_measure('proportion_of_resets')
        #print 'cog burden is', pass_sim_wc_original.levenshtein_set_cost(pa.known_passwords), 'for', len(pa.known_passwords), \
        #      'passwords. Threshold is', pa.cognitive_threshold, \
        #      'proportion of resets is', resets
        self.results = len(pa.known_passwords), self.security_measure(pa)  # , pass_sim_wc_original.expected_number_of_sites(reuses), resets  #, reuses

    def brute_force_attack_risk(self, agent, service, service_dict):
        username = agent.knownUsernames[0]
        # added this part to deal with the case that there is no username/password
        # associated with the user
        if username not in service_dict[service].user_name_passwords:
            return 0.0
        password_for_service = service_dict[service].user_name_passwords[username]
        if float(agent.hacker_guesses_per_s * agent.hacker_attack_s) > \
                float(agent.word_complexity_dict[password_for_service]):
            return 1.0
        direct_attack_risk = float(agent.hacker_guesses_per_s * agent.hacker_attack_s) / \
            float(agent.word_complexity_dict[password_for_service])
        return direct_attack_risk

    def stolen_password_risk(self, agent, service):
        if service not in agent.service_written_pw_dict:
            return 0.0
        else:
            return agent.stolen_password_risk

    def prob_safe_direct_attack(self, agent, s, service_dict):
        return (1.0 - self.stolen_password_risk(agent, s)) * \
            (1.0 - self.brute_force_attack_risk(agent, s, service_dict))

    def prob_safe_indirect_attack(self, agent, service, service_dict):
        prob_safe_indirect_attack = 1.0
        for s in service_dict:
            if s != service:
                prob_safe_indirect_attack *= self.prob_safe_specific_indirect_attack(agent, service, s, service_dict)

        return prob_safe_indirect_attack

    def prob_safe_specific_indirect_attack(self, agent, service, s, service_dict):
        username = agent.knownUsernames[0]
        # print "service dict:"
        # print service_dict[s]
        # print "service dict @ username_passwords"
        # print service_dict[s].user_name_passwords

        # added this part to deal with the case that there is no username/password
        # associated with the user
        if username not in service_dict[service].user_name_passwords or \
                username not in service_dict[s].user_name_passwords:
            return 1.0
        elif service_dict[service].user_name_passwords[username] == \
                service_dict[s].user_name_passwords[username]:
            return agent.reuse_attack_risk * self.prob_safe_direct_attack(agent, s, service_dict)
        else:
            return 1.0

    def prob_safe(self, agent, service, service_dict):
        return self.prob_safe_direct_attack(agent, service, service_dict) * \
            self.prob_safe_indirect_attack(agent, service, service_dict)

    def output(self):
        return self.results

    def security_measure(self, agent):
        service_dict = agent.sendAction('send_service_dict')
        m = 0.0
        for service in service_dict:
            m += self.prob_safe(agent, service, service_dict)
        m /= float(len(service_dict))
        return m

def run_one(arguments):
    e = Experiment(PasswordTrial, num_trials=100, independent=['hardness', Range(0, 9)])  # Range(0, 2)])  # typically 0,14 but shortened for testing
    run_results = e.run(run_data={'max_iterations': 300})  # typically max_iterations is 100, but lowered for testing
    print" run_results"
    print run_results
    print 'processing'
    processed_run_results = e.process_results()
    print 'processed:', processed_run_results
    return e, run_results, processed_run_results


# can be called from the command line with e.g. the number of agents per trial.
if __name__ == "__main__":
    exp, results, processed_results = run_one(sys.argv)
