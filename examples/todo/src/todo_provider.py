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
        # TODO:- Updated response to matche consumer req for xml
        # should use provider states here or matchers
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
                        'name': "Do the laundry",
                    },
                    {
                        'done': False,
                        'id': 2,
                        'name': "Do the dishes",
                    },
                    {
                        'done': False,
                        'id': 3,
                        'name': "Do the backyard",
                    },
                    {
                        'done': False,
                        'id': 4,
                        'name': "Do nothing",
                    },
                ]
            }
        ]
        if request.headers['accept'] == 'application/xml':
            print("todo_response")
            print(json2xml.Json2xml(readfromstring(json.dumps(todo_response)), wrapper='projects', pretty=True).to_xml())
            return Response(json2xml.Json2xml(readfromstring(json.dumps(todo_response)), wrapper='projects').to_xml(), mimetype='application/xml')
        else:
            return jsonify(todo_response)

    @app.route('/projects/<id>/images', methods=['POST'])
    def images(id):
        # TODO:- do something with the binary that has been uploaded
        return Response(status=201)

    return app


if __name__ == '__main__':
    create_app().run(debug=True, port=5001)
