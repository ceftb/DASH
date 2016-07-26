from dash import DASHAgent


class MailReader(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
  sendMail()
  readMail(newmail)
  processMail(newmail)
#  sleep(1)
#  forget([sendMail(),readMail(x),sleep(x)])  # a built-in that removes matching elements from memory

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens

                       """)
        self.primitiveActions([('readMail', self.read_mail), ('sendMail', self.send_mail),
                               ('processMail', self.process_mail)])
        self.register(['mailagent@amail.com'])    # Register with the running mail_hub

        #self.traceGoals = True
        self.traceUpdate = True
        self.trace_add_activation = True

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0

        # Adding spreading activation rules by code until the language for them is set

        # Reading email creates a list of emails. Add activation to each separate email.
        self.create_spread_rule('readMail', self.create_mail_nodes)

    def read_mail(self, (predicate, mail_var)):
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
        print 'process mail call is', call
        return [{}]

    # System 1 support

    # Create neighbor nodes for a node that represents a read_mail action, and so binds a list of emails
    def create_mail_nodes(self, node):
        pass

if __name__ == "__main__":
    mr = MailReader()
    mr.agentLoop()
    # Print out the known tuples and nodes at the end
    print 'known:', mr.knownDict
    print 'known false:', mr.knownFalseDict
    print 'nodes:', mr.nodes

