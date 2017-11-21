#!/usr/bin/env python
from pylint.lint import Run

def test_server():

    results = Run(['../../server.py'], exit=False)
    a = int(results.linter.stats['global_note'])
    assert (a > 7)

def test_server_daemon():

    results = Run(['../../server_daemon.py'], exit=False)
    a = int(results.linter.stats['global_note'])
    assert (a > 7)

def test_bbmq_server():
    
    results = Run(['../../bbmq_server.py'], exit=False)
    a = int(results.linter.stats['global_note'])
    assert (a > 7)

def test_producer():

    results = Run(['../../producer.py'], exit=False)
    a = int(results.linter.stats['global_note'])
    assert (a > 7)

def test_consumer():

    results = Run(['../../consumer.py'], exit=False)
    a = int(results.linter.stats['global_note'])
    assert (a > 7)


