import sys; sys.path.extend(['../../'])
from Dash2.core.dash import DASHAgent
from Dash2.core.system2 import isVar
import random
import numpy
from distributed_event_log_utils import event_types


class GitUserDecisionData(object):

    def __init__(self, **kwargs):
        """
        Initializes empty DecisionData object. If kwargs is empty object must be initialized via
        initialize_using_user_profile() after creation.
        :param kwargs: may contain such paramenters as id, event_rate, event_frequencies, login_h, etc.
        """
        # System 1 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.nodes = set()
        self.action_nodes = set()
        # System 2 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.knownDict = dict()
        self.knowFalseDict = dict()

        # This is taken from the block a area in GitUserMixin referenced below
        self.login_h = kwargs.get("login_h", None)
        self.ght_id_h = kwargs.get("ght_id_h", None)
        self.type = kwargs.get("type", "user")

        # This is block b from GitUserMixin referenced below
        # Other Non-Schema information
        self.total_activity = 0
        self.following_list = {} # ght_id_h: {full_name_h, following_date, following_dow}
        self.watching_list = {} # ght_id_h: {full_name_h, watching_date, watching_dow}
        self.name_to_repo_id = {} # {name_h : ght_id_h} Contains all repos known by the agent
        self.outgoing_requests = {}  # keyed tuple of (head_name, base_name, request_id) valued by state

        self.owned_repos = []
        self.not_own_repos = []
        self.repo_id_to_freq = {}
        self.all_known_repos = []
        self.event_rate = kwargs.get("event_rate", 5)  # number of events per month
        self.id = kwargs.get("id", None)

        event_frequencies = kwargs.get("event_frequencies", [1] * len(event_types))
        f_sum = float(sum(event_frequencies))
        self.event_probabilities = [event/f_sum for event in event_frequencies]
        self.embedding_probabilities = {ev: None for ev in event_types}

    def initialize_using_user_profile(self, profile, hub):
        """
        This method initializes GitUserDecisionData using information from initial state loader. Information from intial
        state loader is passes via profile object. Profile object is created and pickled by initial state loader.
        This method initializes:
            id, event_rate, last_event_time, all_known_repos, repo_id_to_freq, probabilities, event_probabilities,
            embedding probabilities

        :param profile: contains information about the initial state of the agent, created by initial state loader.
        :param hub: hub is needed to register repos.
        :return: None
        """

        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month

        event_frequencies = profile.pop("ef", None)
        f_sum = float(sum(event_frequencies))
        self.event_probabilities = [event / f_sum for event in event_frequencies]

        # for each event type embedding_probabilities keeps {"ids":[23423, 435434, 34534], "probs":[0.34, 0345, 0.42] }
        self.embedding_probabilities = {ev: None for ev in event_types}
        # frequency of use of associated repos:
        self.repo_id_to_freq = {int(repo_id) : int(freq["f"]) for repo_id, freq in profile.iteritems()}
        for repo_id in profile.iterkeys():
            hub.init_repo(repo_id=int(repo_id), user_id=self.id, curr_time=0, is_node_shared=int(repo_id))

        self.all_known_repos = []
        self.all_known_repos.extend(self.repo_id_to_freq.iterkeys())

        f_sum = float(sum(self.repo_id_to_freq.itervalues()))
        self.probabilities = [repo_fr / f_sum for repo_fr in self.repo_id_to_freq.itervalues()]

        self.last_event_time = -1


