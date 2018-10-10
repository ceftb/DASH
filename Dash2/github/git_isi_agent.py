from Dash2.core.dash import DASHAgent
from git_user_agent import GitUserMixin, GitUserDecisionData
import random
from Dash2.socsim.output_event_log_utils import event_types, random_pick_notsorted
import pickle

# Similar to GitUserDecisionData, encapsulates any agent-specific data to minimize creation of DASHAgent objects
class ISIDecisionData(GitUserDecisionData):

    def initialize_using_user_profile(self, profile, hub):

        # initialize:
        # id, event_rate, last_event_time, own_repos, not_own_repos, all_known_repos, repo_id_to_freq,
        # probabilities, event_probabilities, embedding probabilities
        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month

        event_frequencies = profile.pop("ef", None)
        f_sum = float(sum(event_frequencies))
        self.event_probabilities = [event / f_sum for event in event_frequencies]

        # for each event type embedding_probabilities keeps {"ids":[23423, 435434, 34534], "probs":[0.34, 0345, 0.42] }
        self.embedding_probabilities = {ev: None for ev in event_types}
        # frequency of use of associated repos:
        self.repo_id_to_freq = {int(repo_id) : int(freq["f"]) for repo_id, freq in profile["all_repos"].iteritems()}
        self.all_known_repos = []
        self.all_known_repos.extend(self.repo_id_to_freq.iterkeys())

        f_sum = float(sum(self.repo_id_to_freq.itervalues()))
        self.probabilities = [repo_fr / f_sum for repo_fr in self.repo_id_to_freq.itervalues()]
        self.last_event_time = profile["let"]

        # intialize own_repos, not_own_repos
        own_repos = profile.pop("own", None)  # e.g. [234, 2344, 2312] # an array of integer repo ids
        self.own_repos = own_repos if own_repos is not None else []
        self.not_own_repos = []
        for repo_id in self.repo_id_to_freq.iterkeys():
            if hub.repo_id_counter < repo_id:
                hub.repo_id_counter = repo_id
            if repo_id not in self.own_repos:
                self.not_own_repos.append(repo_id)

        self.popularity = profile.pop("pop", 0)

        if hub.graph == None:
            hub.graph = pickle.load(open(hub.graph_file_path, "rb"))
        if len(self.not_own_repos) != 0:
            sum_f = float(sum([hub.graph.nodes[k]["pop"] for k in self.not_own_repos]))
            if sum_f != 0:
                self.probability_based_on_popularity_of_known_but_not_owned_repos = [float(hub.graph.nodes[k]["pop"]) / sum_f for k in self.not_own_repos]
            else:
                ln = len(self.not_own_repos)
                self.probability_based_on_popularity_of_known_but_not_owned_repos = [float(1) / ln for k in self.not_own_repos]

        # top popular repos with popularity > 100
        if hub.topPopularRepos == None:
            hub.topPopularRepos = []
            for node in hub.graph.nodes():
                if hub.graph.nodes[node]["isU"] == 0 and hub.graph.nodes[node]["pop"] > 100:
                    hub.topPopularRepos.append(node)
            if len(hub.topPopularRepos) == 0:
                for index, node in enumerate(hub.graph.nodes()):
                    hub.topPopularRepos.append(node)
                    if index > 100:
                        break



