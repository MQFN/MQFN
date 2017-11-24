#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.server import Server
import logging, logging.config
import traceback, signal
import daemon

import settings

HELP_INSTRUCTIONS = settings.HELP_INSTRUCTIONS
TOPICS = settings.TOPICS
CLIENT_PUBLISHER = settings.CLIENT_PUBLISHER
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILEPATH = settings.LOG_FILEPATH
PID_FILEPATH = settings.PID_FILEPATH
BASE_DIR = settings.BASE_DIR
PID_FILENAME = settings.PID_FILENAME

logging.basicConfig(stream=sys.stdout ,level=LOG_LEVEL)
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger("server_daemon_console_logger")


class Service(object):

    def __init__(self):
        self.logger = logger

    def is_running(self):
        """
        checks the pid location to find if there is any pid already available, if so silently dies
        showing an error message
        :return:
        """
        pid_loc = os.listdir(PID_FILEPATH)
        if PID_FILENAME in pid_loc:
            return True
        return False

    def prepare_for_daemonizing_process(self):
        """
        Stores pid in specific locations to prepare the process for daemonizing
        :return:
        """
        self.logger.debug("Preparing for daemonizing process")
        pid = os.getpid()
        f = open(os.path.join(PID_FILEPATH, PID_FILENAME), "w")
        f.write(str(pid))
        f.close()

    def start(self):
        """
        Starts the server
        :return:
        """
        # it is assumed that the service is not running, checking for already present service must
        # be done before hand.
        self.logger.info("Starting the server")
        self.run()

    def run(self):
        """
        run the process as a daemon
        :return:
        """
        #with daemon.DaemonContext():
            # the pid has to be stored inside the daemon because the daemon actually spawns a
            #  different process

            # The daemon context must have a separate logging.basicConfig and that is crucial.
        self.prepare_for_daemonizing_process()
        server_instance = Server()
        server_instance.start()

    def stop(self):
        """
        stops the process. A sigterm is sent to the process to stop it
        :return:
        """
        # it is assumed that the process is already running and must be stopped
        self.logger.info("Stopping bbmq")
        f = open(os.path.join(PID_FILEPATH, PID_FILENAME), "r")
        pid = f.read()
        f.close()
        os.remove(os.path.join(PID_FILEPATH, PID_FILENAME))

        # The default signal SIGTERM does not work in killing the process. The process must be killed only with -9

        os.system("kill -9 {}".format(str(pid)))
        self.logger.info("Stopped")

    def kill(self):
        """
        sends a kill signal (-9) to the process
        :return:
        """
        self.logger.info("Killing bbmq")
        f = open(os.path.join(PID_FILEPATH, PID_FILENAME), "r")
        pid = f.read()
        f.close()
        os.remove(os.path.join(PID_FILEPATH, PID_FILENAME))
        os.system("kill -9 {}".format(str(pid)))
        self.logger.info("Killed")


def show_help():
    f = open(HELP_INSTRUCTIONS, "r")
    a = f.read()
    f.close()
    logger.info("\n" + a)


def main(args=None):
    """
    Main routine
    :param args:
    :return:
    """
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
                    service = Service()
                    if not service.is_running():
                        service.start()
                    else:
                        logger.info("bbmq is already running")
                        sys.exit(0)
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
                service = Service()
                if not service.is_running():
                    service.start()
                else:
                    logger.info("bbmq is already running")
                    sys.exit(0)
            elif cmd == "stop":
                service = Service()
                if service.is_running():
                    service.stop()
                else:
                    logger.info("bbmq is not running")
                    sys.exit(0)
            elif cmd == "kill":
                service = Service()
                if service.is_running():
                    service.kill()
                else:
                    logger.info("bbmq is not running")
                    sys.exit(0)
            elif cmd == "status":
                service = Service()
                if service.is_running():
                    logger.info("bbmq is running")
                    sys.exit(0)
                else:
                    logger.info("bbmq is not running")
                    sys.exit(0)
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

if __name__ == "__main__":
    main()