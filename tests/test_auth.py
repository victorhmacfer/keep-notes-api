import pytest

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    yield app.test_client()

    with app.app_context():
        db.drop_all()


def test_register_endpoint(client):
    # Good request: neither username nor email already in use.
    response = register_with(client, 'john doe', 'abc123', 'johndoe@gmail.com')
    assert 200 == response.status_code
    assert b'{"message":"User registered successfully."}' in response.data

    # username already in use
    response = register_with(client, 'john doe', '123', 'bla@gmail.com')
    assert 400 == response.status_code
    assert b'{"message":"This username is already in use."}' in response.data

    # email already in use
    response = register_with(client, 'guido', 'bla123', 'johndoe@gmail.com')
    assert 400 == response.status_code
    assert b'{"message":"This email is already in use."}' in response.data

    bad_form_message = b'{"message":"Form filled incorrectly: Missing field."}'

    # form missing username key-value pair
    response = client.post('/api/auth/register', data=dict(
        password='abc123', email='abc@gmail.com'))
    assert 400 == response.status_code
    assert bad_form_message in response.data

    # form missing password key-value pair
    response = client.post('/api/auth/register', data=dict(
        username='guido', email='abc@gmail.com'))
    assert 400 == response.status_code
    assert bad_form_message in response.data

    # register request with form missing email key-value pair
    response = client.post('/api/auth/register', data=dict(
        username='guido', password='abc123'))
    assert 400 == response.status_code
    assert bad_form_message in response.data


def register_with(client, username, password, email):
    endpoint = '/api/auth/register'
    return client.post(endpoint, data=dict(
        username=username, password=password, email=email))

def login_with(client, username, password):
    endpoint = '/api/auth/login'
    return client.post(endpoint, data=dict(
        username=username, password=password))




def test_login_endpoint(client):

    # login attempt with nonexistent USERNAME
    response = login_with(client, 'newuser', 'abc123')
    assert 400 == response.status_code
    assert b'{"message":"No user registered with this username."}' in response.data

    # login attempt with WRONG PASSWORD
    response = register_with(client, 'johndoe', 'abc123', 'johndoe@gmail.com')
    assert 200 == response.status_code
    assert b'{"message":"User registered successfully."}' in response.data
    response = login_with(client, 'johndoe', 'wrongpwd123')
    assert 400 == response.status_code
    assert b'{"message":"Wrong password."}' in response.data

    # successful login should return JWT with response
    response = login_with(client, 'johndoe', 'abc123')
    assert b'access_token' in response.data
    assert 200 == response.status_code




