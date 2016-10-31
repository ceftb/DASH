# Uses the mailReader.py agent and the Tutorial mail_hub to create an experiment with n agents
# reading and sending mail, with known email addresses, and k attacker agents sending phish.
# Based on nurse_experiment.py (probably should extract a reusable test harness from this).

import mailReader


def trial(num_workers=100, num_phishers=1, max_rounds=20):

    workers = [mailReader.MailReader('mailagent'+str(i+1)+'@amail.com') for i in range(0, num_workers)]
    phisher = mailReader.MailReader('phisher@bmail.com')
    phisher.active = True

    # dovetail the worker and phisher agents until they're all finished
    finished_workers = set()
    for w in workers:
        w.traceLoop = False
    phisher.traceLoop = False
    round = 1
    total_mail_stack = 0
    total_mails_read = 0
    total_mails_sent = 0
    last_mails_sent = 0
    last_mails_read = 0
    last_mail_stack = 0
    generations_since_change = 0
    while len(workers) > len(finished_workers) and round <= max_rounds and generations_since_change < 4:
        total_mail_stack = 0
        total_mails_read = 0
        total_mails_sent = 0
        for w in workers:
            if w not in finished_workers:
                next_action = w.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                total_mail_stack += len(w.mail_stack)
                total_mails_read += w.mails_read
                total_mails_sent += w.mails_sent
                if next_action is None:
                    finished_workers.add(w)
        if phisher.active:
            next_action = phisher.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
            if next_action is None:
                phisher.active = False
        if total_mail_stack == last_mail_stack and total_mails_read == last_mails_read and total_mails_sent == last_mails_sent:
            generations_since_change += 1
        else:
            generations_since_change = 0
        print 'round', round, 'total stack', total_mail_stack, 'total read', total_mails_read, \
            'total_sent', total_mails_sent, 'generations since change:', generations_since_change
        last_mail_stack = total_mail_stack
        last_mails_sent = total_mails_sent
        last_mails_read = total_mails_read
        round += 1

    # Print some statistics about the run
    print 'worker, number of emails received, sent, clicked links:'
    for w in workers:
        print w.address, w.mails_read, w.mails_sent, w.urls_clicked
    print 'phisher:', phisher.address, phisher.mails_sent, phisher.urls_clicked


# Run it once
trial()
