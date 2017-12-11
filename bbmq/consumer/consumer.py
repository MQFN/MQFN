#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
import socket
import traceback
import signal
import logging, logging.config
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

logging.config.dictConfig(settings.LOGGING)


class Consumer:

    def __init__(self, topic, port=settings.WORKER_PORT, timeout=2):
        """
        instantiate a producer with that will publish to a specific topic in the queue
        :param topic: string, topic name
        :param port: int, port number
        :param timeout: int, timeout for socket
        """

        self.topic = topic
        self.port = port
        self.timeout = timeout
        self.logger = logging.getLogger("Consumer")
        self.logger.info("Instantiating consumer")
        self.socket = socket.socket()

        # For blocking calls, we cannnot have a socket timeout

        # self.socket.settimeout(self.timeout)
        self.host = socket.gethostname()

    def connect(self):
        """
        connect to the producer if possible
        :return:
        """
        self.logger.info("Attempting to connect to server")
        client_metadata = {
            "type": CLIENT_SUBSCRIBER,
            "topic": self.topic
        }
        try:
            self.socket.connect((self.host, self.port))
            self.logger.info("Connected to server. Sending metadata")
            self.socket.send(str(client_metadata))
            message = self.socket.recv(1024)
            if message == SERVER_ACKNOWLEDGEMENT:
                self.logger.info("Consumer acknowledged by server")
        except socket.error:
            self.logger.error("Unable to connect to the server")
            stack = traceback.format_exc()
            self.logger.error(stack)
            return -1
        return 0

    def close_socket(self):
        """
        closes the socket
        :return:
        """
        msg = Message("SHUTDOWN")
        for packet in msg:
            self.socket.send(packet)

        # message will be sent in the form of packets of a specific size and assimilated in the receiver end
        msg = BaseMessage(message="")
        msg_body = BaseMessage(message="")
        while True:
            part = self.socket.recv(PARTITION_SIZE)
            msg.append(part)

            self.logger.debug("Msg now: {}".format(msg))

            has_tail, msg_tail = msg.has_message_tail()
            has_head, msg_head = msg.has_message_head()

            if has_tail:
                self.logger.debug("TAIL received for message")
                msg_body.append(msg_tail)
                break
            if has_head:
                self.logger.debug("HEAD received for message")
                # the has_message_head method returns the real message clubbed with the HEAD as its
                # second value in tuple
                msg_body.append(msg_head)
            else:
                msg_body.append(str(msg))

        if msg_body.equals(CLOSE_CONNECTION_SIGNAL):
            self.logger.info("Closing socket")
        else:
            self.logger.error("Could not receive the CLOSE_CONNECTION_SIGNAL. Closing socket anyway")

        self.socket.close()

    def fetch(self):
        """
        fetch from the queue
        :return:
        """
        try:
            message = "FETCH"
            msg = Message(message)
            for packet in msg:
                self.socket.send(packet)

            # message will be sent in the form of packets of a specific size and assimilated in the receiver end
            msg = BaseMessage(message="")
            msg_body = BaseMessage(message="")
            while True:
                self.logger.debug("Receiving now")
                part = self.socket.recv(PARTITION_SIZE)
                msg.append(part)

                has_tail, msg_tail = msg.has_message_tail()
                has_head, msg_head = msg.has_message_head()

                if has_tail:
                    self.logger.debug("TAIL received for message")
                    msg_body.append(msg_tail)
                    break
                elif has_head:
                    self.logger.debug("HEAD received for message")

            return str(msg_body)

        except Exception:
            stack = traceback.format_exc()
            self.logger.error(stack)
