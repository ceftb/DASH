import system1
import system2
import client
import human_traits
import dash_action


class DASHAgent(dash_action.DASHAction, client.Client, system2.System2Agent,
                system1.System1Agent, human_traits.HumanTraits):
    """
    The DASHAgent class is a composite of various non-instantiable and
    instantiable classes. This is a fully functional class will all the methods
    necessary for a DASH agent. It is made of DASHAction, Client, System2Agent,
    System1Agent, and HumanTraits classes.

    A new DASHAgent class can be constructed by swapping out any of the above
    classes, so long as the DASHAgent functionality is maintained at the highest
    level.

    The DASHAction class defines methods that define the relationship between
    system1 and system2 as well as how the agent updates and chooses actions.

    The Client class defines the set of communication protocols for the agent.

    The System2Agent class defines the default system2 (goal directed behavior)
    framework developed for DASH.

    The System1Agent class defines the default system1 (instinct behavior)
    framework developed for DASH, based on spreading activation.

    The HumanTraits class defines a set of default human-like properties that
    agents can use.
    """
    def __init__(self):
        client.Client.__init__(self)
        system2.System2Agent.__init__(self)
        system1.System1Agent.__init__(self)
        human_traits.HumanTraits.__init__(self)
        # DASHAction should be initialized last, as it may use methods and
        # attributes from the other classes
        dash_action.DASHAction.__init__(self)
