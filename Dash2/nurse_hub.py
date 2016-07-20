
from world_hub import WorldHub
import random

class Event():
    def __init__(self, agent, computer, patient, medication, spreadsheet_loaded):
        self.agent = agent
        self.computer = computer
        self.patient = patient
        self.medication = medication
        self.spreadsheet_loaded = spreadsheet_loaded

    def __str__(self):
        return "Agent " + str(self.agent) + " recorded giving " + self.medication + " to " + self.patient +\
               " on computer " + str(self.computer) + " in spreadsheet for " + self.spreadsheet_loaded

class NurseHub(WorldHub):

    def __init__(self, number_of_computers=10, number_of_possible_medications=10):
        WorldHub.__init__(self)
        # Initialize the computers to all be available.
        self.number_of_computers = number_of_computers
        self.logged_on = [None for i in range(0, self.number_of_computers)]
        self.logged_out = [None for i in range(0, self.number_of_computers)]
        self.spreadsheet_loaded = [None for i in range(0, self.number_of_computers)]
        self.writeEvents = []  # list of events
        # self.possible_medications = ['_percocet', '_codeine', '_insulin', '_zithromycin']
        self.possible_medications = ['_m' + str(i) for i in range(1, number_of_possible_medications + 1)]
        self.medication_for_patient = dict()

    def find_open_computers(self, agent_id, data):
        return 'success', [i for i in range(1, self.number_of_computers+1) if self.logged_on[i-1] is None]

    def find_all_computers(self, agent_id, data):
        return 'success', range(1, self.number_of_computers + 1)

    def login(self, agent_id, data):
        print "Logging in", agent_id, "with", data
        self.logged_on[data[0]-1] = agent_id           # agent indexes the computer from 1..n, the list is indexed from 0..n-1
        return 'success'

    def logout(self, agent_id, data):
        print "Logging out", agent_id, 'with', data
        self.logged_on[data[0]-1] = None
        self.logged_out[data[0]-1] = agent_id
        return 'success'

    def load_spreadsheet(self, agent_id, (patient, computer)):
        self.spreadsheet_loaded[computer-1] = patient
        return 'success'

    def read_spreadsheet(self, agent_id, (patient, computer)):
        # Read the correct medication for the patient whose spreadsheet is loaded on the computer.
        # If there isn't yet a medication for this patient, pick one at random. If no patient
        # is loaded on the computer, fail.
        real_patient = self.spreadsheet_loaded[computer-1]
        if real_patient is None:
            return 'fail', None
        if real_patient not in self.medication_for_patient:
            self.medication_for_patient[real_patient] = random.choice(self.possible_medications)
        return 'success', self.medication_for_patient[real_patient]

    def write_spreadsheet(self, agent_id, (patient, computer, medication)):
        nh.writeEvents.append(Event(agent_id, computer, patient, medication, self.spreadsheet_loaded[computer-1]))
        return 'success'

    def print_events(self):
        print 'Event summary:'
        for event in self.writeEvents:
            print event
        print len([e for e in self.writeEvents if e.patient != e.spreadsheet_loaded]), "entries on the wrong spreadsheet"


if __name__ == "__main__":
    nh = NurseHub()
    nh.run()
    # When the hub is stopped with 'q', print out the results
    nh.print_events()

