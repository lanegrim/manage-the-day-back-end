from flask import Flask, request, jsonify
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from sqlalchemy_serializer import SerializerMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "https://data.heroku.com/datastores/9b86d52c-b21a-4337-80cd-6292b2d55f63"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)


#################################
# MODELS
#################################

# Board Model


class BoardsModel(db.Model, SerializerMixin):
    __tablename__ = 'boards'

    serialize_rules = ('-columns.board',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    columns = db.relationship('ColumnsModel', backref='board', lazy=True)

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f"< {self.title}>"


# Column Model


class ColumnsModel(db.Model, SerializerMixin):
    __tablename__ = 'columns'

    serialize_rules = ('-todos.column',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    todos = db.relationship('TodosModel', backref='column', lazy=True)
    board_id = db.Column(db.Integer, db.ForeignKey(
        'boards.id'), nullable=False)

    def __init__(self, title, board_id):
        self.title = title
        self.board_id = board_id

    def __repr__(self):
        return f"< {self.title}>"

# To-do Model


class TodosModel(db.Model, SerializerMixin):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String())
    column_id = db.Column(db.Integer, db.ForeignKey(
        'columns.id'), nullable=False)
    completed = db.Column(db.Boolean())

    def __init__(self, task, column_id, completed):
        self.task = task
        self.column_id = column_id
        self.completed = completed

    def __repr__(self):
        return f"< {self.task}>"


#################################
# BOARD CRUD ROUTES
#################################

# Create and retrieve all boards


@app.route('/boards', methods=['POST', 'GET'])
def handle_boards():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_board = BoardsModel(
                title=data['title'])
            db.session.add(new_board)
            db.session.commit()
            return {"message": f"board {new_board.title} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        boards = BoardsModel.query.all()
        results = [
            {
                "id": board.id,
                "title": board.title,
            } for board in boards]

        return {"count": len(results), "boards": results}


# Retrieve, update, or delete one board by ID
@app.route('/boards/<board_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_board(board_id):
    board = BoardsModel.query.get_or_404(board_id)
    dict_board = board.to_dict()

    if request.method == 'GET':
        response = {
            "title": dict_board['title'],
            "columns": dict_board['columns'],
        }
        return {"message": "success", "board": response}

    elif request.method == 'PUT':
        data = request.get_json()
        board.title = data['title'],
        db.session.add(board)
        db.session.commit()
        return {"message": f"board {board.title} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(board)
        db.session.commit()
        return {"message": f"board {board.title} successfully deleted."}

#################################
# COLUMN CRUD ROUTES
#################################

# Create and retrieve all columns


@app.route('/columns', methods=['POST', 'GET'])
def handle_columns():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_column = ColumnsModel(
                title=data['title'],
                board_id=data['board_id'])
            db.session.add(new_column)
            db.session.commit()
            return {"message": f"column {new_column.title} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        columns = ColumnsModel.query.all()
        results = [
            {
                "id": column.id,
                "title": column.title,
                "board_id": column.board_id,
            } for column in columns]

        return {"count": len(results), "columns": results}

# Retrieve, update, or delete one column by ID


@app.route('/columns/<column_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_column(column_id):
    column = ColumnsModel.query.get_or_404(column_id)
    dict_column = column.to_dict()

    if request.method == 'GET':
        response = {
            "title": dict_column['title'],
            "todos": dict_column['todos'],
            "board_id": dict_column['board_id'],
        }
        return {"message": "success", "column": response}

    elif request.method == 'PUT':
        data = request.get_json()
        column.title = data['title'],
        column.board_id = data['board_id']
        db.session.add(column)
        db.session.commit()
        return {"message": f"column {column.title} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(column)
        db.session.commit()
        return {"message": f"column {column.title} successfully deleted."}

#################################
# TO_DO CRUD ROUTES
#################################

# Create and retrieve all to-dos


@app.route('/todos', methods=['POST', 'GET'])
def handle_todos():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_todo = TodosModel(
                task=data['task'],
                column_id=data['column_id'],
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
                "id": todo.id,
                "task": todo.task,
                "column_id": todo.column_id,
                "completed": todo.completed,
            } for todo in todos]

        return {"count": len(results), "todos": results}

# Retrieve, update, or delete one to-do by ID


@app.route('/todos/<todo_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_todo(todo_id):
    todo = TodosModel.query.get_or_404(todo_id)
    dict_todo = todo.to_dict()

    if request.method == 'GET':
        response = {
            "id": dict_todo['id'],
            "task": dict_todo['task'],
            "column_id": dict_todo['column_id'],
            "completed": dict_todo['completed'],
        }
        return {"message": "success", "todo": response}

    elif request.method == 'PUT':
        data = request.get_json()
        todo.task = data['task']
        todo.column_id = data['column_id']
        todo.completed = data['completed']
        db.session.add(todo)
        db.session.commit()
        return {"message": f"todo {todo.task} successfully updated"}

    elif request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()
        return {"message": f"todo {todo.task} successfully deleted."}
