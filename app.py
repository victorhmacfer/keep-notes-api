from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager, jwt_required

from utils.json import make_json_response

import copy


db = SQLAlchemy()


def create_app(testing=False):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

    if testing:
        import os
        if os.path.exists('/tmp/test.db'):
            os.remove('/tmp/test.db')

    jwt = JWTManager(app)

    import models.user
    import models.color
    import models.image
    import models.note

    from models.user import User

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from models.note import Note, Label, create_note_from_json_dict
    from models.image import Image
    from json import JSONDecoder, JSONEncoder


    # FIXME: tightly coupled to Note !!!  hardcoded stuff
    def _is_invalid_note_creation_dict(note_dict):
        if (len(note_dict.keys()) != 7) or (set(note_dict.keys()) != {
            'title', 'text', 'pinned','archived', 
            'color_name', 'images', 'labels'}):

            return True
        return False


    # FIXME: tightly coupled to Note !!!  hardcoded stuff
    def _is_invalid_note_update_dict(note_dict):
        if (len(note_dict.keys()) != 8) or (set(note_dict.keys()) != {
            'title', 'text', 'pinned','archived', 'user_id',
            'color_name', 'images', 'labels'}):

            return True
        return False



    # def unauthorized_loader_callback(s):
    #     rd = {'error': 'Access Denied.', 
    #             'description': 'JWT access token not found in request.'}
    #     with app.app_context():
    #         resp = make_json_response(rd, 401)
    #     return resp


    @app.route('/api/u/<username>/notes', methods=['GET'])
    def get_all_user_notes(username):
        the_user = User.find_by_username(username)

        # FIXME: change this to decent JSON resp
        if the_user is None:
            return 'not found', 404

        user_notes = the_user.notes
        json_dict_notes = [n.to_json_dict() for n in user_notes]
        resp_dict = {'username': username, 'notes': json_dict_notes}

        return make_json_response(resp_dict, 200)


    @app.route('/api/u/<username>/notes', methods=['POST'])
    def create_note_for_user(username):
        the_user = User.find_by_username(username)

        if the_user is None:
            rd = {
                'error': 'Note creation has failed.', 
                'description': f"User with username '{username}' could not be found."
            }
            return make_json_response(rd, 400)

        note_dict = request.json
        if isinstance(note_dict, str):
            note_dict = JSONDecoder().decode(note_dict)

        if _is_invalid_note_creation_dict(note_dict):
            rd = {
                'error': 'Note creation has failed.', 
                'description': "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'color_name', 'images', 'labels'."
            }
            return make_json_response(rd, 400)
        
        note_dict['user_id'] = the_user.id

        the_note = create_note_from_json_dict(note_dict)

        # the problem is here !! this adding of the note makes it have
        # differently ordered labels SOMETIMES.. looks like random order
        db.session.add(the_note)
        db.session.commit()
        
        # solved it by making to_json_dict() have the label dicts ordered alphab
        inserted_note_dict = the_note.to_json_dict()
        resp_dict = {'created_note': inserted_note_dict}

        return make_json_response(resp_dict, 201)

    
        
    @app.route('/api/u/<username>/notes/<nid>', methods=['PUT'])
    def update_note(username, nid):
        the_user = User.find_by_username(username)
        int_nid = int(nid)

        if the_user is None:
            rd = {
                'error': 'Note update has failed.', 
                'description': f"User with username '{username}' could not be found."
            }
            return make_json_response(rd, 400)

        note_dict = request.json
        if isinstance(note_dict, str):
            note_dict = JSONDecoder().decode(note_dict)

        if _is_invalid_note_update_dict(note_dict):
            rd = {
                'error': 'Note update has failed.', 
                'description': "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'user_id', 'color_name', 'images', 'labels'."
            }
            return make_json_response(rd, 400)

        new_note = create_note_from_json_dict(note_dict)

        previous_note = Note.query.filter_by(id=int_nid).first()

        if previous_note is not None:
            previous_note.title = new_note.title
            previous_note.text = new_note.text
            previous_note.pinned = new_note.pinned
            previous_note.archived = new_note.archived
            previous_note.user_id = new_note.user_id
            previous_note.color_name = new_note.color_name
            previous_note.images = new_note.images
            previous_note.labels = new_note.labels
            db.session.add(previous_note)
            db.session.commit()
            updated_note_dict = previous_note.to_json_dict()
        else:
            new_note.id = int_nid
            db.session.add(new_note)
            db.session.commit()
            updated_note_dict = new_note.to_json_dict()

        resp_dict = {'updated_note': updated_note_dict}

        return make_json_response(resp_dict, 200)



    @app.route('/api/u/<username>/notes/<nid>', methods=['DELETE'])
    def delete_note(username, nid):
        the_user = User.find_by_username(username)
        if the_user is None:
            rd = {
                'error': 'Note deletion has failed.', 
                'description': f"User with username '{username}' could not be found."
            }
            return make_json_response(rd, 400)
    
        int_nid = int(nid)
        the_note = Note.query.filter_by(id=int_nid).first()
        if the_note is None:
            rd = {
                'error': 'Note deletion has failed.', 
                'description': f"Note with id '{int_nid}' could not be found."
            }
            return make_json_response(rd, 404)

        db.session.delete(the_note)
        db.session.commit()

        deleted_note_dict = the_note.to_json_dict()
        resp_dict = {'deleted_note': deleted_note_dict}

        return make_json_response(resp_dict, 200)


    @app.route('/api/u/<username>/labels', methods=['POST'])
    def create_label(username):
        the_user = User.find_by_username(username)

        if the_user is None:
            rd = {
                'error': 'Label creation has failed.', 
                'description': f"User with username '{username}' could not be found."
            }
            return make_json_response(rd, 400)

        label_dict = request.json
        if isinstance(label_dict, str):
            label_dict = JSONDecoder().decode(label_dict)


        if 'text' not in label_dict.keys():
            rd = {
                'error': 'Label creation has failed.', 
                'description': "Malformed JSON in request. Required keys: 'text'."
            }
            return make_json_response(rd, 400)

        try:
            the_label = Label.from_json_dict(label_dict)
        except ValueError:
            rd = {
                'error': 'Label creation has failed.', 
                'description': "Value for 'text' key longer than 30 characters."
            }
            return make_json_response(rd, 400)
        
        the_label.user_id = the_user.id
        db.session.add(the_label)
        db.session.commit()

        inserted_label_dict = the_label.to_json_dict()
        resp_dict = {'created_label': inserted_label_dict}

        return make_json_response(resp_dict, 201)


    @app.route('/api/u/<username>/labels', methods=['GET'])
    def get_all_user_labels(username):
        the_user = User.find_by_username(username)
        

        if the_user is None:
            rd = {
                'error': 'Retrieval of user labels has failed.',
                'description': f"User with username '{username}' could not be found."
            }
            return make_json_response(rd, 400)
        
        uid = the_user.id
        user_labels = Label.find_by_user_id(uid)

        sorted_labels = sorted(user_labels, key=lambda label: label.text)
        json_dicts = [lab.to_json_dict() for lab in sorted_labels]

        resp_dict = {'username': username, 'labels': json_dicts}

        return make_json_response(resp_dict, 200)





    # FIXME: this is for debugging purposes.. remove later 
    @app.route('/api/users', methods=['GET'])
    def users():
        all_users = User.query.all()
        user_dicts = [u.to_dict() for u in all_users]
        return jsonify(user_dicts)



     # FIXME: this is for debugging purposes.. remove later
    @app.route('/api/notes', methods=['GET'])
    def notes():
        all_notes = Note.query.all()
        note_dicts = [n.to_json_dict() for n in all_notes]
        json_response = 'notes:' + \
            JSONEncoder(separators=(',', ':')).encode(note_dicts)
        return json_response, 200
    return app
