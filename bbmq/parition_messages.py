import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
import textwrap

MESSAGE_HEAD_SECRET = settings.MESSAGE_HEAD_SECRET
MESSAGE_TAIL_SECRET = settings.MESSAGE_TAIL_SECRET
PARTITION_SIZE = settings.PARTITION_SIZE

class Message:

    def __init__(self, message, size):
        """
        Initialize the Message class
        :param message:
        :param n: size of the message
        """
        self.message = message
        self.i = 0
        self.size = size
        self.body_partitions = int(size/PARTITION_SIZE)
        # partitions the text into self.body_partitions number of partitions
        self.partitions = textwrap.wrap(message, self.body_partitions)

    def __iter__(self):
        """
        this function is necessary for iterators
        :return:
        """
        return self

    def next(self):
        """
        to fetch the next value
        :return:
        """
        if self.i == 0:
            return MESSAGE_HEAD_SECRET
            self.i += 1
        else:
            if self.i < self.body_partitions:
                self.i += 1
                return self.partitions[self.i-1]
            else:
                raise StopIteration()
