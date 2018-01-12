class GitRepo(object):
    """
    An object representing a Github repository
    """
    
    def __init__(self, ght_id_h=None, name_h=None, owner=None, **kwargs):  # don't crash if agent doesn't supply args

        # Setup information
        self.ght_id_h = kwargs.get("ght_id_h")
        self.name_h = kwargs.get("name_h")
        self.owner = kwargs.get("owner") # A dictionary with {login_h, ght_id_h, type}
        self.full_name_h = kwargs.get("full_name_h", "")
        self.is_public = kwargs.get("is_public", True)
        self.description_m = kwargs.get("description_m", "")
        self.created_at = kwargs.get("created_at", None)
        self.updated_at = kwargs.get("updated_at", None)
        self.fork = kwargs.get("fork", False)
        self.language = kwargs.get("language", None)
        self.total = kwargs.get("total", None) # Total num of bytes of languages
        self.languages = kwargs.get("languages", {}) # Key: language str, value: bytes
        self.created_dow = kwargs.get("created_dow", None)
        self.updated_dow = kwargs.get("updated_dow", None)
        self.deleted = kwargs.get("deleted", False)
        self.watchers_count = kwargs.get("watchers_count", 0)
        self.forks_count = kwargs.get("forks_count", 0)
        self.open_issues_count = kwargs.get("open_issues_count", 0)
        self.total_issue_count = kwargs.get("total_issue_count", 0)

        # Watch list would be composed of dictionaries with items:
        # login_h, type, ght_id_h, watching_date, watching_dow
        self.watcher_keys = ('type', 'login_h', 'watching_date', 'watching_dow')
        self.watcher_list = kwargs.get("watcher_list", {}) # Keyed by id

        # Fork list would be composed of dictionaries with items:
        # ght_id_h, full_name_h, forked_date, forked_date_dow
        self.fork_list = kwargs.get("fork_list", {}) # Keyed by id

        # Other possible data, Not in data schema
        self.collaborators = {} #{ght_id_h: permissions}
        # self.branches = set()
        # self.tags = set()
        # # pull requests are temporal, maybe a queue or list, depends on how
        # # agent will prioritize addressing pulls
        # self.pull_requests = []
        self.commit_comments = []

    # Below methods match RepoHub actions
    # RepoHub would call the corresponding repo's method for the user action
    def commit_comment_event(self, agent_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """
        self.commit_comments.append((agent_id, commit_info))
        
    # Following methods match RepoHub actions
    # RepoHub would call the corresponding repo's method for the user action
    def create_tag_event(self, agent_id, tag_info):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        pass

    def create_branch_event(self, agent_id, branch_info):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        pass

    def delete_tag_event(self, agent_id, tag_id):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        pass

    def delete_branch_event(self, agent_id, branch_id):
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

    def issues_event(self, agent_id, issue_info):
        """
        user requests change in issue status
        check if collab
        repo changes issue status
        """
        pass

    def member_event(self, agent_id, target_agent, action, permissions=None):
        """
        user requests add a new collaborator to repo
        check if collab
        repo sends request to target user and awaits response
        if successful repo adds collaborator
        if unsuccessful repo doesn't add collaborator
        """
        
        # Check if agent has permissions to add collaborator
        if agent_id not in self.collaborators:
            return "Failure: Agent not a collaborator"
        if (self.collaborators[agent_id] != "admin" or
            self.collaborators[agent_id] != "owner"):
            return "Failure: Agent does not have sufficient permissions"

        if action == "add" or (action == "modify"):
            self.collaborators[target_agent] = permissions
            return "Successfully added collaborator"

        elif action == "remove":
            self.collaborators.pop(target_agent, None)
            return "Successfully removed collaborator"

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

    def watch_event(self, user_info):
        """
        user tells repo it will watch it quietly
        repo says okay
        """
        
        self.watcher_list[user_info['ght_id_h']] = { key:user_info.get(key, None) for key in self.watcher_keys }

        return "Success"

    def public_event(self, agent_id):
        """
        server tells repo to set public/private status
        repo sets status 
        """
        
        # Check if agent has permissions to add collaborator
        if agent_id not in self.collaborators:
            return "Failure: Agent not a collaborator"
        if (self.collaborators[agent_id] != "admin" or
            self.collaborators[agent_id] != "owner"):
            return "Failure: Agent does not have sufficient permissions"

        self.is_public = not self.is_public

        return "Success"

    def fork_event(self, agent_id, fork_info):
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