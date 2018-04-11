from Dash2.core.dash import DASHAgent
from Dash2.socog.socog_system1 import SocogSystem1Agent, System1Evaluator
from Dash2.core.system2 import substitute
from Dash2.socog.socog_module import *


class SocogDASHAgent(SocogSystem1Agent, DASHAgent):
    """
    An Agent that uses the socog modules system1

    Note: SocogSystem1Agent needs to be inherited on the left in order to
    override DASHAgent's system1 methods. Else original system1 methods take
    precedence in the method resolution order.
    """
    
    def __init__(self, belief_module=None):
        """
        :param belief_module: A BeliefModule
        """
        if belief_module is None:
            belief_module = BeliefModule()

        SocogSystem1Agent.__init__(self, belief_module)
        DASHAgent.__init__(self)
        self.primitiveActions([('listen', self.listen), ['talk', self.talk]])
        self.system1_evaluator = System1Evaluator(self)

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        self.system1_evaluator.initialize_action_queue()
        next_action = self.choose_action()
        iteration = 0
        while next_action is not None \
                and (max_iterations < 0 or iteration < max_iterations):

            if self.traceAction:
                print(self.id, "next action is", next_action)

            result = self.performAction(next_action)
            self.update_beliefs(result, next_action)
            next_action = self.choose_action()
            iteration += 1

        if self.traceLoop and next_action is None:
            print("Exiting simulation: no action chosen")

        elif self.traceLoop and 0 <= max_iterations <= iteration:
            print("Exiting simulation: finished finite agent cycles:",
                  iteration, "of max", max_iterations)

        if disconnect_at_end:
            self.disconnect()

        return next_action

    def choose_action(self):
        system1_action = self.select_action_from_queue()
        if not (system1_action is None):
            return system1_action

        system2_action = self.choose_action_by_reasoning()
        return system2_action

    def update_beliefs(self, result, action):
        if self.traceUpdate:
            print("Updating beliefs based on action", action, "with result", result)

        if result == 'TryAgain':
            return None

        elif not result and not self.isTransient(action):
            if self.traceUpdate:
                print("Adding known false", action)
            self.knownFalseTuple(action)

        if isinstance(result, list):
            for bindings in result:
                concrete_result = substitute(action, bindings)
                if not self.isTransient(concrete_result):
                    if self.traceUpdate:
                        print("Adding known true and performed", concrete_result)
                    self.knownTuple(concrete_result)
                    self.knownTuple(('performed', concrete_result))
                self.update_variable_binding(concrete_result)

    def listen(self, args):
        """
        Takes a two element tuple. The second element must be a Beliefs object
        which system1 will use to update the belief module. Once updated,
        the action queue will be emptied and the rules will be checked for
        satisfied conditions. The action queue will be re-filled with new
        active actions from the rule list.
        :param args: goal, belief tuple
        :return: Empty [{}]
        """
        goal, belief = args

        if isinstance(belief, Beliefs):
            self.belief_module.listen(belief)
            self.system1_evaluator.initialize_action_queue()

        return [{}]

    def talk(self, args):
        """
        Calls the belief module's talk method to get and return a Beliefs
        object with the agents chosen belief for emission.
        :param args: goal, belief tuple
        :return: single element list with dictionary. key=belief, value=Beliefs
        """
        goal, belief = args
        return [{belief: self.belief_module.talk()}]
