# todo & notes
# -define socket in the right way - I am an idiot
# add return values as appropriate
# add time belief depreciation element - in services though
# add counters for memorizations, resets, etc...
# services will have to handle the password same as old one
# check termination

### Create acc
##### - add username list as dict username:complexity
##### in the code refered to as username_list; UN does not contribute to CB yet
##### - add password list as dict pass:complexity
##### in the code referred to as pass list
##### - add update beliefs in the end^

### signIn
##### - add reset password branch

### Utils
##### find a way of rasing an error (42)
##### finish elaborate pass choosing


from dash import DASHAgent, isConstant
import subprocess
import random
from utils import distPicker
import communication_aux
import operator
import sys

class PasswordAgent(DASHAgent):
    # add socket
    def __init__(self):
        DASHAgent.__init__(self)

        response = self.register()
        if response[0] != "success":
            print "Error: world hub not reachable - exiting "
            sys.exit()
        self.id = response[1]

        # Added by Jim based on bruno_user.pl
        self.password_list = ['p', 'P', 'pw', 'Pw', 'pw1', 'Pw1', 'pass', 'Pass', 'pas1', 'Pas1', 'pass1', 'Pass1', 'PaSs1', 'password', 'P4ssW1', 'PassWord', 'PaSs12', 'PaSsWord', 'PaSsW0rd', 'P@SsW0rd', 'PassWord1', 'PaSsWord1', 'P4ssW0rd!', 'P4SsW0rd!', 'PaSsWord12', 'P@SsWord12', 'P@SsWoRd12', 'PaSsWord!2', 'P@SsWord!234', 'P@SsWord!234', 'MyP4SsW0rd!', 'MyP4SsW0rd!234', 'MyP@SsW0rd!234', 'MyPaSsWoRd!234?', 'MyPaSsW0Rd!234?', 'MyS3cUReP@SsW0rd!2345', 'MyV3ryL0ngS3cUReP@SsW0rd!2345?']

        # distribution of probabilities for every service type
        self.serviceProbs = {'mail': 0.35, 'social_net':0.85, 'bank':1.0}
        # bias between memorizing or writing down
        self.memoBias = {'reuse': 0.5, 'write_down': 1.0}
        # initial strenght of beliefs
        self.initial_belief = 0.65
        # forgetting rate - percent of belief lost
        self.forgettingRate = 0.15
        # strenghtening rate
        self.strenghteningRate = 0.2


        # initial cong. burden
        self.cognitiveBurden = 0
        # pairs used - dict {service:[username, password]}
        self.known = {}
        # usernames used - dict {username:complexity}
        self.knownUsernames = {}
        # passwords used - dict {password:complexity}
        self.knownPasswords = {}
        # list of writen pairs
        self.writtenPasswords = []
        # USER beliefs
        self.beliefs = {}

        # i'm not really clear about usage of primitive actions vs just defining
        # new goals
        self.primitiveActions([
        ('checkTermination', self.connectToWorldHub),
        ('setupAccount', self.setupAccount),
        ('signIn', self.signIn),
        ('signOut', self.signOut),
        ('resetPassword', self.resetPassword)
        ])

        self.readAgent( """

goalWeight doWork 1         # repeat the proces

goalRequirements doWork
    checkTermination(criterion, beliefs)
    setupAccount(service_type)
    signIn(service)
    signOut(service)
    resetPassword(service)

""")


    def setupAccount(self, service_type=None, service=None, requirements=None):
        ''' Should be equivalent to createAccount subgoal in prolog version
        It takes service type as an input, and based on that decides which
        username to use[1]. Then, it picks the password and submits the info.

        Based on the service response it adjusts username and password.
        Finally, if successful, it stores info in memory (in one of couple of ways)

        Flow:
            initializeContact(service_type)
            choose username
            choose password - for now random
                memorizeUserName
                memorizePassword
                writeDownUsername
                writeDownPassword
            submit info
                if not ok, repeat

        Defined Actions:
            1. getAccount
            2. createAccount (in utils.py)


        [1] we might add the fact that banks usually don't really let you pick
        password, which additionally adds to the cognitive burden.
        '''
        if service_type is None:
            # choose the service type, and find the actuall service
            service_type = distPicker(self.serviceProbs, random.random())
            # Decide the service to log into
            response = self.sendAction('getAccount', [service_type])
            service = response[1]   # This should be second entry of the response

        ### choose Username
        # if the list of existing usernames is not empty, pick one at random,
        # else pick one from list of predefined usernames
        # here we should add some logic for cognitive burden but I didn't play with
        # it as we didn't have usernames elaborately in prolog
        if bool(self.knownUsernames):
            username = random.sample(self.knownUsernames)
        else:
            username = random.sample(username_list)

        ### choose Password
        desired_pass = random.sample(self.password_list)
        # if there are requirements verify that the password complies them
        if requirements is not None:
            while not requirements.verify(username, desired_pass):
                desired_pass = random.sample(self.password_list)

        # if pass is too hard, reuse the hardest one or write it down,
        # the decision is based on memoBias parameter
        # maybe add some distance heuristics later
        if (password_list[desired_pass] + self.cognitiveBurden) < self.cogThreshold:
            password = desired_pass
            # add to the list of known pass, and remove from potential passes
            self.knownPasswords[desired_pass] = password_list[desired_pass]
            del password_list[desired_pass]
        elif distPicker(self.memoBias, random.random()) == 'reuse':
            password = max(stats.iteritems(), key=operator.itemgetter(1))[0]
        else:
            password = desired_pass
            self.writtenPasswords.append(desired_pass)
            del password_list[desired_pass]

        # If account is be created, update beliefs else repeat
        # I am not sure if it would make more sense to keep beliefs local in this
        # case
        result = self.sendAction('createAccount', [service, username, password])
        if result[0] == 'success':
            print 'Success: Account Created'
            if password not in self.writtenPasswords:
                self.beliefs[service] = [username, password, self.initial_belief]
            else:
                self.beliefs[service] = [username, password, self.initial_belief, 0.9999]
        elif result[0] == 'failed:user':
            print 'Failed: username already exists (should not happen yet)'
        elif result[0] == 'failed:reqs':
            self.setupAccount(service_type, service, result[1])

        return 'succes'


    def signIn(self, service):
        ''' This should be equivalent to singIn subgoal in prolog version
        User looks for service beliefs on the worldHub, and based on the strength
        of his belief tries either one of the known passwords or the password for
        which agent has beliefs. If he has no account on that service it proceeds
        to create the account.
        Depending on the success of the action, it updates strength beliefs.

        Defined Actions:
            1. getServType
            2. retrieveInformation
            3. signIn

        '''
		# check if user has account
        if not bool(self.beliefs[service]):
			print "User has no beliefs for this account"

        belief = self.beliefs[service]
        # Select password: esentially the weaker the belief is there is
        # less chance there is that user will just pick one of their known
        # username/passwords
        distribution = {'known': 1.0, belief[1]:belief[2]}
        if distPicker(distribution, random.random()) == 'known':
            username = random.sample(self.knownUsernames)
            password = random.sample(self.knownPasswords)
            flag = 0
        else:
            username = belief[0]
            password = belief[1]
            flag = 1

        # Try to signIn; if agent knowed the password, update the strength of
        # belief; analogly it works if user did not know the password (flag == 0)
        # Finally, if failed, repeat the sign in process with the updated beliefs
        login_response = self.sendAction('signIn', [service, username, password])
        if login_response[0] == 'success':
            if flag == 1:
                self.beliefs[service][2] += (self.beliefs[service][2]*self.strenghteningRate)
                new_strenght = max(self.beliefs[service][2], 0.9999)
                self.beliefs[service] = [username, password, new_strenght]
            else:
                self.beliefs[service] = [username, password, self.initial_belief]
        elif login_response[0] == 'failed:logged_in':
			self.signOut(service)
			#exit loop
        else:
            if flag == 1:
                self.beliefs[service][2] -= (self.beliefs[service][2]*self.strenghteningRate)
                new_strenght = min(self.beliefs[service][2], 0.0001)
                self.beliefs[service] = [username, password, new_strenght]
            self.signIn(service)


    def signOut(self, service):
        ''' This should be equivalent to the signOut subgoal in prolog
        It checks if the user is logged in, and if so, it sends a message to log
        him out.

        Defined Actions:
            1. retrieveStatus
            2. signOut
        '''
        username = self.beliefs[service][0]
        response = self.sendAction('retrieveStatus', [service, username])
        if response[0] == 'failure':
            print 'Error: User has not been logged in in the first place'
        else:
            self.sendAction('signOut', [service])
            print 'Success: User succesfully logged out'



    def resetPassword(self, service):
        info_response = self.beliefs[service]

        username = info_response[0]
        old_password = info_response[1]


        ### choose Password
        desired_pass = random.sample(password_list)
        # if pass is too hard, reuse the hardest one or write it down,
        # the decision is based on memoBias parameter
        # maybe add some distance heuristics later
        if (password_list[desired_pass] + self.cognitiveBurden) < self.cogThreshold:
            password = desired_pass
            # add to the list of known pass, and remove from potential passes
            self.knownPasswords[desired_pass] = password_list[desired_pass]
            del password_list[desired_pass]
        elif distPicker(self.memoBias, random.random()) == 'reuse':
            password = max(stats.iteritems(), key=operator.itemgetter(1))[0]
        else:
            password = desired_pass
            self.writtenPasswords.append(desired_pass)
            del password_list[desired_pass]

        status_response = self.sendAction('resetPassowrd', [service, username, password])

        if status_response[0]:
            print 'Success: password reset successfully'
        else:
            #not yet implemented handling of requirements
            print 'Handle requirements'

if __name__ == "__main__":
    PasswordAgent().agentLoop()
