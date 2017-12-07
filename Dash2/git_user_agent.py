from dash import DASHAgent

class GitUserAgent(DASHAgent):
    """
    # Data
    login_name, user_id, account_type, company, location, created_at,
    lat, lon, state, city, country_code, site_admin, num_public_repos,
    num_followers, num_following, followers, following, starred, watching

    # Sending
    CommitCommentEvent -> repo_hub
    CreateEvent (tag/branch) -> repo_hub
    DeleteEvent (tag/branch) -> repo_hub
    ForkEvent -> repo_hub
    IssueCommentEvent -> repo_hub
    IssueEvent -> repo_hub [open/close/edited/assigned/unassigned/etc]
    PullRequestEvent -> repo_hub
    PushEvent -> repo_hub
    WatchEvent -> repo_hub
    MemberEvent -> repo_hub -> user
    FollowEvent -> user [needs to add user to follower and increment follow count]
    PublicEvent -> repo_hub
    CreateEvent (repo) -> repo_hub

    # Receiving
    user -> FollowEvent

    # Goals/Tasks
        maybe agent can check repos for updates & pull requests
    """

    def __init__(self, login_name, account_type, **kwargs):
        super(GitUserAgent, self).__init__()

        # Goals
        self.readAgent(
            """
goalWeight MakeRepo 1

goalRequirements MakeRepo
  create_repo(_myRepoName)
  commit_comment_event(_myRepoName, 'intial commit')
            """)

        # Registration
        self.server_host = kwargs.get('host', 'localhost')
        self.server_port = kwargs.get('port', 5678)
        registration = self.register()

        # Required information
        self.login_name = login_name
        self.account_type = account_type

        # Optional information
        self.company = kwargs.get("company", "")
        self.lat = kwargs.get('lat', None)
        self.lon = kwargs.get('lon', None)
        self.state = kwargs.get('state', None)
        self.city = kwargs.get('city', None)
        self.country_code = kwargs.get('country_code', None)
        self.site_admin = kwargs.get('site_admin', None)

        # Assigned information
        self.id = registration[1]
        self.created_at = 0  # How do we want to simulate dates, if at all?
        self.num_public_repos = 0
        self.num_following = 0
        self.num_followers = 0
        self.followers = set()  # user id's
        self.following = set()  # user id's
        self.starred = set()  # repo id's
        self.watching = set()  # repo id's
        self.owned_repos = set()  # repo_id's
        self.name_to_repo_id = {}  # Map name into unique id given by github simulator

        # State
        self.user_feed = []

        # Actions
        self.primitiveActions([
            ('create_repo', self.create_repo_event),
            ('commit_comment', self.commit_comment_event),
            ('create_tag', self.create_tag_event),
            ('create_branch', self.create_branch_event),
            ('delete_tag', self.delete_tag_event),
            ('delete_branch', self.delete_branch_event),
            ('fork', self.fork_event),
            ('issue_comment', self.issue_comment_event),
            ('issue', self.issue_event),
            ('pull_request', self.pull_request_event),
            ('push', self.push_event),
            ('watch', self.watch_event),
            ('follow', self.follow_event),
            ('member', self.member_event),
            ('make_public', self.public_event)])

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
        repo_info = [('name:', repo_name)]
        status, repo_id = self.sendAction("create_repo_event", repo_info)
        print 'repo', repo_name, 'creation status', status, 'id', repo_id
        self.owned_repos.add(repo_id)
        self.name_to_repo_id[repo_name] = repo_id

        return [{}]

    def commit_comment_event(self, args):
        """
        agent sends comment to repo
        """

        _, repo_name, comment = args
        if repo_name not in self.name_to_repo_id:
            print 'Agent does not know the id of the repo, cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (self.name_to_repo_id[repo_name], comment))
        print 'commit comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment
        pass

    def create_tag_event(self):
        """
        agent sends new tag in repo
        """
        pass

    def create_branch_event(self):
        """
        agent sends new tag in repo
        """
        pass

    def delete_tag_event(self):
        """
        agent removes tag from repo
        """
        pass

    def delete_branch_event(self):
        """
        agent removes branch from repo
        """
        pass

    def fork_event(self):
        """
        agent tells server it wants a fork of repo
        """
        pass

    def issue_comment_event(self):
        """
        send a comment to a repo
        """
        pass

    def issue_event(self):
        """
        agent sends status change of issue to repo
        """
        pass

    def pull_request_event(self):
        """
        agent sends a pull request to repo
        """

    def push_event(self):
        """
        agent pushes to repo
        """
        pass

    def watch_event(self):
        """
        agent decides to watch repo
        """
        pass

    def follow_event(self):
        """
        agent decides to follow person
        """
        pass

    def member_event(self):
        """
        agent requests repo to add another user to collaborators
        """
        pass

    def public_event(self):
        """
        agent requests server change repo public status
        """
        pass

if __name__ == '__main__':
    """
    """
    GitUserAgent('bob', 'pro', host='0', port=6000).agentLoop(10)