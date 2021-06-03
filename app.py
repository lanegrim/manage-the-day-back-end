from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/todos"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/')
def hello():
    return {"hello": "world"}


if __name__ == '__main__':
    app.run(debug=True)


class TodosModel(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String())
    column = db.Column(db.String())
    completed = db.Column(db.Boolean())

    def __init__(self, task, column, completed):
        self.task = task
        self.column = column
        self.completed = completed

    def __repr__(self):
        return f"< {self.task}>"


@app.route('/todos', methods=['POST', 'GET'])
def handle_todos():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_todo = TodosModel(
                task=data['task'],
                column=data['column'],
                completed=data['completed'])
            db.session.add(new_todo)
            db.session.commit()
            return {"message": f"task {new_todo.task} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        todos = TodosModel.query.all()
        results = [
            {
                "task": todo.task,
                "column": todo.column,
                "completed": todo.completed,
            } for todo in todos]

        return {"count": len(results), "todos": results}


@app.route('/todos/<todo_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_todo(todo_id):
    todo = TodosModel.query.get_or_404(todo_id)

    if request.method == 'GET':
        response = {
            "task": todo.task,
            "column": todo.column,
            "completed": todo.completed,
        }
        return {"message": "success", "todo": response}

    elif request.method == 'PUT':
        data = request.get_json()
        todo.task = data['task']
        todo.column = data['column']
        todo.completed = data['completed']
        db.session.add(todo)
        db.session.commit()
        return {"message": f"todo {todo.task} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        return {"message": f"todo {todo.task} successfully deleted."}
