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
##### - handle requirements

### signIn
##### - add reset password branch

### Utils
##### find a way of rasing an error (42)
##### finish elaborate pass choosing


from dash import DASHAgent, isConstant
import subprocess
import random
import utils
import communication_aux
import operator

class PasswordAgent(DASHAgent):
    # add socket
    def __init__(self):
        ### Register the agent and get the id
        sendMessageToWorldHub(0, 4)
        response = getResponseFromWorldHub()
        self.id = response[1]

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
        # usernames used - dict {username:complexity}
        self.knownUsernames = {}
        # passwords used - dict {password:complexity}
        self.knownPasswords = {}
        # list of writen pairs
        self.writtenPasswords = []

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


    def setupAccount(self, service_type=None, service=None):
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
            sendMessageToWorldHub(self.port, 1, [id, 'getAccount', service_type])
            response = getResponseFromWorldHub()
            service = response[1]   # This should be second entry of the response

        ### choose Username
        # if the list of existing usernames is not empty, pick one at random,
        # else pick one from list of predefined usernames
        # here we should add some logic for cognitive burden but I didn't play with
        # it as we didn't have usernames elaborately in prolog
        if bool(self.knownUsernames):
            username = random.sample(self.knownUsernames)
        else
            username = random.sample(username_list)

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

        # If account is be created, update beliefs else repeat
        # I am not sure if it would make more sense to keep beliefs local in this
        # case
        if submitInfo(self.port, self.id, username, password):
            print 'Success: Account Created'
            if pass not in self.writtenPasswords:
                sendMessageToWorldHub(self.port, 2, [service, username, password, self.initial_belief])
            else:
                sendMessageToWorldHub(self.port, 2, [service, username, password, 0.99999)
        else:
            setupAccount(self, service_type, service)



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
        sendMessageToWorldHub(self.port, 2, [self.id, 'retrieveInformation', service])
        response = getResponseFromWorldHub()

        # If user doesn't have an account proceed in creating it
        if not response[0]:
            print "Redirect: This user has no account - proceed to create it "
            sendMessageToWorldHub(self.port, 2, [self.id, 'getServType', service)]
            response = getResponseFromWorldHub()
            setupAccount(self, response[1], service)

        # Select password: esentially the weaker the belief is there is
        # less chance there is that user will just pick one of their known
        # username/passwords
        distribution = {'known': 1.0, response[2]: response[3]}
        if distPicker(distribution, random.random()) == 'known':
            username = random.sample(self.knownUsernames)
            password = random.sample(self.knownPasswords)
            flag = 0
        else:
            username = response[1]
            password = response[2]
            flag = 1

        # Try to signIn; if agent knowed the password, update the strength of
        # belief; analogly it works if user did not know the password (flag == 0)
        # Finally, if failed, repeat the sign in process with the updated beliefs
        sendMessageToWorldHub(self.prot, 1, [self.id, 'signIn', [username, password]])
        login_response = getResponseFromWorldHub()
        if login_response[0]:
            if flag == 1:
                response[3] += (response[3]*self.strenghteningRate)
                new_strenght = max(response[3], 0.9999)
                sendMessageToWorldHub(self.port, 2, \
                            [service, username, password, new_strenght])
            else:
                sendMessageToWorldHub(self.port, 2, \
                            [service, username, password, self.initial_belief)
        else:
            if flag == 1:
                response[3] -= (response[3]*self.forgettingRate)
                new_strenght = min(response[3], 0.1)
                sendMessageToWorldHub(self.port, 2, \
                            [service, username, password, new_strenght])
            signIn(self, service)


    def signOut(self, service):
        ''' This should be equivalent to the signOut subgoal in prolog
        It checks if the user is logged in, and if so, it sends a message to log
        him out.

        Defined Actions:
            1. retrieveStatus
            2. signOut
        '''
        sendMessageToWorldHub(self.port, 1, [self.id, 'retrieveStatus', service])
        response = getResponseFromWorldHub()
        if response[1] == 0:
            print 'Error: User has not been logged in in the first place'
        else:
            sendMessageToWorldHub(self.port, 1, [self.id, 'signOut', service])
            print 'Success: User succesfully logged out'



    def resetPassword(self, service):
        sendMessageToWorldHub(self.port, 1, [self.id, 'retrieveInformation', service])
        info_response = getResponseFromWorldHub()

        username = info_response[1]
        old_password = info_response[2]


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

        sendMessageToWorldHub(self.port, 1, [self.id, \
                                'resetPassowrd', service, username, password])
        status_response = getResponseFromWorldHub()

        if status_response[1]:
            print 'Success: password reset successfully'
        else:
            #not yet implemented handling of requirements
            print 'Handle requirements'
