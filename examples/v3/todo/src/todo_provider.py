from flask import Flask, Response, request, jsonify
from json2xml import json2xml
from json2xml.utils import readfromstring
import json


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return ''

    @app.route('/projects')
    def projects():
        todo_response = [
            {
                'id': 1,
                'name': "Project 1",
                'type': "activity",
                'due': "2016-02-11T09:46:56.023Z",
                'tasks': [
                    {
                        'done': True,
                        'id': 1,
                        'name': "Task 1",
                    },
                    {
                        'done': True,
                        'id': 2,
                        'name': "Task 2",
                    },
                    {
                        'done': True,
                        'id': 3,
                        'name': "Task 3",
                    },
                    {
                        'done': True,
                        'id': 4,
                        'name': "Task 4",
                    },
                ]
            }
        ]
        if request.headers['accept'] == 'application/xml':
            print("todo_response")
            print(readfromstring(json.dumps(todo_response)))
            print(json2xml.Json2xml(readfromstring(json.dumps(todo_response)), wrapper='projects').to_xml())
            return Response(json2xml.Json2xml(readfromstring(json.dumps(todo_response)), wrapper='projects').to_xml(), mimetype='application/xml')
        else:
            return jsonify(todo_response)

    return app


if __name__ == '__main__':
    create_app().run(debug=True, port=5001)
