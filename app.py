from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager


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

    from note import note as note_bp
    app.register_blueprint(note_bp, url_prefix='/api/note')



    # FIXME: this is for debugging purposes.. remove later
    from models.user import User
    @app.route('/api/users', methods=['GET'])
    def users():
        all_users = User.query.all()
        user_dicts = [u.to_dict() for u in all_users]
        return jsonify(user_dicts)

    
     # FIXME: this is for debugging purposes.. remove later
    from models.note import Note
    @app.route('/api/notes', methods=['GET'])
    def notes():
        all_notes = Note.query.all()
        note_dicts = [n.to_dict() for n in all_notes]
        return jsonify(note_dicts)


    return app