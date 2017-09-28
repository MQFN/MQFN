#!/usr/bin/env python
import settings
import socket
import sys, os, traceback
import signal

CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
CLIENT_SUBSCRIBER = settings.CLIENT_SUBSCRIBER
SERVER_ACKNOWLEDGEMENT = settings.SERVER_ACKNOWLEDGEMENT
CLIENT_SHUTDOWN_SIGNAL = settings.CLIENT_SHUTDOWN_SIGNAL
PORT = settings.PORT
CLOSE_CONNECTION_SIGNAL = settings.CLOSE_CONNECTION_SIGNAL

s = socket.socket()
s.settimeout(2)
host = socket.gethostname()
port = PORT


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
    while True:
        try:
            message = raw_input("Message to send to queue: ")
            s.send(message)
            acknowledgement = s.recv(1024)
            if acknowledgement == CLOSE_CONNECTION_SIGNAL:
                print "closing socket"
                break
        except KeyboardInterrupt:
            print "interrupt event"
            break
        except socket.timeout:
            print "timeout exception"
            break
    s.close()

def signal_handler(signal, frame):
    print "Killing process"
    s.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()




