#!/bin/bash

# Switch to root user
sudo su

# Navigate to the Chatter directory
cd /home/Chatter || exit

# Activate virtual environment
source venv/bin/activate

# Pull the latest code from the repository
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Kill any existing Flask processes
pkill -f gunicorn

# Pull the latest Docker image
docker pull benyaegerwork/chatter-flask-server:v1

# Run the new Docker container
docker run -d -p 5000:5000 benyaegerwork/chatter-flask-server:v1