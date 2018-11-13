import random
from Dash2.core.dash import DASHAgent
from Dash2.socsim.socsim_agent import SocsimDecisionData, SocsimMixin
from Dash2.socsim.event_types import twitter_events, twitter_events_list
from Dash2.socsim.output_event_log_utils import sort_data_and_prob_to_cumulative_array, random_pick_sorted


class TwitterDecisionData(SocsimDecisionData):

    platform_events_map = twitter_events

    def initialize_using_user_profile(self, profile, hub):
        SocsimDecisionData.initialize_using_user_profile(self, profile, hub)


class TwitterMixin(SocsimMixin):

    def __init__(self, **kwargs):
        SocsimMixin.__init__(self, **kwargs)

    def _new_empty_decision_object(self):
        return TwitterDecisionData()

    def customAgentLoop(self):
        pair = random_pick_sorted(self.decision_data.event_res_pairs, self.decision_data.event_res_pairs_prob)
        selected_event = twitter_events_list[pair.event_index]
        selected_res = pair.res_id

        # additional_attributes
        if selected_event == "tweet":
            parent_id = selected_res
            root_id = selected_res
        else:
            parent_id = 2000000 + random.randint(1, 1000)  # TBD need to fix
            root_id = parent_id

        parent_id = self.hub._try_to_convert_resource_id_to_original_id(parent_id)
        root_id = self.hub._try_to_convert_resource_id_to_original_id(root_id)

        additional_attributes = {"parentID": parent_id, "rootID": root_id}

        self.hub.log_event(self.decision_data.id, selected_res, selected_event, self.hub.time,
                           additional_attributes=additional_attributes)

        return False


class TwitterAgent(TwitterMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        TwitterMixin.__init__(self, **kwargs)


