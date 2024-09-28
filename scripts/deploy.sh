#!/bin/bash

# Switch to root user
sudo su

# Navigate to the Chatter directory
cd /home/Chatter || exit

# Activate venv
source venv/bin/activate

# Activate Env Var
source ~/.bashrc

# Pull the latest code from the repository
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Login to Docker without hardcoding credentials
echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin

# Pull the latest image
docker pull chatter-flask-server:v1

# Stop any existing container running the image
docker stop chatter-flask-server || true

# Remove the existing container if it exists
docker rm chatter-flask-server || true

# Run the new container
docker run -d \
    --name chatter-flask-server \
    -p 5000:5000 \
    chatter-flask-server:v1
