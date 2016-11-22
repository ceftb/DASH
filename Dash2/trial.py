# A trial is a single trial in an experiment. Each trial has some setup that defines a list of agents,
# an iterative period where the agents are dovetailed until some stopping criterion is met,
# and an objective function that defines what gets saved from each trial and processed in the Experiment class.


class Trial(object):
    def __init(self, max_iterations=-1):
        self.agents = []
        self.max_iterations = max_iterations
        self.iteration = 0

    # The initialize function sets up the agent list
    def initialize(self):
        pass

    # The trial's stopping criterion is met. By default, it checks each agent for a stopping
    # criterion and stops if either all the agents are ready to stop or a max iteration level is reached.
    def should_stop(self):
        if self.iteration >= self.max_iterations:
            return True
        if self.agents:
            for a in self.agents:
                if not self.agent_should_stop(a):
                    return False
        return True   # if not overridden, the trial will have no iterations

    # Default method for whether an agent should stop. By default, true, so if neither
    # this method nor should_stop are overridden, nothing will happen.
    def agent_should_stop(self, agent):
        return True

    def run(self):  # overridden in each subclass to do something useful
        self.initialize()
        for agent in self.agents:
            agent.traceLoop = False
        while not self.should_stop():
            for agent in self.agents:
                if not self.agent_should_stop(agent):
                    next_action = agent.agentLoop(max_iterations=1, disconnect_at_end=False)  # don't disconnect since will run again
                    self.process_after_agent_action(agent, next_action)
            self.process_after_iteration()
            self.iteration += 1
        self.process_after_run()
        for agent in self.agents:
            agent.disconnect()

    def process_after_agent_action(self, agent, action):  # do any book-keeping needed after each step by an agent
        pass

    def process_after_iteration(self):  # do any book-keeping needed after each iteration completes
        pass

    def process_after_run(self):  # do any book-keeping needed after the trial ends
        pass

    def output(self):  # overridden with a function to compute and return the output from the trial
        return 1

