CREATE TABLE IF NOT EXISTS Users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password CHARACTER(162) NOT NULL,   -- Hashed password

    UNIQUE(username),
    UNIQUE(password)                    -- Passwords should be unique,
                                        -- otherwise the algorithm has a collision.
);

CREATE TABLE IF NOT EXISTS Assets (
    id SERIAL PRIMARY KEY,
    userid INT NOT NULL
        REFERENCES Users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    name TEXT NOT NULL,     -- Asset name
    details TEXT,           -- Extra details

    UNIQUE(userid, name)    -- Userids should have unique assets
);

CREATE TABLE IF NOT EXISTS AssetHistory (
    assetid INT
        REFERENCES Assets(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    date DATE NOT NULL,
    value NUMERIC(12, 2) NOT NULL,  /* Max 9_999_999_999.99
                                       I don't think anyone using this app
                                       will ever have more than 10 billion
                                       invested into a single asset. */

    UNIQUE(assetid, date)           -- Assets should only have one value per date
) WITH (fillfactor=90);

/* Receipts have line entries, each line entry is a item.
   Each item can be categorised outside of it's original category. */

CREATE TABLE IF NOT EXISTS ItemCategories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent INT NULL                     -- Used if this is a subcategory
        REFERENCES ItemCategories(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Items (
    id SERIAL PRIMARY KEY,
    categoryid INT NOT NULL
        REFERENCES ItemCategories(id)
        DEFAULT 0,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Receipts (
    id SERIAL PRIMARY KEY,
    assetid INT NULL
        REFERENCES Assets(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    name TEXT NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS ReceiptLineEntry (
    id SERIAL PRIMARY KEY,
    receiptid INT NOT NULL
        REFERENCES Receipts(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    itemid INT NOT NULL
        REFERENCES Items(id)
        ON DELETE RESTRICT  /* We don't want to have dangling references,
                               it is safer to set this value to `0` instead
                               of nullifying it. */
        ON UPDATE CASCADE,
    customname TEXT NULL    /* Should be used if original itemid dies,
                               otherwise users are free to use this
                               field if no corresponding item is found. */

);
