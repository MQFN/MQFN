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
    - **`Message`** The server sends the producer a **`PRODUCER_ACK_MESSAGE`** to acknowledge that it has sent the entire message.
    - **`CLIENT_SHUTDOWN_SIGNAL`** indicates that the client is ready to close the 
    connection. The server responds by **`CLOSE_CONNECTION_SIGNAL`**
    
    All messages are exchanged using HEAD <msg> TAIL.
    
2. Consumer:
    - **`CLIENT_SUBSCRIBER`** first verifies that the client is indeed a consumer or a subscriber. The server sends 
    the consumer a **`SERVER_ACKNOWLEDGEMENT`**.
    - **`FETCH`** This message asks the server for any new messages. The server sends the message
    - **`CLIENT_SHUTDOWN_SIGNAL`** indicates that the client is ready to close the connection. The server responds by **`CLOSE_CONNECTION_SIGNAL`**
    
    Once again all messages are exchanged using a HEAD <msg> TAIL.  
    
### Persistence Layer
A persistence layer is super important in order store queue messages in case of any unexpected crash of the server.
    
### Instructions for running mysql docker container:
- Pull the docker image `docker pull mysql:latest`
- Run the docker mysql conatiner `docker run -h <hostname> -e MYSQL_ROOT_PASSWORD=<password> -d --expose 3306 
--publish 0.0.0.0:1337:3306 mysql:latest`. This command will start the mysql docker container in detached mode and expose the 
standard mysql port 3306 to port 1337 in the outer world.

### Instructions for connecting to the mysql docker container from the local machine using the mysql client:
- For connecting to the mysql container from the outer world, we can use the following command `mysql -u root -h 0.0.0.0 --port=1337 -p`. This command will contact
 the mysql server using `0.0.0.0:1337`.
- Note that we cannot use the hostname in order to connect to the container, we will have to use host as `0.0.0.0` 
and the port as `1337` as that is the port that has been exposed

### Instructions for connecting to the mysql docker container from another container:
- For connecting to the mysql container from another container we will need `link` the application container to the 
mysql container in the following way: `docker run --link <mysql_container_name> mysql -it <repo>/<name>:<tag> 
/bin/bash`. Once linked mysql will now be available from the hostname `<hostname>` that was defined to start the 
mysql container and the standard port `3306`. Inside the container the command can be `mysql -u root -h <hostname> -p`
This command will contact the host using the standard port.

For the `mqfn` container the command can be `docker run --link <mysql_container_name>-v $PWD:/app --expose 15333 
--publish 0.0.0.0:15333:15333 -it riflerrick/mqfn:1.0`  

### Instructions for running without Docker:
- `pip install -r requirements.txt` into a virtualenv
- `./bbmq/server/server_daemon.py start` to start the server

You can spawn any number of producers and consumers.

### Instructions for running with Docker(without linking mysql):
- cd to the root dir
- `docker pull riflerrick/mqfn:1.0` to build the image
- `docker run -v $PWD:/app --expose 15333 --publish 0.0.0.0:15333:15333 -it riflerrick/mqfn:1.0` to
 start the container. 
- `docker exec -it <container id> /bin/bash` to login to the container.
- `./bbmq/server/server_daemon.py start` to start the server.