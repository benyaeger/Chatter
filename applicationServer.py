# Importing the Flask library
from flask import Flask
# Importing request
from flask import request
# Importing abort, redirect, url_for
from flask import abort, redirect, url_for

# Importing flask
from flask import *

# We create a Flask app object on our current file
app = Flask(__name__)


# We use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index():
    return redirect(url_for('about_api'))


@app.route('/aboutapi')
def about_api():
    return {
        "api_name": "Ben's API",
        "country": "Israel"
    }


if __name__ == '__main__':
    # Run the app
    app.run(debug=True)
