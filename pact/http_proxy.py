from flask import Flask, jsonify

app = Flask(__name__)

# app.config["DEBUG"] = True

def handler():
    return {
        'documentId': '12334',
        'documentType': 'docx'
    }

@app.route('/')
def home():
    res = jsonify(handler())
    res.status_code = 200
    print(res)
    return res


if __name__ == '__main__':
    app.run(debug=True, port=5001)
