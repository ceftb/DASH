
from world_hub import WorldHub
import random
import sys
import numbers


class Event:
    def __init__(self, agent, event_type, computer, patient, medication, spreadsheet_loaded):
        self.type = event_type  # login, logout, walk away, load spreadsheet, read spreadsheet, write to spreadsheet
        self.agent = agent
        self.computer = computer
        self.patient = patient
        self.medication = medication
        self.spreadsheet_loaded = spreadsheet_loaded

    def __str__(self):
        return "N" + str(self.agent) + " recorded " + self.medication + " to " + self.patient +\
               " on C" + str(self.computer) + " in S:" + self.spreadsheet_loaded


class NurseHub(WorldHub):

    def __init__(self, number_of_computers=10, number_of_possible_medications=10, port=None):
        WorldHub.__init__(self, port=port)
        self.init_world(None, (number_of_computers, number_of_possible_medications))

    # agent_id is a bogus argument so an agent can call this as an action on the hub and we can also
    # call it on the hub. Will fix.
    def init_world(self, agent_id, (number_of_computers, number_of_possible_medications)):
        # Initialize the computers to all be available.
        self.number_of_computers = number_of_computers
        self.logged_on = [None for i in range(0, self.number_of_computers)]
        self.logged_out = [None for i in range(0, self.number_of_computers)]
        self.present = [None for i in range(0, self.number_of_computers)]  # agent who is present at the computer.
        self.spreadsheet_loaded = [None for i in range(0, self.number_of_computers)]
        self.events = []  # list of events
        # self.possible_medications = ['_percocet', '_codeine', '_insulin', '_zithromycin']
        self.possible_medications = ['_m' + str(i) for i in range(1, number_of_possible_medications + 1)]
        self.medication_for_patient = dict()

    def find_open_computers(self, agent_id, data):
        return 'success', [i for i in range(1, self.number_of_computers+1) if self.logged_on[i-1] is None]

    def find_all_computers(self, agent_id, data):
        return 'success', range(1, self.number_of_computers + 1)

    def login(self, agent_id, data):
        print "Logging in", agent_id, "with", data
        computer = data[0]-1
        self.logged_on[computer] = agent_id           # agent indexes the computer from 1..n, the list is indexed from 0..n-1
        self.present[computer] = agent_id
        return 'success'

    # Making these atomic actions inside the hub to reduce the number of times that several agents see the same
    # 'available' computer and log into it in the next step.
    # I haven't put a thread lock on this so it still might happen.

    # This one finds a computer with no-one logged in
    def login_to_open_computer(self, agent_id, data):
        open_computers = [i for i in range(1, self.number_of_computers+1) if self.logged_on[i-1] is None]
        return self.login_to_computer_from_list(agent_id, data, 'open', open_computers)

    # This one finds a computer with no-one present, although someone might be logged in
    def login_to_unattended_computer(self, agent_id, data):
        unattended_computers = [i for i in range(1, self.number_of_computers+1) if self.present[i-1] is None]
        return self.login_to_computer_from_list(agent_id, data, 'unattended', unattended_computers)

    def login_to_computer_from_list(self, agent_id, data, tag, list_of_computers):
        print 'login req from', agent_id, 'with', tag, list_of_computers
        if list_of_computers:  # Might be empty list as computed in one of the calling methods
            target_computer = random.choice(list_of_computers)
            self.logged_on[target_computer-1] = agent_id
            self.present[target_computer-1] = agent_id
            return target_computer
        return 'fail'

    def logout(self, agent_id, data):
        print "Logging out", agent_id, 'with', data
        if isinstance(data[0], numbers.Number):
            self.logged_on[data[0]-1] = None
            self.logged_out[data[0]-1] = agent_id
            return 'success'
        else:
            return 'fail'

    # Might still be logged in, but when not present could be logged out or overwritten by another
    def walk_away(self, agent_id, data):
        print 'walking away from the computer:', agent_id, data
        if not isinstance(data, numbers.Number):
            return 'fail'
        if self.present[data-1] == agent_id:
            self.present[data-1] = None
            return 'success'
        else:
            return 'fail'

    def load_spreadsheet(self, agent_id, (patient, computer)):
        # Check no other agent is present at the computer
        if self.check_present(agent_id, computer):
            self.spreadsheet_loaded[computer-1] = patient
            return 'success'
        else:
            return 'fail'

    def read_spreadsheet(self, agent_id, (patient, computer)):
        # Read the correct medication for the patient whose spreadsheet is loaded on the computer.
        # Check the agent is at the computer (also makes the agent be present if no other agent already is).
        if not self.check_present(agent_id, computer):
            return 'computer_blocked', None, None
        # If there isn't yet a medication for this patient, pick one at random. If no patient
        # is loaded on the computer, fail.
        real_patient = self.spreadsheet_loaded[computer-1]
        if real_patient is None:
            return 'no_patient_loaded', None, None
        if real_patient not in self.medication_for_patient:
            self.medication_for_patient[real_patient] = random.choice(self.possible_medications)
        return 'success', self.medication_for_patient[real_patient], real_patient

    def write_spreadsheet(self, agent_id, (patient, computer, medication)):
        if self.check_present(agent_id, computer):
            print "Writing event", agent_id, computer, patient, medication, self.spreadsheet_loaded[computer-1]
            self.events.append(Event(agent_id, "write", computer, patient, medication, self.spreadsheet_loaded[computer-1]))
            return 'success', self.spreadsheet_loaded[computer-1]
        else:
            return 'computer_blocked', self.spreadsheet_loaded[computer-1]

    def check_present(self, agent_id, computer):
        if self.present[computer-1] == None:
            self.present[computer-1] = agent_id
        return self.present[computer-1] == agent_id

    def print_events(self):
        print len(self.events), 'events:'
        for event in self.events:
            print event
        print len([e for e in self.events if e.patient != e.spreadsheet_loaded]), \
            "entries on the wrong spreadsheet out of", len(self.events)

    # This is not a method the agent should use, but the experimental harness can call it to examine
    # the data after a run
    def show_events(self, agent_id, data):
        return 'success', self.events


if __name__ == "__main__":
    # Take port as a command-line argument
    if len(sys.argv) > 1:
        nh = NurseHub(port=int(sys.argv[1]))
    else:
        nh = NurseHub()
    nh.run()
    # When the hub is stopped with 'q', print out the results
    nh.print_events()

