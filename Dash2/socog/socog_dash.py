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
    An Agent that uses the socog modules system1.
    The SocogDASHAgent class is a composite of various non-instantiable and
    instantiable classes. SocogDASHAction requires SocogSystem1 and system2
    methods for operation.

    This is a fully functional class will all the methods necessary for the DASH
    agent to operate. It is made of action, client, system1, system2, and
    human traits classes.
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
