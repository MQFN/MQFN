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
import logging, logging.config
import threading
import sys, os
import ast
import traceback
import Queue
import signal

# --------------------------Custom imports------------------------------------------
import settings
from bbmq import BBMQ


LOG_FILEPATH = settings.LOG_FILEPATH
LOG_LEVEL = settings.LOG_LEVEL
SERVER_MAX_QUEUED_CON = settings.SERVER_MAX_QUEUED_CON
TOPICS = settings.TOPICS
CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
CLIENT_SUBSCRIBER = settings.CLIENT_SUBSCRIBER
MAX_MESSAGE_SIZE = settings.MAX_MESSAGE_SIZE
SERVER_ACKNOWLEDGEMENT = settings.SERVER_ACKNOWLEDGEMENT
CLIENT_SHUTDOWN_SIGNAL = settings.CLIENT_SHUTDOWN_SIGNAL
CONSUMER_REQUEST_WORD = settings.CONSUMER_REQUEST_WORD
INVALID_PROTOCOL = settings.INVALID_PROTOCOL
EMPTY_QUEUE_MESSAGE = settings.EMPTY_QUEUE_MESSAGE
PRODUCER_ACK_MESSAGE = settings.PRODUCER_ACK_MESSAGE
CLOSE_CONNECTION_SIGNAL = settings.CLOSE_CONNECTION_SIGNAL

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("bbmq_server_module")


class ProducerThread(threading.Thread):
    """
    Connection thread will be waiting for connections from producers or consumers
    """
    def __init__(self, producer_socket, inbound_socket_address, queue, topic_name):
        """
        initialize the thread. During initialization of this thread, it must confirm to the
        producer that the producer can now start communication
        :param producer_socket:
        :param inbound_socket_address:
        :param queue:
        :param topic_name:
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("ProducerThread")
        self.logger.debug("Initializing Producer Thread for socket adddress: {}".format(
            inbound_socket_address))
        self.socket = producer_socket
        self.queue = queue
        self.topic_name = topic_name
        self.socket.send(SERVER_ACKNOWLEDGEMENT)

    def run(self):
        """
        run the thread. called when the start() method of Thread super class is called
        :return:
        """
        try:
            while True:
                try:
                    # TODO: Reduce buffer size (MAX_MESSAGE_SIZE) and receive data in chunks and
                    # TODO: store them in one block in the queue.
                    message = self.socket.recv(MAX_MESSAGE_SIZE)
                    if message == CLIENT_SHUTDOWN_SIGNAL:
                        self.socket.send(CLOSE_CONNECTION_SIGNAL)
                        break
                    self.logger.debug("Received payload")
                    self.logger.debug("Publishing to queue")
                    self.queue.add_message(message)
                    self.socket.send(PRODUCER_ACK_MESSAGE)
                except Exception:
                    raise socket.error

        except Exception:
            self.logger.error("Socket Error. Check the logs to know more")
            exc_type, exc_val, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_val, exc_tb)

        finally:
            self.logger.info("Closing socket: {} for queue: {}".format(self.socket,
                                                                       self.topic_name))
            self.socket.close()

            self.logger.info("Killing Producer Thread for socket: {} and queue: {}".format(
                self.socket, self.topic_name))


class ConsumerThread(threading.Thread):
    """
    Connection thread will be waiting for connections from producers or consumers
    """
    def __init__(self, consumer_socket, inbound_socket_address, queue, topic_name):
        """
        initialize the thread
        :param consumer_socket:
        :param inbound_socket_address:
        :param queue:
        :param topic_name:
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("ConsumerThread")
        self.logger.debug("Initializing Consumer Thread for socket address: {}".format(
            inbound_socket_address))
        self.socket = consumer_socket
        self.queue = queue
        self.topic_name = topic_name
        self.socket.send(SERVER_ACKNOWLEDGEMENT)

    def run(self):
        """
        run the thread. called when the start() method of Thread super class is called
        :return:
        """
        try:
            while True:
                try:
                    request = self.socket.recv(MAX_MESSAGE_SIZE)
                    if request == CLIENT_SHUTDOWN_SIGNAL:
                        self.socket.send(CLOSE_CONNECTION_SIGNAL)
                        break
                    if request == CONSUMER_REQUEST_WORD:
                        self.logger.debug("Received request for new message")
                        self.logger.debug("Fetching from queue")
                        message = self.queue.fetch_message(block=True)
                        self.socket.send(message)
                    else:
                        self.socket.send(INVALID_PROTOCOL)
                except Exception:
                    raise socket.error

        except Exception:
            self.logger.error("Socket Error. Check the logs to know more")
            exc_type, exc_val, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_val, exc_tb)

        finally:
            self.logger.info("Closing socket: {} for queue: {}".format(self.socket,
                                                                           self.topic_name))
            self.socket.close()

            self.logger.info("Killing Consumer Thread for socket: {} and queue: {}".format(
                self.socket, self.topic_name))


