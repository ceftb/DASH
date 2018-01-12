import sys; sys.path.extend(['../../'])
from Dash2.core.world_hub import WorldHub


class GitHub(WorldHub):

    github_ids = []
    repositories = ['repA', 'repB']

    def request_repos(self, agent_id, data):
        return 'success', self.repositories

    def clone(self, agent_id, data):
        print 'request to clone', data, 'from agent', id
        return 'success', []

    def processRegisterRequest(self, agent_id, aux_data):
        id = aux_data[0]
        self.github_ids.append(id)
        return ['success', agent_id, []]


if __name__ == "__main__":
    GitHub().run()
