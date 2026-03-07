import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# PostgreSQL untuk Render
database_url = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

# Fix untuk PostgreSQL Render (postgres -> postgresql)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# MODEL DATABASE
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    repeat = db.Column(db.String(20))
    priority = db.Column(db.Integer, default=0)
# CREATE TABLE AUTOMATIC
with app.app_context():
    db.create_all()


# FORMAT MASA 12 JAM
@app.template_filter("format_time")
def format_time(value):
    try:
        t = datetime.strptime(value, "%H:%M")
        return t.strftime("%I:%M %p")
    except:
        return value


# HALAMAN UTAMA
@app.route("/")
def index():
    tasks = Task.query.order_by(Task.priority).all()
    return render_template("index.html", tasks=tasks)


# TAMBAH TASK
@app.route("/add", methods=["GET", "POST"])
def add_task():

    if request.method == "POST":

        title = request.form["title"]
        date = request.form["date"]
        time = request.form["time"]
        repeat = request.form["repeat"]

        new_task = Task(
            title=title,
            date=date,
            time=time,
            repeat=repeat
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_task.html")


# EDIT TASK
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    task = Task.query.get_or_404(id)

    if request.method == "POST":

        task.title = request.form["title"]
        task.date = request.form["date"]
        task.time = request.form["time"]
        task.repeat = request.form["repeat"]

        db.session.commit()

        return redirect(url_for("index"))

    return render_template("edit_task.html", task=task)


# DELETE TASK
@app.route("/delete/<int:id>")
def delete_task(id):

    task = Task.query.get_or_404(id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for("index"))


# SUSUN PRIORITY TASK
@app.route("/priority/<int:id>/<int:value>")
def change_priority(id, value):

    task = Task.query.get_or_404(id)
    task.priority += value

    db.session.commit()

    return redirect(url_for("index"))


# CREATE TABLE + RUN LOCAL
if __name__ == "__main__":



    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)