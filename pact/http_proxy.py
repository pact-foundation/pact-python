from flask import Flask, jsonify
from message_provider import handler
app = Flask(__name__)

# app.config["DEBUG"] = True


@app.route('/')
def home():
    res = jsonify(handler())
    res.status_code = 200
    print(res)
    return res


if __name__ == '__main__':
    app.run(debug=True, port=5001)
