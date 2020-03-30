import pytest

from flask_sqlalchemy import SQLAlchemy

from app import create_app

from test_register_endpoint import register_with


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    yield app.test_client()

    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')    


def login_with(client, username, password):
    endpoint = '/api/auth/login'
    return client.post(endpoint, data=dict(
        username=username, password=password))


def test_login_with_missing_username_key_value_pair(client):
    BAD_FORM_MESSAGE = b'''{
    "error": "Login Failed.",
    "description": "Form filled incorrectly. Missing field."\n}'''

    response = client.post('/api/auth/login', data=dict(password='abc123'))
    assert 400 == response.status_code
    assert BAD_FORM_MESSAGE in response.data


def test_login_with_missing_password_key_value_pair(client):
    BAD_FORM_MESSAGE = b'''{
    "error": "Login Failed.",
    "description": "Form filled incorrectly. Missing field."\n}'''

    response = client.post('/api/auth/login', data=dict(username='victor'))
    assert 400 == response.status_code
    assert BAD_FORM_MESSAGE in response.data


def test_login_with_nonexistent_username(client):
    FAIL_MESSAGE = b'''{
    "error": "Login Failed.",
    "description": "User with username 'newuser' could not be found."\n}'''

    response = login_with(client, 'newuser', 'abc123')
    assert 400 == response.status_code
    assert FAIL_MESSAGE in response.data


def test_login_with_wrong_password(client):
    response = register_with(client, 'johndoe', 'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    FAIL_MESSAGE = b'''{
    "error": "Login Failed.",
    "description": "Wrong password."\n}'''

    response = login_with(client, 'johndoe', 'wrongpwd123')
    assert 400 == response.status_code
    assert FAIL_MESSAGE in response.data


def test_successful_login_returns_JWT(client):
    response = register_with(client, 'johndoe', 'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    response = login_with(client, 'johndoe', 'abc123')
    assert b'access_token' in response.data
    assert 200 == response.status_code

