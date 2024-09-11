# Navigate to the Chatter directory
cd /home/Chatter || exit

# Pull the latest code from the repository
git pull origin main

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Restart the Flask application
# You may need to modify this part based on how you run your application
pkill -f applicationServer.py
nohup python applicationServer.py &
