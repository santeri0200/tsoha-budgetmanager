"""
    Application database logic.
"""

from main import app

# Database config
from os import getenv
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URI", "postgresql:///tsoha")
if app.debug:
    app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

# Tools
from sqlalchemy.sql import text
from datetime import date as datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# ~~~~~
# ~~~~~

def check_password(
    username: str,
    password: str,
) -> bool:
    """
        Check password against a hash from a row matching the username.
    """

    assert username is not None
    assert password is not None

    res = db.session.execute(
        text("""
            SELECT id, password
            FROM Users
            WHERE username = :username
         """),
        {
            "username": username
        }
    )

    user = res.fetchone()

    if user:
        assert hasattr(user, "id")
        assert hasattr(user, "password")

        if check_password_hash(user.password, password):
            return user.id

    # If username is not found or password doesn't match
    return None

def get_user_preferences(
    userid: int,
) -> dict[any]:
    """
        asd
    """

    assert userid is not None

    res = db.session.execute(
        text("""
            SELECT screenname
            FROM Preferences
            WHERE userid = :userid
        """),
        {
            "userid": userid
        }
    )

    preferences = res.fetchone()
    assert preferences is not None, "`Preferences` row entry is added and deleted along side the user. This should never fail." # pylint: disable=line-too-long

    return preferences._asdict()

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
            INSERT INTO Users (username, password)
            VALUES (:username, :password)
            ON CONFLICT DO NOTHING
            RETURNING id
        """),
        {
            "username": username,
            "password": generate_password_hash("test")
        }
    )

    user = res.fetchone()
    if not hasattr(user, "id"):
        db.session.rollback()
        return False

    res = db.session.execute(
        text("""
            INSERT INTO Preferences (userid)
            VALUES (:userid)
            RETURNING TRUE as success
        """),
        {
            "userid": user.id,
        }
    )

    prefs = res.fetchone()
    if not hasattr(prefs, "success"):
        db.session.rollback()
        return False

    db.session.commit()
    return True

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
    assert name   is not None, "`name` must be set when creating an asset"
    assert value  is not None, "`value` must be set when createing an asset"

    res = db.session.execute(
        text("""
            INSERT INTO Assets (userid, name, details)
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
        db.session.rollback()
        return False

    assert hasattr(asset, "id")
    assetid = asset.id

    # Asset deletion is cascading, so there should never be a history item
    # laying around, even if the asset
    #
    # The call below already commits the changes on success
    # and rollbacks on error
    return create_assethistory_entry(assetid, date or datetime.today(), value)

def create_assethistory_entry(
    assetid: int,
    date: str,
    value: int,
) -> bool:
    """
        asd
    """

    res = db.session.execute(
        text("""
            INSERT INTO AssetHistory
            VALUES (:assetid, :date, :value)
            RETURNING TRUE as success
        """),
        {
            "assetid": assetid,
            "date": date,
            "value": value,
        }
    )

    success = res.fetchone()
    if success:
        db.session.commit()
        return True

    db.session.rollback()
    return False

def get_user_assets(
    userid: int,
    limit: int | None = None
) -> list[tuple[int, datetime, float]]:
    """
        Gets all or limit (amount of) user assets with the most resent value from the asset history.
    """

    assert userid is not None, "`userid` must be set when fetching an asset"

    res = None
    sql = """
        SELECT A.name, A.details, AH.value
        FROM Assets A
        LEFT JOIN AssetHistory AH
        ON A.id = AH.assetid
        AND AH.date = (
            SELECT MAX(date)
            FROM AssetHistory
            WHERE assetid = A.id
        )
        WHERE A.userid = :userid
    """

    if limit:
        sql += "LIMIT :limit"

    res = db.session.execute(
        text(sql),
        {
            "userid": userid,
            "limit": limit,
        }
    )

    return res.fetchall()

# Receipts
def create_receipt(
    userid : int,
    name   : str,
    desc   : str | None,
    date   : str | None,
) -> bool:
    """
        Creates an asset entry and adds the value into asset history.
    """

    assert userid is not None, "`userid` must be set when creating a receipt"
    assert name   is not None, "`name` must be set when creating a receipt"

    res = db.session.execute(
        text("""
            INSERT INTO Receipts (userid, name, date, description)
            VALUES (:userid, LOWER(:name), :date, :details)
            ON CONFLICT DO NOTHING
            RETURNING id
        """),
        {
            "userid": userid,
            "name": name,
            "date": date or datetime.today(),
            "details": desc or None
        }
    )

    receipt = res.fetchone()
    if not receipt:
        db.session.rollback()
        return None

    assert hasattr(receipt, "id")
    db.session.commit()
    return receipt.id

