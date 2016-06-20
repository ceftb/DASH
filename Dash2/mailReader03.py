from dash import DASHAgent
from System2 import isVar
import random


class MailReader(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)

        self.readAgent("""
goalWeight doWork 1

goalRequirements doWork
flightToBuy(flight)
buyFlight(flight)
sleep(1)
forget([flightToBuy(x),buyFlight(x),sleep(x)])

goalRequirements doWork
  sendMail()
  readMail(newmail)
  processMail(newmail)
  sleep(1)
  forget([sendMail(),readMail(x),sleep(x)])  # a built-in that removes matching elements from memory

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens
                       """)
        self.primitiveActions([('readMail', self.read_mail), ('sendMail', self.send_mail), ('processMail', self.process_mail)])

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0
        self.flights_to_buy = [] 
        
    def flight_to_buy(self, call):
        var = call[1]
        if not isVar(var):
            return[]
        result = [{var: flight} for flight in self.flights_to_buy]
        return result
        
    def buy_flight(self, call):
        if flight_to_buy == 'success':
            print 'buys flight tickets'
            return [{}]
        else:
            return[]
    

    def read_mail(self, call):
        mail_var = call[1]
        [status, data] = self.sendAction("getMail")
        print 'response to getMail is', status, data
        if status == "success":
            print "read mail success with", data
            return [{mail_var: data}]
        else:
            return []

    def send_mail(self, call):
        print 'send mail call', call
        [status, data] = self.sendAction("sendMail",
                                         [{'to': 'mailagent@amail.com', 'subject': 'test',
                                           'body': 'this is test message ' + str(self.mailCounter)}])
        self.mailCounter += 1
        if status == "success":
            print 'send mail success with data', data
            return [{}]
        else:
            return []
            
def process_mail(self, call):
    possible_destinations = ['New York','Paris','London','Shanghai']
    print[random.choice(possible_destinations), 'Friday']
    return[random.choice(possible_destinations), 'Friday']
        
        
        
        
        # print call
        # mail = call[1]['subject']
        # if mail == "buyTickets":
        #     print 'buys plane tickets', call
        #     self.flights_to_buy.append(1)
        #     return [{}]
        # elif mail == 'cancelFlight':
        #     print 'cancels flight'
        #     return [{}]
        # else:
        #     return[]


if __name__ == "__main__":
    MailReader().agentLoop()
