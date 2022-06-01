from flask_restx import Namespace, Resource, fields
from app.models import User
from http import HTTPStatus
from flask import request
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

auth_namespace = Namespace('Auth', description="Namespace for authentication", path='/')

login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description="A password")
    }
)

@auth_namespace.route('/auth/login')
class Login(Resource):

    @auth_namespace.expect(login_model)
    def post(self):
        """Generate a bearer token"""
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if (user is not None) and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.email)
            refresh_token = create_refresh_token(identity=user.email)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.OK

        raise BadRequest("Invalid User Credentials")


@auth_namespace.route('/auth/refresh', doc=False)
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        email = get_jwt_identity()

        access_token = create_access_token(identity=email)

        return {'access_token': access_token}, HTTPStatus.OK