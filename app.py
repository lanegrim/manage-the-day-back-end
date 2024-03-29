from flask import Flask, request, jsonify
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from sqlalchemy_serializer import SerializerMixin
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://kzeiikfzxqumzz:3ae3888c9f3dd012a82ba83d668f53a8975836a2a99794ca0145a9c7f22ec8b8@ec2-54-205-183-19.compute-1.amazonaws.com:5432/dbm4r4rgqj1n7"
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
    owner = db.Column(db.String())
    columns = db.relationship(
        'ColumnsModel', backref='board', lazy=True, cascade="all, delete")
    columnOrder = db.Column(db.String())
    collaborators = db.Column(db.String())

    def __init__(self, title, owner, columnOrder, collaborators):
        self.title = title
        self.owner = owner
        self.columnOrder = columnOrder
        self.collaborators = collaborators

    def __repr__(self):
        return f"< {self.title}>"


# Column Model


class ColumnsModel(db.Model, SerializerMixin):
    __tablename__ = 'columns'

    serialize_rules = ('-todos.column',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    todos = db.relationship('TodosModel', backref='column',
                            lazy=True, cascade="all, delete")
    board_id = db.Column(db.Integer, db.ForeignKey(
        'boards.id'), nullable=False)
    todoOrder = db.Column(db.ARRAY(db.String()), nullable=True)

    def __init__(self, title, board_id, todoOrder):
        self.title = title
        self.board_id = board_id
        self.todoOrder = todoOrder

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
                title=data['title'],
                owner=data['owner'],
                columnOrder=data['columnOrder'],
                collaborators=data['collaborators'])
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
                "owner": board.owner,
                "columnOrder": board.columnOrder,
                "collaborators": board.collaborators
            } for board in boards]

        return {"count": len(results), "boards": results}


# Retrieve, update, or delete one board by ID
@app.route('/boards/<board_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_board(board_id):
    board = BoardsModel.query.get_or_404(board_id)
    dict_board = board.to_dict()

    if request.method == 'GET':
        response = {
            "id": dict_board['id'],
            "title": dict_board['title'],
            "columns": dict_board['columns'],
            "columnOrder": dict_board['columnOrder'],
            "owner": dict_board['owner'],
            "collaborators": dict_board['collaborators']
        }
        return {"message": "success", "board": response}

    elif request.method == 'PUT':
        data = request.get_json()
        board.title = data['title'],
        board.columnOrder = data['columnOrder'],
        board.collaborators = data['collaborators'],
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
                board_id=data['board_id'],
                todoOrder=data['todoOrder'])
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
            "id": dict_column['id'],
            "title": dict_column['title'],
            "todos": dict_column['todos'],
            "board_id": dict_column['board_id'],
            "todoOrder": dict_column['todoOrder']
        }
        return {"message": "success", "column": response}

    elif request.method == 'PUT':
        data = request.get_json()
        column.title = data['title'],
        column.board_id = data['board_id'],
        column.todoOrder = data['todoOrder']
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
