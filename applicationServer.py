# Importing the Flask library
from flask import Flask
# Importing request
from flask import request
# Importing abort, redirect, url_for
from flask import abort, redirect, url_for


# We create a Flask app object on our current file
app = Flask(__name__)


# We use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index():
    return f'Hello World!'


# Variable accepting from URL
@app.route('/<username>')
def say_hello_to(username):
    return f'Hello {username}'


@app.route('/greetme')
def greet():
    # Redirecting to the url that corresponds to the say_hello_to() function
    # Why use url_for() instead of hard-coded url? so if I change the route to say_hello_to() function,
    # I would need to change it once
    return redirect(url_for('say_hello_to'))
    # Function never reaches here due to redirect


if __name__ == '__main__':
    # Run the app
    app.run(debug=True)
