from system1 import System1Agent
#from system2 import goalWeight, goalRequirements, printGoals, knownTuple, knownFalseTuple, known, substitute, chooseAction, readAgent, isConstant, isKnown, preferPlan, forget, isTransient, sleep
from system2 import System2Agent, substitute, isConstant, isVar
from client import Client


class DASHAgent(Client, System2Agent, System1Agent):

    def __init__(self):
        Client.__init__(self)
        System2Agent.__init__(self)
        System1Agent.__init__(self)
        self.primitiveActionDict = dict()
        self.traceUpdate = False
        self.traceAction = False
        # Although 'forget' is defined in system2, it is assigned primitive here because
        # that module is compiled first
        self.primitiveActions([('forget', self.forget), ['sleep', self.sleep]])

    # This is in the java part in the old agent
    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        next_action = self.chooseAction()
        iteration = 0
        while next_action is not None and (max_iterations < 0 or iteration < max_iterations):
            if self.traceAction:
                print "Next action is ", next_action
            result = self.performAction(next_action)
            self.updateBeliefs(result, next_action)
            next_action = self.chooseAction()
            iteration += 1
        if next_action is None:
            print "No action chosen"
        elif 0 <= max_iterations <= iteration:
            print "Finished finite agent cycles:", max_iterations, "with", iteration
        print "Exiting simulation."
        if disconnect_at_end:
            self.disconnect()
        # return the action chosen so the caller can tell if there is more for the agent to do
        return next_action

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
            if self.traceUpdate:
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
