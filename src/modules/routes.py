from main import app
from . import database

# Flask
from flask import request, session
from flask import redirect, url_for, render_template, flash

# Tools
from sqlalchemy.sql import text
from datetime import date as datetime

# ~~~~~
# ~~~~~

@app.route("/", methods=["GET"])
def index():
    if "userid" not in session:
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

# Assets
@app.route("/assets", methods=["GET"])
def assets(path = ''):
    if "userid" not in session:
        return redirect(url_for("login"))

    return render_template(
       "assets.jinja",
       session={ "user": session["username"] },
       data=database.get_user_assets(session["userid"])
   )

@app.route("/assets/add", methods=["POST"])
def create_assets():
    is_invalid = False
    
    if "userid" not in session:
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
        if not database.create_asset(session["userid"], assetname, value, description, date):
            flash(f"Asset <b>{ assetname }</b> already exists")

    return redirect(url_for("assets"))

# Session management
@app.route("/login", methods=["GET"])
def login():
    if "userid" in session:
        return redirect(url_for("index"))

    return render_template("login.jinja", title="Login")

@app.route("/login", methods=["POST"])
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

    session["userid"] = userid
    session["username"] = username
    return redirect(url_for('index'))

@app.route("/logout", methods=["GET", "POST"])
def logout():
    for item in list(session):
        _ = session.pop(item, None)

    return redirect(url_for('login'))

@app.route("/api/test/user", methods=["GET", "POST"])
def add_test_user():
    if not database.create_user("test", "test"):
        return f"User already created <a href=\"{url_for('index')}\">Go back</a>", 409

    return f"User created <a href=\"{url_for('index')}\">Go back</a>", 200
