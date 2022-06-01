from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password_hash = db.Column(db.Text(), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    posts = db.relationship("BlogPost", cascade="all, delete", backref="parent")

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body = db.Column(db.String())
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.get_or_404(user_id)