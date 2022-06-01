import unittest
from .. import create_app
from app.models import db, User
from app.config import config_dict
from werkzeug.security import check_password_hash

class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(config=config_dict['test'])
        cls.client = cls.app.test_client()
        cls._ctx = cls.app.test_request_context()
        cls._ctx.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        db.session.begin(subtransactions=True)

    def tearDown(self):
        db.session.rollback()
        db.session.close()
        self._ctx.pop()

    def test_create_user(self):
        data = {
            "name": "testuser",
            "email": "testuser@company.com",
            "password": "password",
            "address": "testaddress",
            "phone": "XXXXXXXXXX"
        }
        response = self.client.post('/users', json=data)
        user = User.query.filter_by(email="testuser@company.com").first()

        assert response.status_code == 201
        assert user.name == "testuser"
        assert check_password_hash(user.password_hash, data.get('password'))
        assert user.address == "testaddress"
        assert user.phone == "XXXXXXXXXX"

    def test_user_login(self):
        data = {
            "name": "testuser",
            "email": "testuser@company.com",
            "password": "password",
            "address": "testaddress",
            "phone": "XXXXXXXXXX"
        }
        response = self.client.post('/users', json=data)

        data = {
            "email": "testuser@company.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 200