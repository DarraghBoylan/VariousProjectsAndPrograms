from flask import Flask, render_template, redirect, url_for, request
from modMinPro import Task
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    tasks = Task.get_tasks()
    return render_template("vueMinPro.html", tasks=tasks)



@app.route("/submit", methods=["POST"])
def submit():
    task = request.form.get("newTask")
    description = request.form.get("descTask")
    nouvtache=Task(task, description)#nouvel objet task
    tasks = Task.get_tasks()#print la bd dans le terminal pour voir
    #print("=== taches dans la bd ===")
    #for t in tasks: #print la bd dans le terminal pour voir
    #   print(f"ID: {t['id']}, Titre: {t['title']}, Description: {t['description']}")
    return redirect(url_for("home"))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    Task.delete_task(task_id)
    return redirect(url_for('home'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    title = request.form['title']
    description = request.form['description']
    Task.update_task(task_id, title, description)
    return redirect(url_for('home'))


if __name__ == "__main__":
    Task.init_db()
    app.run(debug=True)