from random import randrange
from datetime import datetime
from faker import Faker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config_dict
from app.models import User, BlogPost
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

# app
app = Flask(__name__)

# config
app.config.from_object(config_dict['dev'])

db = SQLAlchemy(app)
now = datetime.now()

faker = Faker()

# create dummy users
for i in range(200):
    name = faker.name()
    address = faker.address()
    phone = faker.msisdn()
    email = f'{name.replace(" ", "_")}@email.com'
    password_hash = generate_password_hash(f'{name}@password123')
    new_user = User(name=name, address=address, phone=phone, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

# create dummy blog posts
for i in range(200):
    title = faker.sentence(5)
    body = faker.paragraph(190)
    date = faker.date_time()
    user_id = randrange(1, 200)

    new_blog_post = BlogPost(
        title=title, body=body, date=date, user_id=user_id
    )
    db.session.add(new_blog_post)
    db.session.commit()
