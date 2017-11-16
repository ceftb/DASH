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
        # Need to register agent with server

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

if __name__ == '__main__':
    """
    """
    pass