from project1 import db, login_manager
from flask_login import UserMixin
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000), unique=True)
    ratings = db.relationship('BookRating', backref='user', lazy=True)

    def __repr__(self):
        return("User: {}".format(self.username))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    title = db.Column(db.String(100))
    author = db.Column(db.String(1000))
    ratings = db.relationship('BookRating', backref='book', lazy=True)

    def __repr__(self):
        return("Book: {}".format(self.title))

class BookRating(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'),
        nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    rating = db.Column(db.Integer, default=0)


