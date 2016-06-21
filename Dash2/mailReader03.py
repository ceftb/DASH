from dash import DASHAgent
from system2 import isVar
import random


class MailReader(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.register(['flightagent@amail.com'])    # Register with the running mail_hub

        self.readAgent("""
goalWeight doWork 1

goalRequirements doWork
  flightToBuy(flight)
  buyFlight(flight)
  sleep(1)
  forget([flightToBuy(x),buyFlight(x),sleep(x)])

goalRequirements doWork
  readMail(newmail)
  processMail(newmail)
  sleep(1)
  forget([readMail(x),processMail(x),sleep(x),flightToBuy(x)])  # a built-in that removes matching elements from memory

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens
                       """)
        self.primitiveActions([('readMail', self.read_mail), ('processMail', self.process_mail),
                               ('flightToBuy', self.flight_to_buy), ('buyFlight', self.buy_flight)])

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0
        self.flights_to_buy = []
        
    def flight_to_buy(self, call):
        var = call[1]
        if not isVar(var):
            return[]
        result = [{var: flight} for flight in self.flights_to_buy]
        return result
        
    def buy_flight(self,call):
        flight = call[1]
        print 'buys flight tickets for', flight
        self.flights_to_buy.remove(flight)
        return [{}]

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
                                         [{'to': 'mailagent@amail.com', 'subject': 'buyTickets',
                                           'body': 'I want to go to Pittsburgh' + str(self.mailCounter)}])
        self.mailCounter += 1
        if status == "success":
            print 'send mail success with data', data
            return [{}]
        else:
            return []
            
    def process_mail(self, call):
        print call
        mail_list = call[1]
        for address in mail_list:
            for mail in mail_list[address]:
                if mail['subject'] == 'buyTickets':
                    # Body should be 'I want to go to ' + destination (which currently includes an email serial number)
                    ix = mail['body'].find('I want to go to')
                    if ix == -1:
                        return []    # Can't read the destination: fail
                    destination = mail['body'][ix + 15]
                    print['buy tickets', destination, 'Friday'], call
                    self.flights_to_buy.append([destination,'Friday'])
                elif mail['subject'] == 'cancelFlight':
                    print 'cancels flight'
                else:
                    print 'unknown request:', mail['subject']
        return [{}]


if __name__ == "__main__":
    MailReader().agentLoop(7)
