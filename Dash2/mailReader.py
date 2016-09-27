from dash import DASHAgent


class MailReader(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)

        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
  sendMail('mailagent@amail.com', _test, 'this is a test message')
  readMail(newmail)
  processMail(newmail)
#  sleep(1)
#  forget([sendMail(),readMail(x),sleep(x)])  # a built-in that removes matching elements from memory

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens

                       """)
        self.primitiveActions([('click', self.click_link_in_mail)])
        self.register(['mailagent@amail.com'])    # Register with the running mail_hub

        # Threshold at which actions suggested by system 1 are chosen. At 0.3 this scenario uses only goal-directed
        # actions. At 0.2 the agent clicks a link in the email once, then carries on with the goal.
        # At 0.1 it clicks it twice.
        self.system1_threshold = 0.3

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0

        # Adding spreading activation rules by code until the language for them is set

        # Reading email creates a list of emails. Add activation to each separate email node in system 1.
        self.create_neighbor_rule('readMail', self.create_mail_nodes)

    # primitive actions

    def read_mail(self, (predicate, mail_var)):
        [status, data] = self.sendAction("getMail")
        if status == "success":
            return [{mail_var: data}]
        else:
            return []

    def send_mail(self, (send_mail, to, subject, body)):
        result = self.sendAction("sendMail",
                                 [{'to': to[1:], 'subject': subject[1:], 'body': body[1:] + str(self.mailCounter)}])
        self.mailCounter += 1
        if result is not None and result[0] == "success":
            return [{}]
        else:
            return []

    def process_mail(self, (predicate, mail)):
        print 'processing', mail
        return [{}]

    # This one isn't called through system 2 reasoning, but by system 1
    def click_link_in_mail(self, (predicate, mail)):
        print 'clicked link in', mail
        return [{}]

    # System 1 support

    # Create neighbor nodes for a node that represents a read_mail action, and binds a list of emails
    # For each email that has a link (right now just for each email), suggest an action to click on it
    def create_mail_nodes(self, node):
        for mail in node.fact[1]:
            node.add_neighbor(self.fact_to_node(['mail', mail]))
            node.add_neighbor(self.fact_to_node(['action', 'click', mail]))


if __name__ == "__main__":
    mr = MailReader()
    mr.agentLoop()
    # Print out the system 1 nodes at the end
    print 'nodes:'
    for node in mr.nodes:
        print node

