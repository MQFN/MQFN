#!/usr/bin/env python
import signal
import sys


def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)

def signal_handler_term(signal, frame):
        print "killed using sigterm"
        sys.exit(0)

def signal_handler_stop(signal, frame):
        print "killed using sigstop"
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler_term)
print('Press Ctrl+C')
signal.pause()