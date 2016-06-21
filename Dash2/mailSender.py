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
  forget([sendMail(x),chooseTrip(x),sleep(x)])

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens
                       """)
        self.primitiveActions([('sendMail', self.send_mail), ('chooseTrip', self.choose_trip)])
        self.mailCounter = 0

    def send_mail(self, call):
        print 'send mail call', call
        [status, data] = self.sendAction("sendMail",
                                         [{'to': 'flightagent@amail.com', 'subject': 'buyTickets',
                                           'body': 'I want to go to ' + call[1] + str(self.mailCounter)}])
        self.mailCounter += 1
        if status == "success":
            print 'send mail success with data', data
            return [{}]
        else:
            return []

    # Bind call variable to destination
    def choose_trip(self, call):
        possible_destinations = ['New York','Paris','London','Shanghai']
        return [{call[1]: random.choice(possible_destinations)}]


    # def receive_mail(self, call):
    #     mail_var = call[1]
    #     [status, data] = self.sendAction("getMail")
    #     print 'response to getMail is', status, data
    #     if status == "success":
    #         print "read mail success with", data
    #         return [{mail_var: data}]
    #     else:
    #         return []
    #
    # def get_flight(self, call):
    #     flight = call[1]
    #         print 'buys flight tickets for', trip
    #         self.flights_to_buy.remove(trip)
    #         return [{}]
    #
    # def process_mail(self, call):
    #         print call
    #         mail_list = call[1]
    #         for address in mail_list:
    #             for mail in mail_list[address]:
    #                 if mail['subject'] == 'buyTickets':
    #                     possible_destinations = ['New York','Paris','London','Shanghai']
    #                     print['buy tickets', random.choice(possible_destinations), 'Friday'], call
    #                     self.flights_to_buy.append([random.choice(possible_destinations),'Friday'])
    #                 elif mail['subject'] == 'cancelFlights':
    #                     print 'cancels flight'
    #                 else:
    #                     print 'unknown request:', mail['subject']
    #         return [{}]



if __name__ == "__main__":
    MailSender().agentLoop(3)