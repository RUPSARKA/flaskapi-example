import unittest, json
from .. import create_app
from app.models import db, User, BlogPost
from app.config import config_dict

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

    def create_user(self):
        data = {
            "name": "testuser",
            "email": "testuser@company.com",
            "password": "password",
            "address": "testaddress",
            "phone": "XXXXXXXXXX"
        }
        new_user_response = self.client.post('/users', json=data)
        return

    def log_in(self):
        data = {
            "email": "testuser@company.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=data)
        jsondata = json.loads(response.text)
        headers = {
            "Authorization": f"Bearer {jsondata['access_token']}"
        }
        return headers

    def test_get_create_blogpost(self):
        self.create_user()
        headers = self.log_in()
        data = {
            "title": "Testing",
            "body": "Testing purpose"
        }
        post_response = self.client.post('/blog_posts/users/', json=data, headers=headers)
        get_response = self.client.get('/blog_posts/users/', headers=headers)

        current_user = User.query.filter_by(email='testuser@company.com').first()
        blog_post = BlogPost.query.filter_by(user_id=current_user.id).first()

        assert post_response.status_code == 201
        assert get_response.status_code == 200
        assert blog_post.title == data.get("title") == get_response.json["title"]
        assert blog_post.body == data.get("body") == get_response.json["body"]

    def test_get_update_delete_one_blogpost(self):
        self.create_user()
        headers = self.log_in()

        # Test: Get a blog post by id
        data = {
            "title": "Testing",
            "body": "Testing purpose"
        }

        post_response = self.client.post('/blog_posts/users/', json=data, headers=headers)
        blogpost_id = post_response.json["id"]
        get_response = self.client.get(f'/blog_posts/{blogpost_id}', headers=headers)

        current_user = User.query.filter_by(email='testuser@company.com').first()
        blog_post = BlogPost.query.filter_by(user_id=current_user.id).first()

        assert get_response.status_code == 200
        assert blog_post.title == data.get("title") == get_response.json["title"]
        assert blog_post.body == data.get("body") == get_response.json["body"]

        # Test: Update a blog post by id
        new_data = {
            "title": "Testing Updated",
            "body": "Let's update testing purpose"
        }
        patch_response = self.client.patch(f'/blog_posts/{blogpost_id}', json=new_data, headers=headers)

        assert patch_response.status_code == 200
        assert blog_post.title == new_data.get("title") == patch_response.json["title"]
        assert blog_post.body == new_data.get("body") == patch_response.json["body"]

        # Test: Delete a blog post by id
        delete_response = self.client.delete(f'/blog_posts/{blogpost_id}', headers=headers)

        assert delete_response.status_code == 200