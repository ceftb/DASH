
from dash import DASHAgent
import time

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

        self.primitiveActions([('pickPatient', self.pick_patient), ('findRightMedication', self.find_right_medication),
                               ('logOn', self.log_on)])

    def log_on(self, call):
        print 'logs on successfully' #try to have some variables like tiredness/frustration/busy/rightbed
        return[{}]

    def find_right_medication(self, call):
        while time <= 5:
            print 'still logged in, right medication', call
            return [{}]
        if time > 5:
            print 'login to a different patient account, wrong medication', call # or login again.
            return [{}]
        else:
            print 'must log in again'
            return []


# maybe add some sort of variable to account for human error, even if logged in successfully and


if __name__ == '__main__':
    Nurse().agentLoop()
