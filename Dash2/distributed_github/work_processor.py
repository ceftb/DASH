import sys; sys.path.extend(['../../'])
import random
from kazoo.client import KazooClient
from Dash2.github.git_user_agent import GitUserAgent
from zk_repo_hub import GitRepoHub

# WorkProcessor class is responsible for running experiment trial on a node in cluster
class WorkProcessor:
    def __init__(self, zk, host_id, exp_id, trial_id, task_id):
        self.agents = []
        self.zk = zk
        self.host_id = host_id
        self.exp_id = exp_id
        self.trial_id = trial_id
        self.task_id = task_id
        self.task_path = "/tasks/nodes/" + str(host_id) + "/" + str(exp_id) + "/" + str(trial_id) + "/" + str(task_id)
        self.hub = GitRepoHub(1)  # FIXME register in zk
        self.prob_create_new_agent = float(self.zk.get(self.task_path + "/prob_create_new_agent")[0])
        self.max_iterations = int(self.zk.get(self.task_path + "/max_iterations")[0])
        self.iteration = 0

    def process_task(self):
        if self.zk is not None and self.task_path is not None:

            for agent in self.agents:
                agent.traceLoop = False
            while not self.should_stop():
                self.run_one_iteration()
                self.process_after_iteration()
                self.iteration += 1
            self.process_after_run()
            for agent in self.agents:
                agent.disconnect()

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



    # register a new agent in Zookeeper and return its id
    def register_agent(self, agent):
        lock = self.zk.Lock(self.curr_trial_path + "/agent_id_counter")
        with lock:  # blocks waiting for lock acquisition
            agent.id = self.agent_id_generator.value
            self.agent_id_generator += 1
        # print "next id " + str(self.agent_id_generator.value)
        self.zk.ensure_path("/experiments/" + str(self.exp_id) + "/trials/" + str(self.trial_id) + "/agents/"
                            + str(agent.id) + "/")

        # TBD init other agent attributes if needed
        # assign agent to a worker node


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
