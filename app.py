from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(500))


# db.create_all()

todos = {
    1: {"task": "Write Hell World Program", "summary": "write the code"},
    2: {"task": "Task 2", "summary": "writing task 2"},
    3: {"task": "Task 3", "summary": "writing task 3"}
}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument(
    "task", type=str, help="Task is required", required=True)
task_post_args.add_argument(
    "summary", type=str, help="Summary is required", required=True)

task_update_args = reqparse.RequestParser()
task_update_args.add_argument("task", type=str)
task_update_args.add_argument("summary", type=str)

resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String,
}


class ToDoList(Resource):
    def get(self):
        #     return todos
        tasks = ToDoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"task": task.task, "summary": task.summary}
        return todos


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        # return todos[todo_id]
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="could not find task with that id")
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="task id taken...")
        todo = ToDoModel(
            id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        # if todo_id in todos:
        #     abort(409, "Task ID already taken")
        # todos[todo_id] = {"task": args["task"], "summary": args["summary"]}
        # return todos[todo_id]
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_update_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="task doesn't exist, cannot update")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task
        # if todo_id not in todos:
        #     abort(404, message="Task doesn't exist, cannot update")
        # if args['task']:
        #     todos[todo_id]['task'] = args['task']
        # if args['summary']:
        #     todos[todo_id]['summary'] = args['summary']
        # return todos[todo_id]

    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        return 'ToDo Deleted', 204
        # del todos[todo_id]
        # return todos


api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoList, '/todos')

if __name__ == '__main__':
    app.run(debug=True)
