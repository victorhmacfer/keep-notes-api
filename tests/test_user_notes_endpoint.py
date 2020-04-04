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




# {"user_id":"1","title":"","text":"","pinned":"False","archived":"False","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}



# def test_create_note(client_with_logged_in_user):
#     # create note for user responds json of note & 201 status
#     note_json_string = '''{"user_id":"1","title":"","text":"","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
#     response = client_with_logged_in_user.post(
#         'api/u/johndoe/notes',
#         json=note_json_string
#     )
#     assert 201 == response.status_code
#     assert b'''note:{"id":"1","title":"","text":"","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data

#     # creating another note for the same user
#     note_json_string = '''{"user_id":"1","title":"second note","text":"bla","pinned":"true","archived":"false","color_name":"red","images":[{"url":"www.abc123.com"}],"labels":[]}'''
#     response = client_with_logged_in_user.post(
#         'api/notes',
#         json=note_json_string
#     )
#     assert 201 == response.status_code
#     assert b'''note:{"id":"2","title":"second note","text":"bla","pinned":"true","archived":"false","user_id":"1","color_name":"red","images":[{"url":"www.abc123.com"}],"labels":[]}''' in response.data





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












# def test_update_note(client_with_logged_in_user):
#     # note json with existing id.. change title and text
#     note_json_string = '''{"user_id":"1","title":"initial title","text":"first version","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
#     response = client_with_logged_in_user.post(
#         'api/notes',
#         json=note_json_string
#     )
#     assert 201 == response.status_code
#     assert b'''note:{"id":"1","title":"initial title","text":"first version","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data

#     note_json_string = '''{"id":"1","title":"MODIFIED","text":"SECOND version"}'''
#     response = client_with_logged_in_user.patch(
#         'api/notes',
#         json=note_json_string
#     )
#     assert 200 == response.status_code
#     assert b'''note:{"id":"1","title":"MODIFIED","text":"SECOND version","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data


#     # note json with existing id.. remove one of the images

#     # note json with existing id.. include another label

#     # note json with NON EXISTING id.. return "note id not found"  400




# # FIXME: repeats code for creating note, therefore coupled to it.
# def test_get_all_notes(client_with_logged_in_user):
#     note_json_string = '''{"user_id":"1","title":"","text":"","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
#     response = client_with_logged_in_user.post(
#         'api/notes',
#         json=note_json_string
#     )
#     note_json_string = '''{"user_id":"1","title":"second note","text":"this is a note","pinned":"true","archived":"false","color_name":"red","images":[],"labels":["my-label"]}'''
#     response = client_with_logged_in_user.post(
#         'api/notes',
#         json=note_json_string
#     )
#     response = client_with_logged_in_user.get('api/notes')
#     assert 200 == response.status_code
#     assert b'''{"id":"1","title":"","text":"","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data
#     assert b'''{"id":"2","title":"second note","text":"this is a note","pinned":"true","archived":"false","user_id":"1","color_name":"red","images":[],"labels":["my-label"]}''' in response.data

