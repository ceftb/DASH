from dash import DASHAgent
import time
import random

start_time = time.time()


class Nurse(DASHAgent):

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
        list = ('joe','harry','david','bob')
        print ('successfully looks up medication for',list[0])
        list.pop() # probably need to import something, can't figure out what
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
        return[]

    def find_computer(self, call):
        computer = call[1]
        if computer is 'still open': #is there a way to assign a probability to this?
            print ' stays on same computer successfully'
        elif computer is 'logged into someone new and they notice': #add some sort of probability here
            print 'someone else logged in, and find new computer, either log someone else out or open one'
        elif computer is 'logged into someone and do not notice':
            print 'record medication in the wrong spreadsheet' #need some way to record this in the hub
        return []

    def read_spreadsheet(self, call):
        print 'successfully logs into computer and reads the patient spreadsheet' #should this happen before find medications, but after computer

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



# maybe add some sort of variable to account for human error, even if logged in successfully


if __name__ == '__main__':
    Nurse().agentLoop()
