# the client and server communicate via a simple messaging
# protocol as briefly explained in this file
#
# "message_type, length, message_contents"
#
# where length is the length of the complete message
#       message_type is 4 a byte integer that specify the kind of message
#       length is a 4 byte integer that specifies the length of the message payload
#       message_contents is the message payload
#
# length and message_type can be though of as the header
# and message_contents can be thought of the payload
# 
# The basic messages are as follows.
#
# register:
# "0, length, [aux_information]" (sent from client to server)
# "length, [result, client_id, aux_information]" (sent from server to client)
# 
#
# perform_action:
# "1, length, [client_id, action, aux_information]" (sent from client to server)
# "length, [result, updates/aux_information]" (sent from server to client)
#
# update_state:
# "2, length, [client_id, aux_information]" (sent from client to server)
# "length, [updates/aux_informatiion]" (sent from server to client)
import struct
import socket
import pickle

message_types = {
    'register':    0,
    'send_action': 1,
    'get_updates':   2
    }

def sendMessageToWorldHub(sock, message_type, message_contents):
    # send message header followed by serialized contents
    message_len = len(message_contents)
    message_header = struct.pack("!II", message_type, message_len)
    message = message_header + pickle.dumps(message_contents)
    return sock.sendall(message)

def getResponseFromWorldHub(sock, bytes_to_read):
    # read header
    bytes_read = 0
    bytes_to_read = 4
    message = ""
    while (bytes_read < bytes_to_read):
        data = sock.recv(bytes_read < bytes_to_read)
        if data:
            response_header += data
            bytes_read += len(data)
        else:
            print "trouble retrieving message..."
            sock.close()
    response_len, = struct.unpack("!I", response_header)

    # read message
    bytes_read = 0
    bytes_to_read = response_len
    serialized_response = ""
    while bytes_read < bytes_expected:
        data = self.client.recv(bytes_expected - bytes_read)
        if data:
            serialized_response += data
            bytes_read += len(data)
        else:
            sock.close()
    response = pickle.loads(serialized_response)
    return response

def sendResponseToClient(sock, unserialized_response):
    # send message header followed by serialized contents
    serialized_response = pickle.dumps(unserialized_response)
    message_header = struct.pack("!I", len(serialized_response))
    message = message_header + serialized_response
    return sock.sendall(message)

def getMessageFromClient(sock, message_contents):
    # read header
    bytes_read = 0
    bytes_to_read = 8
    message = ""
    while (bytes_read < bytes_to_read):
        data = sock.recv(bytes_read < bytes_to_read)
        if data:
            message_header += data
            bytes_read += len(data)
        else:
            print "trouble retrieving message..."
            sock.close()
    message_type, message_len = struct.unpack("!II", message_header)

    # read message
    bytes_read = 0
    bytes_to_read = message_len
    serialized_message = ""
    while bytes_read < bytes_expected:
        data = sock.recv(bytes_expected - bytes_read)
        if data:
            serialized_message += data
            bytes_read += len(data)
        else:
            sock.close()
    message = pickle.loads(serialized_message)
    return [message_type, message]
