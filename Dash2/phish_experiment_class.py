# Runs the phishing experiment using the Experiment and Trial classes.

from experiment import Experiment
from trial import Trial
import mailReader
import random
import numpy
import subprocess
import sys


class PhishTrial(Trial):

    def __init__(self, num_workers=100, num_recipients=4, num_phishers=1, phish_targets=20, max_iterations=20, data={}):
        self.max_iterations = max_iterations
        self.num_workers = num_workers
        self.num_recipients = num_recipients
        self.num_phishers = num_phishers
        self.phish_targets = phish_targets
        self.workers = []
        self.phisher = None
        self.phished = False
        self.phish_start_time = 0
        self.phish_end_time = 0

        self.objective = 'number'

        self.iteration = 0

        self.big_5_range = [0.2, 0.9]
        # self.reply_range = {'work': [0, 0.8], 'leisure': [0, 0.8]}  # Note these is currently no separate reply in mailReader
        self.forward_range = {'leisure': [0, 0.8], 'work': [0, 0.8]}
        self.p_recognize_phish = 0.5  # this default is overridden in the trial

        self.total_mail_stack = 0
        self.total_mails_read = 0
        self.total_mails_sent = 0
        self.last_mails_sent = 0
        self.last_mails_read = 0
        self.last_mail_stack = 0
        self.generations_since_change = 0

        Trial.__init__(self, data=data)  # Call the trial initialization here so data will override the other defaults

    def initialize(self):
        print 'initializing with', self.num_workers, 'workers'
        self.workers = []
        for i in range(0, self.num_workers):
            w = mailReader.MailReader('mailagent'+str(i+1)+'@amail.com')
            w.choose_random_gender_personality(self.big_5_range)
            self.workers.append(w)
            for mode in ['leisure', 'work']:
                w.forward_probability[mode] = random.uniform(self.forward_range[mode][0], self.forward_range[mode][1])
            choose_recipients(w, i, self.num_workers, self.num_recipients, attachment='budget.xlsx')
            w.probability_recognize_phish = self.p_recognize_phish
            w.active = True

        self.phisher = mailReader.MailReader('phisher@bmail.com')
        choose_recipients(self.phisher, -1, self.num_workers, self.phish_targets, attachment='phish.xlsx')
        self.phisher.active = True
        self.phisher.print_sent_mail = True

        self.agents = self.workers + [self.phisher]

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


def choose_recipients(agent, worker_i, num_workers, num_recipients, attachment=None, modes=['work', 'leisure'],
                      domain='amail.com'):
    # reset recipients
    for mode in modes:
        del agent.colleagues[mode][:]

    recipients = random.sample([str(i + 1) for i in range(0, num_workers) if i != worker_i], num_recipients)
    agent.mail_stack = []
    for recipient in recipients:
        mode = random.choice(modes)
        mail = {'to': 'mailagent' + recipient + '@' + domain,
                'subject': 'test', 'mode': mode, 'body': 'this is a test message',
                'attachment': attachment}
        agent.colleagues[mode].append('mailagent' + recipient + '@' + domain)
        agent.mail_stack.append(mail)


# Getting slow-down I don't understand when I write this within the same process, so trying to call as
# a subprocess and see if that helps. Because of that, the guts of this aren't encapsulated in the
# experiment object as I'd like.

# In the scenario from the slides, seek to optimize the number of phish_targets given 50 workers and
# a probability of one hit of 0.8 (defined as phisher stealth level). So iterate through phish_targets
# to find the closest to 0.8 as the performance metric.

# As a counterpoint, random sampling of the probability space of parameters (e.g. probabilities of recognizing
# phish, opening attachment and phisher stealth) to show the variety of values for number of phish. Unfortunately
# this is itself an average over many trials which is expensive. I should find a single-trial measure for this part.

def run_subprocess(trials=100, num_phish_candidates=[5, 10, 15, 20, 25]):
    all_data = {}  # for testing
    total = {}
    ave = {}
    for pt in num_phish_candidates:
        all_data[pt] = []
        total[pt] = 0
        ave[pt] = 0
        call = ["python", "phish_experiment_class.py", "run", str(pt)]
        for trial in xrange(0, trials):  # Try creating a new experiment each time to avoid bloat - doesn't work
            print 'iteration', (trial + 1)
            try:
                process = subprocess.Popen(call, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            except BaseException as e:
                print 'unable to run python subprocess:', e
                continue
            #proc.stdin.write('run_one()\n\n\n')
            line = process.stdout.readline()
            while line != "":
                print "sub", pt, trial, ":", line
                if line.startswith("Final"):
                    data = line.split(" ")
                    all_data[pt].append(data)
                    print "data is", data
                    if float(data[1]) != 0:
                        total[pt] += 1
                        ave[pt] += float(data[1])
                line = process.stdout.readline()
            print process.communicate()
            #print 'all data for', pt, 'is', all_data[pt]
            ave[pt] /= trials
    for pt in num_phish_candidates:
        print pt, '-', total[pt], 'of', trials, 'ave', ave[pt]


def run_one(phish_targets):
    e = Experiment(PhishTrial, num_trials=1)
    e.run(run_data={'max_iterations': 10,  # The phishing attachment is opened in iteration 9 in the current setup
                    'objective': 'number',
                    'num_workers': 50, 'num_recipients': 4,
                    # variables on the trial object that are passed to the agents
                    'phish_targets': phish_targets, 'p_recognize_phish': 0.8, 'p_open_attachment': 0.3})
    r = e.process_results()
    print "Final", r[0]


if __name__ == "__main__":
    print 'argv is', sys.argv
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_one(int(sys.argv[2]))

