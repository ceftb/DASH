
from dash import DASHAgent
import random


class Nurse(DASHAgent):

    def __init__(self, patients=['_joe', '_harry', '_david', '_bob']):
        DASHAgent.__init__(self)

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
    pickPatient(patient)
    findMedications(patient, medications)
    deliverMedications(patient, medications)
    logDelivery(patient, medications)
    forget([pickPatient(x), findMedications(x, y), deliverMedications(x, y), logDelivery(x, y), alreadyLoggedOn(c), logIn(c), logOut(c), findComputer(c), readSpreadsheet(p, c, m), writeSpreadsheet(p, c, m)])

goalRequirements findMedications(patient, medications)
    findComputer(computer)
    loadSpreadsheet(patient, computer)
    readSpreadsheet(patient, computer, medications)

goalRequirements logDelivery(patient, medications)
    findComputer(computer)
    loadSpreadsheet(patient, computer)
    writeSpreadsheet(patient, computer, medications)
    # logOut(computer)   # Skip logging out to see what happens

goalRequirements findComputer(computer)
    alreadyLoggedOn(computer)

goalRequirements findComputer(computer)
    logIn(computer)

transient doWork

    """)

        self.primitiveActions([('pickPatient', self.pick_patient), ('deliverMedications', self.deliver_medications),
                               ('loadSpreadsheet', self.load_spreadsheet),
                               ('readSpreadsheet', self.read_spreadsheet), ('writeSpreadsheet', self.write_spreadsheet),
                               ('alreadyLoggedOn', self.already_logged_on), ('logIn', self.log_in),
                               ('logOut', self.log_out)])
        # self.traceAction = True  # uncomment to see more about the internal actions chosen by the agent
        self.register()

        self.patient_list = patients
        self.computer = None    # computer the agent believes it's logged into

    def pick_patient(self, (goal, patient_variable)):
        if self.patient_list:
            patient = self.patient_list.pop()  # probably need to import something, can't figure out what
            print 'starting to work on', patient
            return [{patient_variable: patient}]
        else:
            print "No more patients!"
            return []

    def deliver_medications(self, (goal, patient, medication)):
        print 'delivers', medication, 'to patient', patient
        return [{}]

    def load_spreadsheet(self, (predicate, patient, computer)):
        self.sendAction("loadSpreadsheet", [patient, computer])
        return [{}]

    def read_spreadsheet(self, (predicate, patient, computer, medications_variable)):
        print 'reading the patient spreadsheet for', patient, 'on', computer
        [status, medication] = self.sendAction("readSpreadsheet", [patient, computer])   # returns the medication for the patient
        if status == 'success':
            return [{medications_variable: medication}]
        else:
            return []

    def write_spreadsheet(self, (predicate, patient, computer, medication)):
        print 'opening spreadsheet and writing patient info:', medication, patient, 'on', computer
        result = self.sendAction("writeSpreadsheet", [patient, computer, medication])
        if result == 'success':
            return [{}]
        else:  # somehow failed to write via the hub
            return []

    def log_out(self, (logout, computer)):
        print 'logout of computer', computer
        self.sendAction('logout', [computer])
        self.computer = None
        return[{}]     # call[1] was a constant, there is nothing to bind here

    def already_logged_on(self, (goal, computer_var)):
        if self.computer is None:
            return []
        else:
            return [{computer_var: self.computer}]

    def log_in(self, (login, computer_variable)):
        open_computers = self.sendAction("findOpenComputers")
        if open_computers[0] == 'success' and open_computers[1] != []:
            # ok, we have some computers, pick one at random
            self.computer = random.choice(open_computers[1])
            open_computer = True
        else:  # No open computers. Pick one at random which will log someone else off
            all_computers = self.sendAction("findAllComputers")
            if all_computers[0] == 'success' and all_computers[1] != []:
                open_computer = False
                self.computer = random.choice(all_computers[1])
            else:  # can't find any computers on the hub!
                return []
        print 'login to', 'open' if open else 'occupied', 'computer:', self.computer
        self.sendAction("login", [self.computer])
        return[{computer_variable: self.computer}]


# maybe add some sort of variable to account for human error, even if logged in successfully 

if __name__ == '__main__':
    Nurse().agentLoop()
