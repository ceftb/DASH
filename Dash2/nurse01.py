
from dash import DASHAgent
import time
import random
#import xlwt
#import pop #don't know what needs to be imported
#from collections import deque
#use mock? yield?
#Monitor records time and value(SimPy)
import random

start_time = time.time()  #is time passing for the person standard, or specific to agents? U



class Nurse(DASHAgent):       #keeps saying its trying to connect to the world hub

    def __init__(self):
        DASHAgent.__init__(self)

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
    pickPatient(patient)
    findMedications(patient, medications)
    deliverMedications(patient, medications)
    logDelivery(patient, medications)
    forget([pickPatient(x), findMedications(x, y), deliverMedications(x, y), logDelivery(x, y), findMedications(p, m)])
    forget([findComputer(c), readSpreadsheet(p, c, m), writeSpreadsheet(p, c, m)])

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

        self.primitiveActions([('pickPatient', self.pick_patient), ('deliverMedications',
                               self.deliver_medications),
                               ('readSpreadsheet', self.read_spreadsheet), ('writeSpreadsheet', self.write_spreadsheet),
                               ('alreadyLoggedOn', self.already_logged_on), ('logIn', self.log_in)])
        self.register()

        self.patient_list = ['_joe', '_harry', '_david', '_bob']


    def output(selffilename, sheet, list1, list2, x, y):
        book = xlwt.Workbook() # attempt tp put in the excel sheet
        sh = book.add_sheet(sheet)
        #sheet1 = book.add_sheet("Sheet1")

        variables = [x, y]
        x_desc = 'patient'
        y_desc = 'medication'
        desc = [x_desc, y_desc]

        col1_name = 'patient'
        col2_name = 'medication'

        for n, v_desc, v in enumerate(zip(desc,variables)):
            sh.write(n,0, v_desc)
            sh.write(n, 1, v)

        n+=1

        sh.write(n,0, col1_name)
        sh.write(n, 1, col2_name)

        for m, e1 in enumerate(list1, n+1):
            sh.write(m,0,e1)

        for m, e2 in enumerate(list2, n+1):
            sh.write(m, 1, e2)

        book.save(filename)

        #^ from overflow. Other source: https://automatetheboringstuff.com/chapter12/

        # sheet1.write(1, 'patient', 'medication')
        # sheet1.write(2, 'patient','medication')
        # sheet1.write(3, 'patient','medication')

        # i=4
        #
        # for n in list1:
        #     i = i+1
        #     sheet1.write(i, 0, n)

    def pick_patient(self, call):
        if self.patient_list:
            patient = self.patient_list.pop() # probably need to import something, can't figure out what
            print ('successfully looks up medication for', patient)
            return [{call[1]: patient}]
        else:
            print "No more patients!"
            return []

#    def find_medications(self, call):
#        medications = ['percocet', 'codeine', 'insulin', 'zithromycin']
#        #x = random.choice(medications) - attempt to find someway to reference this later
#        print ['find list of medications', random.choice(medications)], call
#        return [{call[2]: random.choice(medications)}]

    def deliver_medications(self, call):
        print 'delivers medication to patient'
        #maybe this for time
        # if 'joe':
        #     time = 4
        # elif 'harry':
        #     time = 3
        # elif 'david':
        #     time = 2
        # elif 'bob':
        #     time = 5
        return [{}]

    # def find_computer(self, call):
    #     # computer = call[1]
    #     # if computer is 'available': #is there a way to assign a probability to this?
    #     #     print ' logs into computer successfully'
    #     # elif computer is 'unavailable':
    #     #     print 'logs in, but logs another nurse out'
    #     print 'logs in successfully into a computer' #in this case their is only 1 computer
    #     return [{call[1]: 1}]    # Just using '1' to denote the only computer we need to worry about in this version

    def read_spreadsheet(self, call):
        medications = ['_percocet', '_codeine', '_insulin', '_zithromycin']
        print 'successfully logs into computer and reads the patient spreadsheet', call
        (predicate, patient, computer, medications_variable) = call
        return [{medications_variable: random.choice(medications)}]

    def write_spreadsheet(self, call):
        (predicate, patient, computer, medications) = call
        print ['opens spreadsheet and write patient info:', medications, patient]  # in hub version, somehow have to actually record it
        return [{}]

    def already_logged_on(self, call):
        if random.randint(0,1):
            print 'already logged into computer'
            return[{call[1]: 'stays logged in'}]   #random.random() This is always true.Next one never happens
        else:
            return []

    def log_in(self, call):
        print 'login to new computer'
        open_computers = self.sendAction("findOpenComputers")
        if open_computers[0] == 'success' and open_computers[1] != []:
            # ok, we have some computers, pick one at random
            self.sendAction("login", [random.choice(open_computers[1])])
        else: # No open computers. Pick one at random which will log someone else off
            self.sendAction("login", [random.randint(1,10)])
        return[{call[1]: 'logged in to new'}]


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
