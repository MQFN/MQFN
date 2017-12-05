import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

HEAD = settings.HEAD
TAIL = settings.TAIL
PARTITION_SIZE = settings.PARTITION_SIZE


class BaseMessage(object):

    def __init__(self, message):
        """
        Message initialization
        """
        self.message = message

    def append(self, part):
        """
        append the original message with this part
        :param part:
        :return:
        """
        self.message = self.message + part

    def prepend(self, part):
        """
        add the part to the beginning of message
        :param part:
        :return:
        """
        self.message = part + self.message

    def equals(self, message):
        """
        compares self.message and message and returns if they are same
        :param message:
        :return:
        """
        if self.message == message:
            return True
        return False

    def has_message_head(self):
        """
        returns true if the current message has the message HEAD
        :param partition:
        :return: returns whether it has the message and if so, returns the real message clubbed with that separately
        """
        if self.message[:len(HEAD)] == HEAD:
            return True, self.message[len(HEAD):]
        return False, None

    def has_message_tail(self):
        """
        returns true if the message contains TAIL as its rear section
        :param partition:
        :return: returns if the message has tail, if so returns the real message clubbed with that separately
        """
        if self.message[-(len(TAIL)):] == TAIL:
            return True, self.message[:-(len(TAIL))]
        return False, None