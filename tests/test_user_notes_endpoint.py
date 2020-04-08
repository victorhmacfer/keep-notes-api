import pytest

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db

from models.user import User
from models.note import Note, Label
from models.image import Image

from test_register_endpoint import register_with
from test_login_endpoint import login_with
from json import JSONDecoder


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client_with_logged_in_user(app):
    the_client = app.test_client()
    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    response = login_with(the_client, 'johndoe', 'abc123')
    assert b'access_token' in response.data
    assert 200 == response.status_code

    str_resp = response.data.decode('utf-8')
    resp_dict = JSONDecoder().decode(str_resp)
    access_token = resp_dict['access_token']

    yield the_client, access_token
    delete_test_db()


@pytest.fixture
def client_with_regd_user(app):
    the_client = app.test_client()
    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    yield the_client
    delete_test_db()



@pytest.fixture
def client_that_user_created_two_notes(app):
    the_client = app.test_client()
    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 201 == response.status_code

    FIRST_NOTE_JSON_STR = '''{
    "title": "my first note",
    "text": "first note text",
    "pinned": "false",
    "archived": "true",
    "color_name": "purple",
    "images": [
        {
            "url": "www.firstNoteImage.com"
        }
    ],
    "labels": []\n}'''
    r = the_client.post('/api/u/johndoe/notes', json=FIRST_NOTE_JSON_STR)
    assert 201 == r.status_code
    eb = b'''{
    "created_note": {
        "id": "1",
        "title": "my first note",
        "text": "first note text",
        "pinned": "false",
        "archived": "true",
        "user_id": "1",
        "color_name": "purple",
        "images": [
            {
                "url": "www.firstNoteImage.com"
            }
        ],
        "labels": []
    }\n}'''
    assert eb in r.data


    SECOND_NOTE_JSON_STR = '''{
    "title": "my SECOND note",
    "text": "second note text",
    "pinned": "true",
    "archived": "false",
    "color_name": "green",
    "images": [
        {
            "url": "www.blabla.com"
        },
        {
            "url": "www.google.com"
        }
    ],
    "labels": [
        {
            "text": "my-label"
        },
        {
            "text": "anotherLabel"
        }
    ]\n}'''
    r = the_client.post('/api/u/johndoe/notes', json=SECOND_NOTE_JSON_STR)
    assert 201 == r.status_code

    eb = b'''{
    "created_note": {
        "id": "2",
        "title": "my SECOND note",
        "text": "second note text",
        "pinned": "true",
        "archived": "false",
        "user_id": "1",
        "color_name": "green",
        "images": [
            {
                "url": "www.blabla.com"
            },
            {
                "url": "www.google.com"
            }
        ],
        "labels": [
            {
                "text": "anotherLabel"
            },
            {
                "text": "my-label"
            }
        ]
    }\n}'''
    
    assert eb in r.data


    yield the_client
    delete_test_db()


def delete_test_db():
    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')




@pytest.mark.skip(reason="For now I'm disabling jwt required.")
def test_get_all_user_notes_requires_jwt(client_with_logged_in_user):
    # dont use token on request... expecting a 401 error
    logged_in_client = client_with_logged_in_user[0]
    response = logged_in_client.get('/api/u/johndoe/notes')
    assert 401 == response.status_code
    assert b'''{
    "error": "Access Denied.",
    "description": "JWT access token not found in request."\n}''' in response.data



# FIXME: For now I'm implementing this endpoint with NO AUTH required.
def test_get_all_user_notes(client_that_user_created_two_notes):

    resp = client_that_user_created_two_notes.get('/api/u/johndoe/notes')

    EXPECTED_BODY = b'''{
    "username": "johndoe",
    "notes": [
        {
            "id": "1",
            "title": "my first note",
            "text": "first note text",
            "pinned": "false",
            "archived": "true",
            "user_id": "1",
            "color_name": "purple",
            "images": [
                {
                    "url": "www.firstNoteImage.com"
                }
            ],
            "labels": []
        },
        {
            "id": "2",
            "title": "my SECOND note",
            "text": "second note text",
            "pinned": "true",
            "archived": "false",
            "user_id": "1",
            "color_name": "green",
            "images": [
                {
                    "url": "www.blabla.com"
                },
                {
                    "url": "www.google.com"
                }
            ],
            "labels": [
                {
                    "text": "anotherLabel"
                },
                {
                    "text": "my-label"
                }
            ]
        }
    ]\n}'''

    assert EXPECTED_BODY in resp.data
    assert 200 == resp.status_code



