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
For preserving all the data a mysql server is used. The ORM used to interact with the mysql server is sql alchemy. 
For the docs of sql alchemy refer to [http://docs.sqlalchemy.org/en/latest/orm/tutorial.html](http://docs.sqlalchemy.org/en/latest/orm/tutorial.html)
    
### Instructions for running mysql docker container:
- Pull the docker image `docker pull riflerrick/mqfn-mysql`
- Run the docker mysql conatiner `docker run -h <hostname> -e MYSQL_ROOT_PASSWORD=<password> -d --expose 3306 
--publish 0.0.0.0:1337:3306 riflerrick/mqfn-mysql:latest`. This command will start the mysql docker container in
 detached mode and expose the 
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

For the `mqfn` container the command can be `docker run --link <mysql_container_name>-v $PWD:/app --expose
 15333 --publish 0.0.0.0:15333:15333 -it riflerrick/mqfn:1.0`  

### Instructions for running without Docker:
- `pip install -r requirements.txt` into a virtualenv
- `./bbmq/server/server_daemon.py start` to start the server

You can spawn any number of producers and consumers.

### Instructions for running with Docker(without linking mysql):
- cd to the root dir
- `docker pull riflerrick/mqfn:1.0` to build the image
- `docker run -v $PWD:/app --expose 15333 --publish 0.0.0.0:15333:15333 -it riflerrick/mqfn:1.0` to
 start the container. 
- `docker run -d -v $PWD:/app --expose 15333 --publish 0.0.0.0:15333:15333 -it riflerrick/mqfn:1.0` to start
 the container in detached mode
- `docker exec -it <container id> /bin/bash` to login to the container.
- `./bbmq/server/server_daemon.py start` to start the server.

### Running the container in production
- `sudo docker run --restart unless-stopped -d --expose 15333 --publish 0.0.0.0:15333:15333 -it
 riflerrick/mqfn:1.0 ./bbmq/server/server_daemon.py start` for starting the container and the service within it in detached mode.

### Database integration
Tables:
- Queue
- Message

Queues is a table storing all queues with their corresponding topics
Messages will have a one to many relationship with the Queues table.

Attributes of Queue
- **id** (primary key, foreign key to messages, integer)
- **name** of queue (varchar)
- **created_timestamp** timestamp of creation of the queue

Attributes of Message
- **id** (primary key, intger)
- **queue_id** (foreign key to queue)
- **is_fetched**(boolean) (True if the corresponding message has been fetched, false otherwise, default=false)
- **content** (varchar) (content of the message)
- **publish_timestamp** (datetime) (timestamp of publishing of the message)
- **consumed_timestamp** (datetime) (timestamp of consumption of the message) (default=NULL)

At server start:
- Create database entries for new queues if any. 

- A database query will be made in order to check for any messages that was not 
fetched. If such messages are found, such messages will be pushed to the queue. 

- For every new message that is pushed by any producer, the content of the message will be written to the Message table as a new entry with a default is_fetched value of False

- For every message that is pulled by any consumer, the **is_fetched** attribute will be updated as True and the **consumed_timestamp** will be updated.

A `USE_DB` variable has been added in the settings. If this is true, then a database is required for storing all the messages that are enqueued. 

### Producer and Consumer APIs

Producer and Consumer APIs have been written for producers and consumers to communicate with the server. 

**Getting started with a producer:**
```python
from bbmq.producer.producer import Producer

prod = Producer("topic_name") # for initializing the producer and publishing for "topic_name"
prod.connect() # for connecting with the producer 
prod.publish("helloworld") # for publishing the message "helloworld" to the producer
prod.close_socket() # for closing the socket

```

**Getting started with a consumer**
```python

from bbmq.consumer.consumer import Consumer

cons = Consumer("topic_name") # for initializing th consumer and subscribing to topic "topic_name"
cons.connect() # for connecting to the consumer
cons.fetch() # for fetching messsages from the consumer
cons.close_socket() # for closing the socket

```
`fetch()` method of consumer class is a blocking function call and will not return unless something is available from the server. 