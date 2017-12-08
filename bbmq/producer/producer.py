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
CLOSE_CONNECTION_SIGNAL = settings.CLOSE_CONNECTION_SIGNAL
PRODUCER_ACK_MESSAGE = settings.PRODUCER_ACK_MESSAGE
PARTITION_SIZE = settings.PARTITION_SIZE

s = socket.socket()
s.settimeout(2)
host = socket.gethostname()
port = settings.WORKER_PORT

def main():

    client_metadata = {
        "type": CLIENT_PUBLISHER,
        "topic": "PR_PAYLOADS"
    }
    try:
        s.connect((host, port))
    except socket.error:
        print "socket error:"
        exc_type, exc_val, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_val, exc_tb)
        exit(0)

    print "connected to socket"
    print "sending metadata"
    s.send(str(client_metadata))
    message = s.recv(1024)
    if message == SERVER_ACKNOWLEDGEMENT:
        print "go forward"
    print "Start com: Enter SHUTDOWN to stop com"
    msg = None
    msg_body = None
    while True:
        try:
            message = raw_input("Message to send to queue: ")

            packets = Message(message)
            for packet in packets:
                print "packet now: {}".format(packet)

                # import pdb
                # pdb.set_trace()

                data_size = s.send(packet)
                print "size of sent data:"
                print data_size

            msg = BaseMessage(message="")
            msg_body = BaseMessage(message="")
            while True:
                part = s.recv(PARTITION_SIZE)
                msg = BaseMessage(message=part)
                print "msg now: {}".format(msg)

                has_tail, msg_tail = msg.has_message_tail()
                has_head, msg_head = msg.has_message_head()

                if has_tail:
                    print "TAIL received for message"
                    msg_body.append(msg_tail)
                    break
                elif has_head:
                    print "HEAD received for message"

            if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
                print "closing socket"
                break
            elif msg_body.equals(PRODUCER_ACK_MESSAGE):
                print "producer acknowledgement message received"

        except KeyboardInterrupt:
            print "interrupt event"
            break
        except socket.timeout:
            print "timeout exception"
            break

    s.close()


def signal_handler(signal, frame):
    print "Killing process"
    packets = Message("SHUTDOWN")
    for packet in packets:
        print "packet now: {}".format(packet)

        # import pdb
        # pdb.set_trace()

        data_size = s.send(packet)
        print "size of sent data:"
        print data_size

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
            msg_body.append(msg)

    if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
        print "closing socket"
        s.close()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()




