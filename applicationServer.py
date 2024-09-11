from flask import request, redirect, url_for, Flask
import psycopg2
from psycopg2 import sql, errors
from datetime import datetime

# We create a Flask app object on our current file
app = Flask(__name__)

# We connect to DB
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='213746837',
    host='localhost',
    port='5432'
)

# We create a cursor to the connection
cur = conn.cursor()


# We use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index():
    return redirect(url_for('get_all_users'))


@app.route('/user')
def get_user():
    # We get user first and last name from request parameters
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    # Querying the DB for users that meet the parameters
    cur.execute(f"SELECT * FROM users WHERE first_name LIKE '%{first_name}%' AND last_name LIKE '%{last_name}%'")
    users = cur.fetchall()
    # If no users found
    if len(users) == 0:
        return '404 User Not Found'
    return users


@app.route('/users')
def get_all_users():
    cur.execute("SELECT * FROM users ORDER BY first_name")
    users = cur.fetchall()
    # If no users found
    if len(users) == 0:
        return 'No Users Found'
    return users


@app.route('/newchat', methods=["POST"])
def new_chat():
    # We get user id name from request parameters
    owner_id = request.args.get('owner_id', '')

    # Prepare the INSERT query
    insert_query = """
    INSERT INTO chats (chat_name, chat_created_at, chat_owner_id, chat_details_updated_at)
    VALUES (%s, %s, %s, %s)
    """

    # Define the values for insertion
    chat_name = "Test Chat"
    chat_created_at = datetime.now()  # Or any specific timestamp
    chat_owner_id = owner_id
    chat_details_updated_at = datetime.now()  # This is optional; if not specified, it defaults to CURRENT_TIMESTAMP

    # Execute the query with the provided values
    cur.execute(insert_query, (chat_name, chat_created_at, chat_owner_id, chat_details_updated_at))

    # Commit the changes to the database
    conn.commit()
    return 'Chat Created Successfully'


@app.route('/add_user_to_chat', methods=["POST"])
def add_user_to_chat():
    # Get params from request
    chat_id = request.args.get('chat_id', '')
    added_user_id = request.args.get('added_user_id', '')

    # Insert Query Init
    insert_query = """
    INSERT INTO participants (chat_id, user_id) VALUES (%s, %s)
    """
    try:
        # Execute Insert Query
        cur.execute(insert_query, (chat_id, added_user_id))
        # Commit the changes to the database
        conn.commit()
        return f'User ID {added_user_id} added Successfully to Chat ID {chat_id}'
    except errors.UniqueViolation:
        # Handle unique constraint violation, like adding the same user to the same chat
        # The rollback() function ensures the data transaction is rolled back, preventing partial data from being commited to the DB
        conn.rollback()
        return f'Error: User ID {added_user_id} is already added to Chat ID {chat_id}', 400
    except Exception as e:
        # Handle other potential exceptions
        conn.rollback()
        return f'An error occurred: {str(e)}', 500


@app.route('/user_chats')
def get_chats_of_user():
    # We get user id name from request parameters
    owner_id = request.args.get('owner_id', '')

    # Querying the DB for chats that meet the parameters
    cur.execute(f"SELECT * FROM chats WHERE chat_owner_id = {owner_id}")
    chats = cur.fetchall()

    # If no chats found
    if len(chats) == 0:
        return '404 Chats Not Found'
    return chats


if __name__ == '__main__':
    # Run the app
    app.run(debug=True)
