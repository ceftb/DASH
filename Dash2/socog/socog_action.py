import Dash2.core.dash_action as dash_action
from Dash2.socog.socog_system1 import System1Evaluator
from Dash2.core.system2 import substitute
from Dash2.socog.socog_module import *


class SocogDASHAction(dash_action.DASHAction):
    """
    An ABC that defines the action behaviors of the DASH agent. It defines
    an agentLoop and sets up the primitiveActions dictionary and other methods
    used to update the agent and pick either system1 or system2 actions.

    The DASH agent inherits this class, so you can use any methods or
    attributes that would exist in the composite DASH agent.
    """

    def __init__(self):
        dash_action.DASHAction.__init__(self)
        self.primitiveActions([('process_belief', self.process_belief),
                               ('emit_belief', self.emit_belief),
                               ('belief_conflict', self.belief_conflict)])
        self.system1_evaluator = System1Evaluator(self)
        self.sys1_action_taken = False

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        self.system1_evaluator.update()
        next_action = self.choose_action()
        iteration = 0
        while next_action is not None \
                and (max_iterations < 0 or iteration < max_iterations):

            if self.traceAction:
                print(self.id, "next action is", next_action)

            result = self.performAction(next_action)
            self.update_beliefs(result, next_action)
            self.system1_evaluator.update(result)
            self.sys1_action_taken = False
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
        system1_action = self.system1_propose_action()
        if system1_action and self.bypass_system2(system1_action):
            self.sys1_action_taken = True
            return system1_action

        system2_action = self.system2_propose_action()
        return self.arbitrate_system1_system2(system1_action, system2_action)

    def arbitrate_system1_system2(self, system1_action, system2_action):
        # By default return system2 action if it is available
        if system2_action is None and system1_action:
            self.sys1_action_taken = True
            return system1_action
        else:
            return system2_action

    def bypass_system2(self, system1_action_nodes):
        print('considering system1 suggested actions ', system1_action_nodes)
        return True  # try system 1 by default if it's available

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

    def process_belief(self, args):
        """
        Takes a two element tuple. The second element must be a Beliefs object
        which system1 will use to update the belief module. Once updated,
        the action queue will be emptied and the rules will be checked for
        satisfied conditions. The action queue will be re-filled with new
        active actions from the rule list.
        :param args: goal, belief tuple
        :return: [{}]
        """
        goal, belief = args

        if isinstance(belief, Beliefs):
            self.belief_module.process_belief(belief)
            self.system1_evaluator.initialize_action_queue()

        return [{}]

    def emit_belief(self, args):
        """
        Calls the belief module's emit_belief method to get and return a Beliefs
        object with the agents chosen belief for emission.
        :param args: goal, belief tuple
        :return: single element list with dictionary. key=belief, value=Beliefs
        """
        goal, belief = args
        return [{belief: self.belief_module.emit_belief()}]

    def belief_conflict(self, args):
        """
        Checks if an incoming belief is in conflict with internal beliefs. A
        conflict occurs when the belief is of opposite valence to a current
        belief.

        This method does not update own or perceived beliefs.
        :param args: (goal, belief)
        :return: [{}] (evaluated as True) if conflict, else [] (evaluated as False)
        """
        goal, belief = args
        if isinstance(belief, Beliefs):
            if self.belief_module.is_conflicting_belief(belief):
                return [{}]

        return []
