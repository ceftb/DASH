from dash import DASHAgent


class MailReader(DASHAgent):

    def __init__(self, address):
        DASHAgent.__init__(self)

        self.traceLoad = True
        self.traceGoals = True
        self.readAgent("""

goalWeight doWork 1

goalRequirements doWork
  sendMailFromStack
  readMail(newmail)
  processMail(newmail)
#  sleep(1)
#  forget([sendMail(),readMail(x),sleep(x)])  # a built-in that removes matching elements from memory

# This line can replace the first line in the doWork clause above, but commenting it there messes up the reader
#   sendMail(_self, _test, 'this is a test message', 'http://click.here')


# Send mail if there is any, otherwise succeed without doing anything
goalRequirements sendMailFromStack
  haveMailInStack(mail)
  sendMail(mail)

goalRequirements sendMailFromStack
  succeed

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens

                       """)
        self.primitiveActions([('click', self.click_link_in_mail)])

        self.address = address
        self.register([address])    # Register with the running mail_hub

        # Stack of emails to send. This way it is easy enough to task the agent with a set of emails, even dynamically.
        # Setting up with an initial mail to test. Should be the same behavior as with fixed email in the goal.
        self.mail_stack = [{'to': self.address, 'subject': 'test', 'body': 'this is a test message',
                            'url': 'http://click.here'}]

        # Using this as a counter in the email that gets sent
        self.mailCounter = 0

        # This is a list of the urls that are clicked
        self.urls_clicked = []

        # Adding spreading activation rules by code until the language for them is set

        # Threshold at which actions suggested by system 1 are chosen. At 0.3 this scenario uses only goal-directed
        # actions. At 0.2 the agent clicks a link in the email once, then carries on with the goal.
        # At 0.1 it clicks it twice.
        self.system1_threshold = 0.3

        # Reading email creates a list of emails. Add activation to each separate email node in system 1.
        self.create_neighbor_rule('readMail', self.create_mail_nodes)

    # primitive actions

    # If there is mail in the stack, return the first object
    def have_mail_in_stack(self, (predicate, mail_var)):
        if self.mail_stack:
            return [{mail_var: self.mail_stack.pop(0)}]
        else:
            return []

    def read_mail(self, (predicate, mail_var)):
        [status, data] = self.sendAction("getMail")
        if status == "success":
            return [{mail_var: data}]
        else:
            return []

    # Adding a 'url' to the mail message so that we can record clicks. The message can be any dictionary object,
    # although the mail_hub looks for a 'to' field to route it.
    def send_mail(self, goal):
        if len(goal) > 2:  # There are some arguments, 'to', 'subject', 'body' and 'url' that define the email message
            (send_mail, to, subject, body, url) = goal
            result = self.sendAction("sendMail",
                                     [{'to': self.address if to == '_self' else to[1:], 'subject': subject[1:],
                                      'body': body[1:] + str(self.mailCounter), 'url': url[1:]}])
        else:  # Just one argument, assumed to be an email message in dictionary form as expected by the hub
            result = self.sendAction("sendMail", goal[1])

        self.mailCounter += 1
        if result is not None and result[0] == "success":
            return [{}]
        else:
            return []

    def process_mail(self, (predicate, mail)):
        #print 'processing', mail
        return [{}]

    # This one isn't called through system 2 reasoning, but by system 1
    def click_link_in_mail(self, (predicate, mail)):
        #print 'clicked link in', mail
        if 'url' in mail:
            self.urls_clicked.append(mail['url'])
        return [{}]

    def succeed(self, goal):
        return [{}]

    # System 1 support

    # Create neighbor nodes for a node that represents a read_mail action, and binds a list of emails
    # For each email that has a link (right now just for each email), suggest an action to click on it
    def create_mail_nodes(self, node):
        for mail in node.fact[1]:
            node.add_neighbor(self.fact_to_node(['mail', mail]))
            # Turning off the urge to click a link right now for testing
            #node.add_neighbor(self.fact_to_node(['action', 'click', mail]))


if __name__ == "__main__":
    mr = MailReader('mailagent1@amail.com')
    mr.agentLoop()
    # Print out the system 1 nodes at the end
    print 'nodes:'
    for node in mr.nodes:
        print node

