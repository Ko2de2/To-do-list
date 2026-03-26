# python app.py
from flask import Flask, render_template, jsonify, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app)

print("Current directory:", os.getcwd())
print("Database will be created at:", os.path.join(os.getcwd(), 'test.db'))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    deadline = db.Column(db.String(50), nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # get the information based in index.html
        task_content = request.form["content"]      
        task_deadline = request.form["deadline"]   
        task_explanation = request.form["explanation"]
        
        # put the information on Todo class/models
        new_task = Todo(
            content=task_content,
            deadline=task_deadline,
            explanation=task_explanation
        )
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue while adding your task"
        
    else:
        # where the tasks come from
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/AI_processing', methods=["POST"])
def AI_processing():
    user_input = request.json.get('text', '')

    ai_response = requests.get(f"https://text.pollinations.ai/{user_input}")

    return jsonify({'response': ai_response.text})

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "There was an issue when deleting"
    
@app.route('/update/<int:id>',  methods=["GET", "POST"])
def update(id):
    task_to_delete = Todo.query.get_or_404(id)
    
    if request.method == "POST":
        task_content = request.form["content"]
        task_deadline = request.form["deadline"]   
        task_explanation = request.form["explanation"]

        new_task = Todo(
            content=task_content,
            deadline=task_deadline,
            explanation=task_explanation
        )

        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue when updating"
        
    else:
        task = Todo.query.get_or_404(id)
        return render_template('update.html', task=task)          

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


