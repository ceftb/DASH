from dash import DASHAgent
import random
from git_user_agent import GitUserAgent
from git_repo_hub import GitRepoHub
from multiprocessing import Process

class HubManager(DASHAgent):
    """
    This class generates new hubs and can make them return their logs
    """

    def __init__(self, **kwargs):
        super(GitUserAgent, self).__init__()

        self.lowest_unassigned_port = 6000
        self.lowest_unassigned_hub_id = 0
        self.hubs = {} # {keyed by hub_id, valued by {host,port,process}
        self.primitiveActions([
            ('dump_event_log', self.dump_event_log), 
            ('return_event_log', self.return_event_log)])

    def connect_to_new_server(self, host, port):
        """
        Connect to another server
        """

        self.disconnect()
        self.server_host = host
        self.server_port = port
        self.establishConnection()

    def kill_hub(self, hub_id):

        if self.hubs[hub_id].is_alive():
            self.hubs[hub_id].terminate()
            self.hubs.pop(hub_id, None)

    def make_hub(self):
        """
        Generate hub with a given name and access port
        """

        hub_id = self.lowest_unassigned_hub_id
        self.lowest_unassigned_hub_id += 1
        port = self.lowest_unassigned_port
        self.lowest_unassigned_port += 1

        hub_process = Process(targe=run_hub, args=(hub_id, str(hub_id), port))
        hub_process.start()
        self.hubs[hub_id] = {'port':port, 'host':str(hub_id), 'proc':hub_process}

def run_hub(self, hub_id, host, port):
    """
    Starts a new hub worker
    """

    GitRepoHub(hub_id, host=host, port=port).run()

class WatcherExperiment(object):
    """
    This class manages the watcher experiment.
    In the watcher experiment one of three things can happen.
    (1) Create a new user with prob U
    (2) Pick a random user to add a new repo with prob R
    (3) Pick a random user to watch a new repo with prob W

    Pr(U) = U
    Pr(R) = R
    Pr(W) = 1 - U - R

    Where Sum(U,R,W) = 1, 0 < U,R,W < 1.

    A user will be selected according to their activity rank^(-beta)
    A repo will be selected according to their watch rank^(gamma)
    """

    action_types = [
        'make_user',
        'make_repo',
        'watch_repo',
    ]

    def __init__(self, U, R, beta, gamma):

        self.U = U
        self.R = R 
        self.W = 1 - U - R
        assert(U > 0)
        assert(R > 0)
        assert(abs(1 - U + R + W) < 0.0001) # Rough check that probs sum to 1


    def __call__(self, iterations=1):

        for i in iterations:
            self.pick_action()()

    def pick_action(self):

        chosen_type = random.choice(WatcherExperiment.action_types)

        for action_type in action_types:
            if chosen_type == action_type:
                return getattr(WatcherExperiment, chosen_type)

    def make_user(self):
        """
        """

        pass

    def make_repo(self):
        """
        """

        pass

    def watch_repo(self):
        """
        """

        pass

if __name__ == '__main__':
    """
    """

    # Parameters
