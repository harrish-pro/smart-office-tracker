import sqlite3

conn = sqlite3.connect("database.db")

# TASK TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
deadline TEXT,
priority TEXT,
status TEXT
)
''')

# USER TABLE
conn.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
''')

# DEFAULT LOGIN
conn.execute("""

INSERT INTO users
(username, password)

VALUES
('admin', '1234')

""")

conn.commit()

conn.close()

print("Database Ready")