import sys; sys.path.extend(['../../'])
from Dash2.core.world_hub import WorldHub
from Dash2.github.zk_repo import ZkRepo
from Dash2.github.git_repo_hub import GitRepoHub
import datetime

# Zookeeper repository hub
class ZkRepoHub(GitRepoHub):
    """
    A class that handles client requests and modifies the desired repositories
    """

    sync_event_counter = 0

    def __init__(self, zk, task_full_id, start_time, log_file):
        WorldHub.__init__(self, None)
        self.trace_handler = False
        ZkRepo.sync_event_callback = self.event_counter_callback

        self.zk = zk
        self.task_full_id = task_full_id
        self.exp_id, self.trial_id, self.task_num = task_full_id.split("-")  # self.task_num by default is the same as node id

        self.all_repos = {}  # keyed by repo id, valued by repo object
        self.repo_id_counter = 0
        self.log_file = log_file
        # global event clock
        self.time = start_time

    # call this method only for pre-existing repos
    def init_repo(self, repo_id, user_id=None, curr_time=0, is_node_shared=False, **kwargs):
        if not (repo_id in self.all_repos):
            self.all_repos[repo_id] = ZkRepo(id=repo_id, curr_time=curr_time, is_node_shared=is_node_shared, hub=self)
        else:
             pass # update repo properties here if needed


    # global event clock
    def set_curr_time(self, curr_time):
        self.time = curr_time

    def log_event(self, user_id, repo_id, event_type, subevent_type, time):
        self.log_file.write(str(user_id))
        self.log_file.write(",")
        self.log_file.write(str(repo_id))
        self.log_file.write(",")
        date = datetime.datetime.fromtimestamp(time)
        str_time = date.strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(str_time)
        self.log_file.write(",")
        self.log_file.write(event_type)
        #self.log_file.write(subevent_type)
        #self.log_file.write(",")
        self.log_file.write("\n")

    def processRegisterRequest(self, agent_id, aux_data):
        creation_time = self.time
        return ["success", aux_data["id"], creation_time]

    def create_new_repo_id(self):
        max_repo_id_path = "/experiments/" + str(self.exp_id) + "/" + str(self.trial_id) + "/" + str(self.trial_id) + "/max_repo_id"
        lock = self.zk.Lock(max_repo_id_path)
        lock.acquire()
        raw_data, _ = self.zk.get(max_repo_id_path)
        max_repo_id = int(raw_data)
        max_repo_id += 1
        self.zk.set(max_repo_id_path, str(max_repo_id))
        lock.release()
        return max_repo_id

    def event_counter_callback (self, repo_id, curr_time):
        ZkRepoHub.sync_event_counter += 1
        if ZkRepoHub.sync_event_counter % 1000 == 0 and ZkRepoHub.sync_event_counter > 0:
            print "Sync event: ", ZkRepoHub.sync_event_counter

    ############################################################################
    # Create/Delete Events (Tag/branch/repo)
    ############################################################################

    def create_repo_event(self, agent_id, (repo_info, )):
        """
        Requests that a git_repo_hub create and start a new repo given
        the provided repository information
        """
        repo_id = self.create_new_repo_id()
        self.all_repos[repo_id] = ZkRepo(id=repo_id, curr_time=self.time, is_node_shared=False, hub=self)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Repository', self.time)

        return 'success', repo_id

    def create_tag_event(self, agent_id, (repo_id, tag_name)):
        self.all_repos[repo_id].create_tag_event(tag_name, self.zk, self.time)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Tag', self.time)
        return 'success'

    def create_branch_event(self, agent_id, (repo_id, branch_name)):
        self.all_repos[repo_id].create_branch_event(branch_name, self.zk, self.time)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Branch', self.time)
        return 'success'

    def delete_tag_event(self, agent_id, (repo_id, tag_name)):
        self.all_repos[repo_id].delete_tag_event(tag_name)
        self.log_event(agent_id, repo_id, 'DeleteEvent', 'Tag', self.time)
        return 'success'

    def delete_branch_event(self, agent_id, (repo_id, branch_name)):
        self.all_repos[repo_id].delete_branch_event(branch_name)
        self.log_event(agent_id, repo_id, 'DeleteEvent', 'Branch', self.time)
        return 'success'

    ############################################################################
    # Issue comment Events methods
    ############################################################################

    def create_comment_event(self, agent_id, (repo_id, comment)):
        comment_id = self.all_repos[repo_id].create_comment_event({'user': agent_id, 'repo_id': repo_id, 'comment': comment})
        self.log_event(agent_id, repo_id, 'IssueCommentEvent', "created", self.time)
        return ["success", comment_id]

    def edit_comment_event(self, agent_id, (repo_id, comment, comment_id)):
        if self.all_repos[repo_id].edit_comment_event(comment_id, comment):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "edited", self.time)
            return ["Success"]
        else:
            return ["Failure: can't edit comment " + str(comment_id)]

    def delete_comment_event(self, agent_id, (repo_id, comment_id)):
        if self.all_repos[repo_id].delete_comment_event(comment_id):
            self.log_event(agent_id, repo_id, 'IssueCommentEvent', "deleted", self.time)
            return ["Success"]
        else:
            return ["Failure: can't delete comment " + str(comment_id)]

    ############################################################################
    # Issues Events methods
    ############################################################################
    def issue_opened_event(self, agent_id, (repo_id)):
        updated_at = self.time
        issue_id = self.all_repos[repo_id].issue_opened_event(self.zk, updated_at)
        self.log_event(agent_id, repo_id, 'IssuesEvent', 'opened', updated_at)
        return 'success', issue_id

    def issue_reopened_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_reopened_event(issue_id, self.zk, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'reopened', updated_at)
            return 'success'
        return 'failed, event alread open'

    def issue_closed_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_closed_event(issue_id, self.zk, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'closed', updated_at)
            return 'success'
        return 'failed, event alread closed'

    def issue_assigned_event(self, agent_id, (repo_id, issue_id, user_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_assigned_event(issue_id, self.zk, updated_at, user_id):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'assigned', updated_at)
            return 'success'
        return 'failed, to assign user to issue'

    def issue_unassigned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_assigned_event(issue_id, self.zk, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'unassigned', updated_at)
            return 'success'
        return 'failed, to unassign user'

    def issue_labeled_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_labeled_event(issue_id, self.zk, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'labeled', updated_at)
            return 'success'
        return 'failed, issue already labeled'

    def issue_unlabeled_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_unlabeled_event(issue_id, self.zk, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'unlabeled', updated_at)
            return 'success'
        return 'failed, issue already unlabeled'

    def issue_milestoned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_milestoned_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'milestoned', updated_at)
            return 'success'
        return 'failed, issue already milestone'

    def issue_demilestoned_event(self, agent_id, (repo_id, issue_id)):
        updated_at = self.time
        if self.all_repos[repo_id].issue_demilestoned_event(issue_id, updated_at):
            self.log_event(agent_id, repo_id, 'IssuesEvent', 'demilestoned', updated_at)
            return 'success'
        return 'failed, issue already demilestoned'

    ############################################################################
    # Pull Request Events methods
    ############################################################################

    def submit_pull_request_event(self, agent_id, (head_id, base_id)):
        updated_at = self.time
        request_id = self.all_repos[base_id].submit_pull_request_event(head_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'submit', updated_at)
        return 'success', request_id

    def close_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].close_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'close', updated_at)
        return 'success'

    def reopened_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].reopened_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'reopen', updated_at)
        return 'success'

    def label_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].label_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'label', updated_at)
        return 'success'

    def unlabel_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].label_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'unlabel', updated_at)
        return 'success'

    def review_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].review_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'review', updated_at)
        return 'success'

    def remove_review_pull_request_event(self, agent_id, (base_id, request_id)):
        updated_at = self.time
        self.all_repos[base_id].remove_review_pull_request_event(request_id, self.zk, updated_at)
        self.log_event(agent_id, base_id, 'PullRequestEvent', 'unreview', updated_at)
        return 'success'

    ############################################################################
    # Other events
    ############################################################################

    def commit_comment_event(self, agent_id, (repo_id, commit_info)):
        self.all_repos[repo_id].commit_comment_event(agent_id, commit_info)
        self.log_event(agent_id, repo_id, 'CommitCommentEvent', 'None', self.time)
        return 'success'

    def push_event(self, agent_id, (repo_id, commit_to_push)):
        self.all_repos[repo_id].push_event(agent_id, commit_to_push, self.zk, self.time)
        self.log_event(agent_id, repo_id, 'PushEvent', 'None', self.time)
        # print 'agent ', agent_id, 'Pushed to repo id ', repo_id
        return 'success'

    def watch_event(self, agent_id, data):
        repo_id, user_info = data
        self.all_repos[repo_id].watch_event(user_info)
        watch_info = {'full_name_h': self.all_repos[repo_id].full_name_h,
                      'watching_date': self.time,
                      'watching_dow': None}  # TODO: Internal simulation of DOW
        # print agent_id, "is now watching", repo_id, "at", watch_info['watching_date']
        self.log_event(agent_id, repo_id, 'WatchEvent', 'None', self.time)
        return "success", watch_info

    def public_event(self, agent_id, repo_id):
        self.log_event(agent_id, repo_id[0], 'PublicEvent', 'None', self.time)
        return self.all_repos[repo_id[0]].public_event(agent_id)

    def fork_event(self, agent_id, repo_id):
        self.log_event(agent_id, repo_id, 'ForkEvent', 'None', self.time)
        return "success"

    def follow_event(self, agent_id, target_user_id):
        self.log_event(agent_id, -1, 'FollowEvent', 'None', self.time)
        return "success"

    def member_event(self, agent_id, collaborator_info):
        self.log_event(agent_id, collaborator_info[0]['repo_ght_id_h'], 'MemberEvent', 'None', self.time)
        return self.all_repos[collaborator_info[0]['repo_ght_id_h']].member_event(agent_id, **(collaborator_info[0]))

    def pull_repo_event(self, agent_id, (repo_id)):
        self.log_event(agent_id, repo_id, 'PullEvent', 'None', self.time)
        # print 'agent ', agent_id, 'pulled repo id ', repo_id
        return 'success'

