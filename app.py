from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager, jwt_required

from utils.json import make_json_response


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
    def _is_invalid_note_dict(note_dict):
        if (len(note_dict.keys()) != 7) or (set(note_dict.keys()) != {
            'title', 'text', 'pinned','archived', 
            'color_name', 'images', 'labels'}):

            return True
        return False


    # def _patch_dict(json_dict):
    #     pd = {}

    #     if 'id' not in json_dict.keys():
    #         raise KeyError
    #     the_id = int(json_dict['id'])
    #     pd['id'] = the_id

    #     if 'title' in json_dict.keys():
    #         pd['title'] = json_dict['title']
    #     if 'text' in json_dict.keys():
    #         pd['text'] = json_dict['text']

    #     if 'pinned' in json_dict.keys():
    #         if json_dict['pinned'] not in ['true', 'false']:
    #             raise ValueError
    #         pd['pinned'] = True if json_dict['pinned'] == 'true' else False

    #     if 'archived' in json_dict.keys():
    #         if json_dict['archived'] not in ['true', 'false']:
    #             raise ValueError
    #         pd['archived'] = True if json_dict['archived'] == 'true' else False

    #     if 'color_name' in json_dict.keys():
    #         pd['color_name'] = json_dict['color_name']

    #     if 'images' in json_dict.keys():
    #         note_images = []
    #         for i in json_dict['images']:
    #             img = Image(url=i['url'], note_id=the_id)
    #             note_images.append(img)
    #         pd['images'] = note_images

    #     if 'labels' in json_dict.keys():
    #         note_labels = []
    #         for label_text in json_dict['labels']:
    #             label_in_db = Label.find_by_text(label_text)
    #             if label_in_db is not None:
    #                 the_label = label_in_db
    #             else:
    #                 the_label = Label(text=label_text)
    #             note_labels.append(the_label)
    #         pd['labels'] = note_labels

    #     return pd




    # @app.route('/api/notes', methods=['PATCH'])
    # def update_note():

    #     json_dict = request.json
    #     if isinstance(json_dict, str):
    #         json_dict = JSONDecoder().decode(json_dict)

    #     print(json_dict)
    #     print(type(json_dict))

    #     if not is_valid_note_json_dict(json_dict):
    #         return 'Malformed JSON string for updating note.', 400

    #     note_id = int(json_dict['id'])
    #     note_in_db = Note.query.filter_by(id=note_id).first()

    #     if note_in_db is None:
    #         return 'Note not found in database.', 400

    #     try:
    #         patch_dict = _patch_dict(json_dict)
    #     except (KeyError, ValueError):
    #         return 'Malformed JSON string for updating note.', 400

    #     for k in patch_dict.keys():
    #         setattr(note_in_db, k, patch_dict[k])

    #     db.session.commit()

    #     updated_note_dict = note_in_db.to_json_dict()
    #     json_response = 'note:' + \
    #         JSONEncoder(separators=(',', ':')).encode(updated_note_dict)

    #     return json_response, 200



    # def is_valid_note_json_dict(note_dict):
    #     # does not accept user_id since it should not be updated.
    #     accepted_keys = ['id', 'title', 'text', 'pinned', 'archived',
    #                      'color_name', 'images', 'labels']
    #     if 'id' not in note_dict.keys():
    #         return False

    #     for k in note_dict.keys():
    #         if k not in accepted_keys:
    #             return False

    #     return True

    

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
                'description': "User with username 'notregd' could not be found."
            }
            return make_json_response(rd, 404)

        note_dict = request.json
        if isinstance(note_dict, str):
            note_dict = JSONDecoder().decode(note_dict)

        # FIXME: decent JSON resp
        if _is_invalid_note_dict(note_dict):
            rd = {
                'error': 'Note creation has failed.', 
                'description': "Some of the keys are missing and/or an invalid key was sent. Required keys: 'title', 'text', 'pinned', 'archived', 'color_name', 'images', 'labels'."
            }
            return make_json_response(rd, 400)
        
        note_dict['user_id'] = the_user.id

        the_note = create_note_from_json_dict(note_dict)

        db.session.add(the_note)
        db.session.commit()

        inserted_note_dict = the_note.to_json_dict()
        resp_dict = {'created_note': inserted_note_dict}

        return make_json_response(resp_dict, 201)


    

 






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
