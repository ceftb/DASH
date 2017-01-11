import random
import copy
from dash import DASHAgent


class MailReader(DASHAgent):

    def __init__(self, address):
        DASHAgent.__init__(self)

        self.trace_client = False

        self.competence_with_internet = 0.5  # general level of competence e.g. Alseadoon et al. 12

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
        print 'registering', address
        self.register([address])    # Register with the running mail_hub

        # Stack of emails to send. This way it is easy enough to task the agent with a set of emails, even dynamically.
        # Setting up with an initial mail to test. Should be the same behavior as with fixed email in the goal.
        self.mail_stack = [{'to': self.address, 'forwarders': [],
                            'subject': 'test', 'body': 'this is a test message', 'attachment': 'budget.xlsx'},
                           {'to': self.address, 'forwarders': [],
                            'subject': 'test', 'body': 'this is a second test message', 'attachment': 'budget.xlsx'}]

        self.work_colleagues = []  # set of people that work-related email might be sent of forwarded to or expected to come from
        self.leisure_colleagues = []  # set of people that leisure-related email might be sent of forwarded to or expected to come from

        self.phishiness_threshold = 0.5  # messages are score from 0 to 1 and rejected as phish if they score over this threshold

        # probability that email deemed to be legitimate leisure mail will be forwarded to a friend. Shortly this
        # should be calculated based on agreeableness, extraversion and conscientiousness.
        self.leisure_forward_probability = 0.5
        self.work_forward_probability = 0.5


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

        # Record phish that are identified as such (i.e. emails from bmail.com, not amail.com addresses).
        self.phish_identified = []

    # primitive actions

    # If there is mail in the stack, return the first object
    def have_mail_in_stack(self, (predicate, mail_var)):
        if self.mail_stack:
            return [{mail_var: [self.mail_stack.pop(0)]}]  # return as a list so the generic mail sending function could send more than one message in principle
        else:
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

        # Succeed if there's no mail
        if not mail:
            return [{}]

        # Treat each message separately
        for message in mail:

            # First the agent scores the message on phishiness based on mental model and personality traits
            # (and at some point perhaps fatigue, cognitive budget etc.)
            # If the agent decides the mail is too phishy, no further action is taken. Otherwise it might
            # still forward the message or open the attachment depending on personality and expertise.
            phishiness = self.score_phishiness(message)
            if phishiness > self.phishiness_threshold:
                self.phish_identified.append(message)
                #print self.id, 'too phishy:', phishiness, message, 'ignoring all'
                #return [{}]
                continue

            # With some fixed probability the agent forwards a work email to another work colleague, including
            # the sender as a reply
            if message['mode'] == 'work' and self.work_colleagues and random.random() < self.work_forward_probability:
                new_message = copy.copy(message)
                new_message['to'] = random.choice(self.work_colleagues)
                self.mail_stack.append(new_message)
            # Leisure-related mail is forwarded with probability determined from personality and gender to a subset of the
            # agent's friend group. It keeps a 'forward' trail in the mail to avoid sending the same email to someone twice.
            # (forward trail nyi).
            elif message['mode'] == 'leisure' and self.leisure_colleagues and random.random() < self.leisure_forward_probability:
                new_message = copy.copy(message)
                new_message['to'] = random.choice(self.leisure_colleagues)
                self.mail_stack.append(new_message)

            # The probability of opening an attachment in either is related to openness, but is much higher in work-related email.
            if self.decide_to_open(message, phishiness):
                #print 'opening', message['attachment']
                self.attachments_opened.append(message['attachment'])

        return [{}]

    # For now, 1's and 0's without regard to personality or other factors.
    def score_phishiness(self, message):
        # If the mail is legit, it is never identified as phish
        if 'amail.com' in message['from']:
            return 0
        # for now, accept 1 in 2 phishing emails whatever the phishiness threshold
        elif random.random() < 0.5:
            # Return a random number above the threshold
            return self.phishiness_threshold + (1 - self.phishiness_threshold) * random.random()
        else:
            # return a random number below the threshold
            return self.phishiness_threshold * random.random()

    def decide_to_open(self, message, phishiness):
        # The stuff below was never opening anything
        return True
        # Some combination of phishiness score, agreeableness, openness
        threshold = (self.agreeableness + self.extraversion + self.openness) / 3 - phishiness
        if random.random() < threshold:
            return True
        print 'did not open: not below threshold', threshold
        return False

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

