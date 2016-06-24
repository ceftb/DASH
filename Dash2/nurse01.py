
from dash import DASHAgent
import time
import random
#import pop #don't know what needs to be imported
#from collections import deque
#use mock? yield?
#Monitor records time and value(SimPy)

start_time = time.time()  #is time passing for the person standard, or specific to agents? U



class Nurse(DASHAgent):       #keeps saying its trying to connect to the world hub

    def _init_(self):
        DASHAgent.__init__(self)

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
    pickPatient(patient)
    findMedications(patient, medications)
    deliverMedications(patient, medications)
    logDelivery(patient, medications)

goalRequirements findMedications(patient, medications)
    findComputer(computer)
    readSpreadsheet(patient, computer, medications)

goalRequirements logDelivery(patient, medications)
    findComputer(computer)
    writeSpreadsheet(patient, computer, medications)

goalRequirements findComputer(computer)
    alreadyLoggedOn(computer)

goalRequirements findComputer(computer)
    logIn(computer)

    """)

        self.primitiveActions([('pickPatient', self.pick_patient), ('findMedications', self.find_medications),('deliverMedications',
                               self.deliver_medications), ('logDelivery', self.log_delivery), ('findComputer', self.find_computer),
                               ('readSpreadsheet', self.read_spreadsheet), ('writeSpreadsheet', self.write_spreadsheet),
                               ('alreadyLoggedOn', self.already_logged_on), ('logIn', self.log_in)])

    def pick_patient(self,call):
        patientlist = ('joe','harry','david','bob')
        print ('successfully looks up medication for', patientlist[0])
        #patientlist.pop() # probably need to import something, can't figure out what
        return[{}] #do you still need this with pop?

    def find_medications(self, call):
        medications = ['percocet','codeine','insulin','zithromycin']
        #x = random.choice(medications) - attempt to find someway to reference this later
        print ['find list of medications', random.choice(medications)], call
        return [{call[1]: random.choice(medications)}]

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
        return[]

    def log_delivery(self, call):
        print "logs delivery of medications into computer"
        return[{}]

    def find_computer(self, call):
        # computer = call[1]
        # if computer is 'available': #is there a way to assign a probability to this?
        #     print ' logs into computer successfully'
        # elif computer is 'unavailable':
        #     print 'logs in, but logs another nurse out'
        print 'logs in successfully into a computer' #in this case their is only 1 computer
        return [{}]

    def read_spreadsheet(self, call):
        print 'successfully logs into computer and reads the patient spreadsheet'
        return [{}]

    def  write_spreadsheet(self, call):
        patient = pick_patient
        medications = deliver_medications  # somehow, actually record patient and med info
        print ['opens spreadsheet and write patient info:', (medications), (patient)]  # in hub version, somehow have to actually record it
        return []

    def already_logged_on(self, call):
        if time < 5:
            print 'already logged into computer'
            return[{}]

    def log_in(self, call):
        if time > 5:
            print'login to new computer'
            return[{}]

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
