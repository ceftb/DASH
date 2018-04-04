import sys; sys.path.extend(['../../'])
import json

class ZkRepo():
    """
    An object representing a Github repository synchronized via ZooKeeper.
    Object is memory efficient and designed for large scale simulations
    """
    sync_event_callback = None

    def __init__(self, id, curr_time, **kwargs):
        self.id = int(id)
        # zookeeper synchronization:
        self.unsynchronized_events_counter = 0 # number of events/actions with the repo since last synchronization
        self.last_time_synchronized = curr_time
        self.last_time_updated = curr_time
        self.is_node_shared = kwargs.get("is_node_shared", False) # repo is shared if it is used on multiple dash workers
        self.hub = kwargs.get("hub", None)

        # model of the repo, statistic
        self.total_events_counter = kwargs.get("total_events_counter", 0)
        self.number_of_users = kwargs.get("number_of_users", 1)


    def sync(self, zk, curr_time):
        if self.is_sync_needed(curr_time):
            # sync
            repo_path = "/experiments/" + str(self.hub.exp_id) + "/trials/" + str(self.hub.trial_id) + "/repos/" + str(self.id)
            if zk.exists(repo_path) is None:
                zk.ensure_path(repo_path)
                zk.set(repo_path, json.dumps({"repo_activity": 0}))
            else:
                lock = zk.Lock(repo_path)
                lock.acquire(repo_path)
                raw_data, _ = zk.get(repo_path)
                data = None
                if raw_data is not None and raw_data != "":
                    data = json.loads(raw_data)
                else:
                    data = {"repo_activity": 0}
                data["repo_activity"] = int(data["repo_activity"]) + 1
                zk.set(repo_path, json.dumps(data))
                lock.release()

            self.unsynchronized_events_counter = 0
            self.last_time_synchronized = curr_time
            # callback
            if ZkRepo.sync_event_callback is not None:
                ZkRepo.sync_event_callback(self.id, curr_time)

    def is_sync_needed(self, curr_time, max_number_unsynced_events=10, max_time_delta=3600):
        if self.is_node_shared is False:
            return False
        if self.unsynchronized_events_counter > max_number_unsynced_events or curr_time - self.last_time_synchronized > max_time_delta:
            return True
        return False

    ############################################################################
    # Below methods match RepoHub actions - called by repo_hub
    ############################################################################

    def issue_opened_event(self, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return 111

    def issue_reopened_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_closed_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_assigned_event(self, issue_id, zk, curr_time, user_id):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_unassigned_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_labeled_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_unlabeled_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_milestoned_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def issue_demilestoned_event(self, issue_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def create_comment_event(self, comment_info):
        pass
        self.unsynchronized_events_counter += 1
        return 111

    def edit_comment_event(self, comment_id, comment):
        pass
        self.unsynchronized_events_counter += 1
        return True

    def delete_comment_event(self, comment_id):
        pass
        self.unsynchronized_events_counter += 1
        return True

    def commit_comment_event(self, agent_id, commit_info):
        pass
        self.unsynchronized_events_counter += 1
        return True

    def create_tag_event(self, tag_name, tag_creation_date):
        pass
        self.unsynchronized_events_counter += 1
        return True

    def create_branch_event(self, branch_name, branch_creation_date):
        pass
        self.unsynchronized_events_counter += 1
        return True


    def delete_tag_event(self, tag_name):
        pass
        self.unsynchronized_events_counter += 1
        return True


    def delete_branch_event(self, branch_name):
        pass
        self.unsynchronized_events_counter += 1
        return True

    def member_event(self, agent_id, target_agent, action, permissions=None):
        self.unsynchronized_events_counter += 1
        return "Successfully removed collaborator"

    def push_event(self, agent_id, commit_to_push, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return "Successfully pushed"

    def submit_pull_request_event(self, head_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return 111

    def close_pull_request_event(self, request_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def reopened_pull_request_event(self, request_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def label_pull_request_event(self, request_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def review_pull_request_event(self, request_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def remove_review_pull_request_event(self, request_id, zk, curr_time):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True

    def watch_event(self, user_info):
        self.unsynchronized_events_counter += 1
        return "Success"


    def public_event(self, agent_id):
        self.unsynchronized_events_counter += 1
        return "Success"

    def fork_event(self, agent_id, fork_info):
        self.unsynchronized_events_counter += 1
        return True

