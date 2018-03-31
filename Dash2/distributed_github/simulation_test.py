import sys; sys.path.extend(['../../'])
from kazoo.client import KazooClient
import time
import json
import random
from heapq import heappush, heappop
from Dash2.distributed_github.zk_git_repo import ZkGitRepo
from Dash2.github.git_user_agent import GitUserAgent
from zk_repo_hub import ZkRepoHub

class TestAgent(GitUserAgent):
    def __init__(self, id, hub):
        GitUserAgent.__init__(self, id=int(id), useInternalHub=True, hub=hub, trace_client=False, traceLoop=False, trace_github=False)
        self.traceLoop = False
        self.trace_github = False

    def next_event_time(self, curr_time, max_time):
        return random.uniform(curr_time + 0.5, max_time)

def create_repos(number_of_repos):
    start_time = time.time()
    print "Creating repos ... "
    repos = []
    for i in range(0, number_of_repos):
        repos.append(ZkGitRepo(id=i))
    end_time = time.time()
    print "Repos created. Time: ", end_time - start_time
    return repos

if __name__ == "__main__":
    number_of_repos = 2
    number_of_agents = 50000
    number_of_events_to_simulate = 500000
    max_time = 1000000.0
    start_sim_time = 0.0

    # memory test for repo objects
    #repos = create_repos(number_of_repos)

    # zk hub and log file
    log_file = open('event_log_file.txt', 'w')
    github = ZkRepoHub(None, "1-1-1", start_sim_time, log_file)

    # memory test for user/agent objects
    start_time = time.time()
    print "Creating agents ... "
    events_heap = []
    agents = list()
    for id in range(0, number_of_agents):
        agent = TestAgent(id, github)
        agents.append(agent)
        heappush(events_heap, (agent.next_event_time(0.0, max_time), agent.id))
    end_time = time.time()
    print "Agents created. Time: ", end_time - start_time

    # discrete event simulation test
    start_time = time.time()
    print "Running simulation of simulation ... "
    rate_start_time = time.time()
    for event_counter in range(0, number_of_events_to_simulate):
        event_time, agent_id = heappop(events_heap)
        github.set_curr_time(event_time)
        agents[int(agent_id)].agentLoop(max_iterations=1, disconnect_at_end=False)
        heappush(events_heap, (agents[int(agent_id)].next_event_time(event_time, max_time), agent_id))
        if event_counter % 100000 == 0 and event_counter > 0:
            rate_stop_time = time.time()
            print "iteration: ", event_counter, "time per 10K: ", rate_stop_time - rate_start_time
            rate_start_time = time.time()
    end_time = time.time()
    print "Simulation of simulation is completed. Time: ", end_time - start_time, " Number repos created: ", len(github.all_repos)

    log_file.close()
    cmd = raw_input("Press any key to exit")


