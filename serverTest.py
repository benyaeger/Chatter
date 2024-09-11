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
    # Define the test parameters
    owner_id = 1
    chat_name = 'Trofoty Habat'

    # Simulate a POST request to the '/newchat' endpoint
    response = client.post('/newchat', query_string={'owner_id': owner_id, 'chat_name': chat_name})

    # Check the response data
    # Check status code is OK
    assert response.status_code == 200


# This function tests the add_user_to_chat function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_add_user_to_chat(client):
    chat_id = 1
    added_user_id = 7

    response = client.post('/add_user_to_chat', query_string={'chat_id': chat_id, 'added_user_id': added_user_id})

    print(response.data)
    if response.status_code == 200:
        assert b'added Successfully to Chat ID' in response.data
    else:
        # Check status code is OK
        assert b'Error' in response.data


# This function tests the get_chats_of_user function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_chats_of_user(client):
    # Define the test parameters
    owner_id = 1

    # Simulate a POST request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'owner_id': owner_id})

    # Check status code is OK
    assert response.status_code == 200


# This function test the get_chat_participants function
# @pytest.mark.skip(reason="Temporarily skipping this test")
def test_get_chat_participants(client):
    # Define the test parameters
    chat_id = 1

    # Simulate a POST request to the '/get_chat_participants' endpoint
    response = client.get('/get_chat_participants', query_string={'chat_id': chat_id})

    print(response.data)

    # Check status code is OK
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main()
