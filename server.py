#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The BBMQ server is required to accept 2 connections. one from the producer and one from the consumer.

Each topic will have one queue. Topic is an abstraction basically for a queue. The name 'Topic' is inspired from apache kafka

Producer: Publisher of the messages
Consumer: Subscriber of the messages

Communication between the connection thread and the main thread. It uses a simple queue for communication purposes. Whenever a new connection is established, its details will be stored in the queue, for whatever number of new connections

"""

import logging
import sys

import settings
from bbmq_server import BBMQServer

TOPICS = settings.TOPICS
CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILEPATH = settings.LOG_FILEPATH

logging.basicConfig(filename=LOG_FILEPATH, level=LOG_LEVEL)
# logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)

class Server(object):

    def __init__(self):
        """
        Run an instance of the BBMQ server
        """
        self.server = BBMQServer()
        self.logger = logging.getLogger("bbmq_module.Server")
        self.logger.debug("Initializing BBMQ server")

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
            self.logger.info("Created queue for topic: {}".format(topic))

        self.logger.info("Spawning connection thread")
        self.server.spawn_connection_thread()
        while True:
            connection = self.server.connection_queue.get(block=True)
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


# def main():
#    server_instance = Server()
#    server_instance.start()
#
# if __name__ == "__main__":
#    main()
