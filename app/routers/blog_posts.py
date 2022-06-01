from flask_restx import Namespace, Resource, fields, reqparse, marshal
from flask import request
from app.models import User, BlogPost, db
from datetime import datetime
from data_structures import binary_search_tree, custom_queue, hash_table, stack
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx.fields import Nested
from sqlalchemy import desc

class NestedFields(Nested):

    def __init__(self, model, **kwargs):
        super().__init__(model=model, **kwargs)

    def output(self, key, obj, ordered=False):
        if obj is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default

        # directly marshal with obj instead of obj.key or obj.attribute
        return marshal(obj, self.nested, skip_none=self.skip_none, ordered=ordered)

blogpost_namespace = Namespace('Blog Post', description="Namespace for Blog Post", path="/")

parser = reqparse.RequestParser()
parser.add_argument('Limit', type=str, help='limit', location='headers')
parser.add_argument('Search', type=str, help='search', location='headers')

new_parser = reqparse.RequestParser()
new_parser.add_argument('Limit', type=str, help='limit', location='headers')

new_blogpost_model = blogpost_namespace.model(
    'New BlogPost', {
        'title': fields.String(required=True, description="Title"),
        'body': fields.String(required=True, description="Body")
    }
)

user_model = blogpost_namespace.model(
    'User_Response', {
        'id': fields.Integer(),
        'name': fields.String(required=True, description="A username"),
        'email': fields.String(required=True, description="An email"),
        'address': fields.String(required=True, description="Address"),
        'phone': fields.String(required=True, description="Phone Number")
    }
)

blogpost_model = blogpost_namespace.model(
    'BlogPostResponse', {
        'id': fields.Integer(),
        'title': fields.String(required=True, description="Title"),
        'body': fields.String(required=True, description="Body"),
        'date': fields.DateTime(dt_format='rfc822', description="Date"),
        'user_id': fields.Integer(),
        'message': fields.String
    }
)

blogpost_detailed_model = blogpost_namespace.model(
    'BlogPost', {
        'post_id': fields.Integer(),
        'title': fields.String(required=True, description="Title"),
        'body': fields.String(required=True, description="Body"),
        'date': fields.DateTime(dt_format='rfc822', description="Date"),
        'user': NestedFields(user_model, skip_none=True)
    }
)

@blogpost_namespace.route('/blog_posts/bulkFetch')
class GetBlogPost(Resource):

    @blogpost_namespace.expect(parser)
    @blogpost_namespace.marshal_with(blogpost_detailed_model)
    @jwt_required()
    def get(self):
        """Get all blog posts"""
        args = parser.parse_args()
        limit = args['Limit']
        search = args['Search']
        if not search:
            search = ''

        blog_posts = BlogPost.query.join(User, User.id == BlogPost.user_id).\
            add_columns(BlogPost.id.label('post_id'), BlogPost.title, BlogPost.body, BlogPost.date, User.id, User.name, User.email, User.address, User.phone).\
            filter(BlogPost.title.contains(search)).order_by(desc(BlogPost.id)).limit(limit).all()

        return blog_posts

@blogpost_namespace.route('/blog_posts/bulkRemove', endpoint='blog_posts')
class DeleteBlogPost(Resource):

    @blogpost_namespace.expect(new_parser)
    @jwt_required()
    def delete(self):
        """Delete last 'N' blog posts (By default, delete last 10 blog posts)."""
        args = new_parser.parse_args()
        limit = int(args['Limit'])
        if not limit:
            limit = int(10)

        blog_posts = BlogPost.query.all()

        s = stack.Stack()
        for post in blog_posts:
            s.push(post)

        for _ in range(limit):
            post_to_delete = s.pop()
            print(post_to_delete.data)
            db.session.delete(post_to_delete.data)
            db.session.commit()

        return {"message": f"Last {limit} blog post deleted"}, HTTPStatus.OK

