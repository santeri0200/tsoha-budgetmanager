from main import app
from . import database

# Flask
from flask import request, session
from flask import url_for, render_template, flash
from flask import redirect, abort

# Tools
from sqlalchemy.sql import text
from datetime import date as datetime
from functools import wraps
import secrets

# CSRF mitigation tactic
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

def authenticate(f):
    @wraps(f)
    def wrapper(*args):
        if "userid" not in session:
            return redirect(url_for("login"))

        return f(*args)
    return wrapper

def check_csrf(f):
    @wraps(f)
    def wrapper(*args):
        if "csrf_token" not in session or session["csrf_token"] != request.form.get("csrf_token", request.args.get("csrf_token", None)):
            return abort(403)

        return f(*args)
    return wrapper

# ~~~~~
# ~~~~~

@app.route("/", methods=["GET"])
@authenticate
def index():
    return render_template(
        "index.jinja",
        session=session,
        usenav=True
    )

@app.route("/<path:path>", methods=["GET"])
def default_get(path: str):
    _ = path
    return redirect(url_for("index"))

@app.route("/<path:path>", methods=["POST"])
def default_post(path: str):
    _ = path
    abort(403)

# Assets
@app.route("/assets", methods=["GET"])
@authenticate
def assets(path = ''):
    return render_template(
       "assets.jinja",
       session=session,
       data=database.get_user_assets(session["userid"]),
       usenav=True
   )

@app.route("/assets/add", methods=["POST"])
@authenticate
@check_csrf
def create_assets():
    is_invalid = False

    assetname  : str | None = request.form.get("assetname"  , None)  # type: ignore[annotation-unchecked]
    description: str | None = request.form.get("description", None)  # type: ignore[annotation-unchecked]
    date       : str | None = request.form.get("date"       , None)  # type: ignore[annotation-unchecked]
    value      : str | None = request.form.get("value"      , None)  # type: ignore[annotation-unchecked]

    try:
        float(value)
    except ValueError:
        flash("Value must be convertable to a float")
        is_invalid = True        

    try:
        if date: datetime.fromisoformat(date)
    except ValueError:
        flash("Date must be ISO formated")
        is_invalid = True

    if not is_invalid:
        if not database.create_asset(session["userid"], assetname, value, description, date):
            flash(f"Asset <b>{ assetname }</b> already exists")

    return redirect(url_for("assets"))

# Preferences
@app.route("/preferences", methods=["GET"])
@authenticate
def preferences():
    return render_template(
        "preferences.jinja",
        session=session,
        usenav=True
    )
    

# Session management
@app.route("/login", methods=["GET"])
def login():
    if "userid" in session:
        return redirect(url_for("index"))

    # Generate temporary CSRF token
    session["csrf_token"] = secrets.token_hex(16)

    return render_template(
        "login.jinja",
        title="Login",
        session={"csrf_token": session["csrf_token"]}
    )

@app.route("/login", methods=["POST"])
@check_csrf
def handle_login():    
    username = request.form["username"]
    password = request.form["password"]

    if (
        type(username) != str
        or not len(username)
        or type(password) != str
        or not len(password)
    ):
        flash("Invalid credentials!")
        return redirect(url_for('login'))

    userid = database.check_password(username, password)
    if userid is None:
        flash("No matching credentials!")
        return redirect(url_for('login'))

    session["csrf_token"] = secrets.token_hex(16)
    session["userid"] = userid
    session["screenname"] = username
    preferences = database.get_user_preferences(userid)
    for pref in preferences:
        session[pref] = preferences[pref] or session[pref] or None

    return redirect(url_for('index'))

@app.route("/logout", methods=["GET"])
def logout():
    for item in list(session):
        _ = session.pop(item, None)

    return redirect(url_for('login'))

@app.route("/api/test/user", methods=["GET", "POST"])
def add_test_user():
    if not database.create_user("test", "test"):
        return f"User already created <a href=\"{url_for('index')}\">Go back</a>", 409

    return f"User created <a href=\"{url_for('index')}\">Go back</a>", 200
