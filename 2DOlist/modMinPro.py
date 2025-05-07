from urllib import request
from flask import app
import pandas as pd
import sqlite3
from datetime import datetime
#users = pd.DataFrame(columns=["user_id", "username"])  # ajouter utilisateurs si je suis chaud

class Users:
    pass
    



class Task:
    

    # Constructeur
    def __init__(self, title: str, description: str):
        self.titre = title
        self.description = description

        # Insérer directement sans recréer la table
        connection = sqlite3.connect("task.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description) VALUES (?, ?)
        """, (self.titre, self.description))
        connection.commit()
        connection.close()

    @staticmethod#créer la bd
    def init_db():
        connection = sqlite3.connect("task.db")
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP 
            )
        """)
        connection.commit()
        connection.close()

    # Méthodes GET 
    @staticmethod
    def get_tasks():
        connection = sqlite3.connect("task.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, description, date FROM tasks")
        rows = cursor.fetchall()
        connection.close()
        # reformater la date
        tasks = []
        for row in rows:
            date_obj = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%d/%m/%Y")
            tasks.append((row[0], row[1], row[2], formatted_date))
        
        return tasks
        
    
    def get_titre(self):
        return self.titre

    def get_description(self):
        return self.description
    #methodes statiques pour ne pas avoir à les initier
    #supprimer une tache
    @staticmethod
    def delete_task(task_id):
        conn = sqlite3.connect('task.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    @staticmethod #modifier une tache
    def update_task(task_id, title, description):
        conn = sqlite3.connect('task.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET title = ?, description = ? WHERE id = ?", (title, description, task_id))
        conn.commit()
        conn.close()  

