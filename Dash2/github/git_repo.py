class GitRepo(object):
    """
    An object representing a Github repository
    """
    
    def __init__(self, ght_id_h=None, name_h=None, owner=None, **kwargs):

        # Setup information
        self.ght_id_h = ght_id_h
        self.name_h = name_h
        self.owner = owner # A dictionary with {login_h, ght_id_h, type}
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
        # {ght_id_h: permissions}
        self.collaborators = {self.owner['ght_id_h'] : 'owner'}
        # Keyed by request id: valued by dict w/ 
        # {'state':'open'/'closed', 'head':rep_id, 'updated_at':time, 'labeled':T/F, 'review': T/F}
        self.pull_requests = {} 
        # Keyed by issues id: valued by dict w/ 
        # {'state': 'open'/'closed', 'updated_at': time, 'assignment': user_id/None, 
        # 'labeled': True/False, 'milestone': True/False}
        self.smallest_available_issue_id = 0
        self.issues = {}
        self.smallest_available_pull_request_id = 0
        self.commit_comments = []
        self.smallest_available_comment_id = 0
        self.issue_comments = {}
        self.commits = []
        # Each repo starts with a master branch. Currently just has creation date
        self.branches = {'master': {'created_at': self.created_at} }
        self.tags = {}

    ############################################################################
    # Below methods match RepoHub actions - called by repo_hub
    ############################################################################

    def issue_opened_event(self, updated_at):
        issue_id = self.smallest_available_issue_id
        self.smallest_available_issue_id += 1
        self.issues[issue_id] = {'state':'open',
                                 'updated_at': updated_at,
                                 'assignment': None,
                                 'labeled': False,
                                 'milestoned': False}
        return issue_id

    def issue_reopened_event(self, issue_id, updated_at):
        if self.issues[issue_id]['state'] == 'open':
            return False
        else:
            self.issues[issue_id]['state'] = 'open'
            self.issues[issue_id]['updated_at'] = updated_at
            return True

    def issue_closed_event(self, issue_id, updated_at):
        if self.issues[issue_id]['state'] == 'closed':
            return False
        else:
            self.issues[issue_id]['state'] = 'closed'
            self.issues[issue_id]['updated_at'] = updated_at
            return True

    def issue_assigned_event(self, issue_id, updated_at, user_id):
        if user_id in self.collaborators:
            self.issues[issue_id]['updated_at'] = updated_at
            self.issues[issue_id]['assignment'] = user_id
            return True
        else:
            return False

    def issue_unassigned_event(self, issue_id, updated_at):
        self.issues[issue_id]['updated_at'] = updated_at
        self.issues[issue_id]['assignment'] = None
        return True

    def issue_labeled_event(self, issue_id, updated_at):
        if self.issues[issue_id]['labeled'] == False:
            self.issues[issue_id]['updated_at'] = updated_at
            self.issues[issue_id]['labeled'] = True
            return True
        else:
            return False

    def issue_unlabeled_event(self, issue_id, updated_at):
        if self.issues[issue_id]['labeled'] != False:
            self.issues[issue_id]['updated_at'] = updated_at
            self.issues[issue_id]['labeled'] = False
            return True
        else:
            return False

    def issue_milestoned_event(self, issue_id, updated_at):
        if self.issues[issue_id]['milestoned'] == False:
            self.issues[issue_id]['updated_at'] = updated_at
            self.issues[issue_id]['milestoned'] = True
            return True
        else:
            return False

    def issue_demilestoned_event(self, issue_id, updated_at):
        if self.issues[issue_id]['milestoned'] != False:
            self.issues[issue_id]['updated_at'] = updated_at
            self.issues[issue_id]['milestoned'] = False
            return True
        else:
            return False

    def create_comment_event(self, comment_info):
        """
        adds comment information to issue comments and returns the assigned id
        to the client
        """

        comment_id = self.smallest_available_comment_id
        self.smallest_available_comment_id += 1
        self.issue_comments[comment_id] = comment_info

        return comment_id

    def edit_comment_event(self, comment_id, comment):
        """
        replaces the issue comment with new content
        """

        if comment_id in self.issue_comments:
            self.issue_comments[comment_id] = comment
            return True
        else:
            return False

    def delete_comment_event(self, comment_id):
        """
        removes an issue comment if possible
        """

        if comment_id in self.issue_comments:
            self.issue_comments.pop(comment_id)
            return True
        else:
            return False

    def commit_comment_event(self, agent_id, commit_info):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """
        self.commit_comments.append((agent_id, commit_info))
        
    def create_tag_event(self, tag_name, tag_creation_date):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        self.tags[tag_name] = {'created_at': tag_creation_date}

    def create_branch_event(self, branch_name, branch_creation_date):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        self.branches[branch_name] = {'created_at': branch_creation_date}

    def delete_tag_event(self, tag_name):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        self.tags.pop(tag_name)

    def delete_branch_event(self, branch_name):
        """
        user requests repo delete branch
        check if collab
        repo deletes branch
        """
        self.branches.pop(branch_name)

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

    def push_event(self, agent_id, commit_to_push):
        """
        user requests to push to repo
        check if collab 
        repo pushes
        """
        # if agent_id not in self.collaborators: # need to add agent to collaborators first
         #    return "Failure: Agent not a collaborator"
        self.commits.append(commit_to_push)
        return "Successfully pushed"

    def submit_pull_request_event(self, head_id, updated_at):
        """
        adds a pull request to the top of the deque
        """
        request_id = self.smallest_available_pull_request_id
        self.smallest_available_pull_request_id += 1
        self.pull_requests[request_id] = {'head': head_id, 
                                          'updated_at': updated_at, 
                                          'state': 'open',
                                          'labeled': False,
                                          'review': False}

        return request_id

    def close_pull_request_event(self, request_id, updated_at):
        """
        changes status of pull request
        """

        self.pull_requests[request_id]['state'] = 'closed'
        self.pull_requests[request_id]['updated_at'] = updated_at

    def reopened_pull_request_event(self, request_id, updated_at):

        self.pull_requests[request_id]['state'] = 'open'
        self.pull_requests[request_id]['updated_at'] = updated_at

    def label_pull_request_event(self, request_id, updated_at):

        self.pull_requests[request_id]['labeled'] = True
        self.pull_requests[request_id]['updated_at'] = updated_at

    def label_pull_request_event(self, request_id, updated_at):

        self.pull_requests[request_id]['labeled'] = False
        self.pull_requests[request_id]['updated_at'] = updated_at

    def review_pull_request_event(self, request_id, updated_at):

        self.pull_requests[request_id]['review'] = True
        self.pull_requests[request_id]['updated_at'] = updated_at

    def remove_review_pull_request_event(self, request_id, updated_at):

        self.pull_requests[request_id]['review'] = False
        self.pull_requests[request_id]['updated_at'] = updated_at

    def watch_event(self, user_info):
        """
        user tells repo it will watch it quietly
        repo says okay
        """
        
        self.watcher_list[user_info['ght_id_h']] = {key: user_info.get(key, None) for key in self.watcher_keys }

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