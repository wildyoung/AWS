import os

from flask import Flask, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")


@app.route("/")
def index():
    tasks = session.get("tasks", {})
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    time = request.form.get("time")
    task = request.form.get("task")

    if time and task:
        tasks = session.get("tasks", {})
        tasks[time] = task
        session["tasks"] = tasks
        session.modified = True

    return redirect(url_for("index"))


@app.route("/delete/<time>")
def delete(time):
    tasks = session.get("tasks", {})

    if time in tasks:
        del tasks[time]
        session["tasks"] = tasks
        session.modified = True

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
