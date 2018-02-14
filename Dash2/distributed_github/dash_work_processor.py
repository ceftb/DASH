import sys; sys.path.extend(['../../'])
import random
from kazoo.client import KazooClient
import json
from Dash2.github.git_user_agent import GitUserAgent
from zk_repo_hub import GitRepoHub

# TBD: This class to be moved into core module when zookeeper version of DASH is stable
# WorkProcessor class is responsible for running experiment trial on a node in cluster
class DashWorkProcessor:
    def __init__(self, zk, host_id, task_id, data):
        self.agents = []
        self.zk = zk
        self.host_id = host_id
        self.exp_id, self.trial_id, _= task_id.split("-")
        self.task_id = task_id
        self.max_iterations = int(data["max_iterations"])
        self.prob_create_new_agent = float(data["prob_create_new_agent"])

        self.hub = GitRepoHub(1)  # FIXME register in zk
        self.iteration = 0

    def process_task(self):
        if self.zk is not None and self.task_id is not None:
            for agent in self.agents:
                agent.traceLoop = False
            while not self.should_stop():
                self.run_one_iteration()
                self.process_after_iteration()
                self.iteration += 1
            self.process_after_run()
            for agent in self.agents:
                agent.disconnect()

            result_path = "/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/nodes/" + str(self.host_id) + "/dependent_variables/"
            dep_vars = self.dependent()
            data = json.dumps(dep_vars)
            # self.zk.ensure_path(result_path)
            self.zk.set(result_path, data)

    def should_stop(self):
        if self.max_iterations > 0 and self.iteration >= self.max_iterations:
            print 'reached end of iterations for trial'
            return True
        if self.agents:
            for a in self.agents:
                if not self.agent_should_stop(a):
                    return False
        if self.max_iterations > 0 and self.iteration < self.max_iterations:
            return False  # Follow the number of iterations by default
        else:
            return True

    def run_one_iteration(self):
        if not self.agents or random.random() < self.prob_create_new_agent:  # Have to create an agent in the first step
            a = GitUserAgent(useInternalHub=True, hub=self.hub, trace_client=False)
            a.trace_client = False  # cut chatter when connecting and disconnecting
            a.traceLoop = False  # cut chatter when agent runs steps
            a.trace_github = False  # cut chatter when acting in github world
            # print 'created agent', a
            self.agents.append(a)
        else:
            a = random.choice(self.agents)
        a.agentLoop(max_iterations=1, disconnect_at_end=False)


    def dependent(self):
        return [self.num_agents(), self.num_repos(), self.total_agent_activity()]

    # Measures #
    # These are defined above as measures
    def num_agents(self):
        return len(self.agents)

    # Measures should probably query the hub or use a de facto trace soon
    def num_repos(self):
        return sum([len(a.owned_repos) for a in self.agents])

    def total_agent_activity(self):
        return sum([a.total_activity for a in self.agents])

    # Default method for whether an agent should stop. By default, true, so if neither
    # this method nor should_stop are overridden, nothing will happen.
    def agent_should_stop(self, agent):
        return True

    def process_after_agent_action(self, agent, action):  # do any book-keeping needed after each step by an agent
        pass

    def process_after_iteration(self):  # do any book-keeping needed after each iteration completes
        pass

    def process_after_run(self):  # do any book-keeping needed after the trial ends and before agents are disconnected
        pass