def user_owns_receipt(
    userid   : int,
    receiptid: int,
):
    res = db.session.execute(
        text(f"""
             SELECT TRUE as success
             FROM Receipts
             WHERE userid = :userid AND id = :receiptid
        """),
        {
            "userid": userid,
            "receiptid": receiptid,
        }
    )

    return res.fetchone() is not None

def add_item_to_receipt(
    userid   : int,
    receiptid: int,
    itemname : str,
    itemid   : int,
    amount   : int,
) -> bool:
    """
        Adds item(s) to a receipt's line entries.
    """

    assert userid is not None, "`userid` must be set when adding items to receipts"
    assert itemid is not None, "`itemid` must be set when adding items to receipts"
    assert amount is not None, "`amount` must be set when adding items to receipts"

    if not user_owns_receipt(userid, receiptid):
        return False
        
    item = ",".join(["(:receiptid, :itemid)"] * amount)
    res = db.session.execute(
        text(f"""
            INSERT INTO ReceiptLineEntry (receiptid, itemid)
            VALUES { item }
            ON CONFLICT DO NOTHING
            RETURNING TRUE as success
        """),
        {
            "receiptid": receiptid,
            "itemid": itemid,
        }
    )

    success = res.fetchone()
    if not success:
        db.session.rollback()
        return False

    db.session.commit()
    return True

def delete_receipt(
    userid   : int,
    receiptid: int,
) -> bool:
    assert userid    is not None, "`userid` must be set when deleting receipts"
    assert receiptid is not None, "`receiptid` must be set when deleting receipts"

    res = db.session.execute(
        text(f"""
             DELETE FROM Receipts
             WHERE id = :receiptid AND userid = :userid
             RETURNING TRUE as success
        """),
        {
            "userid": userid,
            "receiptid": receiptid,
        }
    )

    success = res.fetchone()
    if not success:
        db.session.rollback()
        return False

    db.session.commit()
    return True

def delete_item_from_receipt(
    userid   : int,
    receiptid: int,
    lineid   : int,
) -> bool:
    """
        Adds item(s) to a receipt's line entries.
    """

    assert userid    is not None, "`userid` must be set when deleting items from receipts"
    assert receiptid is not None, "`receiptid` must be set when deleting items from receipts"
    assert lineid    is not None, "`itemid` must be set when deleting items from receipts"

    if not user_owns_receipt(userid, receiptid):
        return False

    res = db.session.execute(
        text(f"""
             DELETE FROM ReceiptLineEntry
             WHERE receiptid = :receiptid AND id = :lineid
             RETURNING TRUE as success
        """),
        {
            "receiptid": receiptid,
            "lineid": lineid,
        }
    )

    success = res.fetchone()
    if not success:
        db.session.rollback()
        return False

    db.session.commit()
    return True

def get_user_receipts(
    userid: int,
    limit: int | None = None
) -> dict[str, datetime, list[dict[str, float]]]:
    """
        Gets all or limit (amount of) user receipts.
    """

    assert userid is not None, "`userid` must be set when fetching an receipts"

    res = None
    sql = """
        SELECT R.id, R.name, R.date, R.description, SUM(I.value) as value
        FROM Receipts R
        LEFT JOIN ReceiptLineEntry RLE
        ON R.id = RLE.receiptid
        LEFT JOIN Items I
        ON RLE.itemid = I.id
        WHERE R.userid = :userid
        GROUP BY R.id
        ORDER BY R.id DESC
    """

    if limit:
        sql += "LIMIT :limit"

    res = db.session.execute(
        text(sql),
        {
            "userid": userid,
            "limit": limit,
        }
    )

    return res.fetchall()

def get_receipt_entries(
    userid:    int,
    receiptid: int,
):
    """
        Gets all line entries for given receipt.
    """

    res = db.session.execute(
        text("""
            SELECT RLE.id, I.name, I.description, I.value, IC.name as category
            FROM ReceiptLineEntry RLE
            LEFT JOIN Receipts R
            ON R.id = RLE.receiptid
            LEFT JOIN Items I
            ON RLE.itemid = I.id
            LEFT JOIN ItemCategories IC
            ON I.categoryid = IC.id
            WHERE R.id = :receiptid AND R.userid = :userid
            ORDER BY RLE.id
        """),
        {
            "userid": userid,
            "receiptid": receiptid
        }
    )

    return res.fetchall()