class GitUserMixin(object):
    """
    A basic Git user agent that can communicate with a Git repository hub and
    perform basic actions. Can be inherited to perform other specific functions.
    """

    decision_object_class_name = "GitUserDecisionData"

    def _new_empty_decision_object(self):
        return GitUserDecisionData()

    def create_new_decision_object(self, profile, hub):
        decisionObject = self._new_empty_decision_object()
        decisionObject.initialize_using_user_profile(profile, hub)
        return decisionObject

    def __init__(self, **kwargs):
        self.isSharedSocketEnabled = True  # if it is True, then common socket for all agents is used.
        # The first agent to use the socket, gets to set up the connection. All other agents with
        # isSharedSocketEnabled = True will reuse it.
        self.system2_proxy = kwargs.get("system2_proxy")
        if self.system2_proxy is None:
            self.readAgent(
            """
goalWeight MakeRepo 2

goalWeight UpdateOwnRepo 1

goalRequirements MakeRepo
  create_repo_event(RepoName)
  submit_pull_request_event(RepoName, RepoName)
  pick_random_pull_request(Request)
  close_pull_request_event(Request)
  reopened_pull_request_event(Request)
  label_pull_request_event(Request)
  unlabel_pull_request_event(Request)
  review_pull_request_event(Request)
  remove_review_pull_request_event(Request)
  forget([submit_pull_request_event(RepoName, RepoName), pick_random_pull_request(Request), close_pull_request_event(Request), reopened_pull_request_event(Request), label_pull_request_event(Request)])

goalRequirements UpdateOwnRepo
  pick_repo_using_frequencies(RepoName)
  push_event(RepoName)
  forget([pick_repo_using_frequencies(RepoName), push_event(RepoName)])
            """)
        else:
          self.use_system2(self.system2_proxy)

        self.skipS12 = kwargs.get("skipS12", False)
        # Registration
        self.useInternalHub = kwargs.get("useInternalHub")
        self.hub = kwargs.get("hub")
        self.server_host = kwargs.get("host", "localhost")
        self.server_port = kwargs.get("port", 5678)
        self.trace_client = kwargs.get("trace_client", True)
        registration = self.register({"id": kwargs.get("id", None), "freqs": kwargs.get("freqs", {})})

        # This is block a in GitUserDecisionData above. As much as possible is commented out to keep agents small.
        # Setup information
        #self.use_model_assignment = kwargs.get("use_model", True)
        #self.company = kwargs.get("company", "")
        #self.location = kwargs.get("location", "")
        #self.created_at = kwargs.get("created_at", None)
        #self.created_dow = kwargs.get("created_dow", None)
        #self.fake = kwargs.get("fake", False)
        #self.deleted = kwargs.get("deleted", False)
        #self.lat = kwargs.get("lat", None)
        #self.lon = kwargs.get("lon", None)
        #self.state = kwargs.get("state", None)
        #self.city = kwargs.get("city", None)
        #self.country_code = kwargs.get("country_code", None)
        #self.site_admin = kwargs.get("site_admin", False)
        #self.public_repos = kwargs.get("public_repos", 0)
        #self.followers = kwargs.get("followers", 0)
        #self.following = kwargs.get("following", 0)
        # Follower list would be composed of dictionaries with items:
        # login_h, type, ght_id_h, following_date, following_dow
        #self.follower_list = kwargs.get('follower_list', {}) # Keyed by id

        # If account is an organization it can have members
        # members is a list of dictionaries with keys for
        # user: login_h, type, ght_id_h, joined_at_date, joined_at_dow
        #if self.type.lower() == "organization":
        #    self.members = kwargs.get("members", {}) # Keyed by id

        # Assigned information
        self.id = registration[1] if registration is not None else None
        #if self.use_model_assignment:
        #    self.ght_id_h = self.id
        #    self.created_at = registration[2] if registration is not None else None

        self.trace_github = kwargs.get("trace_github", True)  # Will print far less to the screen if this is False
        self.traceLoop = kwargs.get("traceLoop", True)

        # block b taken from here to GitUserDecisionData

        #self.name_to_user_id = {} # {login_h : ght_id_h} Contains all users known by the agent
        #self.known_issue_comments = {} # key: (repo_name) value: [(issue #)]
        #self.known_issues = {} # key: (repo_name) value: [(issue #)]
        self.decision_data = None  # Should be set to the GitUserDecisionData representing the agent on each call

        # Actions
        self.primitiveActions([
            ('generate_random_name', self.generate_random_name),
            ('pick_random_repo', self.pick_random_repo),
            ('pick_repo_using_frequencies', self.pick_repo_using_frequencies),
            ('pick_random_issue_comment', self.pick_random_issue_comment),
            ('pick_random_issue', self.pick_random_issue),
            ('create_repo_event', self.create_repo_event),
            ('commit_comment_event', self.commit_comment_event),
            ('create_tag_event', self.create_tag_event),
            ('create_branch_event', self.create_branch_event),
            ('delete_tag_event', self.delete_tag_event),
            ('delete_branch_event', self.delete_branch_event),
            ('create_comment_event', self.create_comment_event),
            ('edit_comment_event', self.edit_comment_event),
            ('delete_comment_event', self.delete_comment_event),
            ('issue_opened_event', self.issue_opened_event),
            ('issue_reopened_event', self.issue_reopened_event),
            ('issue_closed_event', self.issue_closed_event),
            ('issue_assigned_event', self.issue_assigned_event),
            ('issue_unassigned_event', self.issue_unassigned_event),
            ('issue_labeled_event', self.issue_labeled_event),
            ('issue_unlabeled_event', self.issue_unlabeled_event),
            ('issue_milestoned_event', self.issue_milestoned_event),
            ('issue_demilestoned_event', self.issue_demilestoned_event),
            ('pick_random_pull_request', self.pick_random_pull_request),
            ('submit_pull_request_event', self.submit_pull_request_event),
            ('close_pull_request_event', self.close_pull_request_event),
            ('reopened_pull_request_event', self.reopened_pull_request_event),
            ('label_pull_request_event', self.label_pull_request_event),
            ('unlabel_pull_request_event', self.unlabel_pull_request_event),
            ('review_pull_request_event', self.review_pull_request_event),
            ('remove_review_pull_request_event', self.remove_review_pull_request_event),
            ('fork_event', self.fork_event),
            ('push_event', self.push_event),
            ('watch_event', self.watch_event),
            ('follow_event', self.follow_event),
            ('member_event', self.member_event),
            ('public_event', self.public_event)])

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        """
        This a test agentLoop that can skip System 1 and System 2 and picks repo and event based on frequencies.
        """
        if self.skipS12:
            selected_event = numpy.random.choice(event_types, p=self.decision_data.event_probabilities)
            if self.decision_data.embedding_probabilities[selected_event] is None:
                selected_repo = numpy.random.choice(self.decision_data.all_known_repos, p=self.decision_data.probabilities)
            else:
                selected_repo = numpy.random.choice(self.decision_data.embedding_probabilities[selected_event]['ids'],
                                                    p=self.decision_data.embedding_probabilities[selected_event]['prob'])
                if selected_repo is None:
                    selected_repo = numpy.random.choice(self.decision_data.all_known_repos,
                                                        p=self.decision_data.probabilities)
            self.hub.log_event(self.decision_data.id, selected_repo, selected_event, None, self.hub.time)
            self.decision_data.total_activity += 1
        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

    def first_event_time(self, start_time):
        delta = float(30 * 24 * 3600) / float(self.decision_data.event_rate)
        next_event_time = self.decision_data.last_event_time + delta if self.decision_data.last_event_time != -1 else start_time
        while next_event_time < start_time:
            next_event_time += delta

    def next_event_time(self, curr_time):
        delta = float(30 * 24 * 3600) / float(self.decision_data.event_rate)
        next_time = curr_time + delta
        return next_time

    ############################################################################
    # Core git user methods
    ############################################################################

    def connect_to_new_server(self, host, port):
        """
        Connect to another server
        """

        self.disconnect()
        self.server_host = host
        self.server_port = port
        self.establishConnection()

    ############################################################################
    # Utility Primitive actions
    ############################################################################

    def generate_random_repo_name(self, name=None):
        """
        Function that randomly generates name for a repo
        """
        if self.trace_github:
            print 'generate random repo name'
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        if name is None:
            name = ''.join(random.sample(alphabet, random.randint(1,20)))
        return {'name_h': name,
                'owner': {'login_h': self.decision_data.login_h,
                          'ght_id_h': self.decision_data.ght_id_h,
                          'type': self.decision_data.type}
                }

    def generate_random_name(self, (goal, name_var)):
        """
        Generates a random name. Can be used for the various actions that 
        require a name.
        """
        if self.trace_github:
            print "generating a random name"
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.decision_data.total_activity += 1
        return [{name_var: ''.join(random.sample(alphabet, random.randint(1,20)))}]

    def pick_random_pull_request(self, (goal, pull_request)):
        """
        Sets a pull request variable with head, base, and request_id.
        """

        if self.trace_github:
            print "picking random pull request"

        chosen_head, chosen_base, chosen_id = random.choice(self.decision_data.outgoing_requests.keys())
        return [{pull_request : {'head': chosen_head, 'base': chosen_base, 'id': chosen_id}}]

    def pick_random_repo(self, (goal, repo_name_variable)):
        """
        Function that will randomly pick a repository and return the id
        """
        self.decision_data.total_activity += 1
        return [{repo_name_variable: random.choice(self.decision_data.name_to_repo_id.keys()) }]

    def pick_repo_using_frequencies(self, (goal, repo_name_variable)):
        """
        Function that will pick a repository and return the id
        """
        self.decision_data.total_activity += 1

        if len(self.decision_data.repo_id_to_freq) == 0:
            self.pick_random_repo((goal, repo_name_variable))

        if (self.decision_data.probabilities is None):
            self.decision_data.probabilities = []
            sum = 0.0
            for fr in self.decision_data.repo_id_to_freq.itervalues():
                sum += fr
            for fr in self.decision_data.repo_id_to_freq.itervalues():
                self.decision_data.probabilities.append(fr / sum)
        selected_repo = numpy.random.choice(numpy.arange(1, len(self.decision_data.repo_id_to_freq)+1), p=self.decision_data.probabilities)
        return [{repo_name_variable: random.choice(self.decision_data.repo_id_to_freq.keys()) }]

    def pick_random_issue_comment(self, (goal, issue_comment)):
        self.decision_data.total_activity += 1
        # Picks a repo and then an id
        repo_name = random.choice(self.known_issue_comments.keys())
        issue_id = random.choice(self.known_issue_comments[repo_name])
        return [{issue_comment : (repo_name, issue_id)}]

    def pick_random_issue(self, (goal, issue)):
        self.decision_data.total_activity += 1
        repo_name = random.choice(self.known_issues.keys())
        issue_id = random.choice(self.known_issues[repo_name])
        return [{issue : (repo_name, issue_id)}]

    ############################################################################
    # CreateEvents (Tag/branch/repo)
    ############################################################################

    def create_repo_event(self, (goal, name_var)):
        """
        agent requests server to make new repo
        """
        if self.trace_github:
            print 'create repo event'
        repo_info = self.generate_random_repo_name(None if isVar(name_var) else name_var)
        status, repo_id = self.sendAction("create_repo_event", [repo_info])
        if self.trace_github:
            print 'create repo result:', status, repo_id, 'for', repo_info
        self.decision_data.owned_repos.append(repo_id) #update({repo_id: repo_info['name_h']})
        self.decision_data.name_to_repo_id[repo_info['name_h']] = repo_id
        self.decision_data.total_activity += 1
        # Binds the name of the repo if it was not bound before this call
        return [{name_var: repo_info['name_h']}] if isVar(name_var) else [{}]

    def create_tag_event(self, (goal, repo_name, tag_name)):
        """
        agent sends new tag in repo
        """

        status = self.sendAction("create_tag_event", 
                                [self.decision_data.name_to_repo_id[repo_name], tag_name])
        if self.trace_github:
            print 'create tag result:', status, 'for', tag_name
        self.decision_data.total_activity += 1
        return [{}]

    def create_branch_event(self, (goal, repo_name, branch_name)):
        """
        agent sends new tag in repo
        """

        status = self.sendAction("create_branch_event", 
                                [self.decision_data.name_to_repo_id[repo_name], branch_name])
        if self.trace_github:
            print 'create branch result:', status, 'for', branch_name
        self.decision_data.total_activity += 1
        return [{}]

    def delete_tag_event(self, (goal, repo_name, tag_name)):
        """
        agent removes tag from repo
        """
        status = self.sendAction("delete_tag_event", 
                                [self.decision_data.name_to_repo_id[repo_name], tag_name])
        if self.trace_github:
            print 'delete tag result:', status, 'for', tag_name
        self.decision_data.total_activity += 1
        return [{}]

    def delete_branch_event(self, (goal, repo_name, branch_name)):
        """
        agent removes branch from repo
        """

        status = self.sendAction("delete_branch_event", 
                                [self.decision_data.name_to_repo_id[repo_name], branch_name])
        if self.trace_github:
            print 'delete branch result:', status, 'for', branch_name
        self.decision_data.total_activity += 1
        return [{}]

    ############################################################################
    # Issue Comment methods
    ############################################################################

    def create_comment_event(self, (goal, repo_name, comment_text)):
        """
        send a comment to a repo
        """
        if self.trace_github:
            print goal, repo_name, comment_text
        if repo_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', repo_name, 'cannot create comment'
            return []
        status, comment_id = self.sendAction("create_comment_event", 
            (self.name_to_repo_id[repo_name], comment_text))
        if self.trace_github:
            print 'create comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment_text
        if repo_name in self.known_issue_comments:
            self.known_issue_comments[repo_name].append(comment_id)
        else:
            self.known_issue_comments[repo_name] = [comment_id]
        self.decision_data.total_activity += 1
        return [{}]

    def edit_comment_event(self, (goal, comment, comment_text)):
        """
        send a comment to a repo
        """
        repo_name, comment_id = comment
        if self.trace_github:
            print goal, comment_text, comment_id
        status = self.sendAction("edit_comment_event", 
                                (self.name_to_repo_id[repo_name], 
                                comment_text, comment_id))
        if self.trace_github:
            print 'edit comment event:', status, \
              self.name_to_repo_id[repo_name], comment_text
        self.decision_data.total_activity += 1
        return [{}]

    def delete_comment_event(self, (goal, comment)):
        """
        send a comment to a repo
        """
        repo_name, comment_id = comment
        if self.trace_github:
            print goal, comment_id
        status = self.sendAction("delete_comment_event", 
                                (self.name_to_repo_id[repo_name], 
                                comment_id))
        if self.trace_github:
            print 'delete comment event:', status, \
              self.name_to_repo_id[repo_name], comment_id
        self.decision_data.total_activity += 1
        return [{}]

    ############################################################################
    # Issues Events methods
    ############################################################################

    def issue_opened_event(self, (goal, repo_name)):
        """
        open a new issue
        """
        if self.trace_github:
            print goal, repo_name, "issue_opened_event"
        status, issue_id = self.sendAction("issue_opened_event",
                                          (self.name_to_repo_id[repo_name]))
        if self.trace_github:
            print "issue_opened_event:", status, issue_id
        if repo_name in self.known_issues:
            self.known_issues[repo_name].append(issue_id)
        else:
            self.known_issues[repo_name] = [issue_id]
        self.decision_data.total_activity += 1
        return [{}]

    def issue_reopened_event(self, (goal, issue)):
        """
        reopen issue
        """
        if self.trace_github:
            print goal, issue, "issue_reopened_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_reopened_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        
        return [{}]

    def issue_closed_event(self, (goal, issue)):
        """
        close issue
        """
        if self.trace_github:
            print goal, issue, "issue_closed_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_closed_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_assigned_event(self, (goal, issue, user_name)):
        """
        assign issue
        """
        if self.trace_github:
            print goal, issue, user_name, "issue_assigned_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_assigned_event",
                                (self.name_to_repo_id[repo_name], issue_id,
                                 self.name_to_user_id[user_name]))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_unassigned_event(self, (goal, issue)):
        """
        unassign issue
        """
        if self.trace_github:
            print goal, issue, "issue_unassigned_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_unassigned_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_labeled_event(self, (goal, issue)):
        """
        label issue
        """
        if self.trace_github:
            print goal, issue, "issue_labeled_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_labeled_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_unlabeled_event(self, (goal, issue)):
        """
        unlabel issue
        """
        if self.trace_github:
            print goal, issue, "issue_unlabeled_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_unlabeled_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_milestoned_event(self, (goal, issue)):
        """
        milestone issue
        """
        if self.trace_github:
            print goal, issue, "issue_milestoned_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_milestoned_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    def issue_demilestoned_event(self, (goal, issue)):
        """
        demilestone issue
        """
        if self.trace_github:
            print goal, issue, "issue_demilestoned_event"
        repo_name, issue_id = issue
        status = self.sendAction("issue_demilestoned_event",
                                (self.name_to_repo_id[repo_name], issue_id))
        self.decision_data.total_activity += 1
        return [{}]

    ############################################################################
    # Pull Request Events methods
    ############################################################################

    def submit_pull_request_event(self, (goal, head_name, base_name)):
        """
        submit pull request
        """
        if head_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', head_name, 'cannot pull'
            return []
        elif base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []
        status, request_id = self.sendAction("submit_pull_request_event", 
            (self.decision_data.name_to_repo_id[head_name], self.decision_data.name_to_repo_id[base_name]))
        self.decision_data.outgoing_requests[(head_name, base_name, request_id)] = 'open'
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'submit_pull_request_event', head_name, base_name, request_id
        return [{}]

    def close_pull_request_event(self, (goal, pull_request)):
        """
        close pull request
        """
        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']
        
        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("close_pull_request_event", 
                                (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.outgoing_requests[(head_name, base_name, request_id)] = 'closed'
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'close_pull_request_event', head_name, base_name, request_id
        return [{}]

    def reopened_pull_request_event(self, (goal, pull_request)):
        """
        close pull request
        """
        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']
        
        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("reopened_pull_request_event",
                                (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.outgoing_requests[(head_name, base_name, request_id)] = 'open'
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'reopened_pull_request_event', head_name, base_name, request_id
        return [{}]

    def assign_pull_request_event(self):
        """
        assign pull request
        """
        self.decision_data.total_activity += 1
        pass

    def unassign_pull_request_event(self):
        """
        unassign pull request
        """
        self.decision_data.total_activity += 1
        pass

    def label_pull_request_event(self, (goal, pull_request)):
        """
        label pull request
        """

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("label_pull_request_event", 
                                 (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'label_pull_request_event', head_name, base_name, request_id
        return [{}]

    def unlabel_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("unlabel_pull_request_event", 
                                 (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'unlabel_pull_request_event', head_name, base_name, request_id
        return [{}]

    def review_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("review_pull_request_event", 
                                 (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'review_pull_request_event', head_name, base_name, request_id
        return [{}]

    def remove_review_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("remove_review_pull_request_event", 
                                 (self.decision_data.name_to_repo_id[base_name], request_id))
        self.decision_data.total_activity += 1
        if self.trace_github:
            print status, 'remove_review_pull_request_event', head_name, base_name, request_id
        return [{}]

    def edit_pull_request_event(self):
        """
        edit pull request
        """
        self.decision_data.total_activity += 1
        pass

    ############################################################################
    # Other events
    ############################################################################

    def commit_comment_event(self, (goal, repo_name, comment)):
        """
        agent sends comment to repo
        """
        if self.trace_github:
            print goal, repo_name, comment
        if repo_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', repo_name, 'cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (self.name_to_repo_id[repo_name], comment))
        if self.trace_github:
            print 'commit comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment
        self.decision_data.total_activity += 1
        return [{}]

    def push_event(self, (goal , repo_name)):
        """
        This event describes local code update (pull from the repo)
        """

        if repo_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', repo_name, 'cannot push'
            return []
        status = self.sendAction("push_event", (self.name_to_repo_id[repo_name], "commit to push"))
        self.decision_data.total_activity += 1
        if self.trace_github:
            print 'push event:', status, repo_name, self.name_to_repo_id[repo_name]
        return [{}]

    def fork_event(self):
        """
        agent tells server it wants a fork of repo
        """
        self.decision_data.total_activity += 1
        pass

    def watch_event(self, (goal, target_repo_name)):
        """
        agent decides to watch repo
        """

        # Check if already watching
        if self.decision_data.name_to_repo_id[target_repo_name] not in self.decision_data.watching_list:
            user_info = {'login_h': self.decision_data.login_h, 'type':self.decision_data.type, 'ght_id_h': self.decision_data.ght_id_h}
            status, watch_info = self.sendAction("watch_event", (self.decision_data.name_to_repo_id[target_repo_name], user_info))
            self.decision_data.watching_list[self.decision_data.name_to_repo_id[target_repo_name]] = watch_info
            self.decision_data.total_activity += 1

        return [{}]

    def follow_event(self, args):
        """
        agent decides to follow person
        """
        
        _, target_user_name = args

        # Check if already following
        if self.decision_data.name_to_user_id[target_user_name] not in self.decision_data.following_list:
            status, follow_info = self.sendAction("follow_event", [self.decision_data.name_to_user_id[target_user_name]])
            self.decision_data.following += 1
            self.decision_data.following_list[self.decision_data.name_to_user_id[target_user_name]] = follow_info
            self.decision_data.total_activity += 1

        return [{}]

    def member_event(self, args):
        """
        agent requests for hub to add/remove/modify collaborators from repo
        """
        
        _, target_user_name, repo_name, action, permissions = args
        collaborator_info = {'user_ght_id_h': self.decision_data.name_to_user_id[target_user_name],
                             'repo_ght_id_h': self.decision_data.name_to_repo_id[repo_name],
                             'action': action,
                             'permissions': permissions}
        status = self.sendAction("member_event", [collaborator_info])
        self.decision_data.total_activity += 1

        return [{}]

    def public_event(self, (goal, repo_name)):
        """
        agent requests server change repo public status
        """
        
        if repo_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo, cannot commit'
            return []
        status = self.sendAction("public_event", [self.decision_data.name_to_repo_id[repo_name]])
        if self.trace_github:
            print "Toggling", repo_name, "public", status
        self.decision_data.total_activity += 1

        return [{}]

    def pull_repo_event(self, args):
        """
        This event describes local code update (pull from the repo)
        """
        _, repo_name = args
        if repo_name not in self.decision_data.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', repo_name, 'cannot pull'
            return []
        status = self.sendAction("pull_repo_event", (self.decision_data.name_to_repo_id[repo_name]))
        self.decision_data.total_activity += 1

        if self.trace_github:
            print 'pull event:', status, repo_name, self.decision_data.name_to_repo_id[repo_name]
        return [{}]


class GitUserAgent(GitUserMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        GitUserMixin.__init__(self, **kwargs)


if __name__ == '__main__':
    """
    """
    GitUserAgent(host='0', port=6000).agentLoop(50)
