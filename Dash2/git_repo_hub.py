from world_hub import WorldHub
from git_repo import GitRepo

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

    def __init__(self, repo_hub_id, **kwargs):

        WorldHub.__init__(self, kwargs.get('port', None))
        self.local_repos = {} # keyed by repo_id, valued by repo object
        self.repo_hub_id = repo_hub_id
        self.host = str(self.repo_hub_id)
        self.repos_hubs = kwargs.get('repos_hubs', {}).update({self.host : self.port})
        self.lowest_unassigned_repo_id = 0

    def synch_repo_hub(self, host, port):
        """
        Synchronizes repository hub with other hubs
        """
        pass

    def create_repo_event(self, agent_id, repo_info):
        """
        Requests that a git_repo_hub create and start a new repo given 
        the provided repository information
        """
        
        print('Request to create repo from', agent_id, 'for', repo_info)
        repo_id = self.host + '_' + str(self.port) + '_' + str(self.lowest_unassigned_repo_id)
        self.local_repos[repo_id] = GitRepo(repo_id, **repo_info)
        # self.local_repos[repo_id] = GitRepo(repo_id, 'boop', {'user_id': agent_id, 'login_name':'bob'}, True)

        return 'success', repo_id

    def commit_comment_event(self, agent_id, repo_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """
        pass

    def create_tag_event(self, agent_id, repo_id, tag_info):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        pass

    def create_branch_event(self, agent_id, repo_id, branch_info):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        pass

    def delete_tag_event(self, agent_id, repo_id, tag_id):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        pass

    def delete_branch_event(self, agent_id, repo_id, branch_id):
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

    def request_repos(self, agent_id):
        """
        User requests a set of public repos
        Server returns a set of public repos
        """
        pass

    def request_users(self, agent_id):
        """
        User requests a set of users
        Server returns said set
        """
        pass

if __name__ == '__main__':
    """
    """
    GitRepoHub(0, port=6000).run()