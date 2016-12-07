from experiment import Experiment
from trial import Trial
from client import Client
import nurse01
from nurse_hub import Event

# To see the results, start a nurse_hub and run this file.


class NurseTrial(Trial):

    def __init__(self, num_nurses=20, num_patients=5, num_computers=10, num_medications=10):
        Trial.__init__(self)
        self.iteration = 0  # crashes if not defined even if not used (to fix)
        self.max_iterations = -1
        self.num_nurses = num_nurses
        self.num_patients = num_patients
        self.num_computers = num_computers
        self.num_medications = num_medications
        self.experiment_client = Client()
        self.agents = []
        self.misses = []
        self.events = []

    def initialize(self):
        # Clear out/initialize the data on the hub
        self.experiment_client.register()
        self.experiment_client.sendAction("initWorld", (self.num_computers, self.num_medications))

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

    def process_after_run(self):
        self.events = self.experiment_client.sendAction("showEvents")
        if self.events and self.events[0] == 'success':
            self.events = self.events[1]
        self.misses = len([e for e in self.events if e.patient != e.spreadsheet_loaded])

# Finally close up the server.
# I'm having trouble with this. I think I'll try a new approach where I don't kill and re-start the
# server between trials, just call a method to clear out all the intermediate data.
# t.nurse_hub.listening = False

#data = [trial() for i in range(0,5)]
#misses, events = trial(num_computers=10)
exp = Experiment(NurseTrial, num_trials=1)
exp.run()

# Print the events, with highlighting for the errors
trial = exp.trial_outputs[0]
for event in trial.events:
    print "!!" if event.patient != event.spreadsheet_loaded else "", event
print trial.misses, "misses out of", len([e for e in trial.events if e.type in ["write", "read"]]), "reads and writes"
# Find out which computers were used most heavily
computer_events = {}
computer_misses = {}
for event in trial.events:
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
for c in computer_events:
    print c, len(computer_events[c]), len(computer_misses[c]) if c in computer_misses else 0
