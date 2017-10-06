#!/usr/bin/env python
# -*- coding: utf-8 -*-

from service import Service
from server import Server

import logging, logging.config
import sys, traceback

import settings

HELP_INSTRUCTIONS = settings.HELP_INSTRUCTIONS
TOPICS = settings.TOPICS
CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILEPATH = settings.LOG_FILEPATH
PID_FILEPATH = settings.PID_FILEPATH

logging.config.dictConfig(settings.LOGGING)
logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)
logger = logging.getLogger("server_daemon_console_logger")


class BBMQService(Service):
    def __init__(self, *args, **kwargs):
        super(BBMQService, self).__init__(*args, **kwargs)
        self.server_instance = Server()
        self.logger = logger

    def run(self):
        self.logger.info("Running the server as a daemon")
        while not self.got_sigterm():
            self.server_instance.start()


def show_help():
    f = open(HELP_INSTRUCTIONS, "r")
    a = f.read()
    f.close()
    logger.info("\n" + a)

if __name__ == "__main__":

    if len(sys.argv) == 1:
        show_help()
        sys.exit(0)

    if len(sys.argv) > 4:
        show_help()
        sys.exit(0)

    if len(sys.argv) == 4:
        if sys.argv[1] == "--port":
            try:
                port = int(sys.argv[2])
                if not (port>10000 and port<20000):
                    show_help()
                    sys.exit(0)
                cmd = sys.argv[3]
                if cmd == "start":
                    # start the server
                    settings.PORT = port
                    service = BBMQService('bbmq_server', pid_dir=PID_FILEPATH)
                    service.start()
                else:
                    show_help()
                    sys.exit(0)
            except Exception:
                show_help()
                sys.exit(0)
        else:
            show_help()
            sys.exit(0)

    elif len(sys.argv) == 2:
        try:
            cmd = sys.argv[1]
            if cmd == "start":
                service = BBMQService('bbmq_server', pid_dir=PID_FILEPATH)
                service.start()
            elif cmd == "stop":
                service = BBMQService('bbmq_server', pid_dir=PID_FILEPATH)
                if service.is_running():
                    service.stop()
                else:
                    logger.info("Service is not running")
            elif cmd == "kill":
                service = BBMQService('bbmq_server', pid_dir=PID_FILEPATH)
                if service.is_running():
                    service.kill()
                else:
                    logger.info("Service is not running")
            elif cmd == "status":
                service = BBMQService('bbmq_server', pid_dir=PID_FILEPATH)
                if service.is_running():
                    print "bbmq_server is running"
                else:
                    print "bbmq_server is not running"
            else:
                show_help()
                sys.exit(0)

        except Exception:
            exc_type, exc_val, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_val, exc_tb)
            show_help()
            sys.exit(0)

    else:
        show_help()
        sys.exit(0)