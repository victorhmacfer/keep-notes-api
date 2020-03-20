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
            {"url":"www.abc123.com"},
            {"url":"www.blabla.com"}
        ],
        "labels": ["my-label"]
    }
    the_note = Note.from_json_dict(json_dict)
    assert the_note.user_id == 1
    assert the_note.title == ''
    assert the_note.text == ''
    assert the_note.is_pinned == False
    assert the_note.is_archived == False
    assert the_note.color_name == 'white'
    assert the_note.images[0].url == 'www.abc123.com'
    assert the_note.images[1].url == 'www.blabla.com'
    assert the_note.labels[0].text == 'my-label'
