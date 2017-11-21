#!/usr/bin/env python
from pylint.lint import Run

PASS_VAL = 5

def test_server():

    results = Run(['../../bbmq/server/server.py'], exit=False)
    a = float(results.linter.stats['global_note'])
    assert (a > PASS_VAL)

def test_server_daemon():

    results = Run(['../../bbmq/server/server_daemon.py'], exit=False)
    a = float(results.linter.stats['global_note'])
    assert (a > PASS_VAL)

def test_bbmq_server():
    
    results = Run(['../../bbmq/server/bbmq_server.py'], exit=False)
    a = float(results.linter.stats['global_note'])
    assert (a > PASS_VAL)

def test_producer():

    results = Run(['../../bbmq/producer/producer.py'], exit=False)
    a = float(results.linter.stats['global_note'])
    assert (a > PASS_VAL)

def test_consumer():

    results = Run(['../../bbmq/consumer/consumer.py'], exit=False)
    a = float(results.linter.stats['global_note'])
    assert (a > PASS_VAL)