@pytest.mark.skip(reason='success case already tested in fixture')
def test_create_note_for_user(client_with_regd_user):
    NOTE_JSON_STR = '''{
    "title": "my first note",
    "text": "this is a huge text oaisd joiasjd oiasoidjasoidoaisoi as",
    "pinned": "false",
    "archived": "true",
    "color_name": "purple",
    "images": [
        {
            "url": "www.blabla.com"
        }
    ],
    "labels": [
        {
            "text": "my-label"
        },
        {
            "text": "anotherLabel"
        }
    ]\n}'''

    r = client_with_regd_user.post('/api/u/johndoe/notes', json=NOTE_JSON_STR)
    assert 201 == r.status_code
    EXPECTED_BODY = b'''{
    "created_note": {
        "id": "1",
        "title": "my first note",
        "text": "this is a huge text oaisd joiasjd oiasoidjasoidoaisoi as",
        "pinned": "false",
        "archived": "true",
        "user_id": "1",
        "color_name": "purple",
        "images": [
            {
                "url": "www.blabla.com"
            }
        ],
        "labels": []
    }\n}'''
    assert EXPECTED_BODY in r.data



def test_create_note_for_nonexistent_user(client_with_regd_user):
    NOTE_JSON_STR = '''{
    "title": "my first note",
    "text": "this is a huge text oaisd joiasjd oiasoidjasoidoaisoi as",
    "pinned": "false",
    "archived": "true",
    "color_name": "purple",
    "images": [
        {
            "url": "www.blabla.com"
        }
    ],
    "labels": []\n}'''

    r = client_with_regd_user.post('/api/u/notregd/notes', json=NOTE_JSON_STR)
    assert 404 == r.status_code

    EXPECTED_BODY = b'''{
    "error": "Note creation has failed.",
    "description": "User with username 'notregd' could not be found."\n}'''

    assert EXPECTED_BODY in r.data


def test_create_note_with_bad_json_in_request(client_with_regd_user):
    # key 'pinned' is missing
    MISSING_KEY_NOTE_JSON = '''{
    "title": "my first note",
    "text": "this is a huge text oaisd joiasjd oiasoidjasoidoaisoi as",
    "archived": "true",
    "color_name": "purple",
    "images": [
        {
            "url": "www.blabla.com"
        }
    ],
    "labels": []\n}'''
    r = client_with_regd_user.post(
        '/api/u/johndoe/notes', 
        json=MISSING_KEY_NOTE_JSON
    )
    assert 400 == r.status_code
    EXPECTED_BODY = b'''{
    "error": "Note creation has failed.",
    "description": "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'color_name', 'images', 'labels'."\n}'''
    assert EXPECTED_BODY in r.data


    INVALID_KEY_NOTE_JSON = '''{
    "title": "my first note",
    "text": "this is a huge text oaisd joiasjd oiasoidjasoidoaisoi as",
    "pinned": "false",
    "invalid_key": "3",
    "archived": "true",
    "color_name": "purple",
    "images": [
        {
            "url": "www.blabla.com"
        }
    ],
    "labels": []\n}'''
    r = client_with_regd_user.post(
        '/api/u/johndoe/notes', 
        json=INVALID_KEY_NOTE_JSON
    )
    assert 400 == r.status_code
    EXPECTED_BODY = b'''{
    "error": "Note creation has failed.",
    "description": "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'color_name', 'images', 'labels'."\n}'''
    assert EXPECTED_BODY in r.data



