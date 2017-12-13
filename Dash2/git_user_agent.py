from dash import DASHAgent
import random

class GitUserAgent(DASHAgent):
    """
    A basic Git user agent that can communicate with a Git repository hub and
    perform basic actions. Can be inherited to perform other specific functions.
    """

    def __init__(self, **kwargs):
        super(GitUserAgent, self).__init__()

        # Registration
        self.server_host = kwargs.get("host", "localhost")
        self.server_port = kwargs.get("port", 5678)
        registration = self.register()

        # Setup information
        self.use_model_assignment = kwargs.get("use_model", True) # TODO: Need to check if id/ght_id cause conflicts (also issue w/ time, it all comes from time, which won't work with created_at in the data)
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
        self.id = registration[1]
        if self.use_model_assignment:
            self.ght_id_h = self.id 
            self.created_at = registration[2]

        # Other Non-Schema information
        self.total_activity = 0
        self.following_list = {} # ght_id_h: {full_name_h, following_date, following_dow}
        self.watching_list = {} # ght_id_h: {full_name_h, watching_date, watching_dow}
        self.owned_repos = {} # {ght_id_h : name_h}
        self.name_to_repo_id = {} # {name_h : ght_id_h} Contains all repos known by the agent
        self.name_to_user_id = {} # {login_h : ght_id_h} Contains all users known by the agent

        # Actions
        self.primitiveActions([
            ('generate_random_repo_name', self.generate_random_repo_name),
            ('pick_random_repo', self.pick_random_repo),
            ('create_repo_event', self.create_repo_event),
            ('commit_comment_event', self.commit_comment_event),
            ('create_tag_event', self.create_tag_event),
            ('create_branch_event', self.create_branch_event),
            ('delete_tag_event', self.delete_tag_event),
            ('delete_branch_event', self.delete_branch_event),
            ('fork_event', self.fork_event),
            ('issue_comment_event', self.issue_comment_event),
            ('issues_event', self.issues_event),
            ('pull_request_event', self.pull_request_event),
            ('push_event', self.push_event),
            ('watch_event', self.watch_event),
            ('follow_event', self.follow_event),
            ('member_event', self.member_event),
            ('public_event', self.public_event)])

    ############################################################################
    # Model dependent methods
    ############################################################################

    def generate_random_repo_name(self, (goal, repo_name_variable)):
        """
        Function that randomly generates name for a repo
        """

        alphabet = "abcdefghijklmnopqrstuvwxyz"
        return [{repo_name_variable : ''.join([random.choice(alphabet) 
                                       for i in range(random.randint(3,10))])}]

    def pick_random_repo(self, (goal, repo_name_variable)):
        """
        Function that will randomly pick a repository and return the id
        """

        return [{repo_name_variable : random.choice(self.name_to_repo_id.keys()) }]

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

    def create_repo_event(self, args):
        """
        agent requests server to make new repo
        """
        
        _, repo_name = args
        repo_info = {'name_h': repo_name,
                     'owner': {'login_h': self.login_h, 
                               'ght_id_h': self.ght_id_h, 
                               'type': self.type}}
        status, repo_id = self.sendAction("create_repo_event", [repo_info])
        print 'repo', repo_name, 'creation status', status, 'id', repo_id
        self.owned_repos[repo_id] = repo_info['name_h']
        self.name_to_repo_id[repo_name] = repo_id
        self.total_activity += 1
  
        return [{}]

    def commit_comment_event(self, (goal, repo_name, comment)):
        """
        agent sends comment to repo
        """

        print goal, repo_name, comment
        if repo_name not in self.name_to_repo_id:
            print 'Agent does not know the id of the repo, cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (self.name_to_repo_id[repo_name], comment))
        print 'commit comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment
        self.total_activity += 1

    def create_tag_event(self):
        """
        agent sends new tag in repo
        """
        self.total_activity += 1
        pass

    def create_branch_event(self):
        """
        agent sends new tag in repo
        """
        self.total_activity += 1
        pass

    def delete_tag_event(self):
        """
        agent removes tag from repo
        """
        self.total_activity += 1
        pass

    def delete_branch_event(self):
        """
        agent removes branch from repo
        """
        self.total_activity += 1
        pass

    def issue_comment_event(self):
        """
        send a comment to a repo
        """
        self.total_activity += 1
        pass

    def issues_event(self):
        """
        agent sends status change of issue to repo
        """
        self.total_activity += 1
        pass

    def pull_request_event(self):
        """
        agent sends a pull request to repo
        """
        self.total_activity += 1
        pass

    def push_event(self):
        """
        agent pushes to repo
        """
        self.total_activity += 1
        pass

    def fork_event(self):
        """
        agent tells server it wants a fork of repo
        """
        self.total_activity += 1
        pass

    def watch_event(self, args):
        """
        agent decides to watch repo
        """

        _, target_repo_name = args

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

    def public_event(self, args):
        """
        agent requests server change repo public status
        """
        
        status = self.sendAction("public_event", [])
        self.total_activity += 1

        return [{}]

if __name__ == '__main__':
    """
    """
    test_agent = GitUserAgent(host='0', port=6000)
    test_agent.readAgent(
            """
goalWeight MakeRepo 1

goalRequirements MakeRepo
  generate_random_repo_name(RepoName)
  create_repo_event(RepoName)
            """)
  # pick_repo(RepoName)
  # watch_event(RepoName)
  # commit_comment_event(RepoName, 'intial commit')
    test_agent.agentLoop(10)