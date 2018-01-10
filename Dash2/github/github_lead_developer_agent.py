import sys
sys.path.insert(0, '..')
from git_user_agent import GitUserAgent


class GitLeadDeveloperAgent(GitUserAgent):
    """
    A Lead Developer Git user agent that can communicate with a Git repository hub and
    performs code review actions.
    """

    def __init__(self, **kwargs):
        super(GitLeadDeveloperAgent, self).__init__(**kwargs)

        # Goals
        self.readAgent(
            """
goalWeight ReviewCode 1

goalRequirements ReviewCode
  pull_repo_event(_myRepoName)
  commit_comment_event(_myRepoName, 'code review commit')
            """)

        # Registration
        self.server_host = kwargs.get("host", "localhost")
        self.server_port = kwargs.get("port", 5678)
        registration = self.register()

        # Setup information
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

        # Assigned information
        self.id = registration[1]
        # I want an internal Global time here, but not clear how to assign it

        # Other Non-Schema information
        self.following_list = {}  # ght_id_h: {full_name_h, following_date, following_dow}
        self.watching_list = {}  # ght_id_h: {full_name_h, watching_date, watching_dow}
        self.owned_repos = set()  # ght_id_h
        self.name_to_repo_id = dict()  # hub expects ids in calls other than create_repo_event, not names

        # Actions
        self.primitiveActions([
            ('create_repo_event', self.create_repo_event),
            ('commit_comment_event', self.commit_comment_event),
            ('create_tag_event', self.create_tag_event),
            ('create_branch_event', self.create_branch_event),
            ('delete_tag_event', self.delete_tag_event),
            ('delete_branch_event', self.delete_branch_event),
            ('fork_event', self.fork_event),
            ('issue_comment_event', self.issue_comment_event),
            ('pull_request_event', self.pull_request_event),
            ('push_event', self.push_event),
            ('watch_event', self.watch_event),
            ('follow_event', self.follow_event),
            ('member_event', self.member_event),
            ('public_event', self.public_event)])



    ############################################################################
    # Lead developer git user methods
    ############################################################################
    def commit_comment_event(self, args):
        """
        developer sends comment to repo
        """

        _, repo_name, comment = args
        if repo_name not in self.name_to_repo_id:
            print 'Agent does not know the id of the repo with name', repo_name, 'cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (self.name_to_repo_id[repo_name], comment))
        print 'commit comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment

    def pull_repo_event(self):
        """
        This event describes local code update (pull from the repo)
        """
        pass

if __name__ == '__main__':
    """
    """
    GitLeadDeveloperAgent(host='0', port=6000).agentLoop(10)
