import socket
import sys
import struct
import pickle
from communication_aux import message_types

class Client:
    """
    Template class for the client agent
    """
    def __init__(self, host = None, port = None):
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
        if host == None:
            self.server_host = 'localhost'
        else:
            self.server_host = host
        if port == None:
            self.server_port = 5678
        else:
            self.server_port = port
        self.client = None
        self.id = None

    def run(self):
        """ Registration of the client
        Client establishes connection, and registers the client with the World
        Hub.
        Example:
            c.run()
        """
        try:
            self.establishConnection()
            self.register()
            k = 0

            # test loop
            while True:
                k += 1
                if k % 3 == 0:
                    self.sendAction("look down", [])
                elif k % 2 == 0:
                    self.sendAction("look up", [])
                else:
                    self.getUpdates([])

        finally:
            print "closing socket..."
            self.client.close()
            print "exiting"

    def establishConnection(self):
        """ Establishes physical connection with the worldhub
        """
        print "connecting to %s on port %s..." % (self.server_host, self.server_port)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_host, self.server_port))

        print "successfully connected."

    def register(self):
        """ Registers Client on the world hub
        """
        payload = pickle.dumps([])
        message_len = len(payload)

        print "sending registration request to world hub..."
        message = struct.pack("!II", message_types['register'], message_len) + payload

        self.client.sendall(message)

        bytes_read = 0
        bytes_expected = 4
        response_header = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                response_header += data
                bytes_read += len(data)
            else:
                self.client.close()
        response_len, = struct.unpack("!I", response_header)

        bytes_read = 0
        bytes_expected = response_len
        serialized_response = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                serialized_response += data
                bytes_read += len(data)
            else:
                self.client.close()

        response = pickle.loads(serialized_response)

        result = response[0]
        self.id  = response[1]
        aux_data = response[2:]

        print "successfully received response..."

        print "result: %s." % result
        print "my id: %d." % self.id
        print "aux data: %s." % aux_data

        return response


    def sendAction(self, action, aux_data):
        """ Send actionin form of message_types['send_action'] to the World Hub
        And awaits the appropriate response
        Args:
            action(string)  #  action to be sent to World Hub
            aux_data(string) #  auxirilary data about the client
        Example:
            #to be added
        """

        payload = pickle.dumps([self.id, action] + aux_data)
        message_len = len(payload)

        print "sending following action '%s' to world hub" % action
        message = struct.pack("!II", message_types['send_action'], message_len) + payload

        self.client.sendall(message)

        bytes_read = 0
        bytes_expected = 4
        response_header = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                response_header += data
                bytes_read += len(data)
            else:
                self.client.close()
        response_len, = struct.unpack("!I", response_header)

        bytes_read = 0
        bytes_expected = response_len
        serialized_response = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                serialized_response += data
                bytes_read += len(data)
            else:
                self.client.close()

        response = pickle.loads(serialized_response)

        result = response[0]
        aux_data = response[1:]

        print "successfully received response..."

        print "result: %s." % result
        print "aux data: %s." % aux_data

        return response

    def getUpdates(self, aux_data):
        """ Sends request for update with the aux_data and recieves the update
        from the World Hub
        Args:
            aux_data(string)    # Data to be sent to the world hub
        Example:
            #to be added
        """
        payload = pickle.dumps([self.id] + aux_data)
        message_len = len(payload)

        print "sending action to world hub..."
        message = struct.pack("!II", message_types['get_updates'], message_len) + payload

        self.client.sendall(message)

        bytes_read = 0
        bytes_expected = 4
        response_header = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                response_header += data
                bytes_read += len(data)
            else:
                self.client.close()
        response_len, = struct.unpack("!I", response_header)

        bytes_read = 0
        bytes_expected = response_len
        serialized_response = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                serialized_response += data
                bytes_read += len(data)
            else:
                self.client.close()

        response = pickle.loads(serialized_response)

        aux_data = response[0:]

        print "successfully received response..."

        print "aux data: %s." % aux_data

        return response

if __name__ == "__main__":
    """ Simplistic command line driver
    """
    c = Client()
    c.run()
