from dash import DASHAgent


class GithubAgent(DASHAgent):

    def __init__(self):
        DASHAgent.__init__(self)
        self.register([1])
        self.readAgent("""

goalWeight cloneARepo 1

goalRequirements cloneARepo
  getRepos(repos)
  cloneFirstRepo(repos)

""")

    def get_repos(self, (goal, var)):
        status, data = self.sendAction("request_repos")
        print 'calling get_repos with', var, 'and result', status, data
        return [{var: data}]

    def clone_first_repo(self, (goal, var)):
        status, data = self.sendAction("clone", [var[0]])
        print 'cloning', var[0], 'with result', status, data
        return [{}]


if __name__ == "__main__":
    gh = GithubAgent()
    gh.agentLoop()
