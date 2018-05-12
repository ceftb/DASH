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
        date = datetime.datetime.fromtimestamp(time)
        str_time = date.strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(str_time)
        self.log_file.write(",")
        self.log_file.write(event_type)
        self.log_file.write(",")
        self.log_file.write(str(user_id))
        self.log_file.write(",")
        self.log_file.write(str(repo_id))
        #self.log_file.write(subevent_type)
        #self.log_file.write(",")
        self.log_file.write("\n")

    def processRegisterRequest(self, agent_id, aux_data):
        creation_time = self.time
        return ["success", aux_data["id"], creation_time]

    def _create_new_repo_id(self):
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
        repo_id = self._create_new_repo_id()
        self.all_repos[repo_id] = ZkRepo(id=repo_id, curr_time=self.time, is_node_shared=False, hub=self)
        self.log_event(agent_id, repo_id, 'CreateEvent', 'Repository', self.time)

        return 'success', repo_id

    ############################################################################
    # Other events
    ############################################################################

    def event_handler(self, repo_id, agent_id, event, data=None):
        self.log_event(agent_id, repo_id, event, 'None', self.time)
        self.all_repos[repo_id].event_handler(agent_id, event, self.time, self.zk)
        return 'success'


