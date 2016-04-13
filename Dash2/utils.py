import communication_aux
import operator


def distPicker(distribution, r):
    ''' Function takes distribution of services and a value;
    then returns the value for that particular range

    Input:
        distribution (dict)
        r (float)
    Output
        value (type)
    '''
    previous = 0.0
    for key, value in distribution.iteritems():
        if r in range(previous, key):
            return value
        else:
            previous = key



#### PASSWORD SIMULATION AGENT

def initializeContact(socket, id, service_type):
    ''' Helper function to get the actuall service '''
    sendMessageToWorldHub(self.port, 1, [id, 'getAccount']) # send service type
    return getResponseFromWorldHub(self.port) # recieve actuall service



class requirements():
    ''' Small class that holds password requirements
    '''
    def __init__(self, min_len=6, max_len=30, uppercase=0, numbers=0, symbols=0):
        self.min_len = min_len
        self.max_len = max_len
        self.uppercase = uppercase
        self.numbers = numbers
        self.symbols = symbols

    def getLen(self):
        return [self.min_len, self.max_len]
    def getUppercase(self):
        return self.uppercase
    def getNumerics(self):
        return self.numbers
    def getSymbols(self):
        return self.symbols

    def verify(self, username, password):
        if len(password) in xrange(min_len, max_len) \
        and sum(1 for c in password if c.isupper()) < self.uppercase \
        and sum(1 for c in password if c.isdigit()) < self.numbers \
        and sum(1 for c in password if not (re.match('^[a-zA-Z0-9]*$', c))) < self.symbols:
            return True
        else:
            return False


class service():
	def __init__(self, service_type, name, requirements):
		self.type = service_type
		self.name = name
		self.requirements = requirements

	def getName():
		return self.name

	def getRequirements():
		return self.requirements

	def getServiceType():
		return self.type


### THis is more elaborate way to pick passwords - to finish
# def pickPassword(password_list, method=RDM, service_type=None):
#     ''' Function takes password list, and possible method of picking one and
#     returns possible password.
#
#     Input:
#         password_list (dict, pass:complexity) - passwords from which to pick
#         method (string) - RDM (default) for picking one at random
#                         - HIA for hierachical based on the service type
#         service_type (string) - None (default): pick one at random
#                               - otherwise set arbitrary complexity scheme
#                               (idea is that agents will pick more secure passwords
#                               for more important accounts)
#     Output:
#         password (string)
#     '''
#     # Type safety
#     if not password_list:
#         #raise an error
#         print "Error1: parsing password list - pl empty"
#
#     # if method is random or there is no service_type, pick password at random
#     if method == 'RDM' or service_type is None:
#         import random
#         # I am not concerned about reuse at this point because passwords are deleted
#         # from the potential passwords lists
#         return random.sample(password_list)
#
#     elif method == 'HIA':   # potentially add elif
#         pot_password = random.sample(password_list)
