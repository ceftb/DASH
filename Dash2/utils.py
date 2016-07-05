import communication_aux
import operator
import random
import re


def distPicker(distribution, r=random.random()):
    ''' Function takes distribution of services and a value;
    then returns the value for that particular range

    Input:
        distribution (list of pairs)
        r (float)
    Output
        value (type)
    '''
    previous = 0.0
    # This used to use a dictionary and iteritems, but the order of that is not guaranteed
    for item, value in distribution:
        if previous <= r <= value:
            return item
        else:
            previous = value



#### PASSWORD SIMULATION AGENT

#def initializeContact(socket, id, service_type):
#    ''' Helper function to get the actuall service '''
#    sendMessageToWorldHub(self.port, 1, [id, 'getAccount']) # send service type
#    return getResponseFromWorldHub(self.port) # recieve actuall service


class Requirements:
    ''' Small class that holds password requirements
    '''
    def __init__(self, min_len=6, max_len=30, lowercase=0, uppercase=0, numbers=0, symbols=0):
        self.min_len = min_len
        self.max_len = max_len
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.numbers = numbers
        self.symbols = symbols

    def __str__(self):
        return "[min_len=" + str(self.min_len) + ", max_len=" + str(self.max_len) + ", lowercase=" + str(self.lowercase) \
               + ", uppercase=" + str(self.uppercase) + ", numbers=" + str(self.numbers) + ", symbols=" + str(self.symbols) + "]"

    def get_len(self):
        return [self.min_len, self.max_len]

    def get_lowercase(self):
        return self.lowercase

    def get_uppercase(self):
        return self.uppercase

    def get_numerics(self):
        return self.numbers

    def get_symbols(self):
        return self.symbols

    def verify(self, username, password):   # I guess username might be part of the verification process in the future
        if self.min_len <= len(password) <= self.max_len \
           and (self.uppercase == 0 or sum(1 for c in password if c.isupper()) <= self.uppercase) \
           and (self.numbers == 0 or sum(1 for c in password if c.isdigit()) <= self.numbers) \
           and (self.symbols == 0 or sum(1 for c in password if not (re.match('^[a-zA-Z0-9]*$', c))) <= self.symbols):
            return True
        else:
            return False


# Store information about what constitutes weak, average or strong requirements in this file.
# These numbers come from bruno_services - maybe a different set should be used, let me know (Jim)
def create_requirements(strength):
    if strength == 'weak':
        return Requirements(min_len=1 + rand(4), max_len=64)
    elif strength == 'average':
        return Requirements()


# This is shorthand to make create_requirements above more readable
def rand(max_value):
    return random.randint(0, max_value)


class Service:
    def __init__(self, service_type, name, requirements):
        self.type = service_type
        self.name = name
        self.requirements = requirements
        # Use 'weak', 'average' and 'strong' as shorthand for a distribution of requirements
        if requirements in ['weak', 'average', 'good', 'strong']:
            self.requirements = create_requirements(requirements)
        self.user_name_passwords = {}    # dict of user names and passwords used on this service
        self.user_status = {}    # dict of status of user on service, e.g. 'logged_in'

    def __str__(self):
        return "[" + str(self.name) + ", requirements=" + str(self.requirements) + "]"

    def get_name(self):
        return self.name

    def get_requirements(self):
        return self.requirements

    def get_service_type(self):
        return self.type

    def has_user(self, name):
        return name in self.user_name_passwords

    def add_user(self, user_name, password):
        self.user_name_passwords[user_name] = password


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
