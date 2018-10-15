import sys; sys.path.extend(['../../'])
from Dash2.core.dash import DASHAgent


class SocsimDecisionData(object):

    def __init__(self, **kwargs):
        """
        Initializes empty DecisionData object. If kwargs is empty object must be initialized via
        initialize_using_user_profile() after creation.
        :param kwargs: may contain such paramenters as id, event_rate, event_frequencies, login_h, etc.
        """
        # System 1 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.nodes = set()
        self.action_nodes = set()
        # System 2 dynamic information needs to be separate for each agent. I will add general support for this later.
        self.knownDict = dict()
        self.knowFalseDict = dict()
        self.event_rate = kwargs.get("event_rate", 5)  # number of events per month
        self.id = kwargs.get("id", None)
        self.last_event_time = kwargs.get("event_rate", 0)


    def initialize_using_user_profile(self, profile, hub):
        """
        This method must be overridden/implemented in sub-classes.
        This method initializes SocsimUserDecisionData using information from initial state loader. Information from intial
        state loader is passes via profile object. Profile object is created and pickled by initial state loader.
        This method initializes:
            id, event_rate, last_event_time, etc.

        :param profile: contains information about the initial state of the agent, created by initial state loader.
        :param hub: hub is needed to register repos.
        :return: None
        """
        self.hub = hub
        self.id = profile.pop("id", None)
        self.event_rate = profile.pop("r", 5)  # number of events per month
        self.last_event_time = profile["let"]

class SocsimMixin(object):
    """
    A basic Git user agent that can communicate with a Git repository hub and
    perform basic actions. Can be inherited to perform other specific functions.
    """

    decision_object_class_name = "SocsimUserDecisionData"

    def _new_empty_decision_object(self):
        return SocsimDecisionData()

    def create_new_decision_object(self, profile):
        decisionObject = self._new_empty_decision_object()
        decisionObject.initialize_using_user_profile(profile, self.hub)
        return decisionObject

    def __init__(self, **kwargs):
        self.isSharedSocketEnabled = True  # if it is True, then common socket for all agents is used.
        # The first agent to use the socket, gets to set up the connection. All other agents with
        # isSharedSocketEnabled = True will reuse it.
        self.system2_proxy = kwargs.get("system2_proxy")
        if self.system2_proxy is None:
            self.readAgent(
                """
    goalWeight MakeEvent 1
    
    goalRequirements MakeEvent
      take_action()
                """)
        else:
            self.use_system2(self.system2_proxy)

        # Registration
        self.useInternalHub = kwargs.get("useInternalHub")
        self.hub = kwargs.get("hub")
        self.server_host = kwargs.get("host", "localhost")
        self.server_port = kwargs.get("port", 5678)
        self.trace_client = kwargs.get("trace_client", True)
        registration = self.register({"id": kwargs.get("id", None), "freqs": kwargs.get("freqs", {})})

        # Assigned information
        self.id = registration[1] if registration is not None else None

        self.traceLoop = kwargs.get("traceLoop", True)

        self.decision_data = None  # Should be set to the DecisionData representing the agent on each call

        # Actions
        self.primitiveActions([
            ('take_action', self.socsim_action)])

    def customAgentLoop(self):
        self.socsim_action()
        return False

    def socsim_action(self):
        """
        This is an empty action. For demo purpose only.
        :return:
        """
        print "Primitive action taken."

    def first_event_time(self, start_time):
        delta = float(30 * 24 * 3600) / float(self.hub.graph.nodes[self.decision_data.id]["r"])
        next_event_time = self.hub.graph.nodes[self.decision_data.id]["let"] + delta if self.hub.graph.nodes[self.decision_data.id]["let"] is not None \
            and self.hub.graph.nodes[self.decision_data.id]["let"] != -1 else start_time
        while next_event_time < start_time:
            next_event_time += delta
        return next_event_time

    def next_event_time(self, curr_time):
        delta = float(30 * 24 * 3600) / float(self.hub.graph.nodes[self.decision_data.id]["r"])
        next_time = curr_time + delta
        return next_time

class SocsimAgent(SocsimMixin, DASHAgent):
    def __init__(self, **kwargs):
        DASHAgent.__init__(self)
        SocsimMixin.__init__(self, **kwargs)
