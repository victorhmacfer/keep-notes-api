
from flask import Blueprint, request, jsonify, Response, make_response
from models.user import User
from flask_jwt_extended import create_access_token
from app import db


from utils.json import make_json_response

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    except KeyError:
        resp_dict = {'error': 'Registration Failed.',
            'description': 'Form filled incorrectly. Missing field.'}
        return make_json_response(resp_dict, 400)

    username_is_taken = User.find_by_username(username) is not None
    if username_is_taken:
        resp_dict = {'error': 'Registration Failed.',
            'description': f'The username \'{username}\' is already in use.'}
        return make_json_response(resp_dict, 400)

    email_is_taken = User.find_by_email(email) is not None
    if email_is_taken:
        resp_dict = {'error': 'Registration Failed.',
            'description': f'The email \'{email}\' is already in use.'}
        return make_json_response(resp_dict, 400)

    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    resp_dict = {'created_user': {'username': username, 'email': email}}
    return make_json_response(resp_dict, 201)


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

