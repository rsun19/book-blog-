from datetime import datetime
from bookblog import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    image_file = db.Column(db.String, nullable=False, default = 'cat.jpg')
    comments = db.relationship('Comment', backref='author', lazy = True)
    posts = db.relationship('Post', backref='author', lazy = True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default = datetime.utcnow())
    content = db.Column(db.Text, nullable=False)
    comment_url = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def serializing(self):
        return {
            'id': self.id,
            'title': self.title,
            "content": self.content,
            "comment_url": self.comment_url,
            "user_id": self.user_id
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String, nullable=False)
    rating = db.Column(db.String(100), nullable=False)
    rating_int = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    content_before = db.Column(db.Text, nullable=False)
    content_after = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def serializing(self):
        return {
            'id': self.id,
            'title': self.title,
            'author_name': self.author_name,
            'rating': self.rating,
            "rating_int": self.rating_int,
            "content_before": self.content_before,
            "content_after": self.content_after,
            "user_id": self.user_id
        }