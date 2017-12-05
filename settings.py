import logging
import os

PORT = os.environ["CONTAINER_SERVER_PORT"]
assert PORT

PORT = int(PORT)

WORKER_PORT = 15333

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_FILEPATH = "/srv/webapps/BBMQ/logs/bbmq.log"
LOG_FILEPATH = os.path.join(BASE_DIR, "logs", "bbmq.log")
LOG_LEVEL = logging.DEBUG
SERVER_MAX_QUEUED_CON = 5
TOPICS = ["PR_PAYLOADS"]
CLIENT_PUBLISHER = "PRODUCER"
CLIENT_SUBSCRIBER = "CONSUMER"

MAX_MESSAGE_SIZE = 65536
SERVER_ACKNOWLEDGEMENT = "ROGER"
CLIENT_SHUTDOWN_SIGNAL = "SHUTDOWN"
CONSUMER_REQUEST_WORD = "FETCH"
INVALID_PROTOCOL = "UNKNOWN_WORD"
EMPTY_QUEUE_MESSAGE = "QUEUE EMPTY"
PRODUCER_ACK_MESSAGE = "ACKNOWLEDGED"
CLOSE_CONNECTION_SIGNAL = "CLOSE_CON"
HELP_INSTRUCTIONS = os.path.join(BASE_DIR, "help_instructions.txt")
PID_FILEPATH = os.path.join(BASE_DIR, "pid")
PID_FILENAME = "bbmq.pid"

# Message components
import hashlib
import secrets

MESSAGE_HEAD_SECRET = secrets.MESSAGE_HEAD_SECRET
MESSAGE_TAIL_SECRET = secrets.MESSAGE_TAIL_SECRET

assert MESSAGE_HEAD_SECRET
assert MESSAGE_TAIL_SECRET

HEAD = hashlib.sha256(MESSAGE_HEAD_SECRET).hexdigest()
TAIL = hashlib.sha256(MESSAGE_TAIL_SECRET).hexdigest()
PARTITION_SIZE = 4096

# confirm pid filepath location and log filepath location, if tmp is not found, create a tmp
#  directory in the base dir
dirs = os.listdir(BASE_DIR)
if "pid" not in dirs:
    os.mkdir(PID_FILEPATH)

if "logs" not in dirs:
    os.mkdir(os.path.dirname(LOG_FILEPATH))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILEPATH,
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'server_daemon': {
            'handlers': ['console'],
            'propagate': False
        },
        'server_daemon_console_logger': {
            'handlers': ['console'],
            'propagate': False
        },
        'bbmq_server_module':{
            'handlers': ['console'],
            'propagate': False
        },
        'Server': {
            'handlers': ['console'],
            'propagate': False
        },
        'BBMQServer': {
            'handlers': ['console'],
            'propagate': False
        },
        'ProducerThread': {
            'handlers': ['console'],
            'propagate': False
        },
        'ConsumerThread': {
            'handlers': ['console'],
            'propagate': False
        },
        'ConnectionThread': {
            'handlers': ['console'],
            'propagate': False
        }
    }
}
