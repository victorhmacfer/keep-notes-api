from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager, jwt_required


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

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from models.note import Note, Label
    from models.image import Image
    from json import JSONDecoder, JSONEncoder

    # FIXME: A LOT OF HARDCODED STUFF HERE.. too coupled to Note class
    @app.route('/api/notes', methods=['POST'])
    def create_note():
        note_dict = request.json
        if isinstance(note_dict, str):
            note_dict = JSONDecoder().decode(note_dict)

        # check for existence of all necessary keys and only those.
        if _is_invalid_note_dict(note_dict):
            return 'Malformed JSON string. Some keys for Note are missing.', 400

        # check for invalid values (e.g., nonexistent user id, nonexistent label)

        the_note = create_note_from_json_dict(note_dict)

        db.session.add(the_note)
        db.session.commit()

        inserted_note_dict = the_note.to_json_dict()

        json_response = 'note:' + \
            JSONEncoder(separators=(',', ':')).encode(inserted_note_dict)

        return json_response, 201

    def _is_invalid_note_dict(note_dict):
        if (len(note_dict.keys()) != 8) or (set(note_dict.keys()) != {'title', 'text', 'pinned',
                                                                      'archived', 'user_id', 'color_name', 'images', 'labels'}):
            return True
        return False


    def _patch_dict(json_dict):
        pd = {}

        if 'id' not in json_dict.keys():
            raise KeyError
        the_id = int(json_dict['id'])
        pd['id'] = the_id

        if 'title' in json_dict.keys():
            pd['title'] = json_dict['title']
        if 'text' in json_dict.keys():
            pd['text'] = json_dict['text']

        if 'pinned' in json_dict.keys():
            if json_dict['pinned'] not in ['true', 'false']:
                raise ValueError
            pd['pinned'] = True if json_dict['pinned'] == 'true' else False

        if 'archived' in json_dict.keys():
            if json_dict['archived'] not in ['true', 'false']:
                raise ValueError
            pd['archived'] = True if json_dict['archived'] == 'true' else False

        if 'color_name' in json_dict.keys():
            pd['color_name'] = json_dict['color_name']

        if 'images' in json_dict.keys():
            note_images = []
            for i in json_dict['images']:
                img = Image(url=i['url'], note_id=the_id)
                note_images.append(img)
            pd['images'] = note_images

        if 'labels' in json_dict.keys():
            note_labels = []
            for label_text in json_dict['labels']:
                label_in_db = Label.find_by_text(label_text)
                if label_in_db is not None:
                    the_label = label_in_db
                else:
                    the_label = Label(text=label_text)
                note_labels.append(the_label)
            pd['labels'] = note_labels

        return pd


    def create_note_from_json_dict(json_dict):
        user_id = int(json_dict['user_id'])
        title = json_dict['title']
        text = json_dict['text']
        pinned = True if json_dict['pinned'] == 'true' else False
        archived = True if json_dict['archived'] == 'true' else False
        color_name = json_dict['color_name']

        the_note = Note(
            user_id=user_id,
            title=title,
            text=text,
            pinned=pinned,
            archived=archived,
            color_name=color_name)

        for i in json_dict['images']:
            img = Image(url=i['url'], note_id=the_note.id)
            the_note.images.append(img)

        for label_text in json_dict['labels']:
            label_in_db = Label.find_by_text(label_text)
            if label_in_db is not None:
                the_label = label_in_db
            else:
                the_label = Label(text=label_text)
            the_note.labels.append(the_label)

        return the_note


    @app.route('/api/notes', methods=['PATCH'])
    def update_note():

        json_dict = request.json
        if isinstance(json_dict, str):
            json_dict = JSONDecoder().decode(json_dict)

        print(json_dict)
        print(type(json_dict))

        if not is_valid_note_json_dict(json_dict):
            return 'Malformed JSON string for updating note.', 400

        note_id = int(json_dict['id'])
        note_in_db = Note.query.filter_by(id=note_id).first()

        if note_in_db is None:
            return 'Note not found in database.', 400

        try:
            patch_dict = _patch_dict(json_dict)
        except (KeyError, ValueError):
            return 'Malformed JSON string for updating note.', 400

        for k in patch_dict.keys():
            setattr(note_in_db, k, patch_dict[k])

        db.session.commit()

        updated_note_dict = note_in_db.to_json_dict()
        json_response = 'note:' + \
            JSONEncoder(separators=(',', ':')).encode(updated_note_dict)

        return json_response, 200


    def is_valid_note_json_dict(note_dict):
        # does not accept user_id since it should not be updated.
        accepted_keys = ['id', 'title', 'text', 'pinned', 'archived',
                         'color_name', 'images', 'labels']
        if 'id' not in note_dict.keys():
            return False

        for k in note_dict.keys():
            if k not in accepted_keys:
                return False

        return True



    # FIXME: this is for debugging purposes.. remove later
    from models.user import User
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
