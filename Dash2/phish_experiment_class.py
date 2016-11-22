# Runs the phishing experiment using the Experiment and Trial classes.

from experiment import Experiment
from trial import Trial
import mailReader
import random
import numpy


class PhishTrial(Trial):

    def __init__(self, num_workers=100, num_recipients=4, num_phishers=1, phish_targets=20, max_iterations=20):
        Trial.__init__(self)
        self.iteration = 0
        self.max_iterations = max_iterations
        self.num_workers=num_workers
        self.num_recipients = num_recipients
        self.num_phishers = num_phishers
        self.phish_targets = phish_targets
        self.workers = []
        self.phisher = None
        self.phished = False
        self.phish_start_time = 0
        self.phish_end_time = 0

        self.objective = 'number'

        self.big_5_lower = 0.2
        self.big_5_upper = 0.9
        self.reply_lower = 0
        self.reply_upper = 0.8
        self.work_reply_lower = 0
        self.work_reply_upper = 0.8
        self.leisure_fwd_lower = 0
        self.leisure_fwd_upper = 0.8

        self.total_mail_stack = 0
        self.total_mails_read = 0
        self.total_mails_sent = 0
        self.last_mails_sent = 0
        self.last_mails_read = 0
        self.last_mail_stack = 0
        self.generations_since_change = 0

    def initialize(self):
        self.workers = []
        for i in range(0, self.num_workers):
            self.workers.append(mailReader.MailReader('mailagent'+str(i+1)+'@amail.com'))
            self.choose_gender_personality(self.workers[i])
            choose_recipients(self.workers[i], i, self.num_workers, self.num_recipients)
            self.workers[i].active = True

        self.phisher = mailReader.MailReader('phisher@bmail.com')
        choose_victims(self.phisher, self.phish_targets, self.num_workers)
        self.phisher.active = True

        self.agents = self.workers + [self.phisher]

    def choose_gender_personality(self, worker):
        genders = ['Male', 'Female']
        worker.gender = random.choice(genders)
        worker.extraversion = self.big_5_random()
        worker.agreeableness = self.big_5_random()
        worker.conscientiousness = self.big_5_random()
        worker.emotional_stability = self.big_5_random()
        worker.openness = self.big_5_random()
        worker.leisure_forward_probability = random.uniform(self.leisure_fwd_lower, self.leisure_fwd_upper)
        worker.work_reply_probability = random.uniform(self.work_reply_lower, self.work_reply_upper)

    def big_5_random(self):
        return random.uniform(self.big_5_lower, self.big_5_upper)

    def should_stop(self):
        if Trial.should_stop(self):  # Use the default definition + quiescence
            return True
        if self.generations_since_change >= 4:
            return True
        return False

    def agent_should_stop(self, agent):
        return not agent.active

    def process_after_agent_action(self, agent, action):
        if action is None:
            agent.active = False
        if agent == self.phisher:
            return
        if (not self.phished) and agent.attachments_opened and (agent.attachments_opened.__contains__("phish.xlsx")):
            self.phished = True
            self.phish_end_time = self.iteration  # datetime.now() we should use the iteration, not real-time, here

        self.total_mail_stack += len(agent.mail_stack)
        self.total_mails_read += agent.mails_read
        self.total_mails_sent += agent.mails_sent

    def process_after_iteration(self):
        print 'Iteration', self.iteration, 'total stack', self.total_mail_stack, 'total read', self.total_mails_read,\
              'total sent', self.total_mails_sent, 'generations since change', self.generations_since_change

    def output(self):
        if self.objective == 'number':
            return numpy.mean([len([1 for attachment in worker.attachments_opened if attachment == 'phish.xlsx'])
                              for worker in self.workers])
        elif self.objective == 'time':
            if self.phished:
                return self.phish_end_time
            else:
                return -1


def choose_recipients(agent, worker_i, num_workers, num_recipients):
    # reset recipients
    del agent.work_colleagues[:]
    del agent.leisure_colleagues[:]
    recipients = random.sample([i for i in range(0, num_workers) if i != worker_i], num_recipients)
    mode_options = ['leisure', 'work']

    stack = []
    for i in range(0, num_recipients):
        mode = random.choice(mode_options)
        mail = {'to': 'mailagent' + str(recipients[i] + 1) + '@amail.com', 'subject': 'test',
                'mode': mode,
                'body': 'this is a test message',
                'attachment': 'budget.xlsx' if mode == 'work' else 'kittens.jpeg'}

        if mode == 'leisure':
            agent.leisure_colleagues.append('mailagent'+str(recipients[i]+1)+'@amail.com')
        else:
            agent.work_colleagues.append('mailagent'+str(recipients[i]+1)+'@amail.com')

        stack.append(mail)

    agent.mail_stack = stack


def choose_victims(phisher, num_victims, num_workers):
    # reset victims
    del phisher.work_colleagues[:]
    del phisher.leisure_colleagues[:]
    victims = random.sample(range(0, num_workers), num_victims)
    mode_options = ['leisure', 'work']

    stack = []
    for i in range(0, num_victims):
        mode = random.choice(mode_options)
        mail = {'to': 'mailagent' + str(victims[i] + 1) + '@amail.com', 'subject': 'test',
                'mode': mode,
                'body': 'this is a test message',
                'attachment': 'phish.xlsx'}

        if mode == 'leisure':
            phisher.leisure_colleagues.append('mailagent'+str(victims[i]+1)+'@amail.com')
        else:
            phisher.work_colleagues.append('mailagent'+str(victims[i]+1)+'@amail.com')

        stack.append(mail)

    phisher.mail_stack = stack

e = Experiment(PhishTrial)
e.run()
print e.process_results()
