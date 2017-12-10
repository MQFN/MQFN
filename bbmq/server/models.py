# -------------------------------- Database models----------------------------------------------------------------------
import sys, os
import sqlalchemy
from sqlalchemy import create_engine

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import secrets
import settings

MYSQL_USERNAME = secrets.MYSQL_USERNAME
MYSQL_PASSWORD = secrets.MYSQL_PASSWORD
MYSQL_HOSTNAME = secrets.MYSQL_HOSTNAME
MYSQL_DATABASE_NAME = secrets.MYSQL_DATABASE_NAME

MAX_MESSAGE_SIZE = settings.MAX_MESSAGE_SIZE

database_url = 'mysql://{}:{}@{}/{}'.format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOSTNAME, MYSQL_DATABASE_NAME)
engine = create_engine(database_url)

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ModelManager(object):
    """
    Model manager
    """
    @classmethod
    def create_session(cls, engine):
        """
        create a session based
        :param engine: engine object
        :return: returns the created session object
        """
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    @classmethod
    def add_to_session(cls, session, obj):
        """
        add the object to the session
        :param obj:
        :param session: session object
        :return:
        """
        session.add(obj)

    @classmethod
    def commit_session(cls, session):
        """
        commit to session
        :param session:
        :return:
        """
        session.commit()

    @classmethod
    def rollback_session(cls, session):
        """
        rollback the current session
        :param session:
        :return:
        """
        session.rollback()


class Queue(Base):
    """
    Queues model class
    """
    __tablename__ = "Queue"

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    created_timestamp = Column(DateTime)

    def __repr__(self):
        """
        representation of the Queue class
        :return:
        """
        return "<Queue (name: {}, created_timestamp: {})>".format(self.name, self.created_timestamp)


class Message(Base):
    """
    Message model class
    """
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True)
    queue_id = Column(Integer, ForeignKey('Queue.id'))
    is_fetched = Column(Boolean, default=False)
    content = Column(String(MAX_MESSAGE_SIZE))
    publish_timestamp = Column(DateTime)
    consumed_timestamp = Column(DateTime)

    # The consumed_timestamp should ideally have a null value for default but that is not feasible here so
    # for checking we will first check whether the is_fetched value is true, if so we consider the consumed_timestamp
    # as the date and time when the message was dequeued.

    def __repr__(self):
        """
        representation of the Message class
        :return:
        """
        return "<Message (queue_id: {}, is_fetched: {}, content: {}, publish_timestamp: {}, " \
               "consumed_timestamp: {})>".format(self.queue_id, self.is_fetched, self.content,
                                                 self.publish_timestamp, self.consumed_timestamp)