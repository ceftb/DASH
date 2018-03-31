import sys; sys.path.extend(['../../'])
from Dash2.core.world_hub import WorldHub
from Dash2.distributed_github.zk_git_repo import ZkGitRepo
from Dash2.github.git_repo_hub import GitRepoHub
from time import time
import json
import pickle


# Zookeeper repository hub
class ZkRepoHub(GitRepoHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    def __init__(self, zk, task_full_id, log_file):
        WorldHub.__init__(self, None)
        self.zk = zk
        self.task_full_id = task_full_id
        self.exp_id, self.trial_id, self.task_num = task_full_id.split("-")  # self.task_num by default is the same as node id

        self.users = set()  # User ids
        self.all_repos = {}  # keyed by repo id, valued by repo object
        self.repo_hub_id = 1
        self.local_event_log = []  # Each log item stores a dictionary with keys 'userID', 'repoID', 'eventType', 'subeventtype', 'time'
        self.trace_handler = False
        self.local_repo_id_counter = 0
        self.log_file = log_file

    def init_repo(self, zk, repo_id, user_id):
        pass

    def log_event(self, user_id, repo_id, event_type, subevent_type, time):
        self.log_file.write(str(time))
        self.log_file.write(",")
        self.log_file.write(str(user_id))
        self.log_file.write(",")
        self.log_file.write(str(repo_id))
        self.log_file.write(",")
        self.log_file.write(event_type)
        self.log_file.write(",")
        self.log_file.write(subevent_type)
        self.log_file.write("\n")

    def processRegisterRequest(self, agent_id, aux_data):
        '''
        if (agent_id == None):
            agent_id = int(aux_data["id"])
        self.log_event(agent_id, None, "CreateUser", "None", creation_time)

        sub_tree_1 = agent_id % 10

        agent_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/users/" + str(agent_id % 100) + "/" + str(agent_id)
        self.zk.ensure_path(agent_path)
        raw_data, _ = self.zk.get(agent_path)
        data = None
        if raw_data is not None and raw_data != "":
            data = json.loads(raw_data)
        else:
            data = {"freqs": {}}
        data["freqs"] = aux_data["freqs"]
        self.zk.set(agent_path, json.dumps(data))
        '''
        creation_time = time()
        return ["success", aux_data["id"], creation_time]

    ############################################################################
    # Create/Delete Events (Tag/branch/repo)
    ############################################################################

    def create_repo_event(self, agent_id, (repo_info, )):
        """
        Requests that a git_repo_hub create and start a new repo given
        the provided repository information
        """

        repo_id = self.local_repo_id_counter
        self.local_repo_id_counter += 1
        # print('Request to create repo from', agent_id, 'for', repo_info)
        repo_creation_date = time()
        repo_info['created_at'] = repo_creation_date
        self.all_repos[repo_id] = ZkGitRepo(repo_id, **repo_info)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Repository', repo_creation_date)
        '''
        repo_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/repos"
        self.zk.ensure_path(repo_path)
        raw_data, _ = self.zk.get(repo_path)
        data = None
        if raw_data is not None and raw_data != "":
            data = json.loads(raw_data)
        else:
            data = {"number_of_repos": 0}
        data["number_of_repos"] = int(data["number_of_repos"]) + 1
        data["last_repo_id"] = repo_id
        self.zk.set(repo_path, json.dumps(data))
        '''
        return 'success', repo_id

    def create_tag_event(self, agent_id, (repo_id, tag_name)):
        tag_creation_date = time()
        self.all_repos[repo_id].create_tag_event(tag_name, tag_creation_date)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Tag', tag_creation_date)
        return 'success'

    def create_branch_event(self, agent_id, (repo_id, branch_name)):
        branch_creation_date = time()
        self.all_repos[repo_id].create_branch_event(branch_name, branch_creation_date)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Branch', branch_creation_date)
        return 'success'

    def delete_tag_event(self, agent_id, (repo_id, tag_name)):
        tag_deletion_date = time()
        self.all_repos[repo_id].delete_tag_event(tag_name)
        self.log_event(agent_id, repo_id, 'DeleteEvent', 'Tag', tag_deletion_date)
        return 'success'

    def delete_branch_event(self, agent_id, (repo_id, branch_name)):
        branch_deletion_date = time()
        self.all_repos[repo_id].delete_branch_event(branch_name)
        self.log_event(agent_id, repo_id, 'DeleteEvent', 'Branch', branch_deletion_date)
        return 'success'

    ############################################################################
    # Issue comment Events methods
    ############################################################################

    def create_comment_event(self, agent_id, (repo_id, comment)):
        comment_id = self.all_repos[repo_id].create_comment_event({'user': agent_id, 'repo_id': repo_id, 'comment': comment})
        self.log_event(agent_id, repo_id, 'IssueCommentEvent', "created", time())
        return ["success", comment_id]

    def edit_comment_event(self, agent_id, (repo_id, comment, comment_id)):
        if self.all_repos[repo_id].edit_comment_event(comment_id, comment):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "edited", time())
            return ["Success"]
        else:
            return ["Failure: can't edit comment " + str(comment_id)]

    def delete_comment_event(self, agent_id, (repo_id, comment_id)):
        if self.all_repos[repo_id].delete_comment_event(comment_id):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "deleted", time())
            return ["Success"]
        else:
            return ["Failure: can't delete comment " + str(comment_id)]

    ############################################################################
    # Issues Events methods
    ############################################################################
    def issue_opened_event(self, agent_id, (repo_id)):
        updated_at = time()
        issue_id = self.all_repos[repo_id].issue_opened_event(updated_at)
        self.log_event(agent_id, repo_id, 'IssuesEvent', 'opened', updated_at)
        return 'success', issue_id

    def issue_reopened_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_reopened_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'reopened', updated_at)
            return 'success'
        return 'failed, event alread open'

    def issue_closed_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_closed_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'closed', updated_at)
            return 'success'
        return 'failed, event alread closed'

    def issue_assigned_event(self, agent_id, (repo_id, issue_id, user_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_assigned_event(issue_id, updated_at, user_id):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'assigned', updated_at)
            return 'success'
        return 'failed, to assign user to issue'

    def issue_unassigned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_assigned_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'unassigned', updated_at)
            return 'success'
        return 'failed, to unassign user'

    def issue_labeled_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_labeled_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'labeled', updated_at)
            return 'success'
        return 'failed, issue already labeled'

    def issue_unlabeled_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_unlabeled_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'unlabeled', updated_at)
            return 'success'
        return 'failed, issue already unlabeled'

    def issue_milestoned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_milestoned_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'milestoned', updated_at)
            return 'success'
        return 'failed, issue already milestone'

    def issue_demilestoned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = time()
        if self.all_repos[repo_id].issue_demilestoned_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'demilestoned', updated_at)
            return 'success'
        return 'failed, issue already demilestoned'

    ############################################################################
    # Pull Request Events methods
    ############################################################################

    def submit_pull_request_event(self, agent_id, (head_id, base_id)):
        updated_at = time()
        request_id = self.all_repos[base_id].submit_pull_request_event(head_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'submit', updated_at)
        return 'success', request_id

    def close_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].close_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'close', updated_at)
        return 'success'

    def reopened_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].reopened_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'reopen', updated_at)
        return 'success'

    def label_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].label_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'label', updated_at)
        return 'success'

    def unlabel_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].label_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'unlabel', updated_at)
        return 'success'

    def review_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].review_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'review', updated_at)
        return 'success'

    def remove_review_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = time()
        self.all_repos[base_id].remove_review_pull_request_event(request_id, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'unreview', updated_at)
        return 'success'

    ############################################################################
    # Other events
    ############################################################################

    def commit_comment_event(self, agent_id, (repo_id, commit_info)):
        self.all_repos[repo_id].commit_comment_event(agent_id, commit_info)
        self.log_event(agent_id, repo_id, 'CommitCommentEvent', 'None', time())
        return 'success'

    def push_event(self, agent_id, (repo_id, commit_to_push)):
        self.all_repos[repo_id].push_event(agent_id, commit_to_push)
        self.log_event(agent_id, repo_id, 'PushEvent', 'None', time())
        # print 'agent ', agent_id, 'Pushed to repo id ', repo_id
        return 'success'

    def watch_event(self, agent_id, data):
        repo_id, user_info = data
        self.all_repos[repo_id].watch_event(user_info)
        watch_info = {'full_name_h': self.all_repos[repo_id].full_name_h,
                      'watching_date': time(),
                      'watching_dow': None}  # TODO: Internal simulation of DOW
        # print agent_id, "is now watching", repo_id, "at", watch_info['watching_date']
        self.log_event(agent_id, repo_id, 'WatchEvent', 'None', time())
        return "success", watch_info

    def public_event(self, agent_id, repo_id):
        self.log_event(agent_id, repo_id[0], 'PublicEvent', 'None', time())
        return self.all_repos[repo_id[0]].public_event(agent_id)

    def fork_event(self, agent_id, repo_id):
        self.log_event(agent_id, repo_id, 'ForkEvent', 'None', time())
        return "success"

    def follow_event(self, agent_id, target_user_id):
        self.log_event(agent_id, -1, 'FollowEvent', 'None', time())
        return "success"

    def member_event(self, agent_id, collaborator_info):
        self.log_event(agent_id, collaborator_info[0]['repo_ght_id_h'], 'MemberEvent', 'None', time())
        return self.all_repos[collaborator_info[0]['repo_ght_id_h']].member_event(agent_id, **(collaborator_info[0]))

    def pull_repo_event(self, agent_id, (repo_id)):
        self.log_event(agent_id, repo_id, 'PullEvent', 'None', time())
        # print 'agent ', agent_id, 'pulled repo id ', repo_id
        return 'success'

