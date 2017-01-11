# Uses the mailReader.py agent and the Tutorial mail_hub to create an experiment with n agents
# reading and sending mail, with known email addresses, and k attacker agents sending phish.
# Based on nurse_experiment.py (probably should extract a reusable test harness from this).
from random import sample

import mailReader
import random
import numpy
import sys

from datetime import datetime

BIG_5_LOWER = 0.2
BIG_5_UPPER = 0.9
REPLY_LOWER = 0
REPLY_UPPER = 0.8
WORK_REPLY_LOWER = 0
WORK_REPLY_UPPER = 0.8
LEISURE_FWD_LOWER = 0
LEISURE_FWD_UPPER = 0.8


def trial(objective, num_workers=1, num_recipients=4, num_phishers=1,  # num_workers was 20
          phish_targets=1, max_rounds=20):  # phish_targets was 20

    #workers = [mailReader.MailReader('mailagent'+str(i+1)+'@amail.com') for i in range(0, num_workers)]
    workers = []
    for i in range(0, num_workers):
        w = mailReader.MailReader('mailagent'+str(i+1)+'@amail.com')
        workers.append(w)
        choose_gender_personality(w)
        choose_recipients(w, i, num_workers, num_recipients)
        w.traceLoop = False

    phisher = mailReader.MailReader('phisher@bmail.com')
    choose_victims(phisher, phish_targets, num_workers)
    phisher.active = True
    phisher.traceLoop = False

    # Used as an objective
    phished = False
    phish_start_time = datetime.now()
    phish_end_time = datetime.now()

    # dovetail the worker and phisher agents until they're all finished
    finished_workers = set()
    iteration = 1
    total_mail_stack = 0
    total_mails_read = 0
    total_mails_sent = 0
    last_mails_sent = 0
    last_mails_read = 0
    last_mail_stack = 0
    generations_since_change = 0

    while len(workers) > len(finished_workers) and iteration <= max_rounds and generations_since_change < 4:
        #total_mail_stack = 0  # I'm not sure why these were zeroed on each round
        #total_mails_read = 0
        #total_mails_sent = 0
        for w in workers:
            if w not in finished_workers:
                next_action = w.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again

                if (not phished) and (len(w.attachments_opened) > 0) and (w.attachments_opened.__contains__("phish.xlsx")):
                    phished = True
                    phish_end_time = iteration  # datetime.now() we should use the iteration, not real-time, here

                # Should these really be added each iteration? Each agent stores them across iterations.
                total_mail_stack += len(w.mail_stack)
                total_mails_read += w.mails_read
                total_mails_sent += w.mails_sent
                if next_action is None:
                    finished_workers.add(w)
        if phisher.active:
            next_action = phisher.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
            # total_mail_stack += len(phisher.mail_stack)
            # total_mails_read += phisher.mails_read
            # total_mails_sent += phisher.mails_sent
            if next_action is None:
                phisher.active = False
        if total_mail_stack == last_mail_stack and total_mails_read == last_mails_read and total_mails_sent == last_mails_sent:
            generations_since_change += 1
        else:
            generations_since_change = 0
        print 'round', iteration, 'total stack', total_mail_stack, 'total read', total_mails_read, \
            'total_sent', total_mails_sent, 'generations since change:', generations_since_change
        last_mail_stack = total_mail_stack
        last_mails_sent = total_mails_sent
        last_mails_read = total_mails_read
        iteration += 1

    for w in workers:
        w.disconnect()

    # Print some statistics about the run
    print 'worker, number of emails received, sent, attachments opened:'
    for w in workers:
        print w.address, w.mails_read, w.mails_sent, w.attachments_opened
    print 'phisher:', phisher.address, phisher.mails_sent, phisher.attachments_opened

    if objective == 'number':
        phish_attachments_opened = []
        for w in workers:
            worker_attachments_opened = 0
            for attachment in w.attachments_opened:
                if attachment == "phish.xlsx":
                    worker_attachments_opened += 1
            phish_attachments_opened.append(worker_attachments_opened)
        
        return numpy.mean(phish_attachments_opened)

    elif objective == 'time':
        if phished:
            return (phish_end_time-phish_start_time).total_seconds()
        else:
            return -1


def choose_recipients(agent, worker_i, num_workers, num_recipients):
    # reset recipients
    del agent.work_colleagues[:]
    del agent.leisure_colleagues[:]
    recipients = sample([i for i in range(0, num_workers) if i != worker_i], num_recipients)
    mode_options = ['leisure', 'work']

    stack = []
    for i in range(0, num_recipients):
        mode = random.choice(mode_options)
        mail = {'to': 'mailagent' + str(recipients[i] + 1) + '@amail.com', 'subject': 'test',
                'mode': mode,
                'body': 'this is a test message ' + str(i+1),
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
    victims = sample(range(0, num_workers), num_victims)
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


def choose_gender_personality(worker):
    genders = ['Male', 'Female']
    worker.gender = random.choice(genders)
    worker.extraversion = random.uniform(BIG_5_LOWER, BIG_5_UPPER)
    worker.agreeableness = random.uniform(BIG_5_LOWER, BIG_5_UPPER)
    worker.conscientiousness = random.uniform(BIG_5_LOWER, BIG_5_UPPER)
    worker.emotional_stability = random.uniform(BIG_5_LOWER, BIG_5_UPPER)
    worker.openness = random.uniform(BIG_5_LOWER, BIG_5_UPPER)
    worker.leisure_forward_probability = random.uniform(LEISURE_FWD_LOWER, LEISURE_FWD_UPPER)
    worker.work_reply_probability = random.uniform(WORK_REPLY_LOWER, WORK_REPLY_UPPER)


def run_trials(num_trials, objective, num_workers=50, num_recipients=4,  # num_workers was 100, num_recipients was 4
               num_phishers=1, phish_targets=15, max_rounds=20):  # phish_targets was 20
    output = []
    for _ in range(num_trials):
        trial_output = trial(objective, num_workers, num_recipients,
                             num_phishers, phish_targets, max_rounds)
        if trial_output == -1:
            continue # no phish has occured -> ignore
        output.append(trial_output)

    if len(output) == 0:
        return None

    return [numpy.mean(output), numpy.median(output), numpy.var(output)]

# Run it once
# trial()
num_trials = 1  # was 3
max_num_rounds = 10
print run_trials(num_trials, 'number', max_rounds=max_num_rounds)
print str(num_trials) + " trials run, max_rounds = " + str(max_num_rounds)
