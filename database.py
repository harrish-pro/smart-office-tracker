import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# TASKS TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS tasks(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    title TEXT,

    deadline TEXT,

    priority TEXT,

    status TEXT

)

""")

# USERS TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT,

    role TEXT

)

""")

# INSERT USERS
cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('hari', '1234', 'employee')

""")

cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('arun', '1234', 'employee')

""")

# ADMIN USER
cursor.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('admin', '1234', 'admin')

""")

conn.commit()

conn.close()

print("Database Ready")