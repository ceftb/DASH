from world_hub import WorldHub, serveClientThread
from utils import distPicker, Service, Requirements
import random


class ServiceHub(WorldHub):

    def __init__(self):
        WorldHub.__init__(self)
        self.service_counter = 0
        self.service_dictionary = {}   # dictionary service_name:service built at startup
        self.serviceDist = self.create_services(['mail', 'bank', 'social_net'])

    def processSendActionRequest(self, agent_id, action, aux_data):
        print "Processing Action ", action, aux_data

        if action == 'getAccount':
            return self.get_account(aux_data)
        elif action == 'createAccount':
            return self.create_account(aux_data)
        elif action == 'signIn':
            return self.sign_in(aux_data)
        elif action == 'signOut':
            return self.sign_out(aux_data)
        elif action == 'retrieveStatus':
            return self.retrieve_status(aux_data)
        elif action == 'resetPassword':
            return self.reset_password(aux_data)

    def reset_password(self, aux_data):
        [service_name, username, old_password, new_password] = aux_data
        service = self.service_dictionary[service_name]
        if service is None:
            return 'fail', 'no such service'
        if service.has_user(username) and service.user_name_passwords[username] == old_password:
            service.user_name_passwords[username] = new_password
            return 'success', new_password
        else:
            return 'fail', 'username and password do not match'

    def retrieve_status(self, aux_data):
        # succeed if the user is logged in, otherwise fail
        [service_name, username] = aux_data
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failure'
        if username in service.user_status and service.user_status != 'logged_out':
            return 'success'
        else:
            return 'failure'

    def sign_out(self, aux_data):
        [service_name, username] = aux_data
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failure', 'no service with that name'
        if username in service.user_status and service.user_status[username] != 'logged_out':
            service.user_status[username] = 'logged_out'
            return 'success'
        else:
            return 'failure'

    def sign_in(self, aux_data):
        [service_name, username, password] = aux_data
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failed:no_such_service'
        if service.has_user(username) and service.user_name_passwords[username] == password:
            if username not in service.user_status or service.user_status[username] == 'logged_out':
                service.user_status[username] = 'logged_in'
                print "user logged in successfully to ", service
                return 'success', []
            else:
                print "user already logged in, sign out first"
                return 'failed:logged_in', []
        else:
            print "user \'", username, "\' failed to log in: password and username do not match"
            return 'failed:unknown_password', []

    def create_account(self, aux_data):
        [service_name, username, password] = aux_data
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failed:no_such_service', []
        requirements = service.get_requirements()
        if service.has_user(username):
            print "Create account failed: username already exists"
            return 'failed:user', []
        if requirements is None or requirements.verify(username, password):
            print 'Create account success: account successfully created on ', service
            service.add_user(username, password)
            return 'success', []
        else:
            print "Create account failed on", service, ": password doesn't meet the requirements ", requirements
            return 'failed:reqs', [requirements]

    def get_account(self, aux_data):
        service_type = aux_data[0]
        result = distPicker(self.serviceDist[service_type])
        print 'get account result', result
        return 'success', result.get_name(), result.get_requirements()

    # Create a service distribution for each service type. (I put it in the hub so all agents will
    # see the same set of services - Jim).
    def create_services(self, types_list):
        result = {}
        for service_type in types_list:
            # currently each type will get the same distribution of weak, average and strong services
            result[service_type] = self.create_service_dist(service_type)
        return result

    def create_service_dist(self, service_type):
        # Just create one of each type with equal probability for now to test this out
        services = [(Service(service_type, self.service_counter + 1, 'weak'), 0.33),
                    (Service(service_type, self.service_counter + 2, 'average'), 0.67),
                    (Service(service_type, self.service_counter + 3, 'strong'), 1.0)]
        for (service, prob) in services:
            self.service_dictionary[service.get_name()] = service
        self.service_counter += 3
        return services

if __name__ == "__main__":
    ServiceHub().run()
