import json

import pytest
from applicationServer import app, conn, cur


@pytest.fixture(scope='module', autouse=True)
def prepare_testing_sandbox():
    # Using the existing database connection from the server
    # Clean up the tables before starting the tests
    cur.execute("TRUNCATE TABLE chats RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE participants RESTART IDENTITY CASCADE;")
    cur.execute("INSERT INTO chats (chat_name, chat_created_at, chat_owner_id) VALUES ('The Boys', NOW(), 28);")
    cur.execute("INSERT INTO participants (chat_id, user_id) VALUES (1, 28);")

    # Yield control back to the tests
    yield


# This part of the test file creates a client that can send requests and get responses from my server
@pytest.fixture
def client():
    # Creates a test client for our Flask app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# This function tests the get_user_by_username function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_user_by_username(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameter
    user_name = 'benben1001'

    # Simulate a GET request to the '/user_by_username' endpoint
    response = client.get('/user_by_username', query_string={'user_name': user_name})
    print(response)

    # Check status code
    assert response.status_code == 200

    # Check the response data
    data = response.get_json()
    assert 'user_id' in data
    assert 'first_name' in data
    assert 'last_name' in data
    assert 'username' in data
    assert data['username'] == user_name  # Ensure the username matches

    # Test 2 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a GET request to the '/user_by_username' endpoint without username
    response = client.get('/user_by_username')

    # Check status code
    assert response.status_code == 400
    assert response.get_json()['message'] == 'At least one of the parameters is empty or was not provided'

    # Test 3 - Expected Result: User Does Not Exist #
    # Simulate a GET request to the '/user_by_username' endpoint with a non-existent username
    response = client.get('/user_by_username', query_string={'user_name': 'nonexistentuser'})

    # Check status code
    assert response.status_code == 404
    assert response.get_json()['message'] == 'User Does Not Exist'


# This function tests the new_chat function of the server
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_new_chat(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameters
    owner_id = 1
    chat_name = 'Trofoty Habat'

    # Simulate a POST request to the '/newchat' endpoint
    response = client.post('/newchat', query_string={'owner_id': owner_id, 'chat_name': chat_name})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a POST request to the '/newchat' endpoint
    response = client.post('/newchat', query_string={'chat_name': chat_name})

    # Check status code
    assert response.status_code == 400


# This function tests the add_user_to_chat function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_add_user_to_chat(client):
    # Test 1 - Expected Result: Good Response #
    chat_id = 1
    added_user_id = 7

    # Simulate a POST request to the '/add_user_to_chat' endpoint
    response = client.post('/add_user_to_chat', query_string={'chat_id': chat_id, 'added_user_id': added_user_id})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: Bad Request - Trying to add an existing user to a chat #
    # Simulate a POST request to the '/add_user_to_chat' endpoint
    response = client.post('/add_user_to_chat', query_string={'chat_id': chat_id, 'added_user_id': added_user_id})

    # Check status code
    assert response.status_code == 400

    # Test 3 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a POST request to the '/add_user_to_chat' endpoint
    response = client.post('/add_user_to_chat', query_string={'added_user_id': added_user_id})

    # Check status code
    assert response.status_code == 400


# This function tests the remove_user_from_chat function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_remove_user_from_chat(client):
    # Test 1 - Expected Result: Good Response #
    chat_id = 1
    user_id = 7

    # Simulate a DELETE request to the '/add_user_to_chat' endpoint
    response = client.delete('/remove_user_from_chat', query_string={'chat_id': chat_id, 'user_id': user_id})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: Bad Request - Trying to remove a user that does not exist in the chat #
    # Simulate a DELETE request to the '/add_user_to_chat' endpoint
    response = client.delete('/remove_user_from_chat', query_string={'chat_id': chat_id, 'user_id': user_id})

    # Check status code
    assert response.status_code == 400

    # Test 3 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a DELETE request to the '/add_user_to_chat' endpoint
    response = client.delete('/remove_user_from_chat', query_string={'chat_id': chat_id})

    # Check status code
    assert response.status_code == 400


# This function tests the get_chats_of_user function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_chats_of_user(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameters
    user_name = 'benben1001'

    # Simulate a GET request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'user_name': user_name})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: No Chats Found #
    # Define the test parameters
    user_name = 'whothehellisthis'

    # Simulate a GET request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'user_name': user_name})

    # Check status code
    assert response.status_code == 404

    # Test 3 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a GET request to the '/user_chats' endpoint
    response = client.get('/user_chats')

    # Check status code
    assert response.status_code == 400


# This function test the get_chat_participants function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_chat_participants(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameters
    chat_id = 1

    # Simulate a POST request to the '/get_chat_participants' endpoint
    response = client.get('/get_chat_participants', query_string={'chat_id': chat_id})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: No Participants Found #
    # Define the test parameters
    chat_id = 88

    # Simulate a POST request to the '/get_chat_participants' endpoint
    response = client.get('/get_chat_participants', query_string={'chat_id': chat_id})

    # Check status code
    assert response.status_code == 404

    # Test 3 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a POST request to the '/get_chat_participants' endpoint
    response = client.get('/get_chat_participants')

    # Check status code
    assert response.status_code == 400


# This function tests the send_message function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_send_message(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameters
    user_id = 1
    chat_id = 1
    message_content = 'The big brown fox jumped LMAO'

    # Simulate a POST request to the '/send_message' endpoint
    response = client.post('/send_message',
                           query_string={'user_id': user_id, 'chat_id': chat_id, 'message_content': message_content})
    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: Bad Request - Trying to send a message exceeding 256 chars #
    user_id = 1
    chat_id = 1
    message_content = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    # Simulate a POST request to the '/send_message' endpoint
    response = client.post('/send_message',
                           query_string={'user_id': user_id, 'chat_id': chat_id, 'message_content': message_content})

    # Check status code
    assert response.status_code == 400

    # Test 3 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a POST request to the '/send_message' endpoint
    response = client.post('/send_message')

    # Check status code
    assert response.status_code == 400


# This function test the get_chat_messages function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_chat_messages(client):
    # Test 1 - Expected Result: Good Response #
    # Define the test parameters
    chat_id = 1
    number_of_messages = 20

    # Simulate a GET request to the '/get_chat_messages' endpoint
    response = client.get('/get_chat_messages',
                          query_string={'chat_id': chat_id, 'number_of_messages': number_of_messages})

    # Check status code
    assert response.status_code == 200
    # Check number of messages returned
    assert len(json.loads(response.data)) <= number_of_messages

    # Test 2 - Expected Result: Bad Request - Insufficient Parameters Provided #
    # Simulate a POST request to the '/get_chat_participants' endpoint
    response = client.get('/get_chat_messages')

    # Check status code
    assert response.status_code == 400


if __name__ == '__main__':
    pytest.main()
