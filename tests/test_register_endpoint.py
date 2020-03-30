import pytest

from flask_sqlalchemy import SQLAlchemy

from app import create_app


@pytest.fixture(scope='function')
def fn_app():
    app = create_app(testing=True)
    return app

@pytest.fixture(scope='module')
def mod_app():
    app = create_app(testing=True)
    return app


@pytest.fixture(scope='function')
def fn_client(fn_app):
    yield fn_app.test_client()

    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')


@pytest.fixture(scope='module')
def mod_client(mod_app):
    yield mod_app.test_client()

    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')



# also a test for successful registration
@pytest.fixture(scope='module')
def client_with_regd_user_johndoe_abc123(mod_client):
    response = register_with(mod_client, 'johndoe', 'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    EXPECTED_RESPONSE = b'''{
    "created_user": {
        "username": "johndoe",
        "email": "johndoe@gmail.com"
    }\n}'''

    assert EXPECTED_RESPONSE in response.data
    return mod_client



def register_with(fn_client, username, password, email):
    ENDPOINT = '/api/auth/register'
    return fn_client.post(ENDPOINT, data=dict(
        username=username, password=password, email=email))



def test_username_already_in_use(client_with_regd_user_johndoe_abc123):
    response = register_with(
        client_with_regd_user_johndoe_abc123, 
        'johndoe', '123', 'bla@gmail.com'
    )
    assert 400 == response.status_code

    EXPECTED_RESPONSE = b'''{
    "error": "Registration Failed.",
    "description": "The username 'johndoe' is already in use."\n}'''

    assert EXPECTED_RESPONSE in response.data


def test_email_already_in_use(client_with_regd_user_johndoe_abc123):
    response = register_with(
        client_with_regd_user_johndoe_abc123, 
        'guido', 'bla123', 'johndoe@gmail.com'
    )
    assert 400 == response.status_code

    EXPECTED_RESPONSE = b'''{
    "error": "Registration Failed.",
    "description": "The email 'johndoe@gmail.com' is already in use."\n}'''

    assert EXPECTED_RESPONSE in response.data


def test_form_missing_username_key_value_pair(fn_client):
    BAD_FORM_MESSAGE = b'''{
    "error": "Registration Failed.",
    "description": "Form filled incorrectly. Missing field."\n}'''

    response = fn_client.post('/api/auth/register', data=dict(
        password='abc123', email='abc@gmail.com'))
    assert 400 == response.status_code
    assert BAD_FORM_MESSAGE in response.data


def test_form_missing_password_key_value_pair(fn_client):
    BAD_FORM_MESSAGE = b'''{
    "error": "Registration Failed.",
    "description": "Form filled incorrectly. Missing field."\n}'''

    response = fn_client.post('/api/auth/register', data=dict(
        username='guido', email='abc@gmail.com'))
    assert 400 == response.status_code
    assert BAD_FORM_MESSAGE in response.data


def test_form_missing_email_key_value_pair(fn_client):
    BAD_FORM_MESSAGE = b'''{
    "error": "Registration Failed.",
    "description": "Form filled incorrectly. Missing field."\n}'''

    response = fn_client.post('/api/auth/register', data=dict(
        username='guido', password='abc123'))
    assert 400 == response.status_code
    assert BAD_FORM_MESSAGE in response.data


