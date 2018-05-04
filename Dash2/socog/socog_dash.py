import Dash2.socog.socog_system1 as socog_system1
import Dash2.socog.socog_action as socog_action
import Dash2.core.system2 as system2
import Dash2.core.client as client
import Dash2.core.human_traits as human_traits
from Dash2.socog.socog_module import BeliefModule


class SocogDASHAgent(socog_action.SocogDASHAction, client.Client,
                     system2.System2Agent, socog_system1.SocogSystem1Agent,
                     human_traits.HumanTraits):
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

        client.Client.__init__(self)
        system2.System2Agent.__init__(self)
        socog_system1.SocogSystem1Agent.__init__(self, belief_module)
        human_traits.HumanTraits.__init__(self)
        socog_action.SocogDASHAction.__init__(self)
