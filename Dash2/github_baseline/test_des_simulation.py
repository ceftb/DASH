import sys; sys.path.extend(['../../'])
import time
from heapq import heappush, heappop
from Dash2.github_baseline.zk_repo import ZkRepo
from Dash2.github_baseline.git_user_agent import GitUserAgent
from zk_repo_hub import ZkRepoHub

def create_repos(number_of_repos):
    start_time = time.time()
    print "Creating repos ... "
    repos = []
    for i in range(0, number_of_repos):
        repos.append(ZkRepo(i, 0))
    end_time = time.time()
    print "Repos created. Time: ", end_time - start_time
    return repos

if __name__ == "__main__":
    number_of_repos = 3100000
    number_of_agents = 10
    number_of_events_to_simulate = 1000000
    max_time = 5184000.0 # 60 days = 5184000.0 seconds
    start_sim_time = 0.0

    # populate repo frequencies
    repos = create_repos(number_of_repos) # memory test
    repos = {101: 10, 102: 20, 103: 30}

    # zk hub and log file
    log_file = open('event_log_file.txt', 'w')
    github = ZkRepoHub(None, "1-1-1", start_sim_time, log_file)
    github.all_repos = {101: ZkRepo(id=101, curr_time=0, is_node_shared=False),
                        102: ZkRepo(id=102, curr_time=0, is_node_shared=False),
                        103: ZkRepo(id=103, curr_time=0, is_node_shared=False)}

    # populate users/agents
    start_time = time.time()
    print "Creating agents ... "
    events_heap = []
    agents = list()
    for id in range(0, number_of_agents):
        agent = GitUserAgent(id=int(id), useInternalHub=True, hub=github, trace_client=False, traceLoop=False, trace_github=False, freqs=repos)
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
            print "iteration: ", event_counter, "time per 100K: ", rate_stop_time - rate_start_time
            rate_start_time = time.time()
    end_time = time.time()
    print "Simulation of simulation is completed. Time: ", end_time - start_time, \
        " Number repos created: ", len(github.all_repos), " Number sync events: ", github.sync_event_counter

    log_file.close()
    cmd = raw_input("Press any key to exit")


