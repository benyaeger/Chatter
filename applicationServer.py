from flask import redirect, url_for, Flask, jsonify, request
import psycopg2
from psycopg2 import errors
from datetime import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms

# We create a Flask app object on our current file
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# We config the WebSocket app
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Connecting to Real DB
# conn = psycopg2.connect(
#     dbname='postgres',
#     user='postgres',
#     password='l17JkhOqKwjYofAu14Wt',
#     host='chatter-db-leader.cdkae2i48cd8.eu-north-1.rds.amazonaws.com',
#     port='5432'
# )

# Connecting to A DUMMY DB
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='213746837',
    host='host.docker.internal',
    port='5432'
)

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
        return jsonify(message='User Not Found'), 404
    return jsonify(user_list)


# This function gets the user details by username
@app.route('/user_by_username')
def get_user_by_username():
    # We get the params from args
    user_name = request.args.get('user_name')

    # Querying the DB for users that meet the parameters
    cur.execute(f"SELECT * FROM users WHERE username = '{user_name}'")

    # If username arg is missing
    if user_name == '' or not user_name:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # Fetch matching users
    user = cur.fetchone()
    # If user is None then no users were found
    if user is None:
        return jsonify(message='User Does Not Exist'), 404

    # Create a dictionary from the returned tuple
    user_data = {
        "user_id": user[0],
        "first_name": user[1],
        "last_name": user[2],
        "user_created_at": user[3],
        "user_details_updated_at": user[4],
        "username": user[5]
    }

    # We return the user data
    return jsonify(user_data), 200


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
        return jsonify(message='Chat Created Successfully, Owner added to chat participants', chat_id=new_chat_id), 200

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
    # We get username from request parameters
    user_name = request.args.get('user_name', '')

    if user_name == '' or not user_name:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # Get user_id from users table based on user_name
    cur.execute("SELECT user_id FROM users WHERE username = %s", (user_name,))
    user_search_query = cur.fetchone()

    # If no user matches the username
    if user_search_query is None:
        return jsonify(message='User not found'), 404

    # Get the database user_id of the user
    user_id = user_search_query[0]

    # Querying the DB for participants that meet the parameters
    # The logic is that we query the participants table for chats the user owns and chats he/she participates in
    cur.execute(
        "SELECT * FROM participants JOIN chats ON participants.chat_id = chats.chat_id WHERE user_id = %s",
        (user_id,)
    )
    chats_query = cur.fetchall()
    chats = []
    for chat in chats_query:
        chats_dict = {
            "chat_id": chat[0],
            "chat_name": chat[3],
            "chat_created_at": chat[4],
            "chat_owner_id": chat[5],
            "chat_details_updated_at": chat[6],
        }
        chats.append(chats_dict)

    # If no chats found
    if len(chats) != 0:
        # return jsonify(chats), 200
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


# Tested
@app.route('/send_message', methods=["POST"])
def send_message():
    # Get params from request
    user_id = request.args.get('user_id', '')
    chat_id = request.args.get('chat_id', '')
    message_content = request.args.get('message_content', '')

    # If any parameter invalid or blank, return 400
    if chat_id == '' or user_id == '' or message_content == '' or not chat_id or not user_id or not message_content:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    # If message is longer then 256 chars, return 400
    if len(message_content) >= 256:
        return jsonify(message=f'Message exceeded 256 characters'), 400

    # Insert Query Init
    new_message_query = """
    INSERT INTO messages (sender_id ,message_sent_at ,chat_id, message_content) VALUES (%s, NOW(), %s, %s);
    """

    try:
        # Execute Insert Query
        cur.execute(new_message_query, (user_id, chat_id, message_content))
        # Commit the changes to the database
        conn.commit()
        return jsonify(message=f'Message uploaded Successfully to Chat ID {chat_id}'), 200

    except Exception as e:
        # Handle other potential exceptions
        conn.rollback()
        return jsonify(message=f'An Error occurred: {str(e)}'), 500


