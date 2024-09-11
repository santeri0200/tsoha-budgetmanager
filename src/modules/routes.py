# Server application
from main import app

# Webserver imports
from flask import session
from flask import request
from flask import redirect, url_for
from flask import render_template
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash

# Tools
from markupsafe import escape
from datetime import date

@app.route("/login", methods=["GET"])
def login():
    return render_template(
        "login.jinja",
        error=request.args.get('invalid_credentials')
    )

@app.route("/login", methods=["POST"])
def handle_login():
    from modules.db import get_user
    
    username = request.form["username"]
    password = request.form["password"]

    res = get_user(username)
    if res and check_password_hash(res[2], password):
        session["username"] = username
        return redirect(url_for('index'))
        
    return redirect(url_for('login', invalid_credentials=1))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))

@app.route("/", methods=["GET"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "index.jinja",
        rootpath='/' + request.path.split("/")[0],
        session={ "user": session["username"] },
    )

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("index"))

@app.after_request
def after_request(res):
    return res

@app.before_request
def before_request():
    pass

# Test routes
@app.route("/api/test/user", methods=["GET", "POST"])
def add_test_user():
    from modules.db import create_user

    if not create_user("test", "test"):
        return "User already created", 409

    return "User created", 200

@app.route("/api/test/asset", methods=["GET", "POST"])
def add_test_asset():
    from modules.db import create_asset

    if not create_asset("test", "Some asset", "Have some details...", date(2024, 1, 1), 100.00):
        return "Asset already created", 409

    return "Asset created", 200
