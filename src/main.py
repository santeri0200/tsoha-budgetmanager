# Webserver
from flask import Flask

# Sanitizer
from markupsafe import escape

APPNAME="Budget manager"
app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route("/", defaults={'path': ""})
@app.route("/<path:path>")
def spa(path):
    from flask import render_template

    return render_template(
        "index.html",
        appname=APPNAME,
        title="Frontpage",
        body="Hello, world!"
    )

@app.after_request
def set_headers(res):
    return res
