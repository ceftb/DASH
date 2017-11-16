from world_hub import WorldHub

class GitRepoHub(WorldHub):
    """
    # Data
    repo_id
    repo_name
    full_name (owner_name/repo_name)
    is_public
    owner = {'login_name', 'user_id', 'account_type'}
    description
    fork
    created_on
    language
    languages = {"<lang name>":# bytes in that language}
    watchers_count
    forks_count
    total_issue_count
    open_issues_count
    watchers = [{login_name, user_id, account_type, watching_date}] #watchevents record staring behavior
    forks = [{repo_id, repo_name, full_name, forked_date}]
    pull_requests = [{???}]
    collaborators = [{login_name, user_id, account_type, permissions}]
    branches?
    tags?

    # Sending

    # Receiving
    user -> CommitCommentEvent
    user -> CreateEvent (tag/branch)
    user -> DeleteEvent (tag/branch)
    user -> FollowEvent
    user -> IssueCommentEvent
    user -> IssueEvent
    user -> MemberEvent
    user -> PullRequestEvent
    user -> PushEvent
    user -> WatchEvent
    server -> PublicEvent
    server -> ForkEvent
    """

    def __init__(self, repo_id, repo_name, owner, is_public, date, **kwargs):
        """
        owner: {'login_name', 'user_id', 'account_type'}
        """
        super(GitServerHub, self).__init__()

        # Need to register with?? um server?

        self.repo_id  = repo_id
        self.repo_name = repo_name
        self.is_public = is_public
        self.owner = owner
        self.created_on = date
        self.description = kwargs.get("description", "")
        self.fork = kwargs.get("fork", False)

        self.full_name = owner['login_name'] + '/' + self.repo_name
        self.language = ""#????
        self.languages = {"<lang name>": "bytes in that language"}#???
        self.watchers_count = 0
        self.forks_count = 0
        self.total_issue_count = 0
        self.open_issues_count = 0
        # Sets???
        self.watchers = set() #[{login_name, user_id, account_type, watching_date}]
        self.forks = set() #[{repo_id, repo_name, full_name, forked_date}]
        self.pull_requests = []
        self.collaborators = set() #[{login_name, user_id, account_type, permissions}]
        self.branches = set()
        self.tags = set()

    def commit_comment_event(self, agent_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """
        pass

    def create_tag(self, agent_id, tag_info):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        pass

    def create_branch(self, agent_id, branch_info):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        pass

    def delete_tag(self, agent_id, tag_id):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        pass

    def delete_branch(self, agent_id, branch_id):
        """
        user requests repo delete branch
        check if collab
        repo deletes branch
        """
        pass

    def issue_comment_event(self, agent_id, comment_info):
        """
        user repuests repo add new comment
        repo addes new comment
        """
        pass

    def issue_event(self, agent_id, issue_info):
        """
        user requests change in issue status
        check if collab
        repo changes issue status
        """
        pass

    def member_event(self, agent_id, collaborator_info):
        """
        user requests add a new collaborator to repo
        check if collab
        repo sends request to target user and awaits response
        if successful repo adds collaborator
        if unsuccessful repo doesn't add collaborator
        """
        pass

    def pull_request_event(self, agent_id, pull_request):
        """
        user requests a pull from a fork
        repo adds the pull request to the stack
        """
        pass

    def push_event(self, agent_id, push_request):
        """
        user requests to push to repo
        check if collab 
        repo pushes
        """
        pass

    def watch_event(self, agent_id, status):
        """
        user tells repo it will watch it quietly
        repo says okay
        """
        pass

    def public_event(self, server_id, status):
        """
        server -> PublicEvent
        server tells repo to set public/private status
        repo sets status 
        """
        pass

    def fork_event(self, server_id, fork_info):
        """
        server -> ForkEvent
        server tells repo that it is being forked
        repo adds new fork to its info
        """
        pass

# Make friendly fork function that copies necessary information

if __name__ == '__main__':
    """
    """
    pass