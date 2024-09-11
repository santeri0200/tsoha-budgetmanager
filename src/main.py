from os import getenv
from flask import Flask

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = getenv("SECRET_KEY")

import modules.db
import modules.routes
