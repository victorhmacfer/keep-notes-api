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
    response = register_with(the_client, 'johndoe', 'abc123', 'johndoe@gmail.com')
    assert 200 == response.status_code
    assert b'{"message":"User registered successfully."}' in response.data
    response = login_with(the_client, 'johndoe', 'abc123')
    assert b'access_token' in response.data
    assert 200 == response.status_code

    yield the_client

    import os
    if os.path.exists('/tmp/test.db'):
        os.remove('/tmp/test.db')



# {
#   "user_id": "1",
#   "title": "",
#   "text": "",
#   "pinned": "False",
#   "archived": "False",
#   "color_name": "white",
#   "images": [
#     {
#       "url": "www.abc123.com"
#     },
#     {
#       "url": "www.blabla.com"
#     }
#   ],
#   "labels": [
#     "my-label"
#   ]
# }


# {"user_id":"1","title":"","text":"","pinned":"False","archived":"False","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}







def test_create_endpoint(client_with_logged_in_user):
    note_json_string = '''{"user_id":"1","title":"","text":"","pinned":"false","archived":"false","color_name":"white","images":[{"url":"www.abc123.com"},{"url":"www.blabla.com"}],"labels":["my-label"]}'''
    response = client_with_logged_in_user.post(
        'api/note/create',
        json=note_json_string
    )
    assert 200 == response.status_code

















# def test_create_endpoint(client_with_logged_in_user):
    
#     # most basic note
#     response = create_note(client_with_logged_in_user, user_id=1)
#     assert 200 == response.status_code
#     note = dict(
#         user_id=1, title='', text='', is_pinned=False,
#         is_archived=False, color_name='white', 
#         images=[{'url': 'www.abc123.com'}, {'url': 'www.blabla.com'}],
#         labels=[{'text': 'my-label'}]
#     )
#     json_note = b'''{
#   "message": "Note created."
#   "note": {
#     "user_id": "1",
#     "title": "",
#     "text": "",
#     "pinned": "False",
#     "archived": "False",
#     "color_name": "white",
#     "images": [
#       {
#         "url": "www.abc123.com"
#       },
#       {
#         "url": "www.blabla.com"
#       }
#     ],
#     "labels": [
#       {
#         "text": "my-label"
#       },
#     ],
#   }
# }'''
#     assert json_note in response.data




# def create_note(client, user_id, title='', text='',is_pinned=False,
#     is_archived=False, color_name='white'):

#     endpoint = 'api/note/create'

#     the_note = Note(user_id=user_id, title=title, text=text, is_pinned=is_pinned, is_archived=is_archived, color_name=color_name)
#     the_note.images.append(Image(url='www.abc123.com', note_id=the_note.id))
#     the_note.images.append(Image(url='www.blabla.com', note_id=the_note.id))
    

#     print(the_note.images)

#     return client.post(endpoint, json=the_note.to_dict())

