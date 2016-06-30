
from dash import DASHAgent
import random


class Nurse(DASHAgent):

    def __init__(self):
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
    readSpreadsheet(patient, computer, medications)

goalRequirements logDelivery(patient, medications)
    findComputer(computer)
    writeSpreadsheet(patient, computer, medications)
    logOut(computer)

goalRequirements findComputer(computer)
    alreadyLoggedOn(computer)

goalRequirements findComputer(computer)
    logIn(computer)

transient doWork

    """)

        self.primitiveActions([('pickPatient', self.pick_patient), ('deliverMedications', self.deliver_medications),
                               ('readSpreadsheet', self.read_spreadsheet), ('writeSpreadsheet', self.write_spreadsheet),
                               ('alreadyLoggedOn', self.already_logged_on), ('logIn', self.log_in),
                               ('logOut', self.log_out)])
        # self.traceAction = True  # uncomment to see more about the internal actions chosen by the agent
        self.register()

        self.patient_list = ['_joe', '_harry', '_david', '_bob']
        self.computer = None    # computer the agent believes it's logged into


#    def output(selffilename, sheet, list1, list2, x, y):
#        book = xlwt.Workbook() # attempt tp put in the excel sheet
#        sh = book.add_sheet(sheet)
#        #sheet1 = book.add_sheet("Sheet1")
#
#        variables = [x, y]
#        x_desc = 'patient'
#        y_desc = 'medication'
#        desc = [x_desc, y_desc]
#
#        col1_name = 'patient'
#        col2_name = 'medication'
#
#        for n, v_desc, v in enumerate(zip(desc,variables)):
#            sh.write(n,0, v_desc)
#            sh.write(n, 1, v)
#
#        n+=1
#
#        sh.write(n,0, col1_name)
#        sh.write(n, 1, col2_name)
#
#        for m, e1 in enumerate(list1, n+1):
#            sh.write(m,0,e1)
#
#        for m, e2 in enumerate(list2, n+1):
#            sh.write(m, 1, e2)
#
#        book.save(filename)
#
#        #^ from overflow. Other source: https://automatetheboringstuff.com/chapter12/
#
#        # sheet1.write(1, 'patient', 'medication')
#        # sheet1.write(2, 'patient','medication')
#        # sheet1.write(3, 'patient','medication')
#
#        # i=4
#        #
#        # for n in list1:
#        #     i = i+1
#        #     sheet1.write(i, 0, n)

    def pick_patient(self, (goal, patient_variable)):
        if self.patient_list:
            patient = self.patient_list.pop() # probably need to import something, can't figure out what
            print 'successfully looks up medication for', patient
            return [{patient_variable: patient}]
        else:
            print "No more patients!"
            return []

#    def find_medications(self, call):
#        medications = ['percocet', 'codeine', 'insulin', 'zithromycin']
#        #x = random.choice(medications) - attempt to find someway to reference this later
#        print ['find list of medications', random.choice(medications)], call
#        return [{call[2]: random.choice(medications)}]

    def deliver_medications(self, (goal, patient, medication)):
        print 'delivers', medication, 'to patient', patient
        return [{}]

    # def find_computer(self, call):
    #     # computer = call[1]
    #     # if computer is 'available': #is there a way to assign a probability to this?
    #     #     print ' logs into computer successfully'
    #     # elif computer is 'unavailable':
    #     #     print 'logs in, but logs another nurse out'
    #     print 'logs in successfully into a computer' #in this case their is only 1 computer
    #     return [{call[1]: 1}]    # Just using '1' to denote the only computer we need to worry about in this version

    def read_spreadsheet(self, (predicate, patient, computer, medications_variable)):
        print 'reading the patient spreadsheet for', patient, 'on', computer
        result = self.sendAction("readSpreadsheet", [patient, computer])   # returns the medication for the patient
        if result is not None and result[0] == 'success':
            return [{medications_variable: result[1]}]
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


    # def log_on(self,call):
    #     print 'logs on successfully' #try to have some variables like tiredness/frustration/busy/rightbed, so could be unsuccessful or cant find computer or something
    #     return[{}]
    #     #or doesn't?
    #
    #
    # def find_right_medication(self,call):
    #     if logon = 'success':
    #         while time <= 5:
    #             patient_numbers = ['patient1','patient2','patient3','patient4']
    #             print 'still logged in, right medication for patient 1', call
    #             return [{}]
    #         if time > 5:
    #             print 'login to a different patient account' +  'random.choice(patient_numbers)', call # or login again.
    #             return [{}]
    #         else:
    #             print 'must log in again'
    #             return []

# maybe add some sort of variable to account for human error, even if logged in successfully 

if __name__ == '__main__':
    Nurse().agentLoop()
