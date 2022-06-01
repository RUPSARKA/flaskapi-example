from flask_restx import Namespace, Resource, fields
from app.models import User, db
from http import HTTPStatus
from flask import request
from data_structures import linked_list
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

user_namespace = Namespace('User', description="Namespace for User", path='/')

signup_model = user_namespace.model(
    'User', {
        'name': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'password': fields.String(required=True, description="A password"),
        'address': fields.String(required=True, description="Address"),
        'phone': fields.String(required=True, description="Phone Number")
    }
)

user_model = user_namespace.model(
    'User_Response', {
        'id': fields.Integer(),
        'name': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'password_hash': fields.String(required=True, description="A password"),
        'address': fields.String(required=True, description="Address"),
        'phone': fields.String(required=True, description="Phone Number")
    }
)

@user_namespace.route('/users')
class CreateUser(Resource):

    @user_namespace.expect(signup_model)
    @user_namespace.marshal_with(user_model)
    def post(self):
        data = request.get_json()
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            address=data.get('address'),
            phone=data.get('phone')
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user, HTTPStatus.CREATED

@user_namespace.route('/users/descending_id')
class GetAllUserDescending(Resource):

    @user_namespace.marshal_with(user_model)
    def get(self):
        users = User.query.all()
        all_user_ll = linked_list.LinkedList()
        for user in users:
            all_user_ll.insert_beginning(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "address": user.address,
                    "phone": user.phone
                }
            )
        return (all_user_ll.to_list()), HTTPStatus.OK

@user_namespace.route('/users/ascending_id')
class GetAllUserAscending(Resource):

    @user_namespace.marshal_with(user_model)
    def get(self):
        users = User.query.all()
        all_user_ll = linked_list.LinkedList()
        for user in users:
            all_user_ll.insert_at_end(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "address": user.address,
                    "phone": user.phone
                }
            )
        return (all_user_ll.to_list()), HTTPStatus.OK

@user_namespace.route('/users/<int:user_id>')
class GetDeleteOneUser(Resource):

    @user_namespace.marshal_with(user_model)
    def get(self, user_id):
        users = User.query.all()
        all_user_ll = linked_list.LinkedList()
        for user in users:
            all_user_ll.insert_beginning(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "address": user.address,
                    "phone": user.phone
                }
            )
        user = all_user_ll.get_user_by_id(user_id)

        return user, HTTPStatus.OK

    @user_namespace.marshal_with(user_model)
    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()