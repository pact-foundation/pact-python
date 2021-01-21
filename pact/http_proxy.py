from flask import Flask, jsonify

app = Flask(__name__)

app.config["DEBUG"] = True

def handler():
    return {
        'documentId': '12334',
        'documentType': 'docx'
    }

@app.route('/', methods=['GET'])
def home():
    jsonify(handler())

app.run()