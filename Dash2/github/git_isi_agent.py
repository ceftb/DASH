from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
import random
import numpy
from distributed_event_log_utils import event_types, event_types_indexes


# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class ISIDecisionData(GitUserDecisionData):

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos, repo_id_to_freq,
        # probabilities, event_probabilities, embedding probabilities
        GitUserDecisionData.initialize_using_user_profile(self, profile, hub)

        # intialize own_repos, not_own_repos
        own_repos = profile.pop("own", None)  # e.g. [234, 2344, 2312] # an array of integer repo ids
        self.owned_repos = own_repos if own_repos is not None else []

        self.not_own_repos = []
        for repo_id in self.repo_id_to_freq.iterkeys():
            if repo_id not in self.owned_repos:
                self.not_own_repos.append(repo_id)


# Not inheriting directly from GitUserAgent in case alt system 1 is desired
class ISIMixin(GitUserMixin):

    def _new_empty_decision_object(self):
        return ISIDecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        # If control passes to here, the decision on choosing a user has already been made.
        if self.skipS12:
            repo_for_action = None
            # Pick a random event type.
            selected_event = numpy.random.choice(event_types, p=self.decision_data.event_probabilities)
            if selected_event == "CreateEvent":
                self.create_event()
            elif selected_event == "ForkEvent":
                self.fork_event()
            else:
                self.hub.log_event(self.decision_data.id, repo_for_action, selected_event, None, self.hub.time)
                self.decision_data.total_activity += 1
        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

    def create_event(self):
        new_repo_id = self.hub._create_repo(self.id, (""))
        # TBD:
        self.decision_data.owned_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, new_repo_id, "CreateEvent", None, self.hub.time)

    def fork_event(self):
        repo_to_fork = random.choice(self.decision_data.not_own_repos) # parent repo
        new_repo_id = self.hub._create_repo(self.id, (repo_to_fork))
        # TBD:
        self.decision_data.owned_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, repo_to_fork, "ForkEvent", None, self.hub.time)



class ISIGitUserAgent(ISIMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)

