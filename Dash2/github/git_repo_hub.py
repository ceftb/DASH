import sys; sys.path.extend(['../../'])
from Dash2.core.world_hub import WorldHub
from git_repo import GitRepo
from time import time
import pickle


class GitRepoHub(WorldHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    def __init__(self, repo_hub_id, **kwargs):

        WorldHub.__init__(self, kwargs.get('port', None))
        self.users = set()  # User ids
        self.local_repos = {}  # keyed by repo id, valued by repo object
        self.foreign_repos = {}  # keyed by repo id, valued by host
        self.repo_hub_id = repo_hub_id
        self.host = kwargs.get("host", str(self.repo_hub_id))
        self.repos_hubs = kwargs.get('repos_hubs', {}).update({self.host: self.port})
        self.lowest_unassigned_repo_id = 0
        self.local_event_log = []  # A dictionary with keys 'userID', 'repoID', 'eventType', 'subeventtype', 'time'

    def log_event(self, user_id, repo_id, event_type, subevent_type, time):
        """
        Logs the event in the hubs local log list
        """

        self.local_event_log.append({
            'userID':user_id,
            'repoID':repo_id,
            'eventType':event_type,
            'subeventType':subevent_type,
            'time':time})

    def dump_event_log(self, agent_id):
        """
        prompts the hub to dump it's log to file
        """

        try:
            save_object(str(self.repo_hub_id) + "_hub_log_list.pyobj")
            return "Success"
        except:
            return "Failed to pickle and save log list."

    def return_event_log(self, agent_id):
        """
        Prompts the hub to return its local event log
        """

        return "Success", self.local_event_log

    def processRegisterRequest(self, agent_id, aux_data):
        creation_time = time()
        self.log_event(agent_id, None, "CreateUser", "None", creation_time)
        self.users.add(agent_id)
        return ["success", agent_id, creation_time]

    def synch_repo_hub(self, host, port):
        """
        Synchronizes repository hub with other hubs
        """

        # Needs to update lowest_unassigned_repo_id
        # Needs to synch available users

        pass

    ############################################################################
    # CreateEvents (Tag/branch/repo)
    ############################################################################

    def create_repo_event(self, agent_id, (repo_info,)):
        """
        Requests that a git_repo_hub create and start a new repo given 
        the provided repository information
        """
        
        repo_id = self.lowest_unassigned_repo_id
        self.lowest_unassigned_repo_id += 1
        print('Request to create repo from', agent_id, 'for', repo_info)
        repo_creation_date = time()
        repo_info['created_at'] = repo_creation_date
        self.local_repos[repo_id] = GitRepo(repo_id, **repo_info)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Repository', repo_creation_date)

        return 'success', repo_id

    def create_tag_event(self, agent_id, (repo_id, tag_name)):
        """
        user requests to make a new tag
        check if collab
        repo takes tag info and adds a new tag to repo
        """
        if repo_id not in self.local_repos:
            print 'unknown repo id for push_event:', repo_id
            return 'fail'

        if self.is_collaborator(agent_id, repo_id):
            tag_creation_date = time()
            self.local_repos[repo_id].tags[tag_name] = {'created_at': tag_creation_date}
            self.log_event(agent_id, repo_id, 'CreateEvent', 'Tag', tag_creation_date)
            return 'success'

        return 'failure'

    def create_branch_event(self, agent_id, (branch_info,)):
        """
        user requests to make a new branch
        check if collab
        repo takes branch info and adds a new branch to repo
        """
        pass

    def delete_tag_event(self, agent_id, (tag_info,)):
        """
        user requests repo delete tag
        check if collab
        repo deletes tag
        """
        pass

    def delete_branch_event(self, agent_id, (branch_info,)):
        """
        user requests repo delete branch
        check if collab
        repo deletes branch
        """
        pass

    ############################################################################
    # Issues Events methods
    ############################################################################

    def create_comment_event(self, agent_id, (repo_id, comment)):
        """
        user creates an issue comment on a repo
        """

        if repo_id not in self.local_repos:
            print 'unknown repo id for push_event:', repo_id
            return 'fail'
        comment_id = self.local_repos[repo_id].create_comment_event( 
            {'user': agent_id, 'repo_id': repo_id, 'comment': comment})
        self.log_event(agent_id, repo_id, 'IssueCommentEvent', "created", time())
        return ["success", comment_id]

    def edit_comment_event(self, agent_id, (repo_id, comment, comment_id)):
        """
        user edits an issue comment on a repo
        """

        if repo_id not in self.local_repos:
            print 'unknown repo id for push_event:', repo_id
            return 'fail'
        if self.local_repos[repo_id].edit_comment_event(comment_id, comment):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "edited", time())
            return ["Success"]
        else:
            return ["Failure: can't edit comment " + str(comment_id)]

    def delete_comment_event(self, agent_id, (repo_id, comment_id)):
        """
        user deletes an issue comment on a repo
        """

        if repo_id not in self.local_repos:
            print 'unknown repo id for push_event:', repo_id
            return 'fail'
        if self.local_repos[repo_id].delete_comment_event(comment_id):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "deleted", time())
            return ["Success"]
        else:
            return ["Failure: can't delete comment " + str(comment_id)]

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

        types: open issue, close issue, assign issue, unassign issue, 
        label issue, unlabel issue, milestone issue, demilestone issue,
        reopen issue
        """
        pass

    ############################################################################
    # Pull Request Events methods
    ############################################################################

    def pull_request_event(self, agent_id, (head_id, base_id, action)):
        """
        user requests a pull from a fork
        repo adds the pull request to the stack

        types: submit pull request, close pull request, assign pull request,
        unassign pull request, label pull request, unlabel pull request, 
        request review, remove review request, reopen pull request, 
        edit pull request
        """
        if base_id not in self.local_repos:
            print 'unknown repo id for push_event:', base_id
            return 'fail'
        self.local_repos[base_id].pull_request_event( 
            {'user': agent_id, 'head': head_id, 'action': action})
        self.log_event(agent_id, base_id, 'PullRequestEvent', action, time())

        return "success"

    ############################################################################
    # Other events
    ############################################################################
      
    def commit_comment_event(self, agent_id, (repo_id, commit_info)):
        """
        user requests to make a commit to the repo
        check if collab
        repo takes commit info and applies commit
        """

        # commit_info is assumed to be a comment string for now
        if repo_id not in self.local_repos:
            print 'unknown repo id for comment_comment_event:', repo_id
            return 'fail'
        self.local_repos[repo_id].commit_comment_event(agent_id, commit_info)
        self.log_event(agent_id, repo_id, 'CommitCommentEvent','None',time())
        return 'success'

    def push_event(self, agent_id, (repo_id, commit_to_push)):
        """
        user pushes to remote repository
        """

        if repo_id not in self.local_repos:
            print 'unknown repo id for push_event:', repo_id
            return 'fail'
        self.local_repos[repo_id].push_event(agent_id, commit_to_push)
        self.log_event(agent_id, repo_id, 'PushEvent','None',time())
        print 'agent ', agent_id, 'Pushed to repo id ', repo_id
        return 'success'

    def watch_event(self, agent_id, data):
        """
        user tells repo it will watch it quietly
        repo says okay
        returns {full_name_h, watching_date, watching_dow}
        """
        
        repo_id, user_info = data
        if repo_id in self.local_repos:
            self.local_repos[repo_id].watch_event(user_info)
            watch_info = {'full_name_h': self.local_repos[repo_id].full_name_h, 
                    'watching_date': time(), 
                    'watching_dow': None} # TODO: Internal simulation of DOW
            print agent_id, "is now watching", repo_id, "at", watch_info['watching_date']
            self.log_event(agent_id, repo_id, 'WatchEvent', 'None', time())
            return "Success", watch_info
        else:
            if repo_id in self.foreign_repos:
                raise NotImplementedError # TODO: Will add when we know how reps will be handled
            else:
                return 'Failure: repo not found'

    def public_event(self, agent_id, repo_id):
        """
        server toggles repo status
        repo sets status
        """

        if repo_id[0] in self.local_repos:
            self.log_event(agent_id, repo_id[0], 'PublicEvent', 'None', time())
            return self.local_repos[repo_id[0]].public_event(agent_id)
        else:
            if repo_id[0] in self.foreign_repos:
                raise NotImplementedError # TODO: Will add when we know how reps will be handled
            else:
                return 'Failure: repo not found'

    def fork_event(self, agent_id, fork_info):
        """
        server tells repo that it is being forked
        repo adds new fork to its info
        """
        pass

    def follow_event(self, agent_id, target_user_id):
        """
        server notifies target user that agent is following it
        """

        raise NotImplementedError # TODO: Not sure yet how to notify user

    def member_event(self, agent_id, collaborator_info):
        """
        user requests add a new collaborator to repo
        check if collab
        repo sends request to target user and awaits response
        if successful repo adds collaborator
        if unsuccessful repo doesn't add collaborator
        """

        if collaborator_info[0]['user_ght_id_h'] in self.users:
            if collaborator_info[0]['repo_ght_id_h'] in self.local_repos:
                self.log_event(agent_id, collaborator_info[0]['repo_ght_id_h'], 'MemberEvent', 'None', time())
                return self.local_repos[collaborator_info[0]['repo_ght_id_h']].member_event(agent_id, **(collaborator_info[0]))
            else:
                if collaborator_info[0]['repo_ght_id_h'] in self.foreign_repos:
                    raise NotImplementedError # TODO: Will add when we know how reps will be handled
                else:
                    return 'Failure: repo not found'
        else:
            return 'Failure: user not found'

    def pull_repo_event(self, agent_id, (repo_id)):
        """
        user pulls remove repository to local repository for further review
        """

        if repo_id not in self.local_repos:
            print 'unknown repo id for pull_repo_event:', repo_id
            return 'fail'

        self.log_event(agent_id, repo_id, 'PullEvent','None',time())
        print 'agent ', agent_id, 'pulled repo id ', repo_id
        return 'success'

    ############################################################################
    # Non git-related events
    ############################################################################

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

    def is_collaborator(self, agent_id, repo_id):
        """
        Returns True if agent is a collaborator on the repo
        Returns False if repo doesn't exist or agent is not a collaborator
        """

        if repo_id in self.local_repos:
            if agent_id in self.local_repos[repo_id].collaborators:
                return True

        # This check would be over other repos, will implement
        # when distribution structure is decided upon
        elif False:
            raise NotImplementedError

        return False

def save_object(obj, filename):
    """
    Save an object to file for later use.
    """
    
    file = open(filename, 'wb')
    pickle.dump(obj, file)
    file.close()

def load_object(filename):
    """
    Load a previously saved object.
    """
    
    file = open(filename, 'rb')
    return pickle.load(file)

if __name__ == '__main__':
    """
    """
    GitRepoHub(0, port=6000).run()