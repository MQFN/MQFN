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
port = settings.WORKER_PORT

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
        try:
            message = raw_input("Enter FETCH to fetch message: ")

            msg = Message(message)
            for packet in msg:
                s.send(packet)

            # message will be sent in the form of packets of a specific size and assimilated in the receiver end
            msg = BaseMessage(message="")
            msg_body = BaseMessage(message="")
            while True:
                print "receiving now"
                part = s.recv(PARTITION_SIZE)
                msg.append(part)

                has_tail, msg_tail = msg.has_message_tail()
                has_head, msg_head = msg.has_message_head()

                if has_tail:
                    print "TAIL received for message"
                    msg_body.append(msg_tail)
                    break
                elif has_head:
                    print "HEAD received for message"

            if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
                print "closing con"
                break

            print "Message from queue: " + str(msg_body)

        except KeyboardInterrupt:
            print "interrupt event"
            break
        except socket.timeout:
            print "timeout exception"
            break

    s.close()


def signal_handler(signal, frame):
    print "Killing process"
    msg = Message("SHUTDOWN")
    for packet in msg:
        s.send(packet)

    # message will be sent in the form of packets of a specific size and assimilated in the receiver end
    msg = BaseMessage(message="")
    msg_body = BaseMessage(message="")
    while True:
        part = s.recv(PARTITION_SIZE)
        msg.append(part)

        print "msg now: {}".format(msg)

        has_tail, msg_tail = msg.has_message_tail()
        has_head, msg_head = msg.has_message_head()

        if has_tail:
            print "TAIL received for message"
            msg_body.append(msg_tail)
            break
        if has_head:
            print "HEAD received for message"
            # the has_message_head method returns the real message clubbed with the HEAD as its
            # second value in tuple
            msg_body.append(msg_head)
        else:
            msg_body.append(str(msg))

    if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
        print "closing con"
        s.close()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()