def test_update_note(client_that_user_created_two_notes):
    FIRST_UPDATE_JSON = '''{
    "title": "first note IS UPDATED",
    "text": "tiny text",
    "pinned": "false",
    "archived": "true",
    "user_id": "1",
    "color_name": "purple",
    "images": [],
    "labels": [
        {
            "text": "first-note-label"
        }
    ]\n}'''

    r = client_that_user_created_two_notes.put(
        '/api/u/johndoe/notes/1',
        json=FIRST_UPDATE_JSON
    )
    assert 200 == r.status_code
    eb = b'''{
    "updated_note": {
        "id": "1",
        "title": "first note IS UPDATED",
        "text": "tiny text",
        "pinned": "false",
        "archived": "true",
        "user_id": "1",
        "color_name": "purple",
        "images": [],
        "labels": [
            {
                "text": "first-note-label"
            }
        ]
    }\n}'''
    assert eb in r.data


    SECOND_UPDATE_JSON = '''{
    "title": "second note UPDATED",
    "text": "second note tiny text",
    "pinned": "true",
    "archived": "false",
    "user_id": "1",
    "color_name": "red",
    "images": [
        {
            "url": "www.abc123.com"
        }
    ],
    "labels": []\n}'''

    r = client_that_user_created_two_notes.put(
        '/api/u/johndoe/notes/2',
        json=SECOND_UPDATE_JSON
    )
    assert 200 == r.status_code
    eb = b'''{
    "updated_note": {
        "id": "2",
        "title": "second note UPDATED",
        "text": "second note tiny text",
        "pinned": "true",
        "archived": "false",
        "user_id": "1",
        "color_name": "red",
        "images": [
            {
                "url": "www.abc123.com"
            }
        ],
        "labels": []
    }\n}'''
    assert eb in r.data



def test_update_note_for_nonexistent_user(client_that_user_created_two_notes):
    r = client_that_user_created_two_notes.put(
        'api/u/notregduser/notes/37',
        json='whatever'
    )
    assert 404 == r.status_code
    expected_body = b'''{
    "error": "Note update has failed.",
    "description": "User with username 'notregduser' could not be found."\n}'''
    assert expected_body in r.data



def test_update_note_with_bad_json_in_req(client_that_user_created_two_notes):
    # missing key title
    MISSING_KEY_NOTE_JSON = '''{
    "text": "second note tiny text",
    "pinned": "true",
    "archived": "false",
    "user_id": "1",
    "color_name": "red",
    "images": [
        {
            "url": "www.abc123.com"
        }
    ],
    "labels": []\n}'''

    r = client_that_user_created_two_notes.put(
        'api/u/johndoe/notes/2',
        json=MISSING_KEY_NOTE_JSON
    )
    assert 400 == r.status_code
    eb = b'''{
    "error": "Note update has failed.",
    "description": "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'user_id', 'color_name', 'images', 'labels'."\n}'''
    assert eb in r.data

    INVALID_KEY_NOTE_JSON = '''{
    "INVALID_KEY": "blabla",
    "title": "whatever"
    "text": "second note tiny text",
    "pinned": "true",
    "archived": "false",
    "user_id": "1",
    "color_name": "red",
    "images": [
        {
            "url": "www.abc123.com"
        }
    ],
    "labels": []\n}'''
    assert 400 == r.status_code
    assert eb in r.data



def test_delete_note(client_that_user_created_two_notes):
    r = client_that_user_created_two_notes.delete('api/u/johndoe/notes/2')

    assert 200 == r.status_code
    EXPECTED_BODY = b'''{
    "deleted_note": {
        "id": "2",
        "title": "my SECOND note",
        "text": "second note text",
        "pinned": "true",
        "archived": "false",
        "user_id": "1",
        "color_name": "green",
        "images": [
            {
                "url": "www.blabla.com"
            },
            {
                "url": "www.google.com"
            }
        ],
        "labels": [
            {
                "text": "anotherLabel"
            },
            {
                "text": "my-label"
            }
        ]
    }\n}'''
    assert EXPECTED_BODY in r.data

    r = client_that_user_created_two_notes.get('api/u/johndoe/notes')
    assert 200 == r.status_code
    eb = b'''{
    "username": "johndoe",
    "notes": [
        {
            "id": "1",
            "title": "my first note",
            "text": "first note text",
            "pinned": "false",
            "archived": "true",
            "user_id": "1",
            "color_name": "purple",
            "images": [
                {
                    "url": "www.firstNoteImage.com"
                }
            ],
            "labels": []
        }
    ]\n}'''
    assert eb in r.data


def test_delete_note_for_nonexistent_user(client_that_user_created_two_notes):
    r = client_that_user_created_two_notes.delete('api/u/notregd/notes/1')
    assert 400 == r.status_code
    expected_body = b'''{
    "error": "Note deletion has failed.",
    "description": "User with username 'notregd' could not be found."\n}'''
    assert expected_body in r.data



def test_delete_nonexistent_note(client_that_user_created_two_notes):
    r = client_that_user_created_two_notes.delete('api/u/johndoe/notes/47')
    assert 404 == r.status_code
    expected_body = b'''{
    "error": "Note deletion has failed.",
    "description": "Note with id '47' could not be found."\n}'''
    assert expected_body in r.data

