from Dash2.core.dash import DASHAgent
from Dash2.socsim.socsim_agent import SocsimDecisionData, SocsimMixin
from Dash2.socsim.output_event_log_utils import event_types, sort_data_and_prob_to_cumulative_array, random_pick_sorted

class TweetActionPair:
    def __init__(self, event_index, repo_id):
        self.event_index = event_index
        self.repo_id = repo_id

class TwitterDecisionData(SocsimDecisionData):

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos,
        # probabilities of event-repo pairs, popularity
        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month

        # frequency of use of associated repos:
        tweet_id_to_freq = {int(repo_id) : int(freq["f"]) for repo_id, freq in profile["all_repos"].iteritems()}
        self.all_known_tweets = []
        self.all_known_tweets.extend(tweet_id_to_freq.iterkeys())

        self.last_event_time = profile["let"]

        self.popularity = profile.pop("pop", 0)

        self.tweet_action_pairs = [TweetActionPair(ep[0], ep[1]) for ep in profile["erp"]]
        self.tweet_action_probabilities = profile["erf"]
        sum_ = sum(self.tweet_action_probabilities)
        self.tweet_action_probabilities = [float(v) / float(sum_) for v in self.tweet_action_probabilities]
        # sort:
        self.tweet_action_pairs, self.tweet_action_probabilities = sort_data_and_prob_to_cumulative_array(self.tweet_action_pairs, self.tweet_action_probabilities)

class TwitterMixin(SocsimMixin):

    def _new_empty_decision_object(self):
        return TwitterDecisionData()

    def __init__(self, **kwargs):
        SocsimMixin.__init__(self, **kwargs)

    def customAgentLoop(self):
        # If control passes to here, the decision on choosing a user has already been made.
        pair = random_pick_sorted(self.decision_data.tweet_action_pairs, self.decision_data.tweet_action_probabilities)
        selected_event = event_types[pair.event_index]
        selected_tweet = pair.repo_id

        self.hub.log_event(self.decision_data.id, selected_tweet, selected_event, None, self.hub.time)
        self.decision_data.total_activity += 1

        return False


class TwitterAgent(TwitterMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        TwitterMixin.__init__(self, **kwargs)


