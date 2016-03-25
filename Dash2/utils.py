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



def submitInfo(socket, id, username, password):
    # sends username/pass and waits for response
    sendMessageToWorldHub(socket, 1, [id, 'createAccount', [username, password]])
    result = getResponseFromWorldHub(socket)
    if  result[0]
        return True
    else:
        return False





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
