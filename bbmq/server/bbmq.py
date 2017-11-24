"""
custom queue module implementing a basic queue that will hold the payload
"""
import Queue


class BBMQ(object):
    """
    Custom Queue class
    """
    def __init__(self):
        """
        initialize a queue
        """
        self.queue = Queue.Queue()

    def add_message(self, message):
        """
        enqueues messages into the queue
        :param message:
        :return:
        """
        self.queue.put(message)

    def is_empty(self):
        """
        returns True if the queue is empty, otherwise false
        :return:
        """
        return self.queue.empty()

    def fetch_message(self, block=False):
        """
        fetches first message from queue, following FIFO.
        If block=True the get method of the Queue object will have a blocking function call such that
        if the the queue does not have any messages it will wait for messages to arrive
        :return:
        """
        if block:
            a = self.queue.get(block=True)
            return a
        else:
            if self.is_empty():
                return -1
            else:
                a = self.queue.get()
                return a

    def get_queue_size(self):
        """
        fetches the size of the queue
        :return:
        """
        return self.queue.qsize()

