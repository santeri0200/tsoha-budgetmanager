from main import app
from flask_sqlalchemy import SQLAlchemy

from os import getenv

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI", "postgresql:///tsoha")
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

from sqlalchemy.sql import text
from datetime import date as datetime

def get_userid(
    username: str,
) -> int:
    """
        Get userid corresponding to a username
    """

    assert username is not None, "`username` must be set when fetching a userid"

    res = db.session.execute(
        text("""
            SELECT id
            FROM users
            WHERE name = :username
        """),
        {
            "username": username,
        }
    )

    user = res.fetchone()

    assert hasattr(user, "id")
    return user.id

def get_passwordhash(
    username: str
) -> str | None:
    """
        Get password corresponding to a username
    """

    assert username is not None, "`name` must be set when fetching credentials"

    res = db.session.execute(
        text("""
            SELECT password
            FROM users
            WHERE name = :username
        """),
        {"username": username}
    )

    user = res.fetchone()

    if user:
        password: str = user[0]
        return password

    return None

def create_user(
    username: str,
    password: str,
) -> bool | None:
    """
        Create a new user in the database.
    """

    assert username is not None, "`username` must be set when creating a user"
    assert password is not None, "`password` must be set when creating a user"

    res = db.session.execute(
        text("""
            INSERT INTO Users (name, password)
            VALUES (:username, :password)
            ON CONFLICT DO NOTHING
            RETURNING TRUE as success
        """),
        {
            "username": username,
            "password": generate_password_hash("test")
        }
    )

    user = res.fetchone()
    if user:
        db.session.commit()

    return hasattr(user, "success")

def create_asset(
    userid : int,
    name   : str,
    value  : float,
    details: str | None,
    date   : str | None,
) -> bool:
    """
        Creates an asset entry and adds the value into asset history.
    """

    assert userid is not None, "`userid` must be set when creating an asset"
    assert name   is not None, "`type` must be set when creating an asset"
    assert value  is not None, "`value` must be set when createing an asset"

    res = db.session.execute(
        text("""
            INSERT INTO Assets (userid, type, details)
            VALUES (:userid, LOWER(:name), :details)
            ON CONFLICT DO NOTHING
            RETURNING id
        """),
        {
            "userid": userid,
            "name": name,
            "details": details or None
        }
    )

    asset = res.fetchone()
    if not asset:
        return False

    assert hasattr(asset, "id")
    assetid = asset.id

    # Asset deletion is cascading, so there should never be a history item
    # laying around, even if the asset 
    res = db.session.execute(
        text("""
            INSERT INTO asset_history
            VALUES (:assetid, :date, :value)
        """),
        {
            "assetid": assetid,
            "date": date or None,
            "value": value,
        }
    )

    print(res)

    db.session.commit()
    return True

def get_all_assets(
    userid: int
) -> list[tuple[int, datetime, float]]:
    """
        Gets all user assets with the most resent value from the asset history.
    """

    assert userid is not None, "`userid` must be set when fetching an asset"

    res = db.session.execute(
        text("""
            SELECT A.type, A.details, AH.value
            FROM assets A
            LEFT JOIN asset_history AH
            ON A.id = AH.assetid
            AND AH.date = (
                SELECT MAX(date)
                FROM asset_history
                WHERE assetid = A.id
            )
            WHERE A.userid = :userid
        """),
        {
            "userid": userid,
        }
    )

    return res.fetchall()
