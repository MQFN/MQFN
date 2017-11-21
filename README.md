# MQFN
Message Queuing for Noobs

### Message Queuing

In case of large scale web applications, the web server should not ideally handle all requests, for instance the web server should not be bogged down with requests that should send an email to a certain set of people, there should be dedicated email servers to handle such requests. Hence the concept of message queuing. You can think of a message queuing system as a load balancer for requests. Just like a load balancer can balance loads across multiple servers, a message queuing system can work in a similar fashion where it simply allocates certain types of requests to certain servers. 

### Instructions for running without Docker:
`pip install -r requirements.txt` into a virtualenv
`./server.py start` to start the server
`./producer.py` to start the producer
`.consumer.py` to start the consumer

You can spawn any number of producers and consumers. 

