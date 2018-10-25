from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
import random
from Dash2.socsim.output_event_log_utils import event_types, event_types_indexes, random_pick_notsorted, random_pick_sorted

# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class IUDecisionData(GitUserDecisionData):

    event_types_no_create_fork = [ev for ev in event_types if ev != "CreateEvent" and ev != "ForkEvent"]

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos, repo_id_to_freq,
        # probabilities, event_probabilities, embedding probabilities
        GitUserDecisionData.initialize_using_user_profile(self, profile, hub)

        # intialize own_repos, not_own_repos
        own_repos = profile.pop("own", None)  # e.g. [234, 2344, 2312] # an array of integer repo ids
        self.own_repos = own_repos if own_repos is not None else []

        self.not_own_repos = []
        for repo_id in self.repo_id_to_freq.iterkeys():
            if repo_id not in self.own_repos:
                self.not_own_repos.append(repo_id)

        # remove Fork and Create events from event probabilities
        del self.event_probabilities[event_types_indexes["CreateEvent"]]
        del self.event_probabilities[event_types_indexes["ForkEvent"]]
        sum_ = sum(self.event_probabilities)
        if sum_ != 0:
            self.event_probabilities = [ k / sum_ for k in self.event_probabilities]
        else:
            self.event_probabilities = [1.0 / len(IUDecisionData.event_types_no_create_fork) for _ in IUDecisionData.event_types_no_create_fork]

        self.popularity = profile.pop("pop", 0)

        # init array with repos ids and their popularity
        # only users with own repos selected in hub.userIdAndPopularity
        if hub.userIdAndPopularity == None:
            hub.userIdAndPopularity = {"ids": [], "probability": []}

        if len(own_repos) >= 1:
            hub.userIdAndPopularity["ids"].append(self.id)
            hub.userIdAndPopularity["probability"].append(self.popularity) # it will be normalized later in the agent loop

# Not inheriting directly from GitUserAgent in case alt system 1 is desired
class IUMixin(GitUserMixin):

    p_create_user = 0.015  # The action to create a new user is taken in the controller, e.g. git_user_experiment,
                           # but the value is stored here to keep the IU level 1 values together.
    p_watch_repo = 0.081   # Only appears in the later version
    p_create_repo = 0.042  # was 0.048 in the earlier version
    p_fork = 0.029 # was  0.028 in the earlier version
    p_own_repo = 0.505 # was 0.423 in the earlier version
    p_own_fork = 0.074
    p_other_repo = 0.403
    p_other_fork = (1 - p_create_repo - p_fork - p_own_repo - p_own_fork - p_other_repo)


    def _new_empty_decision_object(self):
        return IUDecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    # An earlier version, circa June 19 18
    def customAgentLoop(self):
        # If control passes to here, the decision on choosing a user has already been made.
        repo_for_action = None
        choice = random.uniform(0, 1)
        if choice < IUMixin.p_create_repo:
            self.create_event()  # Will pick a name and add it to decision_data.own_repos
        elif choice < IUMixin.p_create_repo + IUMixin.p_fork:
            self.fork_event()  # NOT YET IMPLEMENTED in GitUserAgent. Needs to update decision_data.forked_repos
        elif len(self.decision_data.own_repos) > 0 and choice < IUMixin.p_create_repo + IUMixin.p_fork + IUMixin.p_own_repo + IUMixin.p_own_fork: # own repos
            repo_for_action = random.choice(self.decision_data.own_repos)
        else:  # other repos
            repo_for_action = random.choice(self.decision_data.not_own_repos)

        if repo_for_action is not None:  # Otherwise, a create or fork action was already taken and total_activity was incremented
            # Pick a random event type. In later versions the probabilities will change based on the kind of repo
            # But for now uses the same probabilities as used in the original DASH model
            selected_event = random_pick_notsorted(IUDecisionData.event_types_no_create_fork, self.decision_data.event_probabilities)
            self.hub.log_event(self.decision_data.id, repo_for_action, selected_event, None, self.hub.time)
            self.decision_data.total_activity += 1

    # Approximation of the detailed model June 26 18
    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        if self.skipS12:
            if self.hub.userIdAndPopularity["probability"][0] >= 1:
                self.normzlize_probability()
            repo_for_action = None
            choice = random.uniform(0, 1)
            if choice < IUMixin.p_watch_repo:
                self.watch_repo()
            elif choice < IUMixin.p_watch_repo + IUMixin.p_create_repo:
                self.create_event()
            elif choice < IUMixin.p_watch_repo + IUMixin.p_create_repo + IUMixin.p_fork:
                self.fork_event()
            elif len(self.decision_data.own_repos) > 0 and choice < IUMixin.p_watch_repo + IUMixin.p_create_repo + IUMixin.p_fork + IUMixin.p_own_repo:
                repo_for_action = random.choice(self.decision_data.own_repos)  # Should be preferential attachment
            else:  # other repos
                if len(self.decision_data.not_own_repos) > 0:
                    repo_for_action = random.choice(self.decision_data.not_own_repos)  # Should be random walk geometric dist mean 2

            if repo_for_action is not None:  # Otherwise, a create or fork action was already taken and total_activity was incremented
                # Pick a random event type. In later versions the probabilities will change based on the kind of repo
                # But for now uses the same probabilities as used in the original DASH model
                selected_event = random_pick_notsorted(IUDecisionData.event_types_no_create_fork, self.decision_data.event_probabilities)
                self.hub.log_event(self.decision_data.id, repo_for_action, selected_event, None, self.hub.time)
                self.decision_data.total_activity += 1

        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

    def normzlize_probability(self):
        sum_ = sum(self.hub.userIdAndPopularity["probability"])
        self.hub.userIdAndPopularity["probability"] = [float(k) / sum_ for k in self.hub.userIdAndPopularity["probability"]]

    def watch_repo(self):
        # IU: Pick among all owners by preferential attachment (expensive!)
        owner_id = random_pick_sorted(self.hub.userIdAndPopularity["ids"], self.hub.userIdAndPopularity["probability"])
        owner = self.hub.agents_decision_data[owner_id] # 'owner' is a decision_data object
        repo_id = random.choice(owner.own_repos)
        self.decision_data.not_own_repos.append(repo_id)
        self.hub.log_event(self.decision_data.id, repo_id, "WatchEvent", None, self.hub.time)

    def create_event(self):
        new_repo_id = self.hub._create_repo(self.id, (""))
        self.decision_data.own_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, new_repo_id, "CreateEvent", None, self.hub.time)

    def fork_event(self):
        if len(self.decision_data.not_own_repos) > 0:
            repo_to_fork = random.choice(self.decision_data.not_own_repos) # parent repo
        else:
            owner_id = random_pick_sorted(self.hub.userIdAndPopularity["ids"], self.hub.userIdAndPopularity["probability"])
            owner = self.hub.agents_decision_data[owner_id]  # 'owner' is a decision_data object
            repo_to_fork = random.choice(owner.own_repos)

        new_repo_id = self.hub._create_repo(self.id, (""))
        self.decision_data.own_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, repo_to_fork, "ForkEvent", None, self.hub.time)


class IUGitUserAgent(IUMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)
