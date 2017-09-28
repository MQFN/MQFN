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

    def fetch_message(self):
        """
        fetches first message from queue, following FIFO
        :return:
        """
        if self.is_empty():
            print "is empty check"
            return -1
        else:
            print "trying to fetch"
            a = self.queue.get()
            print "a now:" + str(a)
            return a

    def get_queue_size(self):
        """
        fetches the size of the queue
        :return:
        """
        return self.queue.qsize()

