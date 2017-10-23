from experiment import Experiment
from trial import Trial
from client import Client
import nurse01
from parameter import Range
from nurse_hub import Event

# To see the results, start a nurse_hub and run this file.


class NurseTrial(Trial):

    def __init__(self, data):
        Trial.__init__(self, data=data)
        self.iteration = 0  # crashes if not defined even if not used (to fix)
        self.max_iterations = -1
        self.experiment_client = Client()
        self.agents = []
        self.misses = []
        self.events = []
        self.computer_events = {}
        self.computer_misses = {}
        self.tick = 1

    def initialize(self):
        # Clear out/initialize the data on the hub
        self.experiment_client.register()
        self.experiment_client.sendAction("initWorld", (self.num_computers, self.num_medications, self.timeout))

        # Set up the agents. Each of n nurses is given a different list of k patients
        self.agents = [nurse01.Nurse(ident=n,
                                     patients=["_p_" + str(n) + "_" + str(p) for p in range(1, self.num_patients + 1)])
                       for n in range(0, self.num_nurses)]
        for agent in self.agents:
            agent.active = True

    def process_after_agent_action(self, agent, action):
        if action is None:
            print 'agent', agent, 'found no action, stopping'
            agent.active = False

    def agent_should_stop(self, agent):
        return not agent.active

    # After each step with every agent, cause the hub to go one 'tick', which is used to apply timeouts
    def process_after_iteration(self):
        self.experiment_client.sendAction("tick")
        #print "sent tick", self.tick
        self.tick += 1

    def process_after_run(self):
        self.events = self.experiment_client.sendAction("showEvents")
        if self.events and self.events[0] == 'success':
            self.events = self.events[1]
        #for event in self.events:
        #    print "!!" if event.patient != event.spreadsheet_loaded else "", event
        self.misses = len([e for e in self.events if e.patient != e.spreadsheet_loaded])
        print self.misses, "misses out of", len([e for e in self.events if e.type in ["write", "read"]]), "reads and writes"
        # Find out which computers were used most heavily
        for event in self.events:
            if event.computer in self.computer_events:
                self.computer_events[event.computer].append(event)
            else:
                self.computer_events[event.computer] = [event]
            if event.patient != event.spreadsheet_loaded:
                if event.computer in self.computer_misses:
                    self.computer_misses[event.computer].append(event)
                else:
                    self.computer_misses[event.computer] = [event]
        print 'computer, number of uses, number of misses'
        for ce in self.computer_events:
            print ce, len(self.computer_events[ce]), len(self.computer_misses[ce]) if ce in self.computer_misses else 0

    # Return a list of events matching the type name
    def events_of_type(self, type_name):
        return [e for e in self.events if e.type == type_name]


# This spits out the results as the number of computers varies, creating a couple of hundred agents in the process.
def test_num_computers():
    exp = Experiment(NurseTrial,
                     exp_data={'num_nurses': 10, 'num_patients': 5, 'num_medications': 10, 'timeout': 0},  # was 20
                     independent=['num_computers', Range(5, 11, 5)],  # Range gets expanded with python range(), was 21
                     measure=lambda nt: (sum([len(nt.computer_misses[ce]) if ce in nt.computer_misses else 0
                                              for ce in nt.computer_events]),
                                         nt.misses),
                     num_trials=1)
    outputs = exp.run()
    #outputs = [[(t.timeout, t.num_computers, t.misses, t.iteration, len(t.events_of_type("login"))) for t in r]
    #          for r in runs]
    print "Experiment data:", exp.exp_data
    print "Number of computers, Number of misses, Number of iterations, Number of logins"
    for independent_val in sorted(outputs):
        print independent_val, ":", outputs[independent_val]
    print 'exp results:', exp.process_results()
    return outputs


def test_timeout():
    exp = Experiment(NurseTrial,
                     exp_data={'num_nurses': 20, 'num_patients': 5, 'num_medications': 10, 'num_computers': 20},
                     num_trials=8)
    #runs = [exp.run(run_data={'timeout': 65}) for t in range(0, 8)]  # looks like I wanted timeout to vary, coming back to that
    #outputs = [[(trial.timeout, trial.misses, trial.iteration,
    #             len(trial.events_of_type("login")), len(trial.events_of_type("autologout")))
    #            for trial in run]
    #           for run in runs]
    outputs = exp.run(run_data={'timeout': 65})
    print outputs
    #return runs

#timeout_runs = test_timeout()

nc_runs = test_num_computers()
