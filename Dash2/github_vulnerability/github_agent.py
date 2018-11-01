import random
from Dash2.core.dash import DASHAgent
from Dash2.socsim.socsim_agent import SocsimDecisionData, SocsimMixin, ResourceEventTypePair
from Dash2.socsim.output_event_log_utils import random_pick_sorted
from Dash2.socsim.event_types import github_events, github_events_list


class GithubDecisionData(SocsimDecisionData):

    platform_events_map = github_events

    def initialize_using_user_profile(self, profile, hub):
        SocsimDecisionData.initialize_using_user_profile(self, profile, hub)


class GithubMixin(SocsimMixin):

    def __init__(self, **kwargs):
        SocsimMixin.__init__(self, **kwargs)

    def _new_empty_decision_object(self):
        return GithubDecisionData()

    def customAgentLoop(self):
        pair = random_pick_sorted(self.decision_data.event_res_pairs, self.decision_data.event_res_pairs_prob)
        selected_event = github_events_list[pair.event_index]
        selected_res = pair.res_id

        # additional_attributes
        if selected_event == "CreateEvent":
            action_subtype = random.choice(["repo", "branch", "tag"])
            additional_attributes = {"actionSubType": action_subtype}
        elif selected_event == "IssuesEvent":
            action_subtype = random.choice(["open", "close", "reopen"])
            additional_attributes = {"actionSubType": action_subtype}
        elif selected_event == "PullRequestEvent":
            status = random.choice(["True", "False"])
            action_subtype = random.choice(["open", "close", "reopen"])
            additional_attributes = {"actionSubType": action_subtype, "status": status}
        else:
            additional_attributes = None

        self.hub.log_event(self.decision_data.id, selected_res, selected_event, self.hub.time,
                           additional_attributes=additional_attributes)

        return False


class GithubAgent(GithubMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GithubMixin.__init__(self, **kwargs)


