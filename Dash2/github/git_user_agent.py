import sys; sys.path.extend(['../../'])
from Dash2.core.dash import DASHAgent
from Dash2.core.system2 import isVar
import random
import numpy


class GitUserAgent(DASHAgent):
    """
    A basic Git user agent that can communicate with a Git repository hub and
    perform basic actions. Can be inherited to perform other specific functions.
    """

    def __init__(self, **kwargs):
        super(GitUserAgent, self).__init__()
        self.isSharedSocketEnabled = True  # if it is True, then common socket for all agents is used.
        # The first agent to use the socket, gets to set up the connection. All other agents with
        # isSharedSocketEnabled = True will reuse it.
        self.readAgent(
            """
goalWeight MakeRepo 1

goalWeight UpdateOwnRepo 2

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


        # Registration
        self.useInternalHub = kwargs.get("useInternalHub")
        self.hub = kwargs.get("hub")
        self.server_host = kwargs.get("host", "localhost")
        self.server_port = kwargs.get("port", 5678)
        self.trace_client = kwargs.get("trace_client", True)
        registration = self.register({"id": kwargs.get("id", None), "freqs": kwargs.get("freqs", {})})

        # Setup information
        self.use_model_assignment = kwargs.get("use_model", True)
        self.type = kwargs.get("type", "user")
        self.login_h = kwargs.get("login_h", None)
        self.ght_id_h = kwargs.get("ght_id_h", None)
        self.company = kwargs.get("company", "")
        self.location = kwargs.get("location", "")
        self.created_at = kwargs.get("created_at", None)
        self.created_dow = kwargs.get("created_dow", None)
        self.fake = kwargs.get("fake", False)
        self.deleted = kwargs.get("deleted", False)
        self.lat = kwargs.get("lat", None)
        self.lon = kwargs.get("lon", None)
        self.state = kwargs.get("state", None)
        self.city = kwargs.get("city", None)
        self.country_code = kwargs.get("country_code", None)
        self.site_admin = kwargs.get("site_admin", False)
        self.public_repos = kwargs.get("public_repos", 0)
        self.followers = kwargs.get("followers", 0)
        self.following = kwargs.get("following", 0)
        # Follower list would be composed of dictionaries with items:
        # login_h, type, ght_id_h, following_date, following_dow
        self.follower_list = kwargs.get('follower_list', {}) # Keyed by id

        # If account is an organization it can have members
        # members is a list of dictionaries with keys for
        # user: login_h, type, ght_id_h, joined_at_date, joined_at_dow
        if self.type.lower() == "organization":
            self.members = kwargs.get("members", {}) # Keyed by id

        # Assigned information
        self.id = registration[1] if registration is not None else None
        if self.use_model_assignment:
            self.ght_id_h = self.id
            self.created_at = registration[2] if registration is not None else None

        self.trace_github = kwargs.get("trace_github", True)  # Will print far less to the screen if this is False
        self.traceLoop = kwargs.get("traceLoop", True)

        # Other Non-Schema information
        self.total_activity = 0
        self.following_list = {} # ght_id_h: {full_name_h, following_date, following_dow}
        self.watching_list = {} # ght_id_h: {full_name_h, watching_date, watching_dow}
        self.owned_repos = {} # {ght_id_h : name_h}
        self.name_to_repo_id = {} # {name_h : ght_id_h} Contains all repos known by the agent
        self.all_known_repos = []
        if kwargs.get("freqs") is not None:
            self.repo_id_to_freq = kwargs.get("freqs").copy()
            for r_id in self.repo_id_to_freq:
                self.name_to_repo_id[r_id] = r_id
        else:
            self.repo_id_to_freq = {}  # {ght_id_h : frequency of use/communication} Contains all repos agent interacted with
        self.probabilities = None

        self.name_to_user_id = {} # {login_h : ght_id_h} Contains all users known by the agent
        self.known_issue_comments = {} # key: (repo_name) value: [(issue #)]
        self.known_issues = {} # key: (repo_name) value: [(issue #)]
        self.outgoing_requests = {} # keyed tuple of (head_name, base_name, request_id) valued by state

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


    all_event_types = ["CreateEvent", "DeleteEvent", "PullRequestEvent", "IssuesEvent", "PushEvent", "WatchEvent", "ForkEvent"]
    event_probabilities = [0.1, 0.05, 0.3, 0.1, 0.3, 0.1, 0.05]

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True, skipS12=False):
        """
        This a test agentLoop that can skip System 1 and System 2 and picks repo and event based on frequencies.
        """
        if skipS12:
            if (self.probabilities is None or self.all_known_repos == []):
                self.probabilities = []
                self.all_known_repos = []
                sum = 0.0
                for repo_id, fr in self.repo_id_to_freq.iteritems():
                    sum += fr
                    self.all_known_repos.append(repo_id)
                for fr in self.repo_id_to_freq.itervalues():
                    self.probabilities.append(fr / sum)
            selected_repo = numpy.random.choice(self.all_known_repos, p=self.probabilities)
            selected_event = numpy.random.choice(self.all_event_types, p=self.event_probabilities)
            self.hub.log_event(self.id, selected_repo, selected_event, None, self.hub.time)
            self.total_activity += 1
        else:
            return DASHAgent.agentLoop(self, max_iterations, disconnect_at_end)

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
                'owner': {'login_h': self.login_h, 
                          'ght_id_h': self.ght_id_h, 
                          'type': self.type}
                }

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

    def generate_random_name(self, (goal, name_var)):
        """
        Generates a random name. Can be used for the various actions that 
        require a name.
        """
        if self.trace_github:
            print "generating a random name"
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.total_activity += 1
        return [{name_var: ''.join(random.sample(alphabet, random.randint(1,20)))}]

    def pick_random_pull_request(self, (goal, pull_request)):
        """
        Sets a pull request variable with head, base, and request_id.
        """

        if self.trace_github:
            print "picking random pull request"

        chosen_head, chosen_base, chosen_id = random.choice(self.outgoing_requests.keys())
        return [{pull_request : {'head': chosen_head, 'base': chosen_base, 'id': chosen_id}}]

    def pick_random_repo(self, (goal, repo_name_variable)):
        """
        Function that will randomly pick a repository and return the id
        """
        self.total_activity += 1
        return [{repo_name_variable : random.choice(self.name_to_repo_id.keys()) }]

    def pick_repo_using_frequencies(self, (goal, repo_name_variable)):
        """
        Function that will pick a repository and return the id
        """
        self.total_activity += 1

        if (self.probabilities is None):
            self.probabilities = []
            sum = 0.0
            for fr in self.repo_id_to_freq.itervalues():
                sum += fr
            for fr in self.repo_id_to_freq.itervalues():
                self.probabilities.append(fr / sum)
        selected_repo = numpy.random.choice(numpy.arange(1, len(self.repo_id_to_freq)+1), p=self.probabilities)
        return [{repo_name_variable : random.choice(self.repo_id_to_freq.keys()) }]

    def pick_random_issue_comment(self, (goal, issue_comment)):
        self.total_activity += 1
        # Picks a repo and then an id
        repo_name = random.choice(self.known_issue_comments.keys())
        issue_id = random.choice(self.known_issue_comments[repo_name])
        return [{issue_comment : (repo_name, issue_id)}]

    def pick_random_issue(self, (goal, issue)):
        self.total_activity += 1
        repo_name = random.choice(self.known_issues.keys())
        issue_id = random.choice(self.known_issues[repo_name])
        return [{issue : (repo_name, issue_id)}]


    def next_event_time(self, curr_time, max_time):
        return random.uniform(curr_time + 0.1, max_time)

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
        self.owned_repos.update({repo_id: repo_info['name_h']})
        self.name_to_repo_id[repo_info['name_h']] = repo_id
        self.total_activity += 1
        # Binds the name of the repo if it was not bound before this call
        return [{name_var: repo_info['name_h']}] if isVar(name_var) else [{}]

    def create_tag_event(self, (goal, repo_name, tag_name)):
        """
        agent sends new tag in repo
        """

        status = self.sendAction("create_tag_event", 
                                [self.name_to_repo_id[repo_name], tag_name])
        if self.trace_github:
            print 'create tag result:', status, 'for', tag_name
        self.total_activity += 1
        return [{}]

    def create_branch_event(self, (goal, repo_name, branch_name)):
        """
        agent sends new tag in repo
        """

        status = self.sendAction("create_branch_event", 
                                [self.name_to_repo_id[repo_name], branch_name])
        if self.trace_github:
            print 'create branch result:', status, 'for', branch_name
        self.total_activity += 1
        return [{}]

    def delete_tag_event(self, (goal, repo_name, tag_name)):
        """
        agent removes tag from repo
        """
        status = self.sendAction("delete_tag_event", 
                                [self.name_to_repo_id[repo_name], tag_name])
        if self.trace_github:
            print 'delete tag result:', status, 'for', tag_name
        self.total_activity += 1
        return [{}]

    def delete_branch_event(self, (goal, repo_name, branch_name)):
        """
        agent removes branch from repo
        """

        status = self.sendAction("delete_branch_event", 
                                [self.name_to_repo_id[repo_name], branch_name])
        if self.trace_github:
            print 'delete branch result:', status, 'for', branch_name
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
        
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
        return [{}]

    ############################################################################
    # Pull Request Events methods
    ############################################################################

    def submit_pull_request_event(self, (goal, head_name, base_name)):
        """
        submit pull request
        """
        if head_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', head_name, 'cannot pull'
            return []
        elif base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []
        status, request_id = self.sendAction("submit_pull_request_event", 
            (self.name_to_repo_id[head_name], self.name_to_repo_id[base_name]))
        self.outgoing_requests[(head_name, base_name, request_id)] = 'open'
        self.total_activity += 1
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
        
        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("close_pull_request_event", 
                                (self.name_to_repo_id[base_name], request_id))
        self.outgoing_requests[(head_name, base_name, request_id)] = 'closed'
        self.total_activity += 1
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
        
        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("reopened_pull_request_event",
                                (self.name_to_repo_id[base_name], request_id))
        self.outgoing_requests[(head_name, base_name, request_id)] = 'open'
        self.total_activity += 1
        if self.trace_github:
            print status, 'reopened_pull_request_event', head_name, base_name, request_id
        return [{}]

    def assign_pull_request_event(self):
        """
        assign pull request
        """
        self.total_activity += 1
        pass

    def unassign_pull_request_event(self):
        """
        unassign pull request
        """
        self.total_activity += 1
        pass

    def label_pull_request_event(self, (goal, pull_request)):
        """
        label pull request
        """

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("label_pull_request_event", 
                                (self.name_to_repo_id[base_name], request_id))
        self.total_activity += 1
        if self.trace_github:
            print status, 'label_pull_request_event', head_name, base_name, request_id
        return [{}]

    def unlabel_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("unlabel_pull_request_event", 
                                (self.name_to_repo_id[base_name], request_id))
        self.total_activity += 1
        if self.trace_github:
            print status, 'unlabel_pull_request_event', head_name, base_name, request_id
        return [{}]

    def review_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("review_pull_request_event", 
                                (self.name_to_repo_id[base_name], request_id))
        self.total_activity += 1
        if self.trace_github:
            print status, 'review_pull_request_event', head_name, base_name, request_id
        return [{}]

    def remove_review_pull_request_event(self, (goal, pull_request)):

        head_name = pull_request['head']
        base_name = pull_request['base']
        request_id = pull_request['id']

        if base_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', base_name, 'cannot pull'
            return []

        status = self.sendAction("remove_review_pull_request_event", 
                                (self.name_to_repo_id[base_name], request_id))
        self.total_activity += 1
        if self.trace_github:
            print status, 'remove_review_pull_request_event', head_name, base_name, request_id
        return [{}]

    def edit_pull_request_event(self):
        """
        edit pull request
        """
        self.total_activity += 1
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
        self.total_activity += 1
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
        self.total_activity += 1
        if self.trace_github:
            print 'push event:', status, repo_name, self.name_to_repo_id[repo_name]
        return [{}]

    def fork_event(self):
        """
        agent tells server it wants a fork of repo
        """
        self.total_activity += 1
        pass

    def watch_event(self, (goal, target_repo_name)):
        """
        agent decides to watch repo
        """

        # Check if already watching
        if self.name_to_repo_id[target_repo_name] not in self.watching_list:
            user_info = {'login_h': self.login_h, 'type':self.type, 'ght_id_h': self.ght_id_h}
            status, watch_info = self.sendAction("watch_event", (self.name_to_repo_id[target_repo_name], user_info))
            self.watching_list[self.name_to_repo_id[target_repo_name]] = watch_info
            self.total_activity += 1

        return [{}]

    def follow_event(self, args):
        """
        agent decides to follow person
        """
        
        _, target_user_name = args

        # Check if already following
        if self.name_to_user_id[target_user_name] not in self.following_list:
            status, follow_info = self.sendAction("follow_event", [self.name_to_user_id[target_user_name]])
            self.following += 1
            self.following_list[self.name_to_user_id[target_user_name]] = follow_info
            self.total_activity += 1

        return [{}]

    def member_event(self, args):
        """
        agent requests for hub to add/remove/modify collaborators from repo
        """
        
        _, target_user_name, repo_name, action, permissions = args
        collaborator_info = {'user_ght_id_h': self.name_to_user_id[target_user_name],
                             'repo_ght_id_h': self.name_to_repo_id[repo_name],
                             'action': action,
                             'permissions': permissions}
        status = self.sendAction("member_event", [collaborator_info])
        self.total_activity += 1

        return [{}]

    def public_event(self, (goal, repo_name)):
        """
        agent requests server change repo public status
        """
        
        if repo_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo, cannot commit'
            return []
        status = self.sendAction("public_event", [self.name_to_repo_id[repo_name]])
        if self.trace_github:
            print "Toggling", repo_name, "public", status
        self.total_activity += 1

        return [{}]

    def pull_repo_event(self, args):
        """
        This event describes local code update (pull from the repo)
        """
        _, repo_name = args
        if repo_name not in self.name_to_repo_id:
            if self.trace_github:
                print 'Agent does not know the id of the repo with name', repo_name, 'cannot pull'
            return []
        status = self.sendAction("pull_repo_event", (self.name_to_repo_id[repo_name]))
        self.total_activity += 1
        if self.trace_github:
            print 'pull event:', status, repo_name, self.name_to_repo_id[repo_name]
        return [{}]

if __name__ == '__main__':
    """
    """
    GitUserAgent(host='0', port=6000).agentLoop(50)
