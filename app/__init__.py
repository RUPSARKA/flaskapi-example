from app.config import config_dict
from datetime import datetime
from flask import Flask
from flask_migrate import Migrate
from .models import db
from flask_restx import Api
from app.routers.users import user_namespace
from app.routers.blog_posts import blogpost_namespace
from app.routers.auth import auth_namespace
from flask_jwt_extended import JWTManager

# app
def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    now = datetime.now()

    authorizations = {
            'api_key': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
        }
    }

    api = Api(
        app, doc='/',
        authorizations=authorizations, security='api_key'
    )

    api.add_namespace(user_namespace)
    api.add_namespace(blogpost_namespace)
    api.add_namespace(auth_namespace)
    return app