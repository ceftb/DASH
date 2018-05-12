import sys;sys.path.extend(['../../'])
from Dash2.core.dash import DASHAgent
from Dash2.core.system2 import isVar
import random
import numpy


class SimpleGitUserAgent(object):
    """
    A test git user agent.
    """
    all_event_types = ["CreateEvent", "DeleteEvent", "PullRequestEvent", "IssuesEvent", "PushEvent", "WatchEvent", "ForkEvent"]

    def __init__(self, **kwargs):
        self.hub = kwargs.get("hub")
        self.id = kwargs.get("id")
        self.total_activity = 0

        # repos
        self.all_known_repos = []
        if kwargs.get("freqs") is not None:
            repo_id_to_freq = kwargs.get("freqs")
            self.all_known_repos.extend(repo_id_to_freq.iterkeys())
            sum = 0.0
            for repo_id, fr in repo_id_to_freq.iteritems():
                sum += fr
            self.repo_probabilities = []
            for fr in repo_id_to_freq.itervalues():
                self.repo_probabilities.append(fr / sum)
        else:
            self.all_known_repos = [1]
            self.repo_probabilities = [1]

        # events
        if kwargs.get("event_freqs") is not None:
            event_to_freq = kwargs.get("event_freqs")
            sum = 0.0
            for fr in event_to_freq.itervalues():
                sum += fr
            self.event_probabilities = []
            for fr in event_to_freq.itervalues():
                self.event_probabilities.append(fr / sum)
        else:
            self.event_probabilities = [0.1, 0.05, 0.3, 0.1, 0.3, 0.1, 0.05]


    def agentLoop(self, max_iterations=-1, disconnect_at_end=True, skipS12=False):
        selected_repo = numpy.random.choice(self.all_known_repos, p=self.repo_probabilities)
        selected_event = numpy.random.choice(self.all_event_types, p=self.event_probabilities)
        self.hub.event_handler(selected_repo, self.id, selected_event)
        self.total_activity += 1

    def next_event_time(self, curr_time, max_time):
        return random.uniform(curr_time + 0.1, max_time)
