import sqlite3 as sql

from utils import SQLITE_DB_PATH

# connect to SQLite
con = sql.connect(SQLITE_DB_PATH)

# Create a Connection
cur = con.cursor()

# Create players table  in db_web database
sql = '''CREATE TABLE "players" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"name"	TEXT NOT NULL,
	"elo"	INTEGER DEFAULT 0 NOT NULL
)'''
cur.execute(sql)

# commit changes
con.commit()

# close the connection
con.close()
