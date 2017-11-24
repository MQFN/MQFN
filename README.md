# MQFN

[![Build Status](https://travis-ci.org/MQFN/MQFN.svg?branch=master)](https://travis-ci.org/MQFN/MQFN)

Message Queuing for Noobs

### Message Queuing

In case of large scale web applications, the web server should not ideally handle all requests, for instance the web server should not be bogged down with requests that should send an email to a certain set of people, there should be dedicated email servers to handle such requests. Hence the concept of message queuing. You can think of a message queuing system as a load balancer for requests. Just like a load balancer can balance loads across multiple servers, a message queuing system can work in a similar fashion where it simply allocates certain types of requests to certain servers. 

### Communication Protocol

The following communication protocol will be followed during communication between the producer and server and the consumers and server.

1. Producer: 
    - **`CLIENT_PUBLISHER`** first verifies that the client is indeed a producer or a
     publisher. The server sends the producer a **`SERVER_ACKNOWLEDGEMENT`**
    - **`HEAD-msg_body-TAIL`** all messages will be sent in this format and also stored 
    in the queue in this format. The server sends the producer a **`PRODUCER_ACK_MESSAGE`**
    to acknowledge that it has sent the entire message
    - **`CLIENT_SHUTDOWN_SIGNAL`** indicates that the client is ready to close the 
    connection. The server responds by **`CLOSE_CONNECTION_SIGNAL`**
    
    Note that only the message is sent with a head and tail.
    
2. Consumer:
    - **``** 

### Instructions for running without Docker:
`pip install -r requirements.txt` into a virtualenv
`pip install -e .` to install the package bbmq
`bbmq start` to start the server
`./producer.py` to start a producer
`./consumer.py` to start a consumer

You can spawn any number of producers and consumers. 

