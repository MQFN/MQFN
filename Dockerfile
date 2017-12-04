# The base image here is ubuntu:latest
FROM riflerrick/mqfn-essentials:latest

# Set the working directory to /
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 15333 available to the world outside this container
EXPOSE 15333

# Define environment variable
# ENV <env var name> <env var value>

# command to run when the container launches
CMD ["./bbmq/server/server_daemon.py", "start"]
