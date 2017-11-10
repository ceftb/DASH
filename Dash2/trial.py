# A trial is a single trial in an experiment. Each trial has some setup that defines a list of agents,
# an iterative period where the agents are dovetailed until some stopping criterion is met,
# and an objective function that defines what gets saved from each trial and processed in the Experiment class.


class Trial(object):
    def __init__(self, data={}, max_iterations=-1):
        self.agents = []
        self.data = data  # This passes parameter data to be used in the trial. The names are available as attributes
        # Initialize from parameter list first, then any passed data
        if self.__class__.parameters:
            print 'initializing trial from parameters'
            for p in self.__class__.parameters:
                setattr(self, p.name, p.distribution.sample() if p.default is None else p.default)
        print 'initializing trial with data', data
        self.max_iterations = max_iterations
        for attr in data:
            setattr(self, attr, data[attr])
        self.iteration = 0

    # The initialize function sets up the agent list
    def initialize(self):
        pass

    # The trial's stopping criterion is met. By default, it checks each agent for a stopping
    # criterion and stops if either all the agents are ready to stop or a max iteration level is reached.
    def should_stop(self):
        if self.max_iterations > 0 and self.iteration >= self.max_iterations:
            print 'reached end of iterations for trial'
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

    def process_after_run(self):  # do any book-keeping needed after the trial ends and before agents are disconnected
        pass
