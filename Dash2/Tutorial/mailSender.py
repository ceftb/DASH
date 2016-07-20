import sys
sys.path.insert(0, '..')

from dash import DASHAgent
import random


class MailSender(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.register(['flightbuyer@amail.com'])

        self.readAgent("""
goalWeight doWork 1

goalRequirements doWork
  chooseTrip(trip)
  sendMail(trip)
  sleep(1)
  forget([sendMail(x), chooseTrip(x), sleep(x)])

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens
                       """)
        self.primitiveActions([('sendMail', self.send_mail), ('chooseTrip', self.choose_trip)])
        self.mailCounter = 0

    def send_mail(self, (goal, trip)):
        print 'send mail for trip to', trip
        status, data = self.sendAction("sendMail",
                                         [{'to': 'flightagent@amail.com', 'subject': 'buyTickets',
                                           'body': 'I want to go to ' + trip + str(self.mailCounter)}])
        self.mailCounter += 1
        if status == "success":
            print 'send mail success with data', data
            return [{}]
        else:
            return []

    # Bind call variable to destination
    def choose_trip(self, (goal, trip_variable)):
        possible_destinations = ['New York', 'Paris', 'London', 'Shanghai']
        return [{trip_variable: random.choice(possible_destinations)}]


if __name__ == "__main__":
    MailSender().agentLoop()
