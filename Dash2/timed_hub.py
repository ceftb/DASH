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

import time

class WorldHub:

    lowest_unassigned_id = 0
    lock = threading.Lock()

    ############################################################
    # you should only need to modify a few world hub functions #
    #                                                          #
    # usually you'll only need to modify:                      #
    #  - processRegisterRequest                                # 
    #  - processGetUpdatesRequest                              #
    #  - processSendActionRequest                              #
    #  - updateState                                           #
    #  - getUpdates                                            #
    #                                                          #
    # you might also modify:                                   #
    #  - processDisconnectRequest                              #
    #                                                          #
    # remember to acquire lock for critical regions!           #
    ############################################################

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
        print 'This is the base class processSendActionRequest'
        result = "success"
        aux_response = self.updateState(id, action, aux_data) + self.getUpdates(id, aux_data)
        return [result, aux_response]

    def processDisconnectRequest(self, id, aux_data):
        print "Client %d has disconnected from the world hub." % id
        result = "this is ignored"
        return result

    def updateState(self, id, action, aux_data):
        partial_aux_response = []
        return partial_aux_response

    def getUpdates(self, id, aux_data):
        updates = []
        return updates

    ####################################################################
    # you probably shouldn't need to modify anything after this point! #
    ####################################################################

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
        self.run_flag = False

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

        # begin the simulation
        simulator = self.createSimulatorThread()
        simulator.start()

        try:
            # listen for new connections.
            print "successfully opened socket. listening for new connections..."
            print "to start the simulation, press enter s."
            print "if you wish to quit the server program, enter q."
            input = [self.server, sys.stdin]
            listening = True
            while listening:
                input_ready, output_ready, except_ready = select.select(input, [], [])
                for s in input_ready:
                    # if a new connection is requested, start a new thread for it
                    if s == self.server:
                        c = self.createServeClientThread(self.server.accept())
                        c.start()
                        self.threads.append(c)
                    # else if we got input from the keyboard, stop
                    elif s == sys.stdin:
                        user_input = sys.stdin.readline()
                        if user_input == "s\n":
                            self.run_flag = True
                        if user_input == "q\n":
                            #self.run_flag = False
                            listening = False
                        else:
                            print "if you wish to start the simulation, enter s"
                            print "if you wish to quit the simulation, enter q."
        
            # quit
            print "quitting program as requested by user..."
            print "joining client threads and signaling simulator thread to stop..."
            self.server.close()
            for c in self.threads:
                c.join()
            self.run_flag = False
            simulator.join()
            print "successfully quit program."

        except:
            # quit
            print "uhoh! some exception arose! quitting program..."
            print "joining client threads and signaling simulator thread to stop..."
            self.server.close()
            for c in self.threads:
                c.join()
            self.run_flag = False
            simulator.join()
            print "successfully quit program."

    def createServeClientThread(self, (client, address)):
        return serveClientThread(self, (client, address))

    def createSimulatorThread(self):
        return simulatorThread(self)

                    
class serveClientThread(threading.Thread):

    def __init__(self, hub, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.hub = hub

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

        except:
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
        elif message_types['disconnect'] == message_type:
            self.handleDisconnectRequest(message_payload)
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            sys.exit(0)
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
        print 'handling send action request for', self, '...'
        id = message[0]
        action = message[1]
        aux_data = message[2]
        return self.processSendActionRequest(id, action, aux_data)

    def handleGetUpdatesRequest(self, message):
        print 'handling get updates request...'
        id = message[0]
        aux_data = message[1]
        return self.processGetUpdatesRequest(id, aux_data)

    def handleDisconnectRequest(self, message):
        print 'handling disconnect request...'
        id = message[0]
        aux_data = message[1]
        return self.processDisconnectRequest(id, aux_data)

    def processRegisterRequestWrapper(self, aux_data):
        with self.hub.lock:
            assigned_id = self.hub.lowest_unassigned_id
            self.hub.lowest_unassigned_id += 1
        return self.processRegisterRequest(assigned_id, aux_data)

    ######################################################################
    # the following functions are wrappers that call world hub functions #
    #                                                                    #
    # you probably shouldn't need to modify them                         #
    ######################################################################

    def processRegisterRequest(self, id, aux_data):
        return self.hub.processRegisterRequest(id, aux_data)

    def processGetUpdatesRequest(self, id, aux_data):
        return self.hub.processGetUpdatesRequest(id, aux_data)
            
    def processSendActionRequest(self, id, action, aux_data):
        return self.hub.processSendActionRequest(id, action, aux_data)

    def processDisconnectRequest(self, id, aux_data):
        return self.hub.processDisconnectRequest(id, aux_data)

    def updateState(self, id, action, aux_data):
        return self.hub.updateState(id, action, aux_data)

    def getUpdates(self, id, aux_data):
        return self.hub.getUpdates(id, aux_data)

class simulatorThread(threading.Thread):

    def __init__(self, hub):
        threading.Thread.__init__(self)
        self.hub = hub
        return 

    def run(self):
        i = 0
        while not self.hub.run_flag:
            print "waiting for simulation to begin. enter s to begin simulation.\n"
            time.sleep(1)
        while self.hub.run_flag:
            time.sleep(0.01)
            print "%d" % i
            ++i

if __name__ == "__main__":
    s = WorldHub()
    s.run()