@blogpost_namespace.route('/blog_posts/users/')
class GetCreateBlogPost(Resource):

    @blogpost_namespace.marshal_with(blogpost_model, skip_none=True)
    @jwt_required()
    def get(self):
        """Get user specific blog posts"""
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()
        blog_posts = BlogPost.query.filter_by(user_id=current_user.id).first()

        if not blog_posts:
            return {"message": "Blog Post not found"}, HTTPStatus.NOT_FOUND
        return blog_posts, HTTPStatus.OK

    @blogpost_namespace.expect(new_blogpost_model)
    @blogpost_namespace.marshal_with(blogpost_model, skip_none=True)
    @jwt_required()
    def post(self):
        """Post a blog post"""
        data = request.get_json()
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        if not current_user:
            return {'message': "User doesn't exist"}

        ht = hash_table.HashTable(10)
        ht.add_key_value("title", data["title"])
        ht.add_key_value("body", data["body"])
        ht.add_key_value("date", datetime.now())
        ht.add_key_value("user_id", current_user.id)

        new_blog_post = BlogPost(
            title=ht.get_value("title"),
            body=ht.get_value("body"),
            date=ht.get_value("date"),
            user_id=ht.get_value("user_id")
        )

        db.session.add(new_blog_post)
        db.session.commit()
        return new_blog_post, HTTPStatus.CREATED

@blogpost_namespace.route('/blog_posts/<int:blog_post_id>')
class GetUpdateDeleteOneBlogPost(Resource):

    @blogpost_namespace.marshal_with(blogpost_model, skip_none=True)
    @jwt_required()
    def get(self, blog_post_id):
        """Get a blog post by id"""
        blog_posts = BlogPost.query.all()

        treemap = binary_search_tree.TreeMap()
        for post in blog_posts:
            treemap[post.id] = binary_search_tree.Blogpost(post.id, post.title, post.body, post.date, post.user_id)
        post = treemap.search(blog_post_id)

        if not post:
            return {"message": "post not found"}, HTTPStatus.NOT_FOUND
        return post.value, HTTPStatus.OK

    @blogpost_namespace.expect(new_blogpost_model)
    @blogpost_namespace.marshal_with(blogpost_model, skip_none=True)
    @jwt_required()
    def patch(self, blog_post_id):
        """Update a blog post by id"""
        data = request.get_json()

        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        blog_posts = BlogPost.query.all()
        treemap = binary_search_tree.TreeMap()
        for post in blog_posts:
            treemap[post.id] = binary_search_tree.Blogpost(post.id, post.title, post.body, post.date, post.user_id)
        post_found = treemap.search(blog_post_id)
        if not post_found:
            return {"message": "BlogPost not found"}

        post_found = post_found.value
        if post_found.user_id != current_user.id:
            return {"message": "You are not authorized to update this blog!!!"}
        post_found = BlogPost.query.filter_by(user_id=current_user.id).first()
        post_found.title = data["title"]
        post_found.body = data["body"]
        db.session.commit()

        return post_found


    @blogpost_namespace.marshal_with(blogpost_model, skip_none=True)
    @jwt_required()
    def delete(self, blog_post_id):
        """Delete a blog post by id"""
        email = get_jwt_identity()
        current_user = User.query.filter_by(email=email).first()

        blog_posts = BlogPost.query.all()

        treemap = binary_search_tree.TreeMap()
        for post in blog_posts:
            treemap[post.id] = binary_search_tree.Blogpost(post.id, post.title, post.body, post.date, post.user_id)
        post_found = treemap.search(blog_post_id)

        if not post_found:
            return {"message": "post not found"}, HTTPStatus.NOT_FOUND
        post_found = post_found.value
        if post_found.user_id != current_user.id:
            return {"message": "You are not authorized to delete this blog!!!"}
        post = BlogPost.query.filter_by(user_id=current_user.id).first()
        db.session.delete(post)
        db.session.commit()
        return {'message': f'Successfully deleted post having id :{blog_post_id}'}, HTTPStatus.OK

@blogpost_namespace.route('/blog_posts/numeric_body', doc=False)
class GetNumericBlogPostBodies(Resource):

    @blogpost_namespace.marshal_with(blogpost_model)
    def get(self):
        blog_posts = BlogPost.query.all()
        q = custom_queue.Queue()

        for post in blog_posts:
            q.enqueue(post)

        return_list = []

        for _ in range(len(blog_posts)):
            post = q.dequeue()
            numeric_body = 0
            for char in post.data.body:
                numeric_body += ord(char)

            post.data.body = numeric_body
            return_list.append(
                {
                    "id": post.data.id,
                    "title": post.data.title,
                    "body": post.data.body,
                    "date": post.data.date,
                    "user_id": post.data.user_id
                }
            )
        return return_list, HTTPStatus.OK