from flask import Flask, render_template, request
from flask import redirect, session, send_file

import sqlite3
import pandas as pd
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

app = Flask(__name__)

app.secret_key = "smartoffice"

# CREATE FOLDERS
if not os.path.exists("static"):
    os.makedirs("static")

if not os.path.exists("reports"):
    os.makedirs("reports")

# CREATE DATABASE TABLES
conn = sqlite3.connect("database.db")

conn.execute('''
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    title TEXT,
    deadline TEXT,
    priority TEXT,
    status TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# DEFAULT USERS
conn.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('admin', '1234', 'admin')

""")

conn.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('hari', '1234', 'employee')

""")

conn.execute("""

INSERT OR IGNORE INTO users
(username, password, role)

VALUES
('arun', '1234', 'employee')

""")

conn.commit()

conn.close()

# LOGIN PAGE
@app.route("/login")
def login():

    return render_template("login.html")


# LOGIN CHECK
@app.route("/logincheck", methods=["POST"])
def logincheck():

    username = request.form["username"]

    password = request.form["password"]

    conn = sqlite3.connect("database.db")

    user = conn.execute("""

    SELECT * FROM users

    WHERE username=? AND password=?

    """, (username, password)).fetchone()

    conn.close()

    if user:

        session["user"] = username

        session["role"] = user[3]

        return redirect("/")

    else:

        return "Invalid Username or Password"


# HOME PAGE
@app.route("/")
def home():

    if "user" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")

    search = request.args.get("search")

    # ADMIN VIEW
    if session["role"] == "admin":

        if search:

            data = conn.execute("""

            SELECT * FROM tasks

            WHERE title LIKE ?

            """,

            ('%' + search + '%',)

            ).fetchall()

        else:

            data = conn.execute("""

            SELECT * FROM tasks

            """).fetchall()

    # EMPLOYEE VIEW
    else:

        if search:

            data = conn.execute("""

            SELECT * FROM tasks

            WHERE username=? AND title LIKE ?

            """,

            (session["user"], '%' + search + '%')

            ).fetchall()

        else:

            data = conn.execute("""

            SELECT * FROM tasks

            WHERE username=?

            """,

            (session["user"],)

            ).fetchall()

    conn.close()

    # ANALYTICS
    total_tasks = len(data)

    completed_tasks = 0

    pending_tasks = 0

    high_priority = 0

    for task in data:

        if task[5] == "Completed":

            completed_tasks += 1

        else:

            pending_tasks += 1

        if task[4] == "High":

            high_priority += 1

    # AI SUGGESTIONS
    suggestion = ""

    if pending_tasks >= 5:

        suggestion = "⚠ Too many pending tasks! Focus on completing them."

    elif high_priority >= 3:

        suggestion = "🔥 You have multiple high priority tasks."

    elif completed_tasks == total_tasks and total_tasks > 0:

        suggestion = "✅ Excellent productivity! All tasks completed."

    else:

        suggestion = "👍 Productivity is under control."

    # CHART
    labels = ["Completed", "Pending"]

    values = [completed_tasks, pending_tasks]

    plt.figure(figsize=(5, 5))

    plt.bar(labels, values)

    plt.title("Task Analytics")

    plt.savefig("static/chart.png")

    plt.close()

    return render_template(

        "dashboard.html",

        tasks=data,

        total=total_tasks,

        completed=completed_tasks,

        pending=pending_tasks,

        suggestion=suggestion
    )


# ADD TASK
@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:

        return redirect("/login")

    username = session["user"]

    title = request.form["title"]

    deadline = request.form["deadline"]

    priority = request.form["priority"]

    conn = sqlite3.connect("database.db")

    conn.execute("""

    INSERT INTO tasks
    (username, title, deadline, priority, status)

    VALUES
    (?, ?, ?, ?, ?)

    """,

    (username, title, deadline, priority, "Pending")

    )

    conn.commit()

    conn.close()

    return redirect("/")


# DELETE TASK
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")

    conn.execute(

        "DELETE FROM tasks WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()

    return redirect("/")


# EDIT PAGE
@app.route("/edit/<int:id>")
def edit(id):

    conn = sqlite3.connect("database.db")

    task = conn.execute(

        "SELECT * FROM tasks WHERE id=?",

        (id,)

    ).fetchone()

    conn.close()

    return render_template(

        "edit.html",

        task=task

    )


# UPDATE TASK
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    title = request.form["title"]

    deadline = request.form["deadline"]

    status = request.form["status"]

    conn = sqlite3.connect("database.db")

    conn.execute("""

    UPDATE tasks

    SET
    title=?,
    deadline=?,
    status=?

    WHERE id=?

    """,

    (title, deadline, status, id)

    )

    conn.commit()

    conn.close()

    return redirect("/")


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("user", None)

    session.pop("role", None)

    return redirect("/login")


# EXPORT REPORT
@app.route("/report")
def report():

    if "user" not in session:

        return redirect("/login")

    conn = sqlite3.connect("database.db")

    # ADMIN EXPORT
    if session.get("role") == "admin":

        data = conn.execute("""

        SELECT * FROM tasks

        """).fetchall()

    # EMPLOYEE EXPORT
    else:

        data = conn.execute("""

        SELECT * FROM tasks

        WHERE username=?

        """,

        (session["user"],)

        ).fetchall()

    conn.close()

    df = pd.DataFrame(

        data,

        columns=[

            "ID",
            "Username",
            "Task",
            "Deadline",
            "Priority",
            "Status"

        ]

    )

    df.to_csv(

        "reports/task_report.csv",

        index=False

    )

    return send_file(

        "reports/task_report.csv",

        as_attachment=True

    )


# RUN APP
if __name__ == "__main__":

    app.run(debug=True)