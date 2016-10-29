# Uses the mailReader.py agent and the Tutorial mail_hub to create an experiment with n agents
# reading and sending mail, with known email addresses, and k attacker agents sending phish.
# Based on nurse_experiment.py (probably should extract a reusable test harness from this).

import mailReader


def trial(num_workers=100, num_phishers=1):

    workers = [mailReader.MailReader('mailagent'+str(i+1)+'@amail.com') for i in range(0, num_workers)]

    # dovetail the worker and phisher agents until they're all finished
    finished_workers = set()
    for w in workers:
        w.traceLoop = False
    while len(workers) > len(finished_workers):
        for w in workers:
            if w not in finished_workers:
                next_action = w.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                if next_action is None:
                    finished_workers.add(w)

    # Print some statistics about the run
    print 'worker, number of emails, number of clicked links:'
    for w in workers:
        print w.address, w.mailCounter, w.urls_clicked


# Run it once
trial()
