# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN pip install -e .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV <env var name> <env var value>

# command to run when the container launches
CMD ["bbmq", "start"]
