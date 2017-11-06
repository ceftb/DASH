from dash import DASHAgent


class GithubAgent(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.register([1])

    def get_repos(self):
        status, data = self.sendAction("request_repos")
        print status, data


if __name__ == "__main__":
    gh = GithubAgent()
    print 'response from hub is', gh.get_repos()
    #gh.agentLoop(20)
