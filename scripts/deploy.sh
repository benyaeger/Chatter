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
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Kill any existing Flask processes
pkill -f gunicorn

# Start the Flask application with gunicorn
nohup gunicorn -b 0.0.0.0:5000 applicationServer:app > app.log 2>&1 &
