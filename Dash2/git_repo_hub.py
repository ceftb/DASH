from world_hub import WorldHub

class GitRepoHub(WorldHub):
    """
    # Data

    # Sending

    # Receiving
    user -> CommitCommentEvent
    user -> CreateRepo
    user -> CreateEvent (tag/branch)
    user -> DeleteEvent (tag/branch)
    user -> FollowEvent
    user -> IssueCommentEvent
    user -> IssueEvent
    user -> MemberEvent
    user -> PullRequestEvent
    user -> PushEvent
    user -> WatchEvent
    user -> PublicEvent
    user -> ForkEvent
    """

    def __init__(self, repo_id, repo_name, owner, is_public, date, **kwargs):
        """
        owner: {'login_name', 'user_id', 'account_type'}
        """
        super(WorldHub, self).__init__()

        self.local_repos = dict() # keyed by repo_id, valued by repo object
        self.all_repos = set() # by repo_id
        self.users = set() # set of user_ids

    def processRegisterRequest(self, agent_id, aux_data):
        aux_response = []
        # add user to self.users prob: self.users['agent_id'] = aux_data[0]
        return ["successful registration of user", agent_id, aux_response]

    def commit_comment_event(self, agent_id, repo_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """
        pass

    def create_repo(self, agent_id, repo_info):
        """
        Requests that a git_repo_hub create and start a new repo given 
        the provided repository information
        """
        pass

    def create_tag(self, agent_id, repo_id, tag_info):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        pass

    def create_branch(self, agent_id, repo_id, branch_info):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        pass

    def delete_tag(self, agent_id, repo_id, tag_id):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        pass

    def delete_branch(self, agent_id, repo_id, branch_id):
        """
        user requests repo delete branch
        check if collab
        repo deletes branch
        """
        pass

    def issue_comment_event(self, agent_id, repo_id, comment_info):
        """
        user repuests repo add new comment
        repo addes new comment
        """
        pass

    def issue_event(self, agent_id, repo_id, issue_info):
        """
        user requests change in issue status
        check if collab
        repo changes issue status
        """
        pass

    def member_event(self, agent_id, repo_id, collaborator_info):
        """
        user requests add a new collaborator to repo
        check if collab
        repo sends request to target user and awaits response
        if successful repo adds collaborator
        if unsuccessful repo doesn't add collaborator
        """
        pass

    def pull_request_event(self, agent_id, repo_id, pull_request):
        """
        user requests a pull from a fork
        repo adds the pull request to the stack
        """
        pass

    def push_event(self, agent_id, repo_id, push_request):
        """
        user requests to push to repo
        check if collab 
        repo pushes
        """
        pass

    def watch_event(self, agent_id, repo_id, status):
        """
        user tells repo it will watch it quietly
        repo says okay
        """
        pass

    def public_event(self, server_id, repo_id, status):
        """
        server -> PublicEvent
        server tells repo to set public/private status
        repo sets status 
        """
        pass

    def fork_event(self, server_id, repo_id, fork_info):
        """
        server -> ForkEvent
        server tells repo that it is being forked
        repo adds new fork to its info
        """
        pass

    def request_repos(self, agent_id, None):
        """
        User requests a set of public repos
        Server returns a set of public repos
        """
        pass

    def request_users(self, agent_id, None):
        """
        User requests a set of users
        Server returns said set
        """
        pass


# Make friendly fork function that copies necessary information

if __name__ == '__main__':
    """
    """
    pass