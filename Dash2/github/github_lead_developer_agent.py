import sys
sys.path.insert(0, '..')
from git_user_agent import GitUserAgent


class GitLeadDeveloperAgent(GitUserAgent):
    """
    A Lead Developer Git user agent that can communicate with a Git repository hub and
    performs code review actions.
    """

    def __init__(self, **kwargs):
        super(GitLeadDeveloperAgent, self).__init__(**kwargs)

        # Goals
        self.readAgent(
            """
goalWeight ReviewCode 2

goalRequirements ReviewCode
  create_repo_event(RepoName)
  commit_comment_event(RepoName, 'code review commit')
  pick_random_repo(RepoName)
  pull_repo_event(RepoName)
              """)

        # Actions
        self.primitiveActions([
            ('pull_repo_event', self.pull_repo_event),
            ('public_event', self.public_event)])

        self.traceGoals = True

    ############################################################################
    # Lead developer git user methods
    ############################################################################
    def commit_comment_event(self, args):
        """
        developer sends comment to repo
        """

        _, repo_name, comment = args
        if repo_name not in self.name_to_repo_id:
            print 'Agent does not know the id of the repo with name', repo_name, 'cannot commit'
            return []
        status = self.sendAction("commit_comment_event", (self.name_to_repo_id[repo_name], comment))
        print 'commit comment event:', status, repo_name, self.name_to_repo_id[repo_name], comment
        return [{}]

    def pull_repo_event(self, args):
        """
        This event describes local code update (pull from the repo)
        """
        _, repo_name = args
        if repo_name not in self.name_to_repo_id:
            print 'Agent does not know the id of the repo with name', repo_name, 'cannot commit'
            return []
        status = self.sendAction("pull_repo_event", (self.name_to_repo_id[repo_name]))
        return [{}]


if __name__ == '__main__':
    """
    """
    GitLeadDeveloperAgent(host='0', port=6000).agentLoop(10)
