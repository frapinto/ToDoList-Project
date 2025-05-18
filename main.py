from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path= find_dotenv()
load_dotenv(dotenv_path)

API_KEY= os.getenv("TopSecretApiKey")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SECRET_KEY'] = API_KEY

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime)
    deadline = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)


@app.route('/add', methods=["POST"])
def add():
    task = request.form['todo']
    deadline_str = request.form['deadline']

    deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None
    new_todo = Todo(
        task=task,
        done=False,
        created=datetime.utcnow(),
        deadline=deadline
    )
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit(id):
    todo = Todo.query.get_or_404(id)
    if request.method == "POST":
        todo.task = request.form["todo"]
        deadline_str = request.form.get("deadline")
        todo.deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M') if deadline_str else None
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", todo=todo)

@app.route('/check/<int:id>')
def check(id):
    todo = Todo.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for("index"))

@app.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)