class GitRepo(object):

    def __init__(self, repo_id, repo_name, owner, is_public, **kwargs):
        """
        repo_id
        repo_name
        full_name (owner_name/repo_name)
        is_public
        owner = {'login_name', 'user_id'}
        description
        fork
        created_on
        language
        languages = {"<lang name>": ammount of code in that languages}
        watchers_count
        forks_count
        total_issue_count
        open_issues_count
        watchers = [{login_name, user_id, account_type, watching_date}]
        forks = [{repo_id, repo_name, full_name, forked_date}]
        pull_requests = [{???}]
        collaborators = [{login_name, user_id, account_type, permissions}]
        branches?
        tags?
        """

        self.repo_id  = repo_id
        self.repo_name = repo_name
        self.owner = owner
        self.is_public = is_public
        self.created_at = kwargs.get("date", 0)
        self.description = kwargs.get("description", "")
        self.fork = kwargs.get("fork", False)

        self.full_name = owner['login_name'] + '/' + self.repo_name
        self.language = "" # string of dominant language in repo
        self.languages = {} # keyed by language string, valued by ammount of code in that language
        self.watchers_count = 0
        self.forks_count = 0
        self.total_issue_count = 0
        self.open_issues_count = 0
        
        # These might be just dictionaries, keyed by id and valued by another dict
        self.watchers = {} #{login_name, user_id, account_type, watching_date}
        self.forks = {} #{repo_id, repo_name, full_name, forked_date}
        self.collaborators = {} #{login_name, user_id, account_type, permissions}
        self.branches = set()
        self.tags = set()
        # pull requests are temporal, maybe a queue or list, depends on how
        # agent will prioritize addressing pulls
        self.pull_requests = []

    # Below methods match RepoHub actions
    # RepoHub would call the corresponding repo's method for the user action
    def commit_comment(self, agent_id, repo_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
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

    def issue_comment(self, agent_id, repo_id, comment_info):
        """
        user repuests repo add new comment
        repo addes new comment
        """
        pass

    def issue(self, agent_id, repo_id, issue_info):
        """
        user requests change in issue status
        check if collab
        repo changes issue status
        """
        pass

    def member(self, agent_id, repo_id, collaborator_info):
        """
        user requests add a new collaborator to repo
        check if collab
        repo sends request to target user and awaits response
        if successful repo adds collaborator
        if unsuccessful repo doesn't add collaborator
        """
        pass

    def pull_request(self, agent_id, repo_id, pull_request):
        """
        user requests a pull from a fork
        repo adds the pull request to the stack
        """
        pass

    def push(self, agent_id, repo_id, push_request):
        """
        user requests to push to repo
        check if collab 
        repo pushes
        """
        pass

    def watch(self, agent_id, repo_id, status):
        """
        user tells repo it will watch it quietly
        repo says okay
        """
        pass

    def make_public(self, server_id, repo_id, status):
        """
        server -> PublicEvent
        server tells repo to set public/private status
        repo sets status 
        """
        pass

    def fork(self, server_id, repo_id, fork_info):
        """
        server -> ForkEvent
        server tells repo that it is being forked
        repo adds new fork to its info
        """
        pass

if __name__ == '__main__':
    """
    """
    pass