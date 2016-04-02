#!/usr/bin/env python

# this is adapted from http://ilab.cs.byu.edu/python/threadingmodule.html

import select
import socket
import sys
import threading
import struct
import pickle
from communication_aux import message_types
import communication_aux

class WorldHub:
    def __init__(self, port = None):
        print "initializing world hub..."
        self.host = 'localhost'
        if port == None:
            self.port = 5678
        else:
            self.port = port
        self.backlog = 5
        self.server = None
        self.threads = []

    def run(self):
        # attempt to open a socket with initialized values.
        print "opening socket..."
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "could not open. socket. following error occurred: " + message
            sys.exit(1)
        
        # listen for new connections.
        print "successfully opened socket. listening for new connections..."
        print "if you wish to quit the server program, enter q"
        input = [self.server, sys.stdin]
        listening = True
        while listening:
            input_ready, output_ready, except_ready = select.select(input, [], [])
            for s in input_ready:
                # if a new connection is requested, start a new thread for it
                if s == self.server:
                    c = serveClientThread(self.server.accept())
                    c.start()
                    self.threads.append(c)
                # else if we got input from the keyboard, stop
                elif s == sys.stdin:
                    user_input = sys.stdin.readline()
                    listening = False
                    if user_input == "q\n":
                        listening = 0
                    else:
                        print "if you wish to quit, enter q."
        
        # quit
        print "quitting program as requested by user..."
        self.server.close()
        for c in self.threads:
            c.join()
                    
class serveClientThread(threading.Thread):

    lowest_unassigned_id = 0
    lock = threading.Lock()

    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
    
        return

    def run(self):

        try:
            while True:
                # determine what the client wants
                [message_type, message] = self.getClientRequest()
                
                print "received following information in client request:"
                print "message type: %s" % message_type
                print "message: %s" % message
                
                # do something with the message....
                # types of messages to consider: register id, process action, update state 
                self.handleClientRequest(message_type, message)

        finally:
            print "closing socket..."
            self.client.close()
            print "exiting client thread"

    # read message and return a list of form [client_id, message_type, message_contents]
    def getClientRequest(self):
        # read first 4 bytes for message len
        print "getting message type and message length..."
        bytes_read = 0
        bytes_expected = 8
        message_header = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                message_header += data
                bytes_read += len(data)
            else:
                self.client.close()
                running = 0
        message_type, message_len = struct.unpack("!II", message_header)

        print "message type: %d" % message_type
        print "message len: %d" % message_len

        # read payload 
        print "getting payload..."
        bytes_read = 0
        bytes_expected = message_len
        message = ""
        while bytes_read < bytes_expected:
            data = self.client.recv(bytes_expected - bytes_read)
            if data:
                message += data
                bytes_read += len(data)
            else:
                self.client.close()
        message_payload = pickle.loads(message)

        print "successfully retrieved payload %s ... returning." % message_payload

        return [message_type, message_payload]

    def handleClientRequest(self, message_type, message_payload):
        # 3 types:
        #    0: register id, update state
        #    1: handle action, update state, relay relevant observations to client
        #    2: relay recent observations to client

        if message_types['register'] == message_type:
            response = self.handleRegisterRequest(message_payload)
        elif message_types['send_action'] == message_type:
            response = self.handleSendActionRequest(message_payload)
        elif message_types['get_updates'] == message_type:
            response = self.handleGetUpdatesRequest(message_payload)
        else:
            print "uhoh!"

        self.sendMessage(response)

        return

    def sendMessage(self, unserialized_message):
        serialized_message = pickle.dumps(unserialized_message)
        message_len = len(serialized_message)
        message = struct.pack("!I", message_len) + serialized_message
        self.client.sendall(message)
        
        return
    
    def handleRegisterRequest(self, message):
        print 'handling registration request...'
        aux_data = message[0]
        return self.processRegisterRequestWrapper(aux_data)

    def handleSendActionRequest(self, message):
        print 'handling send action request...'
        id = message[0]
        action = message[1]
        aux_data = message[2]
        return self.processSendActionRequest(id, action, aux_data)

    def handleGetUpdatesRequest(self, message):
        print 'handling get updates request...'
        id = message[0]
        aux_data = message[1]
        return self.processGetUpdatesRequest(id, aux_data)

    def processRegisterRequestWrapper(self, aux_data):
        with serveClientThread.lock:
            assigned_id = serveClientThread.lowest_unassigned_id
            serveClientThread.lowest_unassigned_id += 1
        return self.processRegisterRequest(assigned_id, aux_data)

    ###########################################################################
    # - users should not need to change any of the functions above            #
    # - very unlikely processGetUpdatesRequest would need to be changed       #
    # - unlikely processRegisterRequest would need to be changed              #
    # - the remaining 3 functions below will nearly always need to be changed #
    #                                                                         #
    # remember to acquire lock for critical regions!                          #    
    ###########################################################################

    def processRegisterRequest(self, id, aux_data):
        aux_response = []
        return ["success", id, aux_response]

    def processGetUpdatesRequest(self, id, aux_data):
        aux_response = self.getUpdates(id, aux_data)
        return [aux_response]
            
    def processSendActionRequest(self, id, action, aux_data):
        # sample code:
        # if action == "look up":
        #     result = "success"
        #     aux_response = ["agent observes blue sky", "agent observes plane"]
        #     aux_response = aux_response + self.updateState(id, action, aux_data) + self.getUpdates(id, aux_data)
        # elif action == "look down":
        #     result = "success"
        #     aux_response = ["agent observes grass"]
        #     aux_response = aux_response + self.updateState(id, action, aux_data) + self.getUpdates(id, aux_data)
        # return [result, aux_response]

        # placeholder code
        result = "success"
        aux_response = self.updateState(id, action, aux_data) + self.getUpdates(id, aux_data)
        return [result, aux_response]

    def updateState(self, id, action, aux_data):
        partial_aux_response = []
        return partial_aux_response

    def getUpdates(self, id, aux_data):
        updates = []
        return updates

if __name__ == "__main__":
    s = WorldHub()
    s.run()
