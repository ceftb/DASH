

from world_hub import WorldHub


class NurseHub(WorldHub):

    def __init__(self):
        WorldHub.__init__(self)
        self.number_of_computers = 10
        self.logged_on = [None for i in range(0, self.number_of_computers)]
        self.logged_out = [None for i in range(0, self.number_of_computers)]

    def processSendActionRequest(self, agent_id, action, data):
        print "nurse hub processing action", action, data
        if action == "findOpenComputers":    # return a list of computers that noone is logged into
            return 'success', [i for i in range(1, self.number_of_computers+1) if self.logged_on[i-1] is None]
        elif action == "login":
            return self.login(agent_id, data)
        elif action == "logout":
            return self.logout(agent_id, data)
        else:
            print "Unknown action:", action

    def login(self, agent_id, data):
        print "Logging in", agent_id, "with", data
        self.logged_on[data[0]-1] = agent_id           # agent indexes the computer from 1..n, the list is indexed from 0..n-1
        return 'success'

    def logout(self, agent_id, data):
        print "Logging out", agent_id, 'with', data
        self.logged_on[data[0]-1] = None
        self.logged_out[data[0]-1] = agent_id
        return 'success'


        # Marley to implement
 # something like ['success', [i for i in range(1, self.number_of_computers+1) if self.logged_on[i-1] == None]

if __name__ == "__main__":
    NurseHub().run()
