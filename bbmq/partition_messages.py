import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
import textwrap

HEAD = settings.HEAD
TAIL = settings.TAIL
PARTITION_SIZE = settings.PARTITION_SIZE


class Message:

    def __init__(self, message):
        """
        Initialize the Message class
        :param message:
        """
        self.message = message
        self.i = 0
        self.size = sys.getsizeof(message)
        self.body_partitions = int(self.size/PARTITION_SIZE)
        # partitions the text into self.body_partitions number of partitions
        if self.body_partitions == 0:
            self.body_partitions = 1
        self.partitions = textwrap.wrap(self.message, PARTITION_SIZE)

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
            self.i += 1
            return HEAD
        else:
            if self.i <= self.body_partitions:
                self.i += 1
                return self.partitions[self.i-2]
            elif self.i == self.body_partitions + 1:
                return TAIL
            else:
                raise StopIteration()
