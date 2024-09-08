from os import getenv

# Webserver
from flask import Flask

# Sanitizer
from markupsafe import escape

# Webserver imports
from flask import session
from flask import request
from flask import redirect, url_for
from flask import render_template

APPNAME="Budget manager"
app = Flask(__name__, static_folder="static", static_url_path='/static')
app.secret_key = getenv("SECRET_KEY")

# Database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

def nav_items(path: str):
    items = [
        { "name": "Dashboard", "path": "/", },
        { "name": "Settings",  "path": "/settings", },
    ]

    for item in items:
        item["is_active"] = item["path"] == path

    return items

@app.route("/api/test/user")
def add_test_user():
    sql = text("SELECT * FROM users WHERE name = :username")
    res = db.session.execute(sql, {"username": "test"}).fetchone()
    if not res:
        sql = text("INSERT INTO users VALUES (DEFAULT, :username, :password)")
        db.session.execute(sql, {"username": "test", "password": generate_password_hash("test")})
        db.session.commit()

    return redirect(url_for('index'))

@app.route("/api/test/asset")
def add_test_asset():
    from datetime import datetime
    type = "some asset"
    details = "Have some details..."

    sql = text("""
        INSERT INTO assets VALUES (DEFAULT, (
            SELECT id FROM users WHERE name = 'test'
        ), :type, :details)
    """)
    db.session.execute(sql, {"type": type, "details": details})
    sql = text("""
        INSERT INTO asset_history VALUES ((
            SELECT id FROM assets WHERE userid = (
                SELECT id FROM users WHERE name = 'test'
            ) AND type = :type
        ), :date, :value)
    """)
    db.session.execute(sql, {"type": type, "date": datetime(2024, 1, 1).date(), "value": 100.00})
    db.session.commit()

    return redirect(url_for('index'))

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = text("SELECT password FROM users WHERE name = :username")
    res = db.session.execute(sql, {"username": username}).fetchone()
    if res and check_password_hash(res[0], password):
        session["username"] = username
        
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('index'))
    
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    items = nav_items('/' + path.split("/")[0])
    title = [item["name"] for item in items if item["is_active"]]
    return render_template(
        "index.html",
        appname=APPNAME,
        title=title[0] if len(title) else "",
        session={ "user": session["username"] if "username" in session else "" },
        nav_items=items,
    )

@app.after_request
def set_headers(res):
    return res
