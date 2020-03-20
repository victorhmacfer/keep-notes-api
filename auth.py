
from flask import Blueprint, request, jsonify
from models.user import User
from flask_jwt_extended import create_access_token

from app import db

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
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

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

    return {'message': 'User registered successfully.'}, 200



@auth.route('/login', methods=['POST'])
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

    if user.verify_password(password) == False:
        return {'message': 'Wrong password.'}, 400
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


