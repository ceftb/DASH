from Dash2.core.dash import DASHAgent
from Dash2.socsim.socsim_agent import SocsimDecisionData, SocsimMixin
#from Dash2.socsim.output_event_log_utils import event_types, sort_data_and_prob_to_cumulative_array, random_pick_sorted
from Dash2.socsim.event_types import reddit_events, reddit_events_list

class PostActionPair:
    def __init__(self, event_index, repo_id):
        self.event_index = event_index
        self.repo_id = repo_id

class RedditDecisionData(SocsimDecisionData):

    def initialize_using_user_profile(self, profile, hub):
        self.id = profile


class RedditMixin(SocsimMixin):

    def __init__(self, **kwargs):
        SocsimMixin.__init__(self, **kwargs)

    def _new_empty_decision_object(self):
        return RedditDecisionData()

    def customAgentLoop(self):
        agent_id = self.decision_data.id
        agent_event_rate = self.hub.graph.nodes[agent_id]["r"]
        event_frequencies = self.hub.graph.nodes[agent_id]["ef"]
        last_event_time = self.hub.graph.nodes[agent_id]["let"]

        #pair = random_pick_sorted(self.decision_data.post_action_pairs, self.decision_data.post_action_probabilities)
        selected_event = reddit_events_list[0]
        selected_post = -1

        self.hub.log_event(self.decision_data.id, selected_post, selected_event, None, self.hub.time)

        return False


class RedditAgent(RedditMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        RedditMixin.__init__(self, **kwargs)