class ConnectionThread(threading.Thread):
    """
    Connection thread will be waiting for connections from producers or consumers
    """

    def __init__(self, server_socket, connection_queue, topics):
        """
        initialize the thread
        :param server_socket:
        :param connection_queue:
        :param topics: list of available topics that clients can publish/subscribe to
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("ConnectionThread")
        self.sock = server_socket
        self.connection_queue = connection_queue
        self.topics = topics

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
                if client_topic not in self.topics:
                    self.logger.info("Client '{}' has subscribed to a non-existing"
                                     " topic {}".format(inbound_socket_address, client_topic))
                    socket_connection.close()
                    continue
                if client_type == CLIENT_PUBLISHER:
                    self.logger.info("Client is a producer and will publish to queue:"
                                     " {}".format(client_topic))
                elif client_type == CLIENT_SUBSCRIBER:
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

    def join(self, timeout=None):
        """
        join the thread after closing the socket
        :param timeout:
        :return:
        """
        self.logger.info("Closing Server socket")
        self.sock.close()
        threading.Thread.join()

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
        self.logger = logging.getLogger("BBMQServer")
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        self.port = settings.PORT
        self.sock.bind((self.hostname, self.port))
        self.sock.listen(SERVER_MAX_QUEUED_CON)
        self.topics = {}
        self.connection_thread = None
        self.connection_queue = Queue.Queue()
        # store the instances of all the threads.
        self.all_client_threads = {
            "connection_threads":[],
            "producer_threads": [],
            "consumer_threads": []
        }

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

    def get_topic_queue(self, topic_name):
        """
        gets the queue instance for a topic
        :param topic_name:
        :return:
        """
        if topic_name not in self.topics.keys():
            return -1
        return self.topics[topic_name]["queue"]

    def update_topic(self, topic_name, producer, consumer):
        """
        update the topic with new producers and consumers
        :param topic_name:
        :param producers: tuple ()
        :param consumers: tuple ()
        :return:
        """
        if producer == None:
            self.topics[topic_name]["consumers"].append(consumer)
        else:
            self.topics[topic_name]["producers"].append(producer)

    def create_queue(self):
        """
        create an custom queue instance and return it
        :return:
        """
        queue = BBMQ()
        return queue

    def spawn_connection_thread(self):
        """
        This method will spawn a thread to listen for new connections from new producers or
        consumers
        :return:
        """
        self.logger.debug("Starting connection thread")
        self.connection_thread = ConnectionThread(self.sock, self.connection_queue,
                                                  self.topics.keys())
        self.all_client_threads["connection_threads"].append(self.connection_thread)
        self.connection_thread.start()

    def spawn_producer_thread(self, producer_socket, inbound_socket_address, queue,
                              topic_name):
        """
        spawns a producer thread to publish to the queue
        :param inbound_socket_address:
        :param queue:
        :return:
        """
        producer_thread = ProducerThread(producer_socket, inbound_socket_address, queue,
                                        topic_name)
        self.logger.debug("Starting producer thread for socket: {} and queue: {}".format(
            inbound_socket_address, queue))
        self.all_client_threads["producer_threads"].append(producer_thread)
        producer_thread.start()

    def spawn_consumer_thread(self, consumer_socket, inbound_socket_address, queue,
                              topic_name):
        """
        spawns a consumer thread to subscribe to the queue
        :param inbound_socket_address:
        :param queue:
        :return:
        """
        consumer_thread = ConsumerThread(consumer_socket, inbound_socket_address, queue,
                                         topic_name)
        self.logger.debug("Starting consumer thread for socket: {} and queue: {}".format(
            inbound_socket_address, queue))
        self.all_client_threads["consumer_threads"].append(consumer_thread)
        consumer_thread.start()

    def join_connection_thread(self):
        """
        join the connection thread
        :return:
        """
        self.logger.debug("Joining Connection thread")
        self.connection_thread.join()
