"""
    Application entry point.
"""

from os import getenv
from flask import Flask

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = getenv("SECRET_KEY", "MYSECRETKEY")

# Imports routes added to app
from modules import routes # pylint: disable=unused-import
