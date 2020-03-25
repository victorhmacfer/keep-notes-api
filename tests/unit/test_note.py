import pytest
from models.note import Note


def test_creates_note_from_json_dict():
    json_dict = {
        "user_id": "1",
        "title": "",
        "text": "",
        "pinned": "False",
        "archived": "False",
        "color_name": "white",
        "images": [
            {"url": "www.abc123.com"},
            {"url": "www.blabla.com"}
        ],
        "labels": ["my-label"]
    }
    the_note = Note.from_json_dict(json_dict)
    assert the_note.user_id == 1
    assert the_note.title == ''
    assert the_note.text == ''
    assert the_note.pinned == False
    assert the_note.archived == False
    assert the_note.color_name == 'white'
    assert the_note.images[0].url == 'www.abc123.com'
    assert the_note.images[1].url == 'www.blabla.com'
    assert the_note.labels[0].text == 'my-label'


def test_creates_json_dict_from_note():

    the_note = Note(
        id=1, 
        title='xablau', 
        text='mytext', 
        pinned=True, 
        archived=False, 
        user_id=1, 
        color_name='red',
        images=[],
        labels=[]
        )

    the_dict = the_note.to_json_dict()
    assert the_dict['id'] == '1'
    assert the_dict['title'] == 'xablau'
    assert the_dict['text'] == 'mytext'
    assert the_dict['pinned'] == 'true'
    assert the_dict['archived'] == 'false'
    assert the_dict['user_id'] == '1'
    assert the_dict['color_name'] == 'red'
