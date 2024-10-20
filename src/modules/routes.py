"""
    Application routing logic.
"""

from main import app
from modules import database

# Flask
from flask import request, session
from flask import url_for, render_template, flash
from flask import redirect, abort

# Tools
from datetime import date as datetime
from functools import wraps
import secrets

# CSRF mitigation tactic
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "userid" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)
    return wrapper

def check_csrf(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        csrf_token = request.form.get("csrf_token", None) or request.args.get("csrf_token", None)
        if "csrf_token" not in session or session["csrf_token"] != csrf_token:
            return abort(403)

        return f(*args, **kwargs)
    return wrapper

# ~~~~~
# ~~~~~

@app.route("/", methods=["GET"])
@authenticate
def index():
    return render_template(
        "index.jinja",
        session=session,
        usenav=True,
        assets=database.get_user_assets(session["userid"], 10),
        receipts=database.get_user_receipts(session["userid"], 10),
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
def assets():
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
    assetname  : str | None = request.form.get("assetname"  , None)  # type: ignore[annotation-unchecked]
    description: str | None = request.form.get("description", None)  # type: ignore[annotation-unchecked]
    date       : str | None = request.form.get("date"       , None)  # type: ignore[annotation-unchecked]
    value      : str | None = request.form.get("value"      , None)  # type: ignore[annotation-unchecked]

    is_invalid = False

    try:
        float(value)
    except (ValueError, TypeError):
        flash("Value must be convertable to a float")
        is_invalid = True

    try:
        if date:
            datetime.fromisoformat(date)
    except ValueError:
        flash("Date must be ISO formated")
        is_invalid = True

    if not is_invalid:
        if not database.create_asset(session["userid"], assetname, value, description, date):
            flash(f"Asset <b>{ assetname }</b> already exists")

    return redirect(url_for("assets"))

# Receipts
@app.route("/receipts", methods=["GET"])
@authenticate
def receipts():
    return render_template(
       "receipts.jinja",
       session=session,
       data=database.get_user_receipts(session["userid"]),
       usenav=True
   )

@app.route("/receipts/<int:id>", methods=["GET"])
@authenticate
def receipt_view(id):
    return render_template(
       "receipt_view.jinja",
       session=session,
       receiptid=id,
       data=database.get_receipt_entries(session["userid"], id),
       usenav=True
   )

@app.route("/receipt/add", methods=["POST"])
@authenticate
@check_csrf
def create_receipt():
    receiptname: str | None = request.form.get("receiptname", None)  # type: ignore[annotation-unchecked]
    description: str | None = request.form.get("description", None)  # type: ignore[annotation-unchecked]
    date       : str | None = request.form.get("date"       , None)  # type: ignore[annotation-unchecked]

    is_invalid = False

    try:
        if date:
            datetime.fromisoformat(date)
    except ValueError:
        flash("Date must be ISO ormated")
        is_invalid = True

    if not is_invalid:
        receiptid = database.create_receipt(session["userid"], receiptname, description, date)
        if receiptid is not None:
            return redirect(url_for("receipt_view", id=receiptid))
        flash(f"Receipt <b>{ assetname }</b> already exists")

    return redirect(url_for("receipts"))

@app.route("/receipt/modify", methods=["POST"])
@authenticate
@check_csrf
def delete_receipt():
    modify: str | None = request.form.get("modify", None)  # type: ignore[annotation-unchecked]
    delete: str | None = request.form.get("delete", None)  # type: ignore[annotation-unchecked]

    is_invalid = False

    try:
        if modify and str(int(modify)) != modify:
            is_invalid = True
            flash("Trying to modify invalid receipt")
    except ValueError:
        is_invalid = True
        flash("Trying to modify invalid receipt")

    try:
        if delete and str(int(delete)) != delete:
            is_invalid = True
            flash("Trying to delete invalid receipt")
    except ValueError:
        is_invalid = True
        flash("Trying to delete invalid receipt")

    if is_invalid:
        pass
    elif modify:
        return redirect(url_for("receipt_view", id=modify))
    elif delete:
        success = database.delete_receipt(session["userid"], delete)
        if not success:
            flash("Failed to delete item from the receipt")
    else:
        flash("No item specified to be modified")

    return redirect(url_for("receipts"))

@app.route("/receipt/<int:id>/add", methods=["POST"])
@authenticate
@check_csrf
def add_item_to_receipt(id):
    itemname: str | None = request.form.get("itemname", None)  # type: ignore[annotation-unchecked]
    itemid  : str | None = request.form.get("itemid"  , None)  # type: ignore[annotation-unchecked]
    amount  : str | None = request.form.get("amount"  , None)  # type: ignore[annotation-unchecked]

    itemid = "1"

    is_invalid = False

    try:
        if not itemid or str(int(itemid)) != itemid:
            is_invalid = True
            flash("Invalid itemid")
    except ValueError:
        is_invalid = True
        flash("Invalid itemid")

    try:
        if amount and str(int(amount)) != amount:
            is_invalid = True
            flash("Invalid amount")
    except ValueError:
        is_invalid = True
        flash("Invalid amount")

    if not is_invalid:
        success = database.add_item_to_receipt(session["userid"], id, itemname, itemid, int(amount or 1))
        if not success:
            flash(f"Failed to add item: {itemname} to the receipt")

    return redirect(url_for("receipt_view", id=id))

@app.route("/receipt/<int:id>/delete", methods=["POST"])
@authenticate
@check_csrf
def delete_item_from_receipt(id):
    itemid: str | None = request.form.get("delete", None)  # type: ignore[annotation-unchecked]

    is_invalid = False

    try:
        if not itemid or str(int(itemid)) != itemid:
            is_invalid = True
            flash("Trying to delete invalid line entry id")
    except ValueError:
        is_invalid = True
        flash("Trying to delete invalid line entry id")

    if not is_invalid:        
        success = database.delete_item_from_receipt(session["userid"], id, itemid)
        if not success:
            flash(f"Failed to delete item from the receipt")

    return redirect(url_for("receipt_view", id=id))

# Preferences
@app.route("/preferences", methods=["GET"])
@authenticate
def user_preferences():
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
    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if (
        not isinstance(username, str) or not username or
        not isinstance(password, str) or not password
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
