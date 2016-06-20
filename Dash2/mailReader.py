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
  sleep(1)
  forget([sendMail(),readMail(x),sleep(x)])  # a built-in that removes matching elements from memory

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens

                       """)
        self.primitiveActions([('readMail', self.read_mail), ('sendMail', self.send_mail), ('processMail', self.process_mail)])
        self.register(['mailagent@amail.com'])    # Register with the running mail_hub

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0

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
        print 'process mail call is', call
        return [{}]

if __name__ == "__main__":
    MailReader().agentLoop()
