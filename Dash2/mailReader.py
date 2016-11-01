from dash import DASHAgent


class MailReader(DASHAgent):

    def __init__(self, address):
        DASHAgent.__init__(self)

        # Ultimately it makes sense to house Big-5 personality information and the way it might interact with
        # dual processing in a separate class to be inherited, but for this rapid prototyping I will keep it here
        # along with other potentially-relevant demographic information for now.
        # These dimensions are assumed to be on a scale from 0 to 1.
        self.extraversion = 0.5
        self.agreeableness = 0.5
        self.conscientiousness = 0.5
        self.emotional_stability = 0.5
        self.openness = 0.5

        # Other features of importance
        self.gender = 'Male'

        self.competence_with_internet = 0.5  # general level of competence e.g. Alseadoon et al. 12


        # Might be found from the balloon assessment test for example.
        self.impulsivity = 0.5

        self.readAgent("""

goalWeight doWork 1

# This runs forever. While the agent is waiting for new mail, readMail will succeed with an empty list that is then processed.
goalRequirements doWork
  sendMailFromStack(mail)
  readMail(newmail)
  processMail(newmail)
  forget([sendMailFromStack(x), haveMailInStack(x), sendMail(x), readMail(x), processMail(x), sleep(x)])
# Turned off sleep for the experiment harness, so it runs quickly.
#  sleep(1)

# This line can replace the first line in the doWork clause above, but commenting it there messes up the reader
#   sendMail(_self, _test, 'this is a test message', 'http://click.here')


# Send mail if there is any, otherwise succeed without doing anything
goalRequirements sendMailFromStack(mail)
  haveMailInStack(mail)
  sendMail(mail)

goalRequirements sendMailFromStack(mail)
  succeedM(mail)

transient doWork     # Agent will forget goal's achievement or failure as soon as it happens

                       """)
        self.primitiveActions([('click', self.click_link_in_mail)])

        self.address = address
        self.register([address])    # Register with the running mail_hub

        # Stack of emails to send. This way it is easy enough to task the agent with a set of emails, even dynamically.
        # Setting up with an initial mail to test. Should be the same behavior as with fixed email in the goal.
        self.mail_stack = [{'to': self.address, 'subject': 'test', 'body': 'this is a test message',
                            'attachment': 'budget.xlsx'},
                           {'to': self.address, 'subject': 'test', 'body': 'this is a second test message',
                            'attachment': 'budget.xlsx'}]

        self.work_colleagues = []  # set of people that work-related email might be sent of forwarded to or expected to come from
        self.leisure_colleagues = []  # set of people that leisure-related email might be sent of forwarded to or expected to come from

        # probability that email deemed to be legitimate leisure mail will be forwarded to a friend. Shortly this
        # should be calculated based on agreeableness, extraversion and conscientiousness.
        self.leisure_forward_probability = 0.5

        # Keep track of the number of emails read and sent
        self.mails_read = 0
        self.mails_sent = 0

        # This is a list of the urls that are clicked
        self.urls_clicked = []

        # And a list of the attachments that have been opened
        self.attachments_opened = []

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
            #print 'mail in stack:', self.mail_stack
            return [{mail_var: [self.mail_stack.pop(0)]}]  # return as a list so the generic mail sending function could send more than one message in principle
        else:
            #print 'no mail in stack'
            return []

    def read_mail(self, (predicate, mail_var)):
        [status, data] = self.sendAction("getMail")
        if status == "success":
            self.mails_read += len(data)
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
                                      'body': body[1:] + str(self.mails_sent), 'url': url[1:]}])
        else:  # Just one argument, assumed to be an email message in dictionary form as expected by the hub
            result = self.sendAction("sendMail", goal[1])

        self.mails_sent += 1
        if result is not None and result[0] == "success":
            return [{}]
        else:
            return []

    # At the moment all of the agent's work process for work-related email as well as response to phishing email
    # (which might present as work-related or as social/leisure) is handled in this primitive method.
    def process_mail(self, (predicate, mail)):
        #print 'processing', mail

        # First the agent decides whether the mail is phish or legitimate based on mental model and personality traits
        # (and at some point perhaps fatigue, cognitive budget etc.)
        # If the agent decides the mail is phish, no further action is taken.
        if self.decide_phish(mail):
            return [{}]

        # Work-related mail includes tags that describe what should be done with it, in order to embed an organizational
        # process in the mail. e.g., this should be forwarded and recipient should formulate a reply to the original
        # sender. I'll come up with a simple language to generate this path. Alternatively the email could just
        # include probabilities for each of the actions leading to kind of a markov mail process with the same overall
        # activity. Might be fine.

        # Leisure-related mail is forwarded with probability determined from personality and gender to a subset of the
        # agent's friend group. It keeps a 'forward' trail in the mail to avoid sending the same email to someone twice.

        # THe probabilitiy of opening an attachment in either is related to openness, but is much higher in work-related email.

        return [{}]

    def decide_phish(self, mail):
        return True

    # This one isn't called through system 2 reasoning, but by system 1
    def click_link_in_mail(self, (predicate, mail)):
        #print 'clicked link in', mail
        if 'url' in mail:
            self.urls_clicked.append(mail['url'])
        return [{}]

    def open_attachment_in_mail(self, (predicate, mail)):
        if 'attachment' in mail:
            self.attachments_opened.append(mail['attachment'])
        return [{}]

    def succeed_m(self, goal):
        #print 'calling succeed'
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
    mr.agentLoop(20)
    # Print out the system 1 nodes at the end
    print 'nodes:'
    for node in mr.nodes:
        print node

