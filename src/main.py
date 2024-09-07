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
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = b'MYSECRETKEY' # TODO: Add this to .env

users = {
    "test": "test"
}

def nav_items(path: str):
    items = [
        { "name": "Dashboard", "path": "/", },
        { "name": "Settings",  "path": "/settings", },
    ]

    for item in items:
        item["is_active"] = item["path"] == path

    return items

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username in users and users[username] == password:
        session["username"] = username

    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('index'))
    
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    print(f"session: { session }")

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
