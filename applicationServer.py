# Importing the Flask library
from flask import Flask
# Importing request
from flask import request

# We create a Flask app object on our current file
app = Flask(__name__)


# We use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index(name):
    return f'Hello World!'


# Variable accepting from URL
@app.route('/<username>')
def say_hello_to(username):
    return f'Hello {username}'


# Allowing diverse HTTP methods: GET and POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Accessing the request type, handling a POST request
    if request.method == 'POST':
        return 'POST Request Received'
    else:
        return 'GET Request Received'


if __name__ == '__main__':
    # Run the app
    app.run(debug=True)
