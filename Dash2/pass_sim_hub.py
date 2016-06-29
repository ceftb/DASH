from world_hub import WorldHub, serveClientThread
from utils import distPicker
import random

class ServiceHub(WorldHub):
    # def __init__(self):
    serviceList = {}	# predefined dictionary service_name:service
    serviceDist = {'mail': 0.35, 'social_net':0.85, 'bank':1.0}	# predefined distribution list serv_type:distribution
    knownUsernames = {}	# dictionary service_name:[usernames]

    serviceBase = {}	# dictionary service_name:[(username, password)]
    serviceStatus = {}	# dictionary service_name:[username]

    def processSendActionRequest(self, id, action, aux_data):
        print "Processing Action ", action, aux_data

        if action == 'getAccount':
            service_type = aux_data[0]
            return distPicker(self.serviceDist[service_type], random.random())

        elif action == 'createAccount':
            service = aux_data[0]
            username = aux_data[1]
            password = aux_data[2]
            requirements = self.serviceList[service].getRequirements()
            if username in self.knownUsernames[service]:
                print "Failed: username already exists"
                return('failed:user', [])

            if requirements.verify(username, password):
                print 'Success: account successfully created on ', service
                self.knownUsernames[service].append(username)
                self.serviceBase[service].append((username, password))
                return('success', [])
            else:
                print "Failed: password doesn't meet the requirements"
                return('failed:reqs', [requirements])

        elif action == 'signIn':
            service = aux_data[0]
            username = aux_data[1]
            password = aux_data[2]
            if (username, password) in self.serviceBase[service]:
                if username in self.serviceStatus[service]:
                    print "user logged in successfully to ", service
                    return ('success', [])
                else:
                    print "user already logged in, sign out first"
                    return ('failed:logged_in', [])
            else:
                print "user failed to log in"
                return ('failed:unknown_password', [])
        elif action == 'retrieveStatus':
            service = aux_data[0]
            username = aux_data[1]
            if username in self.serviceStatus[service]:
                self.serviceStatus[service].remove(username)
                return ('success', [])
            else:
                return ('failure', [])

if __name__ == "__main__":
    ServiceHub().run()
