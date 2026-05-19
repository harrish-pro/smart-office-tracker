import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# CREATE TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT

)

""")

# INSERT ADMIN USER
cursor.execute("""

INSERT OR IGNORE INTO users
(username, password)

VALUES
('admin', '1234')

""")

conn.commit()

conn.close()

print("Admin User Created Successfully")