import sys; sys.path.extend(['../../'])
from Dash2.github.git_repo import GitRepo


class ZkGitRepo():
    """
    An object representing a Github repository synchronized via ZooKeeper.
    Object is memory efficient and designed for large scale simulations
    """

    def __init__(self, id, **kwargs):
        self.id = int(id)
        # zookeeper synchronization:
        self.unsynchronized_actions_counter = 0 # number of events/actions with the repo since last synchronization
        self.is_node_shared = False # repo is shared if it is used on multiple dash worker nodes

        # model of the repo, statistic
        self.total_events_counter = kwargs.get("total_events_counter", 0)
        self.number_of_users = kwargs.get("number_of_users", 1)

    def sync(self, zk):
        if self.unsynchronized_actions_counter != 0:
            pass
            # sync

