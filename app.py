from flask import Flask, render_template, request, redirect, url_for
from models import init_db, get_all_comments, add_comment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")  # Use a strong secret in production!

login_manager = LoginManager(app)
login_manager.login_view = "google.login"

# Google OAuth setup
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Simple User model for Flask-Login
class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.before_first_request
def initialize():
    init_db()

@app.route("/")
def index():
    comments = get_all_comments()
    return render_template("index.html", comments=comments, current_user=current_user)

@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment_route():
    author = current_user.name
    content = request.form.get("content")
    parent_id = request.form.get("parent_id")
    add_comment(author, content, parent_id)
    return redirect(url_for("index"))

@app.route("/login")
def login():
    if not current_user.is_authenticated:
        return redirect(url_for("google.login"))
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/login/google/authorized")
def authorized():
    if not google.authorized:
        return redirect(url_for("index"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return redirect(url_for("index"))
    user_info = resp.json()
    user_id = user_info["id"]
    name = user_info.get("name", user_info.get("email"))
    email = user_info["email"]
    user = User(user_id, name, email)
    users[user_id] = user
    login_user(user)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
