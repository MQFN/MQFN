#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The BBMQ server is required to accept 2 connections. one from the producer and one from the consumer.

Each topic will have one queue. Topic is an abstraction basically for a queue. The name 'Topic' is inspired from apache kafka

Producer: Publisher of the messages
Consumer: Subscriber of the messages

Communication between the connection thread and the main thread. It uses a simple queue for communication purposes. Whenever a new connection is established, its details will be stored in the queue, for whatever number of new connections

"""

import socket
import logging
import threading
import sys, os
import ast
import traceback
import Queue

# --------------------------Custom imports------------------------------------------
import settings
from bbmq import BBMQ

LOG_FILEPATH = settings.LOG_FILEPATH
LOG_LEVEL = settings.LOG_LEVEL
SERVER_MAX_QUEUED_CON = settings.SERVER_MAX_QUEUED_CON
TOPICS = settings.TOPICS

logging.basicConfig(filename=LOG_FILEPATH, level=LOG_LEVEL)
logger = logging.getLogger("bbmq_module")

class ClientThread(threading.Thread):
    """
    Connection thread will be waiting for connections from producers or consumers
    """
    def __init__(self, thread_id, thread_counter):
        """
        initialize the thread
        :param thread_id:
        :param thread_counter:
        """
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_counter = thread_counter

    def run(self):
        """
        run the thread. called when the start() method of Thread super class is called
        :return:
        """


class ConnectionThread(threading.Thread):
    """
    Connection thread will be waiting for connections from producers or consumers
    """

    def __init__(self, thread_id, thread_counter, server_socket, connection_queue):
        """
        initialize the thread
        :param thread_id:
        :param thread_counter:
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("bbmq_module.BBMQServer.ConnectionThread")
        self.thread_id = thread_id
        self.thread_counter = thread_counter
        self.sock = server_socket
        self.connection_queue = connection_queue

    def run(self):
        """
        run the thread. called when the start() method of Thread super class is called
        :return:
        """
        while True:
            client_metadata, socket_connection, inbound_socket_address = self.connect()

            # client_metadata is a string representation of a dictionary containing 2 fields
            # one for "type" which can be a producer or consumer and another being
            # "topic" specifying the topic the client wants to publish/subscribe
            try:
                client_type = ast.literal_eval(client_metadata)["type"]
                client_topic = ast.literal_eval(client_metadata)["topic"]
                if client_type == "producer":
                    self.logger.info("Client is a producer and will publish to queue:"
                                     " {}".format(client_topic))
                elif client_type == "consumer":
                    self.logger.info("Client is a consumer and will subscribe to queue:"
                                     " {}".format(client_topic))
                else:
                    self.logger.info("Client type not defined. Closing the connection")
                    socket_connection.close()
                    continue
                self.logger.debug("Client data pushed to connection queue")
                self.connection_queue.put({
                    "client_type": client_type,
                    "client_topic": client_topic,
                    "socket": socket_connection,
                    "inbound_socket_address": inbound_socket_address
                })

            except Exception:
                self.logger.error("Error in Connection Thread. Check the logs for the"
                                  " Traceback")
                exc_type, exc_val, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_val, exc_tb)

    def connect(self):
        """
        connect to the socket
        :return:
        """
        # the return value of accept() is a tuple c, addr where c is a new socket object
        #  usable to send and receive data on the other end of the connection and addr is the
        #  address bound to the socket at the other end of the connection
        self.logger.info("Waiting for connection from clients")
        socket_connection, inbound_socket_address = self.sock.accept()
        # client_type can be a  producer or a consumer
        client_metadata = socket_connection.recv(1024)
        self.logger.info("Connection received from client: {}".format(inbound_socket_address))
        return client_metadata, socket_connection, inbound_socket_address


class BBMQServer(object):
    """
    BBMQ server to connect to
    """

    def __init__(self):
        """
        initialize the instance of BBMQ. create the socket, bind the hostname and port with
        the socket and listen for the connections to the socket
        """
        self.logger = logging.getLogger("bbmq_module.BBMQServer")
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        self.port = settings.PORT
        self.sock.bind((self.hostname, self.port))
        self.sock.listen(SERVER_MAX_QUEUED_CON)
        self.topics = {}
        self.connection_thread = None
        self.connection_queue = Queue.Queue()

    def create_topic(self, topic_name):
        """
        create a new topic with the name. returns -1 if the topic is already available
        :param topic_name:
        :return:
        """
        if topic_name in self.topics.keys():
            return -1
        self.logger.info("creating topic: {}".format(topic_name))
        self.topics[topic_name] = {
            "queue": None,
            "producers": [],
            "consumers": []
        }
        return 0

    def create_queue(self):
        """
        create an custom queue instance and return it
        :return:
        """
        queue = BBMQ()
        return queue

    def spawn_connection_thread(self, connection_queue):
        """
        This method will spawn a thread to listen for new connections from new producers or
        consumers
        :return:
        """
        self.logger.info("Starting connection thread")
        self.connection_thread = ConnectionThread(0, 1, self.sock, self.connection_queue)
        self.connection_thread.start()
        self.logger.info("Connection thread started")


def main():
    server = BBMQServer()
    logger.info("Fetching topics from settings and creating queues")
    for topic in TOPICS:
        ec = server.create_topic(topic)
        if ec == -1:
            logger.info("Can't create topic: {}. Topic already exists".format(topic))
            continue
        queue = server.create_queue()
        server.topics[topic]["queue"] = queue
        logger.info("Created queue for topic: {}".format(topic))

    logger.info("Spawning connection thread")
    server.spawn_connection_thread()
    while True:
        connection = server.connection_queue.get(block=True)





















