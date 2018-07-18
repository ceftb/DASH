from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
from distributed_event_log_utils import event_types, event_types_indexes, sort_data_and_prob_to_cumulative_array, \
    random_pick_notsorted, coin_types
from user_repo_graph_utils import IdDictionaryStream

class EventRepoPair:
    def __init__(self, event_index, repo_id):
        self.event_index = event_index
        self.repo_id = repo_id

# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class ISI2DecisionData(GitUserDecisionData):

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


class ISI2Mixin(GitUserMixin):

    def _new_empty_decision_object(self):
        return ISI2DecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        # If control passes to here, the decision on choosing a user has already been made.
        if self.skipS12:
            if len(self.hub.prices) != 0:
                new_weight_sum = self.update_weights(self.hub.time, self.decision_data.event_repo_pairs, self.decision_data.event_repo_probabilities)
            pair = random_pick_notsorted(self.decision_data.event_repo_pairs, self.decision_data.event_repo_probabilities, max_val=new_weight_sum)
            selected_event = event_types[pair.event_index]
            selected_repo = pair.repo_id

            if pair.event_index == 14: #selected_event == "CreateEvent/new":
                selected_event = "CreateEvent"
            self.hub.log_event(self.decision_data.id, selected_repo, selected_event, None, self.hub.time)
            self.decision_data.total_activity += 1
        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

    def update_weights(self, time, event_repo_pairs, event_repo_probabilities):
        event_repo_pairs_with_coins = self.find_event_repo_pair(event_repo_pairs)
        for event, repo, index in event_repo_pairs_with_coins:
            event_repo_probabilities[index] = self.compute_new_probability(time, event_repo_probabilities[index], event, coin_types[repo - IdDictionaryStream.MAGIC_NUMBER - 1])
        if len(event_repo_pairs_with_coins) > 0:
            new_sum = sum(event_repo_probabilities)
            return new_sum
        else:
            return 1.0

    def compute_new_probability(self, time, past_probability, event_type, coin_type):
        time_in_days = int(time / (86400))
        current_price = self.hub.prices[coin_type][time_in_days][0]
        past_price = self.hub.prices[coin_type][time_in_days - 3][0]
        alpha = self.hub.price_regression[event_type][coin_type]["alpha"]
        intercept = self.hub.price_regression[event_type][coin_type]["intercept"]
        multiplier = (alpha * current_price + intercept) / (alpha * past_price + intercept)
        new_probability = past_probability * multiplier
        return new_probability

    def find_event_repo_pair(self, event_repo_pairs):
        result = []
        index = 0
        for pair in event_repo_pairs:
            event = event_types[pair.event_index]
            repo = pair.repo_id
            if event == "WatchEvent" or event == "ForkEvent":
                if repo in [IdDictionaryStream.MAGIC_NUMBER + 1, IdDictionaryStream.MAGIC_NUMBER + 2, IdDictionaryStream.MAGIC_NUMBER + 3]:
                    result.append((event, repo, index))
            index += 1
        return result

class ISI2GitUserAgent(ISI2Mixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)

