from world_hub import WorldHub

class GitServerHub(WorldHub):
    """
    # Data
    # repos = [{repo_id, repo_name, full_name (owner_name/repo_name), is_public, created_on}]
    # users = [{login_name, user_id, account_type, created_on}]
    # repos = [] # list of GitRepoHub objects (or id's?)
    # users = [] # list of GitUserAgent objects (or id's?)

    # Sending

    # Receiving
    # user -> CreateEvent
    # user -> ForkEvent
    # user -> PublicEvent
    # user -> RequestRepos
    # master -> AddNewUser
    """

    def __init__(self):
        super(GitServerHub, self).__init__()

        # Sets probably.. or maybe dict based on ids? or just ref to object
        self.repos = []
        self.users = []

    def processRegisterRequest(self, agent_id, aux_data):
        aux_response = []
        # add user to self.users
        return ["successful registration of user", agent_id, aux_response]

    def create_repo(self, agent_id, repo_info):
        """
        Requests that the hub create and start a new repo server given 
        the provided repository information
        """
        pass

    def fork_event(self, agent_id, repo_id):
        """
        User requests that server fork given repo
        Server will create and start a new repo server that is a fork of
        the given repo
        """
        pass

    def public_event(self, agent_id, repo_id):
        """
        User requests that server change repo to public/private
        Server will change tag and instruct repo to do the same
        """
        pass

    def request_repos(self, agent_id, None):
        """
        User requests a list of public repos
        Server returns a list of public repos
        """
        pass

if __name__ == '__main__':
    """
    """
    pass