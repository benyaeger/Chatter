import pytest
from datetime import datetime
from flask import Flask
from applicationServer import app


# This part of the test file creates a client that can send requests and get responses from my server
@pytest.fixture
def client():
    # Creates a test client for our Flask app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# This function tests the get_all_users function
def test_get_all_users(client):
    response = client.get('/users')
    # Check status code is OK
    assert response.status_code == 200
    assert len(response.data) > 0 or b'No Users Found' in response.data


# This function tests the new_chat function of the server
@pytest.mark.skip(reason="Temporarily skipping this test")
def test_new_chat(client):
    # Define the test parameters
    owner_id = 1

    # Simulate a POST request to the '/newchat' endpoint
    response = client.post('/newchat', query_string={'owner_id': owner_id})

    # Check the response data
    # Check status code is OK
    assert response.status_code == 200


# This function tests the add_user_to_chat function
def test_add_user_to_chat(client):
    chat_id = 1
    added_user_id = 6

    response = client.post('/add_user_to_chat', query_string={'chat_id': chat_id, 'added_user_id': added_user_id})

    # Check status code is OK
    assert response.status_code == 200
    assert b'added Successfully to Chat ID' in response.data


# This function tests the get_chats_of_user function
def test_get_chats_of_user(client):
    # Define the test parameters
    owner_id = 1

    # Simulate a POST request to the '/user_chats' endpoint
    response = client.get('/user_chats', query_string={'owner_id': owner_id})

    # Check status code is OK
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main()