# Not inheriting directly from GitUserAgent in case alt system 1 is desired
class ISIMixin(GitUserMixin):

    def _new_empty_decision_object(self):
        return ISIDecisionData()

    def __init__(self, **kwargs):
        GitUserMixin.__init__(self, **kwargs)

    def customAgentLoop(self):
        # If control passes to here, the decision on choosing a user has already been made.
        # Pick a random event type.
        selected_event = random_pick_notsorted(event_types, self.decision_data.event_probabilities)
        if selected_event == "CreateEvent/new":
            self.create_new_event()
        elif selected_event == "ForkEvent":
            self.fork_event()
        elif selected_event == "WatchEvent":
            self.watch_event_()
        else:
            selected_repo = None
            if self.decision_data.embedding_probabilities[selected_event] is None:
                selected_repo = random_pick_notsorted(self.decision_data.all_known_repos, self.decision_data.probabilities)
            else:
                selected_repo = random_pick_notsorted(
                    self.decision_data.embedding_probabilities[selected_event]['ids'], self.decision_data.embedding_probabilities[selected_event]['prob'])
                if selected_repo is None:
                    selected_repo = random_pick_notsorted(self.decision_data.all_known_repos, self.decision_data.probabilities)
                if selected_repo == -1:  # embedding long tail, random choice.
                    selected_repo = random.choice(self.hub.topPopularRepos) #self.hub.pick_random_repo()
            self.hub.log_event(self.decision_data.id, selected_repo, selected_event, None, self.hub.time)
            self.decision_data.total_activity += 1

        return False

    def create_new_event(self):
        new_repo_id = self.hub._create_repo(self.id, (""))
        popularity = 0
        for own_repo in self.decision_data.own_repos:
            popularity += self.hub.graph.nodes[own_repo]["pop"]
        if popularity == 0:
            popularity = 1
        else:
            popularity = popularity / len(self.decision_data.own_repos)

        self.hub.graph.add_node(new_repo_id, shared=0, isU=0, pop=popularity) # TBD non zero popularity
        self.hub.graph.add_edge(new_repo_id, self.decision_data.id, own=1, weight= 1)
        #print "New repo popularity ", self.hub.graph.nodes[new_repo_id]["pop"]

        self.decision_data.own_repos.append(new_repo_id)
        self.hub.log_event(self.decision_data.id, new_repo_id, "CreateEvent", None, self.hub.time)

    def fork_event(self):
        repo_to_fork = self._pick_popular_repo_from_neighborhood() # parent repo
        new_repo_id = self.hub._create_repo(self.id, (repo_to_fork))
        popularity = 0
        for own_repo in self.decision_data.own_repos:
            popularity += self.hub.graph.nodes[own_repo]["pop"]
        if popularity == 0:
            popularity = 1
        else:
            popularity = popularity / len(self.decision_data.own_repos)

        self.hub.graph.add_node(new_repo_id, shared=0, isU=0, pop=popularity) # TBD non zero popularity
        self.hub.graph.add_edge(new_repo_id, self.decision_data.id, own=1, weight= 1)
        #print "New repo popularity ", self.hub.graph.nodes[new_repo_id]["pop"]

        self.decision_data.own_repos.append(new_repo_id)
        self.hub.graph.nodes[repo_to_fork]["pop"] += 1
        self.hub.log_event(self.decision_data.id, repo_to_fork, "ForkEvent", None, self.hub.time)

    def watch_event_(self):
        repo_to_watch = self._pick_popular_repo_from_neighborhood()
        self.hub.graph.nodes[repo_to_watch]["pop"] += 1
        self.hub.log_event(self.decision_data.id, repo_to_watch, "WatchEvent", None, self.hub.time)

    def _get_neighbors(self, neighbor_iterator):
        neighbors = [_id for _id in neighbor_iterator]
        return neighbors

    def _preferential_attachment_walk(self, start_node):
        """
        returns one of the neighbors of a node based on popularity of the neighbors. If no neighbors found picks some
        random popular repo
        :param start_node:
        :return:
        """
        neighbors = self._get_neighbors(self.hub.graph.neighbors(start_node))  # neighbors here are repos
        if len(neighbors) <= 1:
            popular_repo_id = random.choice(self.hub.topPopularRepos)
            return popular_repo_id, False
        popularity_of_neighbors = [self.hub.graph.nodes[v]["pop"] for v in neighbors]
        sum_f = float(sum(popularity_of_neighbors))
        popularity_of_neighbors = [float(v) / sum_f for v in popularity_of_neighbors] if sum_f != 0 else [1.0 / len(neighbors) for v in popularity_of_neighbors]
        next_node = random_pick_notsorted(neighbors, popularity_of_neighbors)

        return next_node, True

    def _pick_popular_repo_from_neighborhood(self):
        # step one: pick some other repo agent had interacted with
        node_id, is_next = self._preferential_attachment_walk(self.decision_data.id)
        if not is_next:
            return node_id
        # step two: choose some other user who also worked on this repo
        node_id, is_next = self._preferential_attachment_walk(node_id)
        if not is_next:
            return  node_id
        # step three selecting repo of a popular user
        node_id, is_next = self._preferential_attachment_walk(node_id)
        return node_id



class ISIGitUserAgent(ISIMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)

