from dash import DASHAgent
import random

class GitUserAgent(DASHAgent):
    """
    A basic Git user agent that can communicate with a Git repository hub and
    perform basic actions. Can be inherited to perform other specific functions.
    """

    def __init__(self, **kwargs):
        super(GitUserAgent, self).__init__()

        # Goals Should add goals in child class
        self.readAgent(
            """
goalWeight MakeRepo 1

goalRequirements MakeRepo
  create_repo_event()
  pick_repo(repo_id)
  commit_comment_event(repo_id, 'intial commit')
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
        # I want an internal Global time here, but not clear how to assign it

        # Other Non-Schema information
        self.following_list = {} # ght_id_h: {full_name_h, following_date, following_dow}
        self.watching_list = {} # ght_id_h: {full_name_h, watching_date, watching_dow}
        self.owned_repos = {} # {ght_id_h : name_h}

        # Actions
        self.primitiveActions([
            ('pick_repo', self.pick_repo),
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

    def generate_repo(self):
        """
        Funtion that will return a dictionary with the necessary information
        to build a repository.

        Returns bare minimum randomly generated repo
        """

        alphabet = "abcdefghijklmnopqrstuvwxyz"
        return {'name_h': ''.join(random.sample(alphabet, random.randint(1,10))),
                'owner': {'login_h': self.login_h, 
                          'ght_id_h': self.ght_id_h, 
                          'type': self.type}
                }

    def pick_repo(self, (goal, repo_id)):
        """
        Function that will randomly pick a repository and return the id
        """

        return [{'repo_id' : random.choice(self.owned_repos.keys()) }]

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
        
        # _, repo_name = args
        repo_info = self.generate_repo()
        status, repo_id = self.sendAction("create_repo_event", repo_info)
        self.owned_repos[repo_id] = repo_info['name_h']
  
        return [{}]

    def commit_comment_event(self, (goal, repo_id, comment)):
        """
        agent sends comment to repo
        """

        print goal, repo_id, comment
        if repo_id not in self.owned_repos: # Maybe use something like self.known_repos???
            print 'Agent does not know the id of the repo, cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (repo_id, comment))
        print 'commit comment event:', status, repo_id, comment

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

    def issue_comment_event(self):
        """
        send a comment to a repo
        """
        pass

    def issues_event(self):
        """
        agent sends status change of issue to repo
        """
        pass

    def pull_request_event(self):
        """
        agent sends a pull request to repo
        """
        pass

    def push_event(self):
        """
        agent pushes to repo
        """
        pass

    def fork_event(self):
        """
        agent tells server it wants a fork of repo
        """
        pass

    def watch_event(self, args):
        """
        agent decides to watch repo
        """
        
        _, target_repo_id = args

        # Check if already watching
        if target_repo_id not in self.watching_list:
            user_info = {'login_h': self.login_h, 'type':self.type, 'ght_id_h': self.ght_id_h}
            status, watch_info = self.sendAction("watch_event", [target_repo_id, user_info])
            self.watching_list[target_repo_id] = watch_info

        return [{}]

    def follow_event(self, args):
        """
        agent decides to follow person
        """
        
        _, target_user_id = args

        # Check if already following
        if target_user_id not in self.following_list:
            status, follow_info = self.sendAction("follow_event", [target_user_id])
            self.following += 1
            self.following_list[target_user_id] = follow_info

        return [{}]

    def member_event(self, args):
        """
        agent requests for hub to add/remove/modify collaborators from repo
        """
        
        _, target_user_id, repo_id, action, permissions = args
        collaborator_info = {'user_ght_id_h': target_user_id,
                             'repo_ght_id_h': repo_id,
                             'action': action,
                             'permissions': permissions}
        status = self.sendAction("member_event", [collaborator_info])

        return [{}]

    def public_event(self, args):
        """
        agent requests server change repo public status
        """
        
        status = self.sendAction("public_event", [])

        return [{}]

if __name__ == '__main__':
    """
    """
    GitUserAgent(host='0', port=6000).agentLoop(10)