# Server application
from main import app

# Database imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# Tools
from typing import Optional

from os import getenv
from datetime import date

# CONSTS
NULL = "NULL"

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI")
db = SQLAlchemy(app)

# USERS
def get_user(username: str) -> Optional[tuple[int, text, text]]:
    assert username is not None, "`username` must be set when fetching a user"

    return db.session.execute(
        text("SELECT * FROM users WHERE name = :username"),
        {"username": username}
    ).fetchone()

def get_userid(username: str) -> Optional[int]:
    assert username is not None, "`username` must be set when fetching a userid"

    if userid := db.session.execute(
        text("SELECT id FROM users WHERE name = :username"),
        {"username": username}
    ).fetchone():
        return userid[0]

def create_user(username: str, password: str) -> Optional[str]:
    assert username is not None, "`username` must be set when creating a user"
    assert password is not None, "`password` must be set when creating a user"

    from werkzeug.security import generate_password_hash
    res = db.session.execute(
        text("""
            INSERT INTO users VALUES (DEFAULT, :username, :password)
            ON CONFLICT DO NOTHING
            RETURNING name
        """),
        {"username": "test", "password": generate_password_hash("test")}
    ).fetchone()

    db.session.commit()
    return res

# ASSETS
def get_asset(userid: int, type: str) -> Optional[tuple[int, date, float]]:
    assert userid is not None, "`userid` must be set when fetching an asset"
    assert type   is not None, "`type` must be set when fetching an asset"

    return db.session.execute(
        text("SELECT * FROM assets WHERE userid = :userid AND type = :assettype"),
        {"userid": userid, "assettype": type}
    )

def get_assetid(userid: int, type: str) -> Optional[tuple[int, date, float]]:
    assert userid is not None, "`userid` must be set when fetching an assetid"
    assert type   is not None, "`type` must be set when fetching an assetid"

    return db.session.execute(
        text("SELECT id FROM assets WHERE userid = :userid AND type = :assettype"),
        {"userid": userid, "assettype": type}
    )

def create_asset(
    username: str,
    type: str,
    details: Optional[str] = None,
    date: Optional[str] = None,
    value: Optional[float] = None,
) -> Optional[bool]:
    assert username is not None, "`username` must be set when creating an asset"
    assert type     is not None, "`type` must be set when creating an asset"

    if (
        userid := get_userid(username)
    ) and (
        asset := db.session.execute(
            text("""
                INSERT INTO assets VALUES (DEFAULT, :userid, :type, :details)
                ON CONFLICT DO NOTHING
                RETURNING id
            """),
            {"userid": userid, "type": type, "details": details or NULL}
        ).fetchone()
    ):
        assert len(asset) == 1
        (assetid, ) = asset

        # Asset deletion is cascading, so there should never be a history item
        # laying around, even if the asset 
        db.session.execute(
            text("""
                INSERT INTO asset_history VALUES (:assetid, :date, :value)
            """),
            {"assetid": assetid, "date": date or NULL, "value": value or 0.00}
        )

        db.session.commit()
        return True