@socketio.on('connect')
def handle_connection():
    print(f'new connection')


# Websocket handling of new message
@socketio.on('message')
def handle_message(message):
    # Get params from request
    user_id = message["user_id"]
    chat_id = message["chat_id"]
    message_content = message["message_content"]

    # If any parameter invalid or blank, return 400
    if chat_id == '' or user_id == '' or message_content == '' or not chat_id or not user_id or not message_content:
        # We send an error message to sender
        emit('error_sending_message', 'At least one of the parameters is empty or was not provided', room=request.sid)
        return  # Prevent further execution

    # If message is longer then 256 chars, return 400
    if len(message_content) >= 256:
        # We send an error message to sender
        emit('error_sending_message', 'Message exceeded 256 characters', to=request.sid)
        return  # Prevent further execution

    # Insert Message Query
    new_message_query = """
    INSERT INTO messages (sender_id, message_sent_at, chat_id, message_content) 
    VALUES (%s, NOW(), %s, %s) RETURNING *;
    """

    try:
        # Execute Insert Query
        cur.execute(new_message_query, (user_id, chat_id, message_content))

        # Fetch the entire row back
        new_message_data = cur.fetchone()

        # Commit the changes to the database
        conn.commit()

        # Convert datetime to ISO format for JSON serialization
        message_sent_at = new_message_data[2].isoformat() if isinstance(new_message_data[2], datetime) else \
            new_message_data[2]

        # Create a dictionary from the returned tuple
        new_message = {
            "first_name": message["first_name"],
            "last_name": message["last_name"],
            "message_id": new_message_data[0],  # Assuming this is the first column
            "sender_id": message["user_id"],
            "message_sent_at": message_sent_at,
            "chat_id": message["chat_id"],
            "message_content": message["message_content"]
        }

        # We send the new message to all room listeners
        emit('new_message', new_message, to=chat_id)

    except Exception as e:
        # Handle other potential exceptions
        conn.rollback()
        # We send an error message to sender
        emit('error_sending_message', f'An Error occurred: {str(e)}', to=request.sid)


@socketio.on('join')
def on_join(data):
    username = data['username']
    chat_id = data['chat_id']
    print(f'{username} has joined room {chat_id}')
    join_room(chat_id)
    display_room_status(chat_id)
    send(username + ' has entered the room.', to=chat_id)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    chat_id = data['chat_id']
    leave_room(chat_id)
    send(username + ' has left the room.', to=chat_id)


# Utility function to display room status
def display_room_status(chat_id):
    room_clients = socketio.server.manager.rooms.get('/')[chat_id]
    print(f'Room {chat_id} has {len(room_clients)} client(s) connected:')
    for client_id in room_clients:
        print(f' - {client_id}')


# Tested
@app.route('/get_chat_messages')
def get_chat_messages():
    # Get chat id and number of messages to read
    chat_id = request.args.get('chat_id', '')
    number_of_messages = request.args.get('number_of_messages', '')

    if chat_id == '' or not chat_id or number_of_messages == '' or not number_of_messages:
        return jsonify(message=f'At least one of the parameters is empty or was not provided'), 400

    cur.execute(
        f'''
        SELECT * 
        FROM messages 
        JOIN users ON messages.sender_id = users.user_id 
        WHERE chat_id = {chat_id} 
        ORDER BY messages.message_sent_at DESC 
        LIMIT {number_of_messages}
        '''
    )

    chat_messages_query = cur.fetchall()

    chat_messages = []
    for chat_message in chat_messages_query:
        chat_message_dict = {
            'message_id': chat_message[0],
            'sender_id': chat_message[1],
            'first_name': chat_message[6],
            'last_name': chat_message[7],
            'message_sent_at': chat_message[2],
            'message_content': chat_message[4]
        }
        chat_messages.append(chat_message_dict)

    if len(chat_messages) != 0:
        return jsonify(chat_messages), 200
    return jsonify(error='No Chat Messages Found'), 404


if __name__ == '__main__':
    # Run the app
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)