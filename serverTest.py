import pytest
from applicationServer import app, conn, cur


@pytest.fixture(scope='module', autouse=True)
def prepare_testing_sandbox():
    # Using the existing database connection from the server
    # Clean up the tables before starting the tests
    cur.execute("TRUNCATE TABLE chats RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE TABLE participants RESTART IDENTITY CASCADE;")
    conn.commit()

    # Yield control back to the tests
    yield


# This part of the test file creates a client that can send requests and get responses from my server
@pytest.fixture
def client():
    # Creates a test client for our Flask app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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
    user_id = 1

    # Simulate a GET request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'user_id': user_id})

    # Check status code
    assert response.status_code == 200

    # Test 2 - Expected Result: No Chats Found #
    # Define the test parameters
    user_id = 88

    # Simulate a GET request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'user_id': user_id})

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


if __name__ == '__main__':
    pytest.main()
