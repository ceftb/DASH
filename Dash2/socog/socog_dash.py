from Dash2.core.dash import DASHAgent
from socog_system1 import SocogSystem1Agent


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
