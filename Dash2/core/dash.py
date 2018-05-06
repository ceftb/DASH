import system1
import system2
import client
import human_traits
import dash_action


class DASHAgent(dash_action.DASHAction, client.Client, system2.System2Agent,
                system1.System1Agent, human_traits.HumanTraits):
    """
    The DASHAgent class is a composite of various non-instantiable and
    instantiable classes. DASHAction requires system1 and system2 methods for
    operation.

    This is a fully functional class will all the methods necessary for the DASH
    agent to operate.
    """
    def __init__(self):
        client.Client.__init__(self)
        system2.System2Agent.__init__(self)
        system1.System1Agent.__init__(self)
        human_traits.HumanTraits.__init__(self)
        # DASHAction should be initialized last, as it may use methods and
        # attributes from the other classes
        dash_action.DASHAction.__init__(self)
