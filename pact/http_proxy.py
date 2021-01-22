from flask import Flask, jsonify
import sys
import json

app = Flask(__name__)

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))


@app.route('/')
def home():
    res = jsonify(sys.argv[1])
    res.status_code = 200
    print(res)
    return res


if __name__ == '__main__':
    app.run(debug=True, port=5001)
