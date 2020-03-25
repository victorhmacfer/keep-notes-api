import pytest

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db

from models.user import User
from models.note import Note, Label
from models.image import Image

from test_auth_endpoints import register_with, login_with


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app


@pytest.fixture
def client_with_logged_in_user(app):
    the_client = app.test_client()
    response = register_with(the_client, 'johndoe',
                             'abc123', 'johndoe@gmail.com')
    assert 200 == response.status_code
    assert b'{"message":"User registered successfully."}' in response.data
    response = login_with(the_client, 'johndoe', 'abc123')
    assert b'access_token' in response.data
    assert 200 == response.status_code

    yield the_client
    delete_test_db()


def delete_test_db():
    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')


# {"user_id":"1","title":"","text":"","pinned":"False","archived":"False","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}


def test_create_note(client_with_logged_in_user):
    # create note for user responds json of note & 200 status
    note_json_string = '''{"user_id":"1","title":"","text":"","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
    response = client_with_logged_in_user.post(
        'api/notes',
        json=note_json_string
    )
    assert 201 == response.status_code
    assert b'''note:{"id":"1","title":"","text":"","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data

    #



# FIXME: repeats code for creating note, therefore coupled to it.
def test_get_all_notes(client_with_logged_in_user):
    # get all notes
    note_json_string = '''{"user_id":"1","title":"","text":"","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
    response = client_with_logged_in_user.post(
        'api/notes',
        json=note_json_string
    )
    note_json_string = '''{"user_id":"1","title":"second note","text":"this is a note","pinned":"true","archived":"false","color_name":"red","images":[],"labels":["my-label"]}'''
    response = client_with_logged_in_user.post(
        'api/notes',
        json=note_json_string
    )
    response = client_with_logged_in_user.get('api/notes')
    assert 200 == response.status_code
    assert b'''{"id":"1","title":"","text":"","pinned":"false","archived":"false","user_id":"1","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}''' in response.data
    assert b'''{"id":"2","title":"second note","text":"this is a note","pinned":"true","archived":"false","user_id":"1","color_name":"red","images":[],"labels":["my-label"]}''' in response.data

