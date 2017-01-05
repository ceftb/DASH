from experiment import Experiment
from trial import Trial
from client import Client
import nurse01
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
        self.tick = 1

    def initialize(self):
        # Clear out/initialize the data on the hub
        self.experiment_client.register()
        self.experiment_client.sendAction("initWorld", (self.num_computers, self.num_medications, self.timeout))

        # Set up the agents. Each of n nurses is given a different list of k patients
        self.agents = [nurse01.Nurse(ident=n,
                                     patients=["_p_" + str(n) + "_" + str(p)for p in range(1, self.num_patients + 1)])
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
        print "sent tick", self.tick
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
        computer_events = {}
        computer_misses = {}
        for event in self.events:
            if event.computer in computer_events:
                computer_events[event.computer].append(event)
            else:
                computer_events[event.computer] = [event]
            if event.patient != event.spreadsheet_loaded:
                if event.computer in computer_misses:
                    computer_misses[event.computer].append(event)
            else:
                computer_misses[event.computer] = [event]
        print 'computer, number of uses, number of misses'
        for ce in computer_events:
            print ce, len(computer_events[ce]), len(computer_misses[ce]) if ce in computer_misses else 0

    # Return a list of events matching the type name
    def events_of_type(self, type_name):
        return [e for e in self.events if e.type == type_name]


# This spits out the results as the number of computers varies, creating a couple of hundred agents in the process.
def test_num_computers():
    exp = Experiment(NurseTrial, exp_data={'num_nurses': 20, 'num_patients': 5, 'num_medications': 10, 'timeout': 0},
                     num_trials=1)
    runs = [exp.run(run_data={'num_computers': c}) for c in range(2, 5, 3)]
    outputs = [[(trial.timeout, trial.num_computers, trial.misses, trial.iteration, len(trial.events_of_type("login"))) for trial in e]
               for e in runs]
    print "Timeout, Number of computers, Number of misses, Number of iterations, Number of logins"
    for output in outputs:
        print output
    return runs


def test_timeout():
    exp = Experiment(NurseTrial,
                     exp_data={'num_nurses': 20, 'num_patients': 5, 'num_medications': 10, 'num_computers': 20},
                     num_trials=1)
    runs = [exp.run(run_data={'timeout': 65 }) for t in range(0, 8)]
    outputs = [[(trial.timeout, trial.misses, trial.iteration,
                 len(trial.events_of_type("login")), len(trial.events_of_type("autologout")))
                for trial in run]
               for run in runs]
    print outputs
    return runs

#timeout_runs = test_timeout()

nc_runes = test_num_computers()