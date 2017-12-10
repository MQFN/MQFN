#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The BBMQ server is required to accept 2 connections. one from the producer and one from the consumer.
Each topic will have one queue. Topic is an abstraction basically for a queue. 
The name 'Topic' is inspired from apache kafka
Producer: Publisher of the messages
Consumer: Subscriber of the messages

Communication between the connection thread and the main thread. It uses a simple queue for communication purposes. Whenever a new connection is established, its details will be stored in the queue, for whatever number of new connections
"""

import logging, logging.config
import sys, os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
from models import ModelManager
from models import Queue
from models import Message

import settings
import signal
from bbmq_server import BBMQServer

TOPICS = settings.TOPICS
CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILEPATH = settings.LOG_FILEPATH


def signal_handler(signal, frame):
    """
    handle the signals sent to the process
    :param signal:
    :param frame:
    :return:
    """
    pass


class Server(object):

    def __init__(self):
        """
        Run an instance of the BBMQ server
        """
        logging.basicConfig(filename=LOG_FILEPATH, level=LOG_LEVEL)
        logging.config.dictConfig(settings.LOGGING)
        logger = logging.getLogger("bbmq_server_module")
        self.server = BBMQServer()
        self.logger = logger
        self.logger.debug("Initializing BBMQ server")

        self.logger.info("Creating a session for database")
        self.session = ModelManager.create_session(models.engine)

        self.logger.info("Creating all tables")
        models.Base.metadata.create_all(models.engine)

    def start(self):
        """
        start the server
        :return:
        """
        self.run()

    def stop(self):
        """
        stop the server
        :return:
        """
        self.logger.info("Stopping the server")
        self.server.join_connection_thread()
        sys.exit(0)

    def run(self):
        """
        executes the server
        :return:
        """
        self.logger.info("Fetching topics from settings and creating queues")
        for topic in TOPICS:
            ec = self.server.create_topic(topic)
            if ec == -1:
                self.logger.info("Can't create topic: {}. Topic already exists".format(topic))
                continue
            queue = self.server.create_queue()
            self.server.topics[topic]["queue"] = queue

            self.logger.info("Writing topic to database if not already exist")
            queue_obj = Queue(name=topic, created_timestamp=datetime.datetime.utcnow())
            if len((self.session.query(Queue).filter(Queue.name == topic)).all()) == 0:
                ModelManager.add_to_session(self.session, queue_obj)

            self.logger.info("Created queue for topic: {}".format(topic))

        self.logger.info("Committing to database")
        ModelManager.commit_session(self.session)
        self.logger.info("Closing database session")
        ModelManager.close_session(self.session)

        self.logger.debug("Spawning connection thread")
        self.server.spawn_connection_thread()
        while True:
            self.logger.debug("Waiting for connections from connection queue")
            connection = self.server.connection_queue.get(block=True)
            self.logger.debug("new connection received from connection queue: ")
            self.logger.debug(connection)
            # The connection will be a dictionary of the following format
            # {
            #     "client_type": client_type,
            #     "client_topic": client_topic,
            #     "socket": socket_connection,
            #     "inbound_socket_address": inbound_socket_address
            # }
            client_type = connection["client_type"]
            client_topic = connection["client_topic"]
            client_socket = connection["socket"]
            inbound_socket_address = connection["inbound_socket_address"]
            queue = self.server.get_topic_queue(topic_name=client_topic)
            if client_type == CLIENT_PUBLISHER:
                self.server.update_topic(client_topic, (client_socket, inbound_socket_address), None)
                self.server.spawn_producer_thread(client_socket, inbound_socket_address, queue,
                                             client_topic)
            else:
                self.server.update_topic(client_topic, None, (client_socket, inbound_socket_address))
                self.server.spawn_consumer_thread(client_socket, inbound_socket_address, queue,
                                             client_topic)


def main():
    server_instance = Server()
    server_instance.start()

if __name__ == "__main__":
    main()
