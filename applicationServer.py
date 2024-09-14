from flask import request, redirect, url_for, Flask, jsonify
import psycopg2
from psycopg2 import errors
from datetime import datetime
from flask_cors import CORS

# We create a Flask app object on our current file
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Connecting to Real DB
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='l17JkhOqKwjYofAu14Wt',
    host='chatter-db-leader.cdkae2i48cd8.eu-north-1.rds.amazonaws.com',
    port='5432'
)

# Connecting to A DUMMY DB
# conn = psycopg2.connect(
#     dbname='postgres',
#     user='postgres',
#     password='213746837',
#     host='localhost',
#     port='5432'
# )

# We create a cursor to the connection
cur = conn.cursor()


# We use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index():
    return jsonify(message='Hello World!')


@app.route('/user')
def get_user():
    # We get user first and last name from request parameters
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    # Querying the DB for users that meet the parameters
    cur.execute(f"SELECT * FROM users WHERE first_name LIKE '%{first_name}%' AND last_name LIKE '%{last_name}%'")
    users = cur.fetchall()

    user_list = []
    for user in users:
        user_dict = {
            'user_id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'user_created_at': user[3],
            'user_details_updated_at': user[4]
        }
        user_list.append(user_dict)

    # If no users found
    if len(user_list) == 0:
        return jsonify(error='User Not Found'), 404
    return jsonify(user_list)


# Tested
@app.route('/newchat', methods=["POST"])
def new_chat():
    # We get new chat parameters from request parameters
    owner_id = request.args.get('owner_id', '')
    chat_name = request.args.get('chat_name', '')
    if owner_id == '' or chat_name == '' or not owner_id or not chat_name:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # Prepare the new chat INSERT query to the chats table
    new_chat_insert_query = """
    INSERT INTO chats (chat_name, chat_created_at, chat_owner_id, chat_details_updated_at)
    VALUES (%s, %s, %s, %s) RETURNING chat_id
    """

    # These fields don't require the user's input
    chat_created_at = datetime.now()  # Or any specific timestamp
    chat_owner_id = owner_id
    chat_details_updated_at = datetime.now()  # This is optional; if not specified, it defaults to CURRENT_TIMESTAMP
    try:
        # Execute the query with the provided values
        cur.execute(new_chat_insert_query, (chat_name, chat_created_at, chat_owner_id, chat_details_updated_at))

        # Fetch the chat generated ID
        new_chat_id = cur.fetchone()[0]

        # Commit the changes to the database
        conn.commit()

        # We also need to add the owner as a chat participant
        # We use previously implemented function
        add_user_to_chat(new_chat_id, owner_id)
        return jsonify(message='Chat Created Successfully, Owner added to chat participants'), 200

    except Exception as e:
        return jsonify(error=f'An Error occurred: {e}'), 500


# Tested
@app.route('/add_user_to_chat', methods=["POST"])
def add_user_to_chat(chat_id=None, added_user_id=None):
    if chat_id is None and added_user_id is None:
        # Get params from request
        chat_id = request.args.get('chat_id', '')
        added_user_id = request.args.get('added_user_id', '')
        if chat_id == '' or added_user_id == '' or not chat_id or not added_user_id:
            return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # Insert Query Init
    new_participant_insert_query = """
    INSERT INTO participants (chat_id, user_id) VALUES (%s, %s)
    """
    try:
        # Execute Insert Query
        cur.execute(new_participant_insert_query, (chat_id, added_user_id))
        # Commit the changes to the database
        conn.commit()
        return jsonify(message=f'User ID {added_user_id} added Successfully to Chat ID {chat_id}'), 200
    except errors.UniqueViolation:
        # Handle unique constraint violation, like adding the same user to the same chat
        # The rollback() function ensures the data transaction is rolled back, preventing partial data from being commited to the DB
        conn.rollback()
        return jsonify(message=f'Error: User ID {added_user_id} is already added to Chat ID {chat_id}'), 400
    except Exception as e:
        # Handle other potential exceptions
        conn.rollback()
        return jsonify(message=f'An Error occurred: {str(e)}'), 500


# Tested
@app.route('/remove_user_from_chat', methods=["DELETE"])
def remove_user_from_chat(chat_id=None, user_id=None):
    if chat_id is None and user_id is None:
        chat_id = request.args.get("chat_id", "")
        user_id = request.args.get("user_id", "")
        if chat_id == '' or user_id == '' or not chat_id or not user_id:
            return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    delete_query = "DELETE FROM participants WHERE user_id = %s AND chat_id = %s"
    try:
        # Execute Delete Query
        cur.execute(delete_query, (user_id, chat_id))

        # Check if any row was deleted
        if cur.rowcount == 0:
            return jsonify(message=f'User ID {user_id} is not a participant in Chat ID {chat_id}'), 400

        # Commit the changes to the database
        conn.commit()
        return jsonify(message=f'User ID {user_id} removed Successfully from Chat ID {chat_id}'), 200
    except Exception as e:
        return jsonify(error=f'An Error occurred: {e}'), 500


# Tested
@app.route('/user_chats')
def get_chats_of_user():
    # We get user id name from request parameters
    owner_id = request.args.get('owner_id', '')

    if owner_id == '' or not owner_id:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # Querying the DB for chats that meet the parameters
    cur.execute(f"SELECT * FROM chats WHERE chat_owner_id = {owner_id}")
    chats_query = cur.fetchall()

    chats = []
    for chat in chats_query:
        chats_dict = {
            "chat_id": chat[0],
            "chat_name": chat[1],
            "chat_created_at": chat[2],
            "chat_owner_id": chat[3],
            "chat_details_updated_at": chat[4],
        }
        chats.append(chats_dict)

    # If no chats found
    if len(chats) != 0:
        return jsonify(chats), 200
    return jsonify(error='No Chats Found'), 404


# Tested
@app.route('/get_chat_participants')
def get_chat_participants():
    # Get chat id
    chat_id = request.args.get('chat_id', '')
    if chat_id == '' or not chat_id:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    cur.execute(
        f'SELECT * FROM participants JOIN users ON participants.user_id = users.user_id WHERE chat_id = {chat_id}')

    chat_participants_query = cur.fetchall()

    chat_participants = []
    for participant in chat_participants_query:
        print(participant)
        participant_dict = {
            'user_id': participant[2],
            'first_name': participant[3],
            'last_name': participant[4],
            'user_created_at': participant[5],
            'user_details_updated_at': participant[6]
        }
        chat_participants.append(participant_dict)

    if len(chat_participants) != 0:
        return jsonify(chat_participants), 200
    return jsonify(error='No Chat Participants Found'), 404


if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
