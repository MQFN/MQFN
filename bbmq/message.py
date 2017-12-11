import sys, os, logging, logging.config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

HEAD = settings.HEAD
TAIL = settings.TAIL
PARTITION_SIZE = settings.PARTITION_SIZE

logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("bbmq_server_module")


class BaseMessage(object):

    def __init__(self, message):
        """
        Message initialization
        """
        self.message = message
        self.logger = logger
        self.id = None

    def set_id(self, id):
        """
        sets the id of the message
        :param id:
        :return:
        """
        self.id = id

    def get_id(self, id):
        """
        gets the id of the message
        :param id:
        :return:
        """
        return self.id

    def __str__(self):
        """
        for printing the message
        :return:
        """
        return self.message

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
        # self.logger.debug("Message now: " + self.message)
        # self.logger.debug("HEAD: {} and message[-(len(HEAD)):] = {}".format(HEAD, self.message[-(len(HEAD)):]))
        if self.message[:len(HEAD)] == HEAD:
            return True, self.message[len(HEAD):]
        return False, ""

    def has_message_tail(self):
        """
        returns true if the message contains TAIL as its rear section
        :param partition:
        :return: returns if the message has tail, if so returns the real message clubbed with that separately
        """
        # self.logger.debug("Message now: " + self.message)
        # self.logger.debug("TAIL: {} and message[-(len(TAIL)):] = {}".format(TAIL, self.message[-(len(TAIL)):]))
        if self.message[-(len(TAIL)):] == TAIL:
            # the tail will always contain the HEAD
            return True, self.message[len(HEAD):-(len(TAIL))]
        return False, ""
