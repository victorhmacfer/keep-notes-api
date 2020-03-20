
from flask import Blueprint, request

from app import db

from models.note import Note

from json import JSONDecoder


note = Blueprint('note', __name__)


@note.route('/create', methods=['POST'])
def create():

    print(type(request.json))

    note_dict = request.json
    
    if isinstance(note_dict, str):
        note_dict = JSONDecoder().decode(note_dict)
        

    the_note = Note.from_json_dict(note_dict)

    db.session.add(the_note)
    db.session.commit()

    return 'Note created successfully', 200



        

