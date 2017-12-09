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
    - **`HEAD-msg_body-TAIL`** all messages will be sent in this format. The server sends the
     producer a **`PRODUCER_ACK_MESSAGE`** to acknowledge that it has sent the entire message.
    - **`CLIENT_SHUTDOWN_SIGNAL`** indicates that the client is ready to close the 
    connection. The server responds by **`CLOSE_CONNECTION_SIGNAL`**
    
    All messages are exchanged using HEAD <msg> TAIL 
    
2. Consumer:
    - **``** 
    
### Instructions for running mysql docker container and contacting the container using mysql client
- Pull the docker image `docker pull mysql:latest`
- Run the docker mysql conatiner `docker run -e MYSQL_ROOT_PASSWORD=<password> -d --expose 3306 --publish 0.0.0
.0:1337:3306 mysql:latest`. This command will start the mysql docker container in detached mode and expose the 
standard mysql port 3306 to port 1337 in the outer world.
- For connecting to the mysql container from the outer world, we can use the following command `mysql -u root -h 0.0
.0.0 --port=1337 -p`. This command will contact the mysql server using `0.0.0.0:1337`. 

### Instructions for running without Docker:
- `pip install -r requirements.txt` into a virtualenv
- `./bbmq/server/server_daemon.py start` to start the server
- `./producer.py` to start a producer
- `./consumer.py` to start a consumer

You can spawn any number of producers and consumers.

### Instructions for running with Docker:
- cd to the root dir
- `docker build -t mqfn/mqfn:1.0 .` to build the image
- `docker run -v $PWD:/app --expose 15333 --publish 0.0.0.0:15333:15333 -it mqfn/mqfn:1.0` to
 start the container. 
- `docker exec -it <container id> /bin/bash` to login to the container
- `./producer.py` to start the producer
- `./consumer.py` to start the consumer

