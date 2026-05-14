from flask import Flask, render_template, request, redirect, session
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "smartoffice"

# CREATE STATIC FOLDER IF NOT EXISTS
if not os.path.exists("static"):
    os.makedirs("static")


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

    user = conn.execute(
        """
        SELECT * FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        session["user"] = username
        return redirect("/")

    else:
        return "Invalid Username or Password"


# HOME PAGE
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")

    data = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    # ANALYTICS
    total_tasks = len(data)

    completed_tasks = 0

    pending_tasks = 0

    high_priority = 0

    for task in data:

        # task structure:
        # 0 = id
        # 1 = title
        # 2 = deadline
        # 3 = priority
        # 4 = status

        if task[4] == "Completed":
            completed_tasks += 1

        else:
            pending_tasks += 1

        if task[3] == "High":
            high_priority += 1

    # AI SMART SUGGESTIONS
    suggestion = ""

    if pending_tasks >= 5:
        suggestion = "⚠ Too many pending tasks! Focus on completing them."

    elif high_priority >= 3:
        suggestion = "🔥 You have multiple high priority tasks."

    elif completed_tasks == total_tasks and total_tasks > 0:
        suggestion = "✅ Excellent productivity! All tasks completed."

    else:
        suggestion = "👍 Productivity is under control."

    # CREATE ANALYTICS CHART
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


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ADD TASK
@app.route("/add", methods=["POST"])
def add_task():

    title = request.form["title"]

    deadline = request.form["deadline"]

    # SMART PRIORITY LOGIC
    today = datetime.today()

    task_date = datetime.strptime(
        deadline,
        "%Y-%m-%d"
    )

    diff = (task_date - today).days

    if diff <= 1:
        priority = "High"

    elif diff <= 3:
        priority = "Medium"

    else:
        priority = "Low"

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO tasks
        (title, deadline, priority, status)

        VALUES
        (?, ?, ?, ?)
        """,
        (title, deadline, priority, "Pending")
    )

    conn.commit()

    conn.close()

    return redirect("/")


# DELETE TASK
@app.route("/delete/<int:id>")
def delete_task(id):

    conn = sqlite3.connect("database.db")

    conn.execute(
        "DELETE FROM tasks WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect("/")


# EDIT TASK PAGE
@app.route("/edit/<int:id>")
def edit_task(id):

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
def update_task(id):

    title = request.form["title"]

    deadline = request.form["deadline"]

    status = request.form["status"]

    # SMART PRIORITY
    today = datetime.today()

    task_date = datetime.strptime(
        deadline,
        "%Y-%m-%d"
    )

    diff = (task_date - today).days

    if diff <= 1:
        priority = "High"

    elif diff <= 3:
        priority = "Medium"

    else:
        priority = "Low"

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        UPDATE tasks

        SET
            title=?,
            deadline=?,
            priority=?,
            status=?

        WHERE id=?
        """,
        (title, deadline, priority, status, id)
    )

    conn.commit()

    conn.close()

    return redirect("/")


# RUN APP
if __name__ == "__main__":
    app.run(debug=True)