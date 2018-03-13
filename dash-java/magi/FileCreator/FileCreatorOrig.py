from magi.util.agent import DispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent

# The FileCreator agent implementation, derived from DispatchAgent.
class FileCreator(DispatchAgent):
    def __init__(self):
        DispatchAgent.__init__(self)
        self.filename = '/tmp/newfile'

    # A single method which creates the file named by self.filename.
    # (The @agentmethod() decorator is not required, but is encouraged.
    #  it does nothing of substance now, but may in the future.)
    @agentmethod()
    def createFile(self, msg):
        '''Create a file on the host.'''
        # open and immediately close the file to create it.
        open(self.filename, 'w').close()

# the getAgent() method must be defined somewhere for all agents.
# The Magi daemon invokes this mehod to get a reference to an
# agent. It uses this reference to run and interact with an agent
# instance.
def getAgent():
    agent = FileCreator()
    return agent

# In case the agent is run as a separate process, we need to
# create an instance of the agent, initialize the required
# parameters based on the received arguments, and then call the
# run method defined in DispatchAgent.
if __name__ == "__main__":
    agent = FileCreator()
    initializeProcessAgent(agent, sys.argv)
    agent.run()

