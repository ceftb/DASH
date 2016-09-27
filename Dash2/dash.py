from system1 import System1Agent
from system2 import System2Agent, substitute, isConstant, isVar
from client import Client
import re


class DASHAgent(Client, System2Agent, System1Agent):

    def __init__(self):
        Client.__init__(self)
        System2Agent.__init__(self)
        System1Agent.__init__(self)
        self.primitiveActionDict = dict()
        # Activation threshold at which actions suggested by system 1 will be considered over deliberation
        # A low threshold will produce more 'impulsive' actions
        self.system1_threshold = 0.1
        self.traceUpdate = False
        self.traceAction = False
        # Although 'forget' is defined in system2, it is assigned primitive here because
        # that module is compiled first
        self.primitiveActions([('forget', self.forget), ['sleep', self.sleep]])

    # This is in the java part in the old agent
    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        self.spreading_activation()
        next_action = self.choose_action()
        iteration = 0
        while next_action is not None and (max_iterations < 0 or iteration < max_iterations):
            if self.traceAction:
                print "Next action is ", next_action
            result = self.performAction(next_action)
            self.update_beliefs(result, next_action)
            self.spreading_activation()
            next_action = self.choose_action()
            self.system1_decay()
            iteration += 1
        if next_action is None:
            print "Exiting simulation: no action chosen"
        elif 0 <= max_iterations <= iteration:
            print "Exiting simulation: finished finite agent cycles:", iteration, "of max", max_iterations
        if disconnect_at_end:
            self.disconnect()
        # return the action chosen so the caller can tell if there is more for the agent to do
        return next_action

    def choose_action(self):
        system1_actions = self.actions_over_threshold(threshold=self.system1_threshold)
        if system1_actions and self.reject_reasoning(system1_actions):
            return system1_actions[0].node_to_action()  # will ultimately choose
        system2_action = self.choose_action_by_reasoning()
        # For now always go with the result of reasoning if it was performed
        return system2_action

    # If system1 proposes some actions, should the agent just go with them or opt to employ deliberative reasoning?
    def reject_reasoning(self, system1_action_nodes):
        # print 'considering system1 suggested actions ', [n.fact[1:] for n in system1_action_nodes]
        return True  # try system 1 if it's available

    def primitiveActions(self, l):
        # Add the items into the set of known primitive actions
        # mapping name to function
        for item in l:
            if isinstance(item, basestring):
                self.primitiveActionDict[item] = item # store the name and look for the function at planning time
            else:
                self.primitiveActionDict[item[0]] = item[1]

    # A primitive action is declared in primitiveActionDict, or it might be a method
    # on the agent with the same name, or the same name with camelCase converted to underscores
    def isPrimitive(self, goal):
        predicate = goal[0]
        # Protect some predicates from being treated as primitive by this permissive method
        if predicate in ['known']:
            return False
        if predicate in self.primitiveActionDict:
            return True
        if hasattr(self, predicate) and callable(getattr(self, predicate)):
            return True
        underscore_action = convert_camel(predicate)
        if hasattr(self, underscore_action) and callable(getattr(self, underscore_action)):
            return True
        return False

    # This format is now inefficient since we have different ways that a predicate can be a primitive action
    def performAction(self, action):
        if self.isPrimitive(action):
            predicate = action[0]
            if predicate in self.primitiveActionDict:
                function = self.primitiveActionDict[action[0]]
            elif hasattr(self, predicate) and callable(getattr(self, predicate)):
                function = getattr(self, predicate)
            else:
                underscore_action = convert_camel(predicate)
                if hasattr(self, underscore_action) and callable(getattr(self, underscore_action)):
                    function = getattr(self, underscore_action)
                else:
                    return
            return function(action)

    def update_beliefs(self, result, action):
        if self.traceUpdate:
            print "Updating beliefs based on action", action, "with result", result
        if not result and not self.isTransient(action):
            if self.traceUpdate:
                print "Adding known false", action
            self.knownFalseTuple(action)
            self.add_activation(action, 0.3)  # smaller bump for a failed action
        if isinstance(result, list):
            for bindings in result:
                concrete_result = substitute(action, bindings)
                if not self.isTransient(concrete_result):
                    self.knownTuple(concrete_result)   # Mark action as performed/known
                    self.knownTuple(('performed', concrete_result))   # Adding both lets both idioms be used in the agent code.
                self.add_activation(concrete_result, 0.8)

    # Generic primitive actions

    # A null action that always succeeds, useful for dummy steps
    def succeed(self, action):
        #print "Primitive action", action, "trivially succeeds"
        return [{'performed': action}]


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_camel(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()
