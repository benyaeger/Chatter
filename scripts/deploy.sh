# Navigate to the Chatter directory
cd /home/Chatter || exit

# Pull the latest code from the repository
git pull origin main

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Restart the Flask application
# Kill any existing Flask processes
pkill -f gunicorn

# Start the Flask application with gunicorn
nohup gunicorn -b 0.0.0.0:5000 applicationServer:app > app.log 2>&1 &
