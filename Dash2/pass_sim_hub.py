from world_hub import WorldHub
from utils import distPicker, Service, Requirements
import random


class ServiceHub(WorldHub):

    def __init__(self):
        WorldHub.__init__(self)
        self.initialize()

    # Defined separately from the __init__ method so a client can use it to reset the trial
    def initialize(self):
        self.service_counter = 0
        self.service_dictionary = {}   # dictionary service_name:service built at startup
        self.serviceDist = self.create_services(['mail', 'bank', 'social_net'])

    # Use disconnect of a client as an excuse to print out all the usernames and passwords to debug reuse attacks
    # Also prints out the number of reuse opportunities and the probability of a random reuse attack succeeding
    def processDisconnectRequest(self, agent_id, aux_data):
        user_pwd_hosts = dict()
        reuse_possibilities = 0     # Total number of reuses that might be tried - every u/p combo on every other host
        print 'user', agent_id, 'disconnected, here are the current users'
        for name in self.service_dictionary:
            print name
            upw = self.service_dictionary[name].user_name_passwords
            for user in upw:
                print '  ', user, upw[user]
                if user not in user_pwd_hosts:
                    user_pwd_hosts[user] = dict()
                if upw[user] not in user_pwd_hosts[user]:
                    user_pwd_hosts[user][upw[user]] = [name]
                else:
                    user_pwd_hosts[user][upw[user]].append(name)
            reuse_possibilities += len(upw) * (len(user_pwd_hosts) - 1)
        reuse_opportunities = 0
        total = 0
        histogram = [0]*reuse_possibilities
        for user in user_pwd_hosts:
            for pwd in user_pwd_hosts[user]:
                reuse_opportunities += len(user_pwd_hosts[user][pwd]) - 1
                histogram[len(user_pwd_hosts[user][pwd])] += 1
                total += 1
        print reuse_opportunities, 'reuse opportunities out of', reuse_possibilities, 'options'
        # Print everything, then the number of username-password combos used once, twice etc.
        print user_pwd_hosts
        print 'x, number of username password pairs used x times'
        i = 1
        for val in histogram:
            print i, histogram[i]
            total -= histogram[i]
            if total <= 0:
                break
            i += 1
        # For now, clear everything so we can run again without re-starting the hub
        self.initialize()

    def reset_password(self, agent_id, (service_name, username, old_password, new_password)):
        service = self.service_dictionary[service_name]
        if service is None:
            return 'fail', 'no such service'
        if service.has_user(username) and service.user_name_passwords[username] == old_password:
            service.user_name_passwords[username] = new_password
            return 'success', new_password
        else:
            return 'fail', 'username and password do not match'

    def retrieve_status(self, agent_id, (service_name, username)):
        # succeed if the user is logged in, otherwise fail
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failure'
        if username in service.user_status and service.user_status != 'logged_out':
            return 'success'
        else:
            return 'failure'

    def sign_out(self, agent_id, (service_name, username)):
        service = self.service_dictionary[service_name]
        if service is None:
            return 'failure', 'no service with that name'
        if username in service.user_status and service.user_status[username] != 'logged_out':
            service.user_status[username] = 'logged_out'
            return 'success'
        else:
            return 'failure'

    def sign_in(self, agent_id, (service_name, username, password)):
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

    def create_account(self, agent_id, (service_name, username, password)):
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

    def get_account(self, agent_id, aux_data):
        result = distPicker(self.serviceDist[aux_data[0]], random.random())
        print 'get account result', result
        return 'success', result.get_name(), result.get_requirements()

    def list_all_sites(self, agent_id, aux_data):
        return 'success', self.service_dictionary.keys()

    def direct_attack(self, agent_id, (service_name)):
        # Currently arbitrary probabilities based on the service type
        # TODO: consider the attacker competence
        service_type = self.service_dictionary[service_name].get_service_type()
        if "bank" in service_type:
            prob = 0.1
        elif "mail" in service_type:
            prob = 0.25
        else:
            prob = 0.6

        if random.random() < prob:
            service = self.service_dictionary[service_name]
            service.compromised_by.append(agent_id)
            return 'success'
        else:
            return 'fail'

    def get_user_pw_list(self, agent_id, (service_name)):
        service = self.service_dictionary[service_name]
        # Check that this agent successfully compromised this site
        if agent_id in service.compromised_by:
            return 'success', [(user, service.user_name_passwords[user]) for user in service.user_name_passwords]
        else:
            return 'fail', []

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
