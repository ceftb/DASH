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


from dash import DASHAgent, isConstant, isVar
import random
from utils import distPicker
import operator
import sys
import minimum_spanning_tree


class PasswordAgent(DASHAgent):
    # add socket
    def __init__(self):
        DASHAgent.__init__(self)

        response = self.register()
        if response is None or response[0] != "success":
            print "Error: world hub not reachable - exiting. This agent will only run with a world hub (e.g pass_sim_hub)."
            sys.exit()
        self.id = response[1]

        # Added by Jim based on bruno_user.pl. This is the list of all possible password choices for
        # the agent, not the ones the agent currently users.
        self.password_list = ['p', 'P', 'pw', 'Pw', 'pw1', 'Pw1', 'pass', 'Pass', 'pas1', 'Pas1', 'pass1', 'Pass1',
                              'PaSs1', 'password', 'P4ssW1', 'PassWord', 'PaSs12', 'PaSsWord', 'PaSsW0rd', 'P@SsW0rd',
                              'PassWord1', 'PaSsWord1', 'P4ssW0rd!', 'P4SsW0rd!', 'PaSsWord12', 'P@SsWord12',
                              'P@SsWoRd12', 'PaSsWord!2', 'P@SsWord!234', 'P@SsWord!234', 'MyP4SsW0rd!',
                              'MyP4SsW0rd!234', 'MyP@SsW0rd!234', 'MyPaSsWoRd!234?', 'MyPaSsW0Rd!234?',
                              'MyS3cUReP@SsW0rd!2345', 'MyV3ryL0ngS3cUReP@SsW0rd!2345?']

        # distribution of probabilities for every service type. Used to be dictionaries, but then order is not guaranteed
        self.serviceProbs = [('mail', 0.35), ('social_net', 0.85), ('bank', 1.0)]
        # bias between memorizing or writing down
        self.memoBias = [('reuse', 0.5), ('write_down', 1.0)]
        # initial strength of beliefs
        self.initial_belief = 0.65
        # forgetting rate - percent of belief lost
        self.forgettingRate = 0.15
        # strengthening rate
        self.strengtheningRate = 0.2

        self.choose_password_method = 'random'  # 'list-order' or 'random' -
        # how passwords are chosen either from the list of new or existing passwords


        # initial cog. burden
        self.cognitiveBurden = 0  # Perhaps this is computed at each point, haven't figured out the details yet.
        # These were copied from bruno_user.pl in lib/logic - check for comments there.
        self.cognitiveThreshold = 30  # was 68 in the prolog but trying one that limits to something like 12 passwords
        # (the prolog version included the cost for usernames, not currently included)
        self.recallThreshold = 0.5
        self.passwordReusePriority = 'long'
        self.passwordReuseThreshold = 54
        self.passwordForgetRateStoppingCriterion = 0.0005
        # pairs used - dict {service:[username, password]}
        self.known = {}
        # usernames used - dict {username:complexity} (I changed to just a list - Jim)
        self.knownUsernames = []
        # passwords used - dict {password:complexity} (I changed to just a list - Jim)
        self.known_passwords = []
        # list of writen pairs
        self.writtenPasswords = []
        # USER beliefs
        self.beliefs = {}

        # This is used below so I added it here to make the code run.
        # Not sure how it should interact with the variables above
        self.username_list = ['user1', 'user12', 'admin']

        # i'm not really clear about usage of primitive actions vs just defining
        # new goals
        self.primitiveActions([
                               ('checkTermination', self.check_termination),
                               ('setupAccount', self.setupAccount),
                               ('signIn', self.signIn),
                               ('signOut', self.signOut),
                               ('resetPassword', self.resetPassword)
                               ])

        # The agent goal description is short, because the rational task is not that important here.
        self.readAgent("""

goalWeight doWork 1         # repeat the proces

goalRequirements doWork
    checkTermination(criterion, beliefs)
    forget([checkTermination(c, b)])

goalRequirements doWork
    setupAccount(service_type, service)
    signIn(service)
    signOut(service)
    resetPassword(service)
    forget([setupAccount(st,s), signIn(s), signOut(s), resetPassword(s)])

# This means that every iteration it will need to be re-achieved
transient doWork

""")
        self.trace_action = True


    # service_type_var may be unbound or bound to a requested service_type. service_var is unbound
    # and will be bound to the result of setting up the service
    def setupAccount(self, (goal, service_type_var, service_var)):
        ''' Should be equivalent to createAccount subgoal in prolog version
        It takes service type as an input, and decides which
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
        if isVar(service_type_var):
            # choose the service type, and find the actual service
            service_type = distPicker(self.serviceProbs, random.random())

        # Decide the service to log into
        [status, service, requirements] = self.sendAction('getAccount', [service_type])
        #print 'chosen account to set up:', status, service, requirements

        ### choose Username
        # if the list of existing usernames is not empty, pick one at random,
        # else pick one from list of predefined usernames
        # here we should add some logic for cognitive burden but I didn't play with
        # it as we didn't have usernames elaborately in prolog
        if self.knownUsernames:
            username = random.choice(self.knownUsernames)
        else:
            username = random.choice(self.username_list)

        password = self.choose_password(username, requirements)

        # If account is be created, update beliefs else repeat
        # I am not sure if it would make more sense to keep beliefs local in this
        # case
        [status, data] = self.sendAction('createAccount', [service, username, password])
        #print 'create account result:', [status, data]
        if status == 'success':
            print 'Account created on', service, 'with user', username, 'and password', password, requirements
            if password not in self.writtenPasswords:
                self.beliefs[service] = [username, password, self.initial_belief]
            else:
                self.beliefs[service] = [username, password, self.initial_belief, 0.9999]
            if isVar(service_type_var):
                return [{service_type_var: service_type, service_var: service}]
            else:
                return [{service_var: service}]
        elif status == 'failed:user':
            #print 'Failed to create account on', service, ': username already exists'  # too frequent to print
            # Should succeed in 'setting up' the account though
            if isVar(service_type_var):
                return [{service_type_var: service_type, service_var: service}]
            else:
                return [{service_var: service}]
        elif status == 'failed:reqs':
            #self.setupAccount(service_type, service, result[1])
            print 'Failed to create account on ', service, ': password failed the requirements'
            return []
        else:
            print 'unknown result for creating account:', service, status, data
            return []


    def signIn(self, (goal, service)):
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
        if service not in self.beliefs or not self.beliefs[service]:
            print "User has no beliefs for this account"

        [username, password, belief] = self.beliefs[service]
        # Select password: essentially the weaker the belief is the greater the chance
        # that user will just pick one of their known username/passwords
        distribution = [(password, belief), ('other_known', 1.0)]
        if distPicker(distribution, random.random()) == 'other_known' and self.knownUsernames and self.known_passwords:
            changed_password = True
            username = random.choice(self.knownUsernames)
            password = random.choice(self.known_passwords)
        else:
            changed_password = False

        # Try to signIn; if agent knew the password, update the strength of
        # belief; analogously it works if user did not know the password.
        # Finally, if failed, repeat the sign in process with the updated beliefs
        login_response = self.sendAction('signIn', [service, username, password])
        if login_response[0] == 'success':
            if changed_password:
                self.beliefs[service][2] += (self.beliefs[service][2]*self.strengtheningRate)
                new_strength = min(self.beliefs[service][2], 0.9999)   # used to be 'max' but I think 'min' was intended
                self.beliefs[service] = [username, password, new_strength]
                print 'signed into', service, 'with changed username and password', username, ',', password
            else:
                self.beliefs[service] = [username, password, self.initial_belief]
                print 'signed into', service, 'with same username and password', username, ',', password
            return [{}]
        elif login_response[0] == 'failed:logged_in':
            self.signOut(service)
            return []
        else:
            if changed_password:
                self.beliefs[service][2] -= (self.beliefs[service][2]*self.strengtheningRate)
                new_strength = max(self.beliefs[service][2], 0.0001)  # used to be 'min' but I think 'max' was intended
                self.beliefs[service] = [username, password, new_strength]
            return self.signIn((goal, service))

    def signOut(self, (goal, service)):
        """ This should be equivalent to the signOut subgoal in prolog
        It checks if the user is logged in, and if so, it sends a message to log
        him out.

        Defined Actions:
            1. retrieveStatus
            2. signOut
        """
        username = self.beliefs[service][0]
        response = self.sendAction('retrieveStatus', [service, username])
        if response[0] == 'failure':
            print 'Error signing out: User was not logged in to', service, 'as', username
            return []
        else:
            self.sendAction('signOut', [service, username])
            print 'User successfully logged out from', service, 'as', username
            return [{}]

    def resetPassword(self, (goal, service)):
        #print 'Resetting: agent beliefs for service', service, 'are', self.beliefs[service]
        [username, old_password, belief] = self.beliefs[service]

        new_password = self.choose_password(username)

        status_response = self.sendAction('resetPassword', [service, username, old_password, new_password])

        if status_response[0] == 'success':
            if new_password in self.writtenPasswords:
                self.beliefs[service] = [username, new_password, self.initial_belief, 0.999]
            else:
                self.beliefs[service] = [username, new_password, self.initial_belief]
            print 'new beliefs for', service, 'after resetting:', self.beliefs[service]
            return [{}]
        else:
            #not yet implemented handling of requirements
            print 'Reset password failed: Handle requirements'
            return []

    # Will be about password forget rate stopping criterion, but for now just false
    # This means the simulation will go on forever if the agentLoop call doesn't use a finite number of steps
    def check_termination(self, call):
        return []

    # Extracted by Jim from setUpAccount and resetPassword, and modified to match the description in papers
    # such as the HotSoS 15 paper.
    def choose_password(self, username, requirements=None):
                ### choose Password
        # Note - this fails when the password_list is exhausted, which happens because passwords are moved
        # from this list to the knownPasswords list. I'm not sure what the correct behavior is here -
        # is it to choose something from that list when this one is empty? - Jim
        # I've added code below that uses the 'password_list' if there are still values on it, and otherwise picks
        # a known password.
        # This used to make a random choice, now it runs through the password_list in order, which is assumed
        # to be roughly in complexity order (added indices into password_list and known_passwords)
        list_of_new = self.password_list  # These are used with random choice, to pick without replacement
        list_of_old = self.known_passwords
        new_pw_index = 0
        old_pw_index = 0
        if list_of_new:
            if self.choose_password_method == 'random':
                desired_pass = random.choice(self.password_list)
                list_of_new = [x for x in list_of_new if x is not desired_pass]  # constructive, not surgical
            else:
                desired_pass = self.password_list[new_pw_index]  # random.choice(self.password_list)
                new_pw_index += 1
        elif self.known_passwords:
            if self.choose_password_method == 'random':
                desired_pass = random.choice(self.known_passwords)
                list_of_old = [x for x in list_of_old if x is not desired_pass]  # constructive not surgical
            else:
                desired_pass = self.known_passwords[old_pw_index]  # random.choice(self.known_passwords)
                old_pw_index += 1
        # if there are requirements verify that the password complies with them
        if requirements is not None:
            # will run through every unused password, then every used one, so maxTries is more of a timeout
            # for long lists
            max_tries = 100
            while (not requirements.verify(username, desired_pass) or self.overCogLoad(desired_pass)) and max_tries > 0:
                #print 'password', desired_pass, 'chosen from', len(list_of_new), len(list_of_old), \
                #    'not verified against', requirements
                if (self.choose_password_method == 'list-order' and new_pw_index < len(self.password_list)) or \
                        (self.choose_password_method == 'random' and list_of_new):
                    if self.choose_password_method == 'list-order':
                        desired_pass = self.password_list[new_pw_index]
                        new_pw_index += 1
                    else:
                        desired_pass = random.choice(list_of_new)
                        list_of_new = [x for x in list_of_new if x is not desired_pass]
                elif (self.choose_password_method == 'list-order' and old_pw_index < len(self.known_passwords)) or \
                        (self.choose_password_method == 'random' and list_of_old):
                    if self.choose_password_method == 'list-order':
                        desired_pass = self.known_passwords[old_pw_index]
                        old_pw_index += 1
                    else:
                        desired_pass = random.choice(list_of_old)
                        list_of_old = [x for x in list_of_old if x is not desired_pass]
                else:
                    break  # no more passwords to try
                max_tries -= 1

        # if pass is too hard, reuse the hardest one or write it down,
        # the decision is based on memoBias parameter
        # maybe add some distance heuristics later
        new_password_verified = (requirements is None or requirements.verify(username, desired_pass)) \
            and not self.overCogLoad(desired_pass)

        if new_password_verified:
            password = desired_pass
            # add to the list of known pass, and remove from potential passes
            if desired_pass not in self.known_passwords:
                self.known_passwords.append(desired_pass)
                # For now, compute and print the levenshtein set cost of the known passwords
                print len(self.known_passwords), 'Levenshtein cost:', levenshtein_set_cost(self.known_passwords), self.known_passwords
            if desired_pass in self.password_list:
                self.password_list.remove(desired_pass)
        elif self.known_passwords and \
                (not new_password_verified or distPicker(self.memoBias, random.random()) == 'reuse'):
            # We have to reuse if we didn't find a good enough new password.
            #password = max(stats.iteritems(), key=operator.itemgetter(1))[0]
            # .. but actually we tried to reuse above, so we need to add something that synthesizes a password
            # here, e.g. adding numbers or characters if that is the problem, etc.
            password = max(self.known_passwords, key=self.password_complexity)
        else:
            password = desired_pass
            self.writtenPasswords.append(desired_pass)
            self.password_list.remove(desired_pass)
        return password

    # Boolean - whether adding the password as a new password will tip the agent over its cognitive load threshold
    def overCogLoad(self, password):
        if password in self.known_passwords:
            return False  # only increases the load if it's not already used
        else:
            new_cost = levenshtein_set_cost(self.known_passwords + [password])
            # Should also check username cost, but currently don't
            return new_cost > self.cognitiveThreshold

    # Should return a measure of the complexity of the password by our usual standards.
    # Here I'm just using the length to get this up and running - and not sure this is what will be used finally
    def password_complexity(self, password):
        return len(password)

# The cost of a set of strings is the cost of the minimum spanning tree over the set, with
# levenshtein distance as edge weight.
def levenshtein_set_cost(strings):
    # First create the graph (a complete graph)
    graph = {}
    for i in xrange(0, len(strings)):
        graph[i] = {}
        for j in xrange(0, len(strings)):
            if i < j:  # this will always come first
                graph[i][j] = levenshtein_distance(strings[i], strings[j])
            elif i > j:  # (so don't compute twice)
                graph[i][j] = graph[j][i]
    # Next compute the minimum spanning tree
    mst = minimum_spanning_tree.minimum_spanning_tree(graph)
    return sum([graph[x][y] for (x,y) in mst])


# Copied from http://rosettacode.org/wiki/Levenshtein_distance
def levenshtein_distance(str1, str2):
    m = len(str1)
    n = len(str2)
    len_sum = float(m + n)
    d = []
    for i in range(m+1):
        d.append([i])
    del d[0][0]
    for j in range(n+1):
        d[0].append(j)
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)
                d[i].insert(j, minimum)
    l_dist = d[-1][-1]
    #ratio = (len_sum - l_dist)/len_sum
    #return {'distance':l_dist, 'ratio':ratio}
    return l_dist

print(levenshtein_distance("kitten","sitting"))
print(levenshtein_distance("rosettacode","raisethysword"))




if __name__ == "__main__":
    pa = PasswordAgent()
    pa.agentLoop(1000)
    # Use the results on the hub, because the agent may create ids and passwords and then forget them,
    # but they still exist.
    # print 'final beliefs are', pa.beliefs