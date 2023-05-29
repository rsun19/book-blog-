from bookblog.models import User, Comment, Post
from flask import render_template, url_for, abort, redirect, request, make_response
from flask_restful import Api, Resource, reqparse
import json
from bookblog import app, db
from bookblog.forms import CommentForm, PostForm
from html.entities import name2codepoint
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests
from flask_wtf.file import FileField, FileAllowed
import os

BASE = "https://127.0.0.1:5000/"

GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
GOOGLE_DISCOVERY_URL = ("")

#SECRET INFO REDACTED, need it for Google Auth!!

master_email = 'MASTER_EMAIL'
login_manager = LoginManager(app)
login_manager.init_app(app)
api = Api(app)

post_put_args = reqparse.RequestParser(bundle_errors=True)
post_put_args.add_argument("title", type=str, help="Title of the book", required=True)
post_put_args.add_argument("author_name", type=str, help="Author of the book", required=True)
post_put_args.add_argument("rating", type=str, help="Book rating", required=True)
post_put_args.add_argument("rating_int", type=int, help="0", required=True)
post_put_args.add_argument("content_before", type=str, help="Content before spoiler", required=True)
post_put_args.add_argument("content_after", type=str, help="Content after spoiler", required=True)

class Post_(Resource):
    def get(self, post_id):
        comment_url = "/post/" + str(post_id) + "/comment"
        response = json.dumps(Post.serializing(Post.query.filter_by(id=post_id).first()))
        post_details = json.loads(response)
        title = post_details["author_name"]
        author_name = post_details["author_name"]
        content_after = post_details["content_after"]
        content_before = post_details["content_before"]
        rating=post_details["rating"]
        book_title=post_details["title"]
        post = Post.query.filter_by(id=post_id).first()
        image_file = url_for('static', filename='posts/' + post.image_file)
        comments = Comment.query.filter_by(comment_url=post_id)
        return make_response(render_template("post.html", image_file=image_file, comment_url=comment_url, title=title, author_name=author_name, content_after=content_after, content_before=content_before, rating=rating, book_title=book_title, comments=comments, master_email=master_email))

    def put(self, post_id):
        args = post_put_args.parse_args()
        post = Post.query.filter_by(id=post_id).first()
        post.title = args["title"]
        post.author_name = args["author_name"]
        post.rating = args["rating"]
        post.rating_int = args["rating_int"]
        post.content_before = args["content_before"]
        post.content_after = args["content_after"]
        db.session.commit()
        return Post.serializing(post), 201

api.add_resource(Post_, "/post/<int:post_id>")

@app.route("/post/<int:post_id>/comment", methods=['GET', 'POST'])
@login_required
def new_comment(post_id):
    form = CommentForm()
    comment_url = post_id
    if form.validate_on_submit():
        comment = Comment(title=form.title.data, content=form.content.data, author=current_user, comment_url=comment_url)
        db.session.add(comment)
        db.session.commit()
        return(redirect("/books"))
    elif current_user.is_authenticated:
        return render_template('comment.html', title='Create a comment', form=form)
    else:
        return "Access denied."

comment_put_args = reqparse.RequestParser(bundle_errors=True)
comment_put_args.add_argument("title", type=str, help="Title of the comment", required=True)
comment_put_args.add_argument("content", type=str, help="Content", required=True)

class Comment_(Resource):
    def get(self, comment_id):
        response = json.dumps(Comment.serializing(Comment.query.filter_by(id=comment_id).first()))
        comment_details = json.loads(response)
        title = comment_details["title"]
        comment = comment_details["content"]
        return make_response(render_template("viewcomment.html", title=title, comment=comment))

    def post(self, comment_id):
        args = comment_put_args.parse_args()
        comment = Comment.query.filter_by(id=comment_id).first()
        comment.title = args["title"]
        comment.content = args["content"]
        db.session.commit()
        return Comment.serializing(comment), 201

api.add_resource(Comment_, "/comment/<int:comment_id>")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 404

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About Me')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact Me')

@app.route('/books')
def books():
    book_dict = {}
    author_more_books = []
    posts = Post.query.all()
    for post in posts:
        base_url = BASE
        post_id = str(post.id)
        temp_url = base_url + 'post/' + post_id
        image_file = url_for('static', filename='posts/' + post.image_file)
        if post.author_name in book_dict:
            book_dict[post.author_name].append([post.title, temp_url, image_file])
        else:
            book_dict[post.author_name] = [[post.title, temp_url, image_file]]
    for author in book_dict:
        if len(book_dict[author]) > 1:
            author_more_books.append(author)
    sorted_author_list = sorted(book_dict)
    return render_template('books.html', title='Book Reviews', book_dict=book_dict, sorted_author_list=sorted_author_list, author_more=author_more_books)

@app.route("/googlelogin")
def googlelogin():
    return render_template("login.html")

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        prompt="select_account"
    )
    return redirect(request_uri)

@app.route("/login/callback", methods=['GET', 'POST'])
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]
    else:
        return "User email not available or not verified by Google.", 404
    user = User(username=users_name, email=users_email, image_file=picture)
    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(username=users_name, email=users_email, image_file=picture)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for("account"))

@app.route("/account")
@login_required
def account():
    users_name = current_user.username
    email = current_user.email
    profile_pic = current_user.image_file
    comments = Comment.query.filter_by(author=current_user)
    return render_template('account.html', title='Account', username = users_name, email=email, profile_pic=profile_pic, comments=comments)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.image_file.data)
        post = Post(title=form.title.data, author_name = form.author_name.data, rating = form.rating.data, rating_int = form.rating_int.data, content_before=form.content_before.data, content_after = form.content_after.data, author=current_user, image_file=picture_file)
        db.session.add(post)
        db.session.commit()
        return(redirect("/"))
    elif current_user.email == 'robertssun1234@gmail.com':
        return render_template('createpost.html', title='Create a Post', form=form)
    else:
        return "Access denied."

def save_picture(form_picture):
    picture_path = os.path.join(app.root_path, 'static/posts', form_picture.filename)
    form_picture.save(picture_path)
    return form_picture.filename

@app.route("/post/<int:post_id>/delete", methods=['GET','POST'])
@login_required
def delete_post(post_id):
    if request.method == 'GET':
        post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('books'))

@app.route("/comment/<int:comment_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    if request.method == 'GET':
        comment = Comment.query.get_or_404(comment_id)
    if comment.author == current_user or current_user.email == 'robertssun1234@gmail.com':
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('books'))