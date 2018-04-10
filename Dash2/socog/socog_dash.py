from Dash2.core.dash import DASHAgent
from Dash2.socog.socog_system1 import SocogSystem1Agent


class SocogDASHAgent(SocogSystem1Agent, DASHAgent):
    """
    An Agent that uses the socog modules system1

    Note: SocogSystem1Agent needs to be inherited on the left in order to
    override DASHAgent's system1 methods. Else original system1 methods take
    precedence in the method resolution order.
    """
    
    def __init__(self, belief_module=None):
        SocogSystem1Agent.__init__(self, belief_module)
        DASHAgent.__init__(self)
        self.primitiveActions([('listen', self.listen), ['talk', self.talk]])

    def agentLoop(self, max_iterations=-1, disconnect_at_end=True):
        next_action = self.choose_action()
        iteration = 0
        while next_action is not None \
                and (max_iterations < 0 or iteration < max_iterations):

            if self.traceAction:
                print(self.id, "next action is", next_action)

            self.performAction(next_action)
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
