
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
    findRightMedication(computer)
    logOn(computer)

    """)

        self.primitiveActions([('findRightMedication', self.find_right_medication),('logOn', self.log_on)])

    def log_on(self,call):
        print 'logs on successfully' #try to have some variables like tiredness/frustration/busy/rightbed, so could be unsuccessful or cant find computer or something
        return[{}]
        #or doesn't?


    def find_right_medication(self,call):
        if logon = 'success':
            while time <= 5:
                patient_numbers = ['patient1','patient2','patient3','patient4']
                print 'still logged in, right medication for patient 1', call
                return [{}]
            if time > 5:
                print 'login to a different patient account' +  'random.choice(patient_numbers)', call # or login again.
                return [{}]
            else:
                print 'must log in again'
                return []


# maybe add some sort of variable to account for human error, even if logged in successfully 


#if _name_ == '_main_':
  #  nurse().agentLoop()
