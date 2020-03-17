from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
    jwt = JWTManager(app)

    from models.user import User
    import models.color 
    import models.image 
    import models.line 
    import models.note 
    import models.sub_line
    
    

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        try:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
        except KeyError:
            return {'message': 'Form filled incorrectly: Missing field.'}, 400
        else:
            username_is_taken = User.find_by_username(username) is not None
            if username_is_taken:
                return {'message': 'This username is already in use.'}, 400

            email_is_taken = User.find_by_email(email) is not None
            if email_is_taken:
                return {'message': 'This email is already in use.'}, 400

            # TODO: SHOULD NOT STORE PASSWORD.. hash it !
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()

        return {'message': 'User registered successfully.'}, 200


    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            username = request.form['username']
            password = request.form['password']
        except KeyError:
            return {'message': 'Form filled incorrectly: Missing field.'}, 400
        
        user = User.find_by_username(username)
        username_not_registered = user is None
        if username_not_registered:
            return {'message': 'No user registered with this username.'}, 400

        #  TODO: this should change to 
        if password != user.password:
            return {'message': 'Wrong password.'}, 400
        
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200




    @app.route('/api/users')
    def users():
        dict_users = [u.to_dict() for u in User.query.all()]
        return {'users': dict_users}, 200

    return app
