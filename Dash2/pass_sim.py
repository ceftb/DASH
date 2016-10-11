# todo & notes
# -define socket in the right way - I am an idiot
# add return values as appropriate
# add time belief depreciation element - in services though
# add counters for memorizations, resets, etc...
# services will have to handle the password same as old one
# check termination

# ## Create acc
# - add username list as dict username:complexity
# in the code refered to as username_list; UN does not contribute to CB yet
# - add password list as dict pass:complexity
# in the code referred to as pass list
# - add update beliefs in the end^

# ## signIn
# - add reset password branch

# ## Utils
# find a way of rasing an error (42)
# finish elaborate pass choosing


from dash import DASHAgent, isConstant, isVar
import random
from utils import distPicker
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
        self.password_list = ['p', 'P', 'pw', 'Pw', 'pw1', 'Pw1', 'pass',
                              'Pass', 'pas1', 'Pas1', 'pass1', 'Pass1',
                              'PaSs1', 'password', 'P4ssW1', 'PassWord',
                              'PaSs12', 'PaSsWord', 'PaSsW0rd', 'P@SsW0rd',
                              'PassWord1', 'PaSsWord1', 'P4ssW0rd!',
                              'P4SsW0rd!', 'PaSsWord12', 'P@SsWord12',
                              'P@SsWoRd12', 'PaSsWord!2', 'P@SsWord!234',
                              'P@SsWord!234', 'MyP4SsW0rd!', 'MyP4SsW0rd!234',
                              'MyP@SsW0rd!234', 'MyPaSsWoRd!234?',
                              'MyPaSsW0Rd!234?', 'MyS3cUReP@SsW0rd!2345',
                              'MyV3ryL0ngS3cUReP@SsW0rd!2345?']

        # distribution of probabilities for every service type. Used to be
        # dictionaries, but then order is not guaranteed
        self.serviceProbs = [('mail', 0.35), ('social_net', 0.85),
                             ('bank', 1.0)]

        # bias between memorizing or writing down
        # if cognitive burden is too high, the user will write down or memorize
        # the password
        self.memoBias = [('reuse', 0.5), ('write_down', 1.0)]

        # initial belief strength
        self.initial_belief = 0.65

        # rate at which user forgets a belief;
        # NOTE: currently not being used --Chris
        self.forgettingRate = 0.15

        # rate at which user's belief strengthens
        # NOTE: it looks like we're using this instead of forgetting rate
        # --Chris
        self.strengtheningRate = 0.2

        # initial congnitive burden
        self.cognitiveBurden = 0

        # after the cognitive burden reaches this threshold users will write
        # down passwords
        # NOTE: being used instead of passwordReuseThreshold
        self.cognitiveThreshold = 68

        # the user will not be able to recall passwords below this threshold
        # NOTE: currently not being used --Chris
        self.recallThreshold = 0.5

        # short or long - this determines whether users will prefer to reuse
        # the longest password or new password construction
        # NOTE: currently not being used --Chris
        self.passwordReusePriority = 'long'

        # after the cognitive burden reaches this threshold users will begin to
        # reuse passwords
        # NOTE: currently not being used --Chris
        self.passwordReuseThreshold = 54

        # after all forget rates are below this threshold the program will stop
        # NOTE: currently not being used --Chris
        self.passwordForgetRateStoppingCriterion = 0.0005

        # pairs used - dict {service:[username, password]}
        self.known = {}

        # usernames used - dict {username:complexity} (I changed to just a
        # list - Jim)
        self.knownUsernames = []

        # passwords used - dict {password:complexity}(I changed to just a
        # list - Jim)
        self.known_passwords = []

        # list of writen pairs
        self.writtenPasswords = []

        # USER beliefs
        self.beliefs = {}

        # This is used below so I added it here to make the code run.
        # Not sure how it should interact with the variables above
        self.username_list = ['user1', 'user12', 'admin']

        # i'm not really clear about usage of primitive actions vs just
        # defining new goals
        self.primitiveActions([
                               ('checkTermination', self.check_termination),
                               ('setupAccount', self.setupAccount),
                               ('signIn', self.signIn),
                               ('signOut', self.signOut),
                               ('resetPassword', self.resetPassword)
                               ])

        # The agent goal description is short, because the rational task is
        # not that important here.
        self.readAgent
        ("""
        goalWeight doWork 1         # repeat the process

        goalRequirements doWork
            checkTermination(criterion, beliefs)
            forget([checkTermination(c, b)])

        goalRequirements doWork
            setupAccount(service_type, service)
            signIn(service)
            signOut(service)
            resetPassword(service)
            forget([setupAccount(st,s), signIn(s), signOut(s),
            resetPassword(s)])

        # This means that every iteration it will need to be re-achieved
        transient doWork

        """)
        self.trace_action = True

    # service_type_var may be unbound or bound to a requested service_type.
    # service_var is unbound and will be bound to the result of setting up the
    # service
    def setupAccount(self, (goal, service_type_var, service_var)):
        ''' Should be equivalent to createAccount subgoal in prolog version
        It takes service type as an input, and based on that decides which
        username to use[1]. Then, it picks the password and submits the info.

        Based on the service response it adjusts username and password.
        Finally, if successful, it stores info in memory (in one of couple of
        ways)

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

        if isVar(service_type_var):
            # choose the service type, and find the actual service
            service_type = distPicker(self.serviceProbs, random.random())

        # Decide the service to log into
        [status, service, requirements] = self.sendAction('getAccount',
                                                          [service_type])
        print 'getaccount result:', status, service

        # choose Username
        # if the list of existing usernames is not empty, pick one at random,
        # else pick one from list of predefined usernames
        # here we should add some logic for cognitive burden but I didn't play
        # with it as we didn't have usernames elaborately in prolog
        if self.knownUsernames:
            username = random.choice(self.knownUsernames)
        else:
            username = random.choice(self.username_list)
        password = self.choose_password(username, requirements)

        # If account is be created, update beliefs else repeat
        # I am not sure if it would make more sense to keep beliefs local in
        # this case
        [status, data] = self.sendAction('createAccount', [service, username,
                                         password])
        print 'create account result:', [status, data]

        if status == 'success':
            print 'Success: Account Created'
            if password not in self.writtenPasswords:
                self.beliefs[service] = [username, password,
                                         self.initial_belief]
            else:
                self.beliefs[service] = [username, password,
                                         self.initial_belief, 0.9999]
            if isVar(service_type_var):
                return [{service_type_var: service_type, service_var: service}]
            else:
                return [{service_var: service}]

        elif status == 'failed:user':
            print 'Failed to create account: username already exists'
            # Should succeed in 'setting up' the account though
            if isVar(service_type_var):
                return [{service_type_var: service_type, service_var: service}]
            else:
                return [{service_var: service}]

        elif status == 'failed:reqs':
            # self.setupAccount(service_type, service, result[1])
            return []

        else:
            print 'unknown result for creating account'
            return []

    def signIn(self, (goal, service)):
        ''' This should be equivalent to singIn subgoal in prolog version
        User looks for service beliefs on the worldHub, and based on the
        strength of his belief tries either one of the known passwords or the
        password for which agent has beliefs. If he has no account on that
        service it proceeds to create the account. Depending on the success of
        the action, it updates strength beliefs.

        Defined Actions:
            1. getServType
            2. retrieveInformation
            3. signIn

        '''
        # check if user has account
        if service not in self.beliefs or not self.beliefs[service]:
            print "User has no beliefs for this account"

        [username, password, belief] = self.beliefs[service]
        # Select password: essentially the weaker the belief is, the greater
        # the chance that user will just pick one of their known
        # username/passwords
        distribution = [(password, belief), ('known', 1.0)]
        if distPicker(distribution, random.random()) == 'known' \
                and self.knownUsernames and self.known_passwords:
            changed_password = True
            username = random.choice(self.knownUsernames)
            password = random.choice(self.known_passwords)
        else:
            changed_password = False

        # Try to signIn; if agent knew the password, update the strength of
        # belief; analogously it works if user did not know the password.
        # Finally, if failed, repeat the sign in process with the updated
        # beliefs
        login_response = self.sendAction('signIn', [service, username,
                                         password])

        if login_response[0] == 'success':
            if changed_password:
                # NOTE: as mentioned above, we're not using the forgetting
                # rate, but instead updating belief strength using
                # strengtheningRate --Chris
                self.beliefs[service][2] += (self.beliefs[service][2] *
                                             self.strengtheningRate)
                # used to be 'max' but I think 'min' was intended
                new_strength = min(self.beliefs[service][2], 0.9999)
                self.beliefs[service] = [username, password, new_strength]
            else:
                self.beliefs[service] = [username, password,
                                         self.initial_belief]
            return [{}]

        elif login_response[0] == 'failed:logged_in':
            self.signOut(service)
            return []

        else:
            if changed_password:
                # NOTE: as mentioned above, we're not using the forgetting
                # rate, but instead updating belief strength using
                # strengtheningRate --Chris
                self.beliefs[service][2] -= (self.beliefs[service][2] *
                                             self.strengtheningRate)
                # used to be 'min' but I think 'max' was intended
                new_strength = max(self.beliefs[service][2], 0.0001)
                self.beliefs[service] = [username, password, new_strength]
            return self.signIn((goal, service))

    def signOut(self, (goal, service)):
        """ This should be equivalent to the signOut subgoal in prolog
        It checks if the user is logged in, and if so, it sends a message to
        log him out.

        Defined Actions:
            1. retrieveStatus
            2. signOut
        """
        username = self.beliefs[service][0]
        response = self.sendAction('retrieveStatus', [service, username])
        if response[0] == 'failure':
            print 'Error: User was not logged in'
            return []

        else:
            self.sendAction('signOut', [service, username])
            print 'Success: User successfully logged out'
            return [{}]

    def resetPassword(self, (goal, service)):
        print 'agent beliefs for service', service, 'are', \
            self.beliefs[service]

        [username, old_password, belief] = self.beliefs[service]
        new_password = self.choose_password(username)
        status_response = self.sendAction('resetPassword', [service, username,
                                          old_password, new_password])

        if status_response[0] == 'success':
            print 'Success: password reset successfully'
            if new_password in self.writtenPasswords:
                self.beliefs[service] = [username, new_password,
                                         self.initial_belief, 0.999]
            else:
                self.beliefs[service] = [username, new_password,
                                         self.initial_belief]
            print 'new beliefs:', self.beliefs[service]
            return [{}]

        else:
            # not yet implemented handling of requirements
            print 'Reset password failed: Handle requirements'
            return []

    # Will be about password forget rate stopping criterion, but for now just
    # false
    def check_termination(self, call):
        return []

    # Extracted by Jim from setUpAccount and resetPassword
    def choose_password(self, username, requirements=None):
        # Note - this fails when the password_list is exhausted, which happens
        # because passwords are moved from this list to the knownPasswords
        # list. I'm not sure what the correct behavior is here - is it to
        # choose something from that list when this one is empty? - Jim
        #
        # I've added code below that uses the 'password_list' if there are
        # still values on it, and otherwise picks a known password.
        list_of_new = self.password_list
        list_of_old = self.known_passwords

        if list_of_new:
            desired_pass = random.choice(self.password_list)
            # constructive not surgical
            list_of_new = [x for x in list_of_new if x is not desired_pass]

        elif self.known_passwords:
            desired_pass = random.choice(self.known_passwords)
            # constructive not surgical
            list_of_old = [x for x in list_of_old if x is not desired_pass]

        # if there are requirements verify that the password complies with them
        if requirements is not None:
            # will run through every unused password, then every used one, so
            # maxTries is more of a timeout for long lists
            maxTries = 100
            while not requirements.verify(username, desired_pass) \
                    and maxTries > 0:
                print 'password', desired_pass, 'chosen from', \
                    len(list_of_new), len(list_of_old), \
                    'not verified against', requirements

                if list_of_new:
                    desired_pass = random.choice(list_of_new)
                    list_of_new = [x for x in list_of_new if x is not
                                   desired_pass]

                elif list_of_old:
                    desired_pass = random.choice(list_of_old)
                    list_of_old = [x for x in list_of_old if x is not
                                   desired_pass]
                else:
                    break  # no more passwords to try
                maxTries -= 1

        # if pass is too hard on the user's cognitive burden, reuse the hardest
        # one or write it down, the decision is based on memoBias parameter
        # maybe add some distance heuristics later
        new_password_verified = True if requirements is None else \
            requirements.verify(username, desired_pass)

        if new_password_verified and \
            (self.password_complexity(desired_pass) + self.cognitiveBurden) < \
                self.cognitiveThreshold:
            password = desired_pass
            # add to the list of known pass, and remove from potential passes
            if desired_pass not in self.known_passwords:
                self.known_passwords.append(desired_pass)
            if desired_pass in self.password_list:
                self.password_list.remove(desired_pass)

        elif self.known_passwords and \
                (not new_password_verified or
                 distPicker(self.memoBias, random.random()) == 'reuse'):
            # We have to reuse if we didn't find a good enough new password.
            # password = max(stats.iteritems(), key=operator.itemgetter(1))[0]
            # .. but actually we tried to reuse above, so we need to add
            # something that synthesizes a password
            # here, e.g. adding numbers or characters if that is the problem,
            # etc.
            password = max(self.known_passwords, key=self.password_complexity)

        else:
            password = desired_pass
            self.writtenPasswords.append(desired_pass)
            self.password_list.remove(desired_pass)
        return password

    # Should return a measure of the complexity of the password by our usual
    # standards. Here I'm just using the length to get this up and running
    # (Jim)
    # NOTE: used for determining cognitive burden of passwords
    def password_complexity(self, password):
        return len(password)


if __name__ == "__main__":
    PasswordAgent().agentLoop(1000)
