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
    # General event handler
    ############################################################################

    def event_handler(self, agent_id, event, curr_time, zk):
        self.last_time_updated = curr_time
        self.unsynchronized_events_counter += 1
        self.sync(zk, curr_time)
        return True
