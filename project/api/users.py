from flask import Blueprint, request
from flask_restx import Resource, Api, fields

from project import db
from project.api.models import User
import re
import logging
users_blueprint = Blueprint('users', __name__)
api = Api(users_blueprint)

user = api.model('User', {
    'id': fields.Integer(readOnly=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'created_date': fields.DateTime
})


class UsersList(Resource):
    def is_valid_email(self, email: str) -> bool:
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def is_valid_request(self, request_json: str) -> bool:
        if request_json is None:
            return False

        has_required_fields = 'username' in request_json and 'email' in request_json
        return has_required_fields and self.is_valid_email(request_json['email'])

    @api.marshal_with(user)
    def get(self):
        return User.query.all(), 200

    @api.expect(user, validate=True)
    def post(self):
        """ @api.expect(user) validates the post input """
        post_data = request.get_json()

        logging.info(f'received request user: {post_data}')
        # input validation

        if not self.is_valid_request(post_data):
            response_object = {
                'message': 'Input payload validation failed'
            }
            return response_object, 400

        username = post_data.get('username')
        email = post_data.get('email')

        # check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            response_object = {'message': 'Sorry. That email already exists.'}
            return response_object, 400

        db.session.add(User(username=username, email=email))
        db.session.commit()
        response_object = {
            'message': f'{email} was added!'
        }
        return response_object, 201


class Users(Resource):
    @api.marshal_with(user)
    def get(self, user_id):
        """ @api.marshal_with(user) serializes the user model into json """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            api.abort(404, f'User {user_id} does not exist')

        return user, 200


api.add_resource(UsersList, '/users')
api.add_resource(Users, '/users/<int:user_id>')
