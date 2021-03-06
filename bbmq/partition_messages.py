import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
import textwrap
from message import BaseMessage

HEAD = settings.HEAD
TAIL = settings.TAIL
PARTITION_SIZE = settings.PARTITION_SIZE


class Message(BaseMessage):

    def __init__(self, message):
        """
        Initialize the Message class
        :param message:
        """
        BaseMessage.__init__(self, message)
        self.i = 0

        self.partitions = textwrap.wrap(self.message, PARTITION_SIZE)
        self.body_partitions = len(self.partitions)
        print "body_partitions"
        print self.body_partitions
        print "partitions"
        print self.partitions

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
                self.i += 1
                return TAIL
            else:
                raise StopIteration()

