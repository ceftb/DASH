from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin
import random
import numpy
from distributed_event_log_utils import event_types, event_types_indexes


# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class IUDecisionData(object):

    def __init__(self, **kwargs):
        # System 1 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.nodes = set()
        self.action_nodes = set()
        # System 2 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.knownDict = dict()
        self.knowFalseDict = dict()

        # IU Github specific
        self.owned_forks = []
        self.other_repos = []
        self.other_forks = []

        # Event probabilities and book-keeping data used in primitive events copied from GitUserDecisionData
        self.owned_repos = []
        self.not_own_repos = []
        self.name_to_repo_id = []
        self.event_rate = kwargs.get("event_rate", 5)  # number of events per month
        self.id = kwargs.get("id", None)
        self.probabilities = None
        event_frequencies = kwargs.get("event_frequencies", [1] * len(event_types))
        del event_frequencies[event_types_indexes["CreateEvent"]]
        del event_frequencies[event_types_indexes["ForkEvent"]]
        f_sum = float(sum(event_frequencies))
        self.event_probabilities = [event/f_sum for event in event_frequencies] if f_sum != 0 else [1.0 / len(event_frequencies) for event in event_frequencies]

        if kwargs.get("freqs") is not None:
            self.repo_id_to_freq = kwargs.get("freqs").copy()
        else:
            self.repo_id_to_freq = {}  # {ght_id_h : frequency of use/communication} Contains all repos agent interacted with



# Not inheriting directly from GitUserAgent in case alt system 1 is desired
class IUMixin(GitUserMixin):

    p_create_user = 0.015  # The action to create a new user is taken in the controller, e.g. git_user_experiment,
                           # but the value is stored here to keep the IU level 1 values together.
    p_create_repo = 0.048
    p_fork = 0.028
    p_own_repo = 0.423
    p_own_fork = 0.074
    p_other_repo = 0.403
    p_other_fork = (1 - p_create_repo - p_fork - p_own_repo - p_own_fork - p_other_repo)
    event_types_no_create_fork = [ev for ev in event_types if ev != "CreateEvent" and ev != "ForkEvent"]

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        # If control passes to here, the decision on choosing a user has already been made.
        repo_for_action = None
        if (self.decision_data.probabilities is None or self.decision_data.all_known_repos == []):
            self.decision_data.probabilities = []
            self.decision_data.all_known_repos = []
            sum = 0.0
            for repo_id, fr in self.decision_data.repo_id_to_freq.iteritems():
                sum += fr
                self.decision_data.all_known_repos.append(repo_id)
                if repo_id not in self.decision_data.owned_repos:
                    self.decision_data.not_own_repos.append(repo_id)
            for fr in self.decision_data.repo_id_to_freq.itervalues():
                self.decision_data.probabilities.append(fr / sum)

        if self.skipS12:
            choice = random.uniform(0, 1)
            if choice < IUMixin.p_create_repo:
                self.create_event()  # Will pick a name and add it to decision_data.owned_repos
            elif choice < IUMixin.p_create_repo + IUMixin.p_fork:
                self.fork_event()  # NOT YET IMPLEMENTED in GitUserAgent. Needs to update decision_data.forked_repos
            elif len(self.decision_data.owned_repos) > 0 and choice < IUMixin.p_create_repo + IUMixin.p_fork + IUMixin.p_own_repo + IUMixin.p_own_fork: # own repos
                repo_for_action = random.choice(self.decision_data.owned_repos)
            else: # other repos
                repo_for_action = random.choice(self.decision_data.not_own_repos)

            if repo_for_action is not None:  # Otherwise, a create or fork action was already taken and total_activity was incremented
                # Pick a random event type. In later versions the probabilities will change based on the kind of repo
                # But for now uses the same probabilities as used in the original DASH model
                #selected_event = random.choice(self.event_types_no_create_fork, p=self.decision_data.event_probabilities) # random.choice() does not accept attribut p. Replaced with numpy
                selected_event = numpy.random.choice(self.event_types_no_create_fork, p=self.decision_data.event_probabilities)
                self.hub.log_event(self.decision_data.id, repo_for_action, selected_event, None, self.hub.time)
                self.decision_data.total_activity += 1
        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

    def create_event(self):
        new_repo_id = self.hub.create_repo(self.id, (""))
        self.decision_data.owned_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, new_repo_id, "CreateEvent", None, self.hub.time)

    def fork_event(self):
        repo_to_fork = random.choice(self.decision_data.not_own_repos) # parent repo
        new_repo_id = self.hub.create_repo(self.id, (repo_to_fork))
        self.decision_data.owned_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, repo_to_fork, "ForkEvent", None, self.hub.time)



class IUGitUserAgent(IUMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)

