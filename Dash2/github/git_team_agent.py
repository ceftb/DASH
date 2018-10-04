from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
from Dash2.socsim.distributed_event_log_utils import event_types, sort_data_and_prob_to_cumulative_array, random_pick_sorted

class EventRepoPair:
    def __init__(self, event_index, repo_id):
        self.event_index = event_index
        self.repo_id = repo_id

# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class GitTeamDecisionData(GitUserDecisionData):

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos,
        # probabilities of event-repo pairs, popularity
        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month

        # frequency of user activity within a team:
        user_id_to_freq = {int(user_id): int(freq["f"]) for user_id, freq in profile["team"].iteritems()}

        # frequency of use of associated repos:
        repo_id_to_freq = {int(repo_id) : int(freq["f"]) for repo_id, freq in profile["all_repos"].iteritems()}
        self.all_known_repos = []
        self.all_known_repos.extend(repo_id_to_freq.iterkeys())

        #f_sum = float(sum(self.repo_id_to_freq.itervalues()))
        #self.probabilities = [repo_fr / f_sum for repo_fr in self.repo_id_to_freq.itervalues()]
        self.last_event_time = profile["let"]

        # intialize own_repos, not_own_repos
        own_repos = profile.pop("own", None)  # e.g. [234, 2344, 2312] # an array of integer repo ids
        self.own_repos = own_repos if own_repos is not None else []
        self.not_own_repos = []
        for repo_id in repo_id_to_freq.iterkeys():
            if hub.repo_id_counter < repo_id:
                hub.repo_id_counter = repo_id
            if repo_id not in self.own_repos:
                self.not_own_repos.append(repo_id)

        self.popularity = profile.pop("pop", 0)

        self.event_repo_pairs = [ EventRepoPair(ep[0], ep[1]) for ep in profile["erp"]]
        self.event_repo_probabilities = profile["erf"]
        sum_ = sum(self.event_repo_probabilities)
        self.event_repo_probabilities = [float(v) / float(sum_) for v in self.event_repo_probabilities]
        # sort:
        self.event_repo_pairs, self.event_repo_probabilities = sort_data_and_prob_to_cumulative_array(self.event_repo_pairs, self.event_repo_probabilities)

class GitTeamAgentMixin(GitUserMixin):

    def _new_empty_decision_object(self):
        return GitTeamDecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def customAgentLoop(self):
        # If control passes to here, the decision on choosing a user has already been made.
        pair = random_pick_sorted(self.decision_data.event_repo_pairs, self.decision_data.event_repo_probabilities)
        selected_event = event_types[pair.event_index]
        selected_repo = pair.repo_id

        if pair.event_index == 14: #selected_event == "CreateEvent/new":
            selected_event = "CreateEvent"
        # select user id
        user_id = random_pick_sorted(self.decision_data.user_id_to_freq.keys(), self.decision_data.user_id_to_freq.imtems())
        self.hub.log_event(user_id, selected_repo, selected_event, None, self.hub.time)
        self.decision_data.total_activity += 1

        return False


class ISI2GitUserAgent(GitTeamAgentMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitTeamAgentMixin.__init__(self, **kwargs)


