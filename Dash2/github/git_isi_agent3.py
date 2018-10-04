from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
from Dash2.socsim.distributed_event_log_utils import event_types, sort_data_and_prob_to_cumulative_array, random_pick_sorted

class EventRepoPair:
    def __init__(self, event_index, repo_id):
        self.event_index = event_index
        self.repo_id = repo_id

# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class ISI3DecisionData(GitUserDecisionData):

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos,
        # probabilities of event-repo pairs, popularity
        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month

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

        self.is_new_id = False

        # statistics:
        if "n_users" not in hub.aggregated_statistic:
            def count_repos(var_data, aggregated_statistic, isFinalUpdate=False):
                if not isFinalUpdate:
                    var_data["val"] += 1
            hub.aggregated_statistic["n_users"] = {"val": 0, "func": count_repos}
        else:
            hub.aggregated_statistic["n_users"]["func"](hub.aggregated_statistic["n_users"], hub.aggregated_statistic)

        if "n_new_users" not in hub.aggregated_statistic:
            def count_repos(var_data, aggregated_statistic, isFinalUpdate=False, number_of_repos = None, event_rate = None):
                if isFinalUpdate:
                    #total_number_of_users = aggregated_statistic["n_users"]["val"]
                    print "number of new users", var_data["val"]
                else:
                    if event_rate <= 1:
                        var_data["val"] += 1
            hub.aggregated_statistic["n_new_users"] = {"val": 0, "func": count_repos}
        else:
            hub.aggregated_statistic["n_new_users"]["func"](hub.aggregated_statistic["n_new_users"],
                                                            hub.aggregated_statistic, False, len(self.all_known_repos),
                                                            self.event_rate)

        if "p_new_users" not in hub.aggregated_statistic:
            def count_repos(var_data, aggregated_statistic, isFinalUpdate=False):
                if isFinalUpdate:
                    total_number_of_users = aggregated_statistic["n_users"]["val"]
                    total_number_of_new_users = aggregated_statistic["n_new_users"]["val"]
                    var_data["val"] = float(total_number_of_new_users) / float (total_number_of_users)
                    print "percent of new users", var_data["val"]
            hub.aggregated_statistic["p_new_users"] = {"val": 0, "func": count_repos}


class ISI3Mixin(GitUserMixin):

    def _new_empty_decision_object(self):
        return ISI3DecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def customAgentLoop(self):
        # If control passes to here, the decision on choosing a user has already been made.
        if not self.decision_data.is_new_id and self.decision_data.event_rate <= 1:
            self.decision_data.is_new_id = True
            self.decision_data.id += 10000000

        pair = random_pick_sorted(self.decision_data.event_repo_pairs, self.decision_data.event_repo_probabilities)
        selected_event = event_types[pair.event_index]
        selected_repo = pair.repo_id

        if pair.event_index == 14: #selected_event == "CreateEvent/new":
            selected_event = "CreateEvent"
        self.hub.log_event(self.decision_data.id, selected_repo, selected_event, None, self.hub.time)
        self.decision_data.total_activity += 1

        return False

class ISI3GitUserAgent(ISI3Mixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)

