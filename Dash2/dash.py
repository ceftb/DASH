from system1 import System1Agent
#from system2 import goalWeight, goalRequirements, printGoals, knownTuple, knownFalseTuple, known, substitute, chooseAction, readAgent, isConstant, isKnown, preferPlan, forget, isTransient, sleep
from system2 import System2Agent, substitute, isConstant
from client import Client


class DASHAgent(Client, System2Agent, System1Agent):

    def __init__(self):
        Client.__init__(self)
        System2Agent.__init__(self)
        System1Agent.__init__(self)
        self.primitiveActionDict = dict()
        self.traceUpdate = False
        # Although 'forget' is defined in system2, it is assigned primitive here because
        # that module is compiled first
        self.primitiveActions([('forget', self.forget), ['sleep', self.sleep]])

    # This is in the java part in the old agent
    def agentLoop(self, maxIterations=-1):
        nextAction = self.chooseAction()
        iteration = 0
        while nextAction is not None and (maxIterations < 0 or iteration < maxIterations):
            print "Next action is ", nextAction
            result = self.performAction(nextAction)
            self.updateBeliefs(result, nextAction)
            nextAction = self.chooseAction()
            iteration += 1
        if nextAction is None:
            print "No action chosen"
        elif maxIterations >= 0 and iteration >= maxIterations:
            print "Finished finite agent cycles:", maxIterations, "with", iteration

    def primitiveActions(self, l):
        # Add the items into the set of known primitive actions
        # mapping name to function
        for item in l:
            if isinstance(item, basestring):
                self.primitiveActionDict[item] = item # store the name and look for the function at planning time
            else:
                self.primitiveActionDict[item[0]] = item[1]

    def isPrimitive(self, goal):
        return goal[0] in self.primitiveActionDict

    def performAction(self, action):
        if self.isPrimitive(action):
            function = self.primitiveActionDict[action[0]]
            return function(action)

    def updateBeliefs(self, result, action):
        if self.traceUpdate:
            print "Updating beliefs based on action", action, "with result", result
        if not result and not self.isTransient(action):
            print "Adding known false", action
            self.knownFalseTuple(action)
        if isinstance(result, list):
            for bindings in result:
                concreteResult = substitute(action, bindings)
                if not self.isTransient(concreteResult):
                    self.knownTuple(concreteResult)   # Mark action as performed/known
                    self.knownTuple(('performed', concreteResult))   # Adding both lets both idioms be used in the agent code.

    # Generic primitive actions

    # A null action that always succeeds, useful for dummy steps
    def succeed(self, action):
        #print "Primitive action", action, "trivially succeeds"
        return [{'performed': action}]
