#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, logging.config
import time
import os
import settings
import sys

from service import Service
LOG_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_log.log")

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
        'test_service': {
            'handlers': ['file'],
            'propagate': False
        }
    }
}
logging.config.dictConfig(LOGGING)
logging.basicConfig(filename=LOG_FILEPATH, level=logging.DEBUG)


class MyService(Service):

    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger("test_service")

    def run(self):
        while not self.got_sigterm():
            self.logger.info("I'm working...")
            time.sleep(5)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = MyService('my_service', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'status':
        if service.is_running():
            print "Service is running."
        else:
            print "Service is not running."
    else:
        sys.exit('Unknown command "%s".' % cmd)