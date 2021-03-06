import socket
import struct
import pickle
from communication_aux import message_types


class Client(object):
    """
    Template class for the client agent
    """
    def __init__(self, host=None, port=None):
        """ Initialization of the client.
        It is required to run Client.run() in order to recieve ID from the
        World Hub.
        Args:
            host(string) - default='localhost' #  hostname of the worldhub
            port(int) - default:5678           # port for opening connections
        Example:
            c = Client()
        """
        print "initializing client..."
        if host is None:
            self.server_host = 'localhost'
        else:
            self.server_host = host
        if port is None:
            self.server_port = 5678
        else:
            self.server_port = port
        self.sock = None
        self.id = None
        self.connected = False

    def test(self):
        """
        Registration of the client
        Client establishes connection, and registers the client with the World
        Hub.
        Example:
            c.run()
        """
        try:
            self.register([])
            k = 0

            # test loop
            while k < 100:
                k += 1
                if k % 3 == 0:
                    self.sendAction("look down", [])
                elif k % 2 == 0:
                    self.sendAction("look up", [])
                else:
                    self.getUpdates([])

            print "closing socket..."
            self.disconnect([])
            print "exiting"
            return

        except:
            print "closing socket..."
            self.sock.close()
            print "exiting"

    def establishConnection(self):
        """ Establishes physical connection with the worldhub
        """
        print "connecting to %s on port %s..." % (self.server_host, self.server_port)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            print "successfully connected."
        except:
            self.connected = False
            print "Problem connecting to hub server, continuing without agent communications"

    def register(self, aux_data=[]):
        """ Register with world hub. Essentially, this is used to assign the client a unique id
        Args:
            aux_data(list) # any extra information you want to relay to the world hub during registration
        """

        print "establishing connection..."

        self.establishConnection()

        if not self.connected:
            print "no connection established, agent not registered"
            return None
        
        print "registering..."

        response = self.sendAndReceive(message_types['register'], [aux_data])

        result = response[0]
        self.id = response[1]
        aux_response = response[2]

        print "result: %s." % result
        print "my id: %d." % self.id
        print "aux response: %s." % aux_response

        return response

    def sendAction(self, action, aux_data=[]):
        """ Send actionin form of message_types['send_action'] to the World Hub
        And awaits the appropriate response
        Args:
            action(string)  #  action to be sent to World Hub
            aux_data(list) #  auxiliary data about the client
        Example:
            #to be added
        """

        if self.sock is None or not self.connected:
            print 'Client sent an action, but there is no connection to a hub. Check if register() was called.'
            return None

        response = self.sendAndReceive(message_types['send_action'], [self.id, action, aux_data])

        # Allow for the result to be a list, e.g. ['success', [data]], or just an object, e.g. 'fail'.
        if isinstance(response, (list, tuple)):
            result = response[0]
            if len(response) > 1:
                aux_response = response[1]
            else:
                aux_response = []
        else:
            result = response
            aux_response = []

        print "hub action", action, str(aux_data) if aux_data else "", \
            "received response:", result, ", aux response: " + str(aux_response) if aux_response != [] else ""

        self.processActionResponse(result, aux_response)

        return response

    def getUpdates(self, aux_data=[]):
        """ Sends request for update with the aux_data and receives the update
        from the World Hub
        Args:
            aux_data(list)    # Data to be sent to the world hub
        Example:
            #to be added
        """
        response = self.sendAndReceive(message_types['get_updates'], [self.id, aux_data])
        aux_response = response[0]

        print "successfully received response..."
        print "aux data: %s." % aux_data

        self.processUpdates(aux_response)

        return

    def disconnect(self, aux_data=[]):
        """ Sends request to disconnect from world hub"
        Args:
            aux_data(list)    # Data to be sent to the world hub
        """

        if self.sock is not None:
            self.sendMessage(message_types['disconnect'], [self.id, aux_data])
        
            print "disconnecting from world hub."
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        #sys.exit(0)  # Should not automatically kill the process

    def processActionResponse(self, result, aux_response):
        # we may want to hook in some sort of inference engine here
        self.processUpdates(aux_response)
        return

    def processUpdates(self, aux_data):
        return

    def sendAndReceive(self, message_type, message_contents):
        self.sendMessage(message_type, message_contents)
        return self.receiveResponse()

    def sendMessage(self, message_type, message_contents):
        # send message header followed by serialized contents
        serialized_message_contents = pickle.dumps(message_contents)
        message_len = len(serialized_message_contents)
        message_header = struct.pack("!II", message_type, message_len)
        message = message_header + serialized_message_contents
        return self.sock.sendall(message)

    def receiveResponse(self):
        # read header (i.e., find length of response)
        bytes_read = 0
        bytes_to_read = 4
        response_header = ""
        while bytes_read < bytes_to_read:
            data = self.sock.recv(bytes_to_read - bytes_read)
            if data:
                response_header += data
                bytes_read += len(data)
            else:
                print "trouble receiving message..."
                self.sock.close()
        response_len, = struct.unpack("!I", response_header)

        # read message
        bytes_read = 0
        bytes_to_read = response_len
        serialized_response = ""
        while bytes_read < bytes_to_read:
            data = self.sock.recv(bytes_to_read - bytes_read)
            if data:
                serialized_response += data
                bytes_read += len(data)
            else:
                self.sock.close()
        response = pickle.loads(serialized_response)

        return response

if __name__ == "__main__":
    """ Simplistic command line driver
    """
    c = Client()
    c.test()
