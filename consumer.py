#!/usr/bin/env python
import settings
import socket
import sys, os, traceback

CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
CLIENT_SUBSCRIBER = settings.CLIENT_SUBSCRIBER
SERVER_ACKNOWLEDGEMENT = settings.SERVER_ACKNOWLEDGEMENT
CLIENT_SHUTDOWN_SIGNAL = settings.CLIENT_SHUTDOWN_SIGNAL
PORT = settings.PORT
MAX_MESSAGE_SIZE = settings.MAX_MESSAGE_SIZE
CLOSE_CONNECTION_SIGNAL = settings.CLOSE_CONNECTION_SIGNAL

def main():
    s = socket.socket()
    host = socket.gethostname()
    port = PORT

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
        s.send(message)
        msg = s.recv(MAX_MESSAGE_SIZE)
        if msg == CLOSE_CONNECTION_SIGNAL:
            print "closing con"
            break
        print "Message from queue: " + str(msg)
    s.close()

if __name__ == "__main__":
    main()




