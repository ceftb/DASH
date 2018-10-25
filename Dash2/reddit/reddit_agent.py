import random
from Dash2.core.dash import DASHAgent
from Dash2.socsim.socsim_agent import SocsimDecisionData, SocsimMixin, ResourceEventTypePair
from Dash2.socsim.output_event_log_utils import random_pick_sorted
from Dash2.socsim.event_types import reddit_events, reddit_events_list


class RedditDecisionData(SocsimDecisionData):

    platform_events_map = reddit_events

    def initialize_using_user_profile(self, profile, hub):
        SocsimDecisionData.initialize_using_user_profile(self, profile, hub)


class RedditMixin(SocsimMixin):

    def __init__(self, **kwargs):
        SocsimMixin.__init__(self, **kwargs)

    def _new_empty_decision_object(self):
        return RedditDecisionData()

    def customAgentLoop(self):
        pair = random_pick_sorted(self.decision_data.event_res_pairs, self.decision_data.event_res_pairs_prob)
        selected_event = reddit_events_list[pair.event_index]
        selected_res = pair.res_id

        # additional_attributes
        if selected_event == "post":
            parent_id = selected_res
            root_id = selected_res
        else:
            parent_id = 2000000 + random.randint(1, 1000) # TBD need to fix
            root_id = parent_id

        parent_id = self.hub._try_to_convert_resource_id_to_original_id(parent_id)
        root_id = self.hub._try_to_convert_resource_id_to_original_id(root_id)
        community = random.choice(self.hub.graph.nodes[self.decision_data.id]["cmt"].keys())

        additional_attributes = {"communityID": community, "parentID": parent_id, "rootID": root_id}

        self.hub.log_event(self.decision_data.id, selected_res, selected_event, self.hub.time,
                           additional_attributes=additional_attributes)

        return False


class RedditAgent(RedditMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        RedditMixin.__init__(self, **kwargs)


