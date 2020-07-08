from flask import session, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from project1.models import Book, User, BookRating
from project1 import app, db, bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from flask_login import login_user, current_user, logout_user

@app.route("/")
def index():
    return render_template("landing.html")


def bookRatingsAverage(book):
    # (BookRating.query.with_entities(func.avg(BookRating.rating).label('average')).filter(BookRating.book_id == book.id)[0][0])
    return db.session.query(func.avg(BookRating.rating).label('average')).filter(BookRating.book_id == book.id)[0][0]

def bookRatingsTotal(book):
    # (BookRating.query.with_entities(func.avg(BookRating.rating).label('average')).filter(BookRating.book_id == book.id)[0][0])
    return BookRating.query.filter(BookRating.book_id == book.id).count()
"""
@app.context_processor
def context_processor():
    return dict(bookRatingsAverage=bookRatingsAverage, bookRatingsTotal=bookRatingsTotal)
"""

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/book_reviews")
def mainBookPage():
    books = Book.query.all()
    return render_template("book_main.html", books=books, bookRatingsAverage=bookRatingsAverage, bookRatingsTotal=bookRatingsTotal)

@app.route("/book/add", methods=["POST"])
def addBook():
    title = request.form.get("title")
    author = request.form.get("author")
    same_book = Book.query.filter_by(author=author).filter_by(title=title)
    if same_book.count() >= 1:
        pass
    else:
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()

    return redirect(url_for('mainBookPage'))



@app.route("/book/<string:book_id>/rating", methods=["POST"])
def addRating(book_id):
    rating = request.form.get("rating")
    book = Book.query.get(book_id)
    new_rating = BookRating(book=book, user_id=current_user.id, rating=rating)
    db.session.add(new_rating)
    db.session.commit()

    return redirect("/book_reviews/{}".format(book_id))

@app.route("/book_reviews/<string:book_id>")
def bookPage(book_id):

    book = Book.query.get(book_id)
    book_ratings = BookRating.query.filter_by(book=book)
    ratings_count = book_ratings.count()
    ratings_average = db.session.query(func.avg(BookRating.rating)).filter(BookRating.book == book).scalar()

    user_rating = None
    if current_user.is_authenticated:
        user_rating_query = book_ratings.filter_by(user=current_user)
        if user_rating_query.count() == 1:
            user_rating = user_rating_query.first().rating

    return render_template("book_page.html", book=book, ratings_count=ratings_count, ratings_average=ratings_average, user_rating=user_rating)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/signup", methods=["POST"])
def signup():
    username=request.form.get("username")
    password=bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(username=username, password=password)

    # add the new user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    except IntegrityError:
        return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    username=request.form.get("username")
    password=request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user, remember=True)
        return redirect(url_for('home'))
    else:
        return render_template("landing.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
