#!/usr/bin/env python

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
import socket
import traceback
import signal
from partition_messages import Message
from message import BaseMessage

CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
CLIENT_SUBSCRIBER = settings.CLIENT_SUBSCRIBER
SERVER_ACKNOWLEDGEMENT = settings.SERVER_ACKNOWLEDGEMENT
CLIENT_SHUTDOWN_SIGNAL = settings.CLIENT_SHUTDOWN_SIGNAL
PORT = settings.PORT
MAX_MESSAGE_SIZE = settings.MAX_MESSAGE_SIZE
CLOSE_CONNECTION_SIGNAL = settings.CLOSE_CONNECTION_SIGNAL
PARTITION_SIZE = settings.PARTITION_SIZE
HEAD = settings.HEAD
TAIL = settings.TAIL

s = socket.socket()
host = socket.gethostname()
port = 32770

def main():
    client_metadata = {
        "type": CLIENT_SUBSCRIBER,
        "topic": "PR_PAYLOADS"
    }
    s.connect((host, port))
    print "connected to socket"
    print "sending metadata"
    s.send(str(client_metadata))
    message = s.recv(1024)
    if message == SERVER_ACKNOWLEDGEMENT:
        print "go forward"
    print "Start com: Enter SHUTDOWN to stop com"
    while True:
        message = raw_input("Enter FETCH to fetch message: ")

        msg = Message(message)
        for packet in msg:
            s.send(packet)

        # message will be sent in the form of packets of a specific size and assimilated in the receiver end
        msg = BaseMessage(message="")
        msg_body = BaseMessage(message="")
        while True:
            part = s.recv(PARTITION_SIZE)
            msg.append(part)
            if msg.has_message_head():
                print "HEAD received for message"
                # the has_message_head method returns the real message clubbed with the HEAD as its
                # second value in tuple
                msg_body.append(msg.has_message_head()[1])
            if msg.has_message_tail():
                print "TAIL received for message"
                msg_body.append(msg.has_message_tail()[1])
                break
            else:
                msg_body.append(msg)

        if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
            print "closing con"
            break

        print "Message from queue: " + str(msg_body)

        del(msg)
        del(msg_body)

    s.close()


def signal_handler(signal, frame):
    print "Killing process"
    s.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()




