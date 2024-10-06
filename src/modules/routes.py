from main import app
from . import database

# Flask
from flask import request, session
from flask import redirect, url_for, render_template, flash

# Tools
from sqlalchemy.sql import text
from datetime import date as datetime
from werkzeug.security import check_password_hash

# ~~~~~
# ~~~~~

@app.route("/", methods=["GET"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("index.jinja", session={ "user": session["username"] })

@app.route("/<path:path>", methods=["GET"])
def default_get(path: str):
    _ = path
    return redirect(url_for("index"))

@app.route("/<path:path>", methods=["POST"])
def default_post(path: str):
    _ = path
    abort(403)

@app.route("/assets", methods=["GET"])
def assets(path = ''):
    if "username" not in session:
        return redirect(url_for("login"))

    userid = database.get_userid(session["username"])
    return render_template(
       "assets.jinja",
       session={ "user": session["username"] },
       data=database.get_all_assets(userid)
   )

@app.route("/assets/add", methods=["POST"])
def create_assets():
    is_invalid = False
    
    if "username" not in session:
        return redirect(url_for("login"))

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
        userid = database.get_userid(session["username"])
        if not database.create_asset(userid, assetname, value, description, date):
            flash(f"Asset <b>{ assetname }</b> already exists")

    return redirect(url_for("assets"))

@app.route("/login", methods=["GET"])
def login():
    if "username" in session:
        return redirect(url_for("index"))

    return render_template("login.jinja", title="Login")

@app.route("/login", methods=["POST"])
def handle_login():    
    username = request.form["username"]
    password = request.form["password"]

    hash = database.get_passwordhash(username)
    if hash and check_password_hash(hash, password):
        session["username"] = username
        return redirect(url_for('index'))
    
    flash("Invalid credentials!")
    return redirect(url_for('login'))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))

@app.route("/api/test/user", methods=["GET", "POST"])
def add_test_user():
    from modules.users import create_user

    if not create_user("test", "test"):
        return "User already created <a href=\"/\">Go back</a>", 409

    return "User created <a href=\"/\">Go back</a>", 200
