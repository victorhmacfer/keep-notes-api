import pytest

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db

from models.user import User
from models.note import Note, Label

from test_register_endpoint import register_with

@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client_with_regd_user(app):
    the_client = app.test_client()
    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    yield the_client
    delete_test_db()


@pytest.fixture
def client_that_user_created_two_labels(app):
    the_client = app.test_client()

    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code


    FIRST_LABEL_JSON_STR = '''{
    "text": "my-first-label"\n}'''
    

    r = the_client.post('/api/u/johndoe/labels', json=FIRST_LABEL_JSON_STR)
    assert 201 == r.status_code

    eb = b'''{
    "created_label": {
        "text": "my-first-label"
    }\n}'''
    assert eb in r.data


    SECOND_LABEL_JSON_STR = '''{
    "text": "mySecondLabel"\n}'''

    r = the_client.post('/api/u/johndoe/labels', json=SECOND_LABEL_JSON_STR)
    assert 201 == r.status_code
    
    eb = b'''{
    "created_label": {
        "text": "mySecondLabel"
    }\n}'''
    assert eb in r.data

    yield the_client
    delete_test_db()


def delete_test_db():
    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')




def test_create_label_for_nonexistent_user(client_with_regd_user):
    r = client_with_regd_user.post(
        '/api/u/notregd/labels',
        json='whatever'
    )
    assert 400 == r.status_code
    EXPECTED_BODY = b'''{
    "error": "Label creation has failed.",
    "description": "User with username 'notregd' could not be found."\n}'''

    assert EXPECTED_BODY in r.data



def test_create_label_with_bad_json_in_request(client_with_regd_user):
    MISSING_KEY_JSON = '''{
    "wrongkey": "mySecondLabel"\n}'''

    r = client_with_regd_user.post(
        '/api/u/johndoe/labels',
        json=MISSING_KEY_JSON
    )
    assert 400 == r.status_code
    EXPECTED_BODY = b'''{
    "error": "Label creation has failed.",
    "description": "Malformed JSON in request. Required keys: 'text'."\n}'''
    assert EXPECTED_BODY in r.data


    KEY_TOO_LONG_JSON = '''{
    "text": "veryveryveryveryveryveryverylongLabel"\n}'''

    r = client_with_regd_user.post(
        '/api/u/johndoe/labels',
        json=KEY_TOO_LONG_JSON
    )
    assert 400 == r.status_code
    EXPECTED_BODY = b'''{
    "error": "Label creation has failed.",
    "description": "Value for 'text' key longer than 30 characters."\n}'''
    assert EXPECTED_BODY in r.data



def test_get_all_user_labels(client_that_user_created_two_labels):
    r = client_that_user_created_two_labels.get('/api/u/johndoe/labels')

    EXPECTED_BODY = b'''{
    "username": "johndoe",
    "labels": [
        {
            "text": "my-first-label"
        },
        {
            "text": "mySecondLabel"
        }
    ]\n}'''
    assert 200 == r.status_code
    assert EXPECTED_BODY in r.data



def test_get_labels_for_nonexistent_user(client_with_regd_user):
    r = client_with_regd_user.get('/api/u/notregd/labels')
    eb = b'''{
    "error": "Retrieval of user labels has failed.",
    "description": "User with username 'notregd' could not be found."\n}'''
    assert 400 == r.status_code
    assert eb in r.data



