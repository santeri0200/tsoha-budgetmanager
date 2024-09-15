CREATE TABLE IF NOT EXISTS users (
    id SERIAL NOT NULL,
    name TEXT NOT NULL,
    password CHARACTER(162) NOT NULL,     /* HASHED `password` */

    PRIMARY KEY (id),

    UNIQUE(id),
    UNIQUE(name),                         /* Usernames should always be UNIQUE. */
    UNIQUE(password)                      /* Passwords should always be UNIQUE. */
);

CREATE TABLE IF NOT EXISTS assets (
    id SERIAL NOT NULL,          /* This key is used to refer into asset history
                                    otherwise unused. */
    userid INT NOT NULL,
    type TEXT NOT NULL,          /* ASSET TYPE */
    details TEXT,                /* EXTRA DETAILS */

    PRIMARY KEY (id),
    FOREIGN KEY (userid) REFERENCES users(id)
        ON DELETE CASCADE        /* DELETE ENTRY ON `user` DELETION */
        ON UPDATE CASCADE,       /* UPDATE `userid` ON `user` UPDATE */

    UNIQUE(id),
    UNIQUE(userid, type)         /* EACH `userid` HAS UNIQUE `type`s */
                                 /* This constrain is good as it allows
                                    us to add UNIQUE data into
                                    the asset history. */
);

CREATE TABLE IF NOT EXISTS asset_history (
    assetid INT NOT NULL,
    date DATE,                       /* EVAL DATE (no timestamp) */
                                     /* This allows us to use "indefinite"
                                        dates, when users don't have
                                        defined starting date.
                                        For example: this is the first
                                        time they log this info. */
    value NUMERIC(12, 2) NOT NULL,   /* MAX 9_999_999_999.99 */
                                     /* I don't think anyone using this app
                                        will ever have more than 10 billion
                                        invested into a single asset. */

    FOREIGN KEY (assetid) REFERENCES assets(id)
        ON DELETE CASCADE            /* DELETE ENTRY ON asset DELETION */
        ON UPDATE CASCADE,           /* UPDATE `assetid` ON `asset` UPDATE */

    UNIQUE(assetid, date)
) WITH (fillfactor=90);
