from dash import DASHAgent

class GitUserAgent(DASHAgent):
    """
    # Data
    login_name
    user_id
    account_type
    company
    location
    created_on
    lat
    lon
    state
    city
    country_code
    site_admin
    num_public_repos
    num_followers
    num_following
    followers = [{login_name, user_id, account_type, following_date}]
    following = [{login_name, user_id, account_type, following_date}]
    starred = [{login_name, user_id, account_type, starred_date}]
    watching = [{login_name, user_id, account_type, watching_date}]

    # Sending
    CommitCommentEvent -> repo
    CreateEvent (tag/branch) -> repo
    DeleteEvent (tag/branch) -> repo
    ForkEvent -> server (created new repo) -> repo (copies existing repo & adds to forked list)
    IssueCommentEvent -> repo
    IssueEvent -> repo?? [open/close/edited/assigned/unassigned/etc]
    PullRequestEvent -> repo
    PushEvent -> repo
    WatchEvent -> repo
    MemberEvent -> repo/user (???not sure who gives okay to event)
    FollowEvent -> user [needs to add user to follower and increment follow count]
    PublicEvent -> server
    CreateEvent (repo) -> server

    # Receiving
    user -> FollowEvent

    # Goals/Tasks
        #maybe agent can check repos for updates & pull requests
    """

    def __init__(self, login_name, user_id, account_type, date, **kwargs):
        super(DASHAgent, self).__init__()

        self.register([{'login_name': login_name,
                        'user_id': user_id,
                        'account_type': account_type,
                        'date': date}]) # maybe just send id?

        self.login_name = login_name
        self.user_id = user_id
        self.account_type = account_type
        self.company = kwargs.get("company", "")
        self.created_on = date
        self.lat = kwargs.get('lat': None)
        self.lon = kwargs.get('lon': None)
        self.state = kwargs.get('state': None)
        self.city = kwargs.get('city': None)
        self.country_code = kwargs.get('country_code', None)
        self.site_admin = kwargs.get('site_admin', None)

        self.num_public_repos = 0
        self.num_followers = 0
        self.num_following = 0
        self.followers = [] #maybe make these sets
        self.following = []
        self.starred = []
        self.watching = []


    def commit_comment_event(self, (goal, var)):
        """
        agent sends comment to repo
        """
        pass

    def create_event(self, ()):
        """
        agent sends new tag/branch in repo
        """
        pass

    def delete_event(self, ()):
        """
        agent removes tag/branch from repo
        """
        pass

    def fork_event(self, ()):
        """
        agent tells server it wants a fork of repo
        """
        pass

    def issue_comment_event(self, ()):
        """
        send a comment to a repo
        """
        pass

    def issue_event(self, ()):
        """
        agent sends status change of issue to repo
        """
        pass

    def pull_request_event(self, ()):
        """
        agent sends a pull request to repo
        """

    def push_event(self, ()):
        """
        agent pushes to repo
        """
        pass

    def watch_even(self, ()):
        """
        agent decides to watch repo
        """
        pass

    def follow_event(self, ()):
        """
        agent decides to follow person
        """
        pass

    def member_event(self, ()):
        """
        agent requests repo to add another user to collaborators
        """
        pass

    def public_event(eslf, ()):
        """
        agent requests server change repo public status
        """
        pass

    def create_repo(self, ()):
        """
        agent requests server to make new repo
        """
        pass

if __name__ == '__main__':
    """
    """
    pass