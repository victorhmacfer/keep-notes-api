import pytest
from models.note import Note


